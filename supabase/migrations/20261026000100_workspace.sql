-- One catalog, reproducible screening snapshots, and a separate acquisition log.
-- Geometry is GeoJSON; PostgreSQL's native GiST box index serves viewport queries.
-- The feet-based placement engine lives in tools/screening, not in client code.
create table public.workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(name) between 1 and 120),
  owner_id uuid not null references auth.users(id),
  revision bigint not null default 0,
  active_run uuid,
  created_at timestamptz not null default now(),
  unique(owner_id)
);
create table public.workspace_members (
  workspace_id uuid not null references public.workspaces on delete cascade,
  user_id uuid not null references auth.users on delete cascade,
  primary key(workspace_id,user_id)
);
create function public.is_member(w uuid) returns boolean language sql stable security definer
set search_path = '' as $$
  select exists(select 1 from public.workspace_members where workspace_id=w and user_id=auth.uid());
$$;

create table public.parcels (
  workspace_id uuid not null references public.workspaces,
  account text not null check(account ~ '^[0-9]{13}$'),
  primary key(workspace_id,account)
);
create table public.sites (
  workspace_id uuid not null references public.workspaces,
  id text not null check(id ~ '^(S[0-9]{13}|A[0-9a-f]{24})$'),
  accounts text[] not null check(cardinality(accounts)>0),
  primary key(workspace_id,id), unique(workspace_id,accounts)
);
create table public.site_parcels (
  workspace_id uuid not null,
  site_id text not null,
  account text not null,
  primary key(workspace_id,site_id,account),
  foreign key(workspace_id,site_id) references public.sites,
  foreign key(workspace_id,account) references public.parcels
);
create table public.screening_runs (
  workspace_id uuid not null references public.workspaces,
  id uuid not null,
  fingerprint text not null,
  model jsonb not null,
  sources jsonb not null,
  scope text not null,
  expected_sites integer not null check(expected_sites>0),
  expected_parcels integer not null check(expected_parcels>0),
  status text not null default 'loading' check(status in ('loading','ready')),
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  primary key(workspace_id,id), unique(workspace_id,fingerprint)
);
alter table public.workspaces add constraint active_run_fk
  foreign key(id,active_run) references public.screening_runs(workspace_id,id);
create table public.screening_results (
  workspace_id uuid not null,
  run_id uuid not null,
  site_id text not null,
  address text not null,
  neighborhood text not null,
  area_sf double precision not null check(area_sf>=0),
  fits boolean not null,
  status text not null,
  geometry jsonb,
  bounds box,
  details jsonb not null,
  primary key(workspace_id,run_id,site_id),
  foreign key(workspace_id,run_id) references public.screening_runs,
  foreign key(workspace_id,site_id) references public.sites
);
create index screening_neighborhood on public.screening_results(workspace_id,run_id,neighborhood,fits,site_id);
create index screening_bounds on public.screening_results using gist(bounds);
create table public.saved_lists (
  workspace_id uuid not null references public.workspaces,
  id uuid not null,
  name text not null check(length(name) between 1 and 120),
  revision bigint not null,
  primary key(workspace_id,id)
);
create table public.list_items (
  workspace_id uuid not null,
  list_id uuid not null,
  site_id text not null,
  status text not null check(status in ('saved','visited','pursue','pass')),
  deleted boolean not null default false,
  revision bigint not null,
  updated_by uuid not null references auth.users,
  updated_at timestamptz not null default now(),
  primary key(workspace_id,list_id,site_id),
  foreign key(workspace_id,list_id) references public.saved_lists,
  foreign key(workspace_id,site_id) references public.sites
);
create table public.observations (
  workspace_id uuid not null,
  id uuid not null,
  site_id text not null,
  note text not null check(length(note) between 1 and 12000),
  block_rating integer check(block_rating between 1 and 5),
  observed_at timestamptz not null,
  received_at timestamptz not null default now(),
  author_id uuid not null references auth.users,
  revision bigint not null,
  primary key(workspace_id,id),
  foreign key(workspace_id,site_id) references public.sites
);
create table public.sync_events (
  workspace_id uuid not null references public.workspaces,
  revision bigint not null,
  kind text not null,
  payload jsonb not null,
  created_at timestamptz not null default now(),
  primary key(workspace_id,revision)
);
create table public.mutation_receipts (
  workspace_id uuid not null references public.workspaces,
  id uuid not null,
  actor_id uuid not null references auth.users,
  request jsonb not null,
  response jsonb not null,
  primary key(workspace_id,id)
);

-- All direct client access is read-only and constrained to a workspace.
do $$ declare t text; begin
  foreach t in array array['workspaces','workspace_members','parcels','sites','site_parcels',
    'screening_runs','screening_results','saved_lists','list_items','observations','sync_events','mutation_receipts'] loop
    execute format('alter table public.%I enable row level security',t);
    execute format('revoke all on public.%I from anon, authenticated',t);
    execute format('grant select on public.%I to authenticated',t);
    execute format('grant all on public.%I to service_role',t);
    execute format('create policy member_read on public.%I for select to authenticated using (public.is_member(%I))',
      t,case when t='workspaces' then 'id' else 'workspace_id' end);
  end loop;
end $$;

create function public.open_workspace() returns jsonb language plpgsql security definer set search_path='' as $$
declare w public.workspaces; lid uuid; rev bigint;
begin
  if auth.uid() is null then raise exception 'Sign in required' using errcode='42501'; end if;
  -- One workspace per owner; repeat sign-in reuses it on every device.
  insert into public.workspaces(name,owner_id) values('Inner Loop acquisitions',auth.uid())
    on conflict(owner_id) do nothing;
  select * into w from public.workspaces where owner_id=auth.uid() for update;
  insert into public.workspace_members values(w.id,auth.uid()) on conflict do nothing;
  if not exists(select 1 from public.saved_lists where workspace_id=w.id) then
    lid:=gen_random_uuid();
    update public.workspaces set revision=revision+1 where id=w.id returning revision into rev;
    insert into public.saved_lists values(w.id,lid,'Driving shortlist',rev);
    insert into public.sync_events values(w.id,rev,'list',jsonb_build_object('id',lid,'name','Driving shortlist','revision',rev),now());
  end if;
  return jsonb_build_object('id',w.id,'name',w.name);
end $$;

create function public.site_detail(w uuid, s text) returns jsonb language sql stable security definer set search_path='' as $$
  select to_jsonb(r)-'bounds' || jsonb_build_object('accounts',a.accounts)
  from public.screening_results r join public.workspaces x on x.id=r.workspace_id and x.active_run=r.run_id
  join public.sites a on a.workspace_id=r.workspace_id and a.id=r.site_id
  where r.workspace_id=w and r.site_id=s and public.is_member(w);
$$;

create function public.mutate(w uuid, mutation jsonb) returns jsonb language plpgsql security definer set search_path='' as $$
declare mid uuid:=(mutation->>'id')::uuid; kind text:=mutation->>'kind'; p jsonb:=mutation->'payload';
  old public.mutation_receipts; rev bigint; item public.list_items; payload jsonb; response jsonb;
  lid uuid; sid text; noteid uuid;
begin
  if not public.is_member(w) then raise exception 'Workspace access denied' using errcode='42501'; end if;
  if mid is null or p is null then raise exception 'Mutation id and payload required'; end if;
  -- Serializing writes on this row makes the event cursor safe across commits.
  perform 1 from public.workspaces where id=w for update;
  select * into old from public.mutation_receipts where workspace_id=w and id=mid;
  if found then
    if old.actor_id<>auth.uid() or old.request<>mutation then raise exception 'Mutation id reused with different content'; end if;
    return old.response;
  end if;
  if kind='save' then
    lid:=(p->>'list_id')::uuid; sid:=p->>'site_id';
    select * into item from public.list_items where workspace_id=w and list_id=lid and site_id=sid;
    if coalesce(item.revision,0)<>coalesce((p->>'expected_revision')::bigint,-1) then
      return jsonb_build_object('conflict',true,'current',to_jsonb(item));
    end if;
  elsif kind not in ('visit','list') then raise exception 'Unknown mutation kind'; end if;
  update public.workspaces set revision=revision+1 where id=w returning revision into rev;
  if kind='save' then
    insert into public.list_items values(w,lid,sid,p->>'status',coalesce((p->>'deleted')::boolean,false),rev,auth.uid(),now())
    on conflict(workspace_id,list_id,site_id) do update set status=excluded.status,deleted=excluded.deleted,
      revision=excluded.revision,updated_by=excluded.updated_by,updated_at=excluded.updated_at;
    select to_jsonb(i) into payload from public.list_items i where workspace_id=w and list_id=lid and site_id=sid;
    payload:=payload || jsonb_build_object('site',public.site_detail(w,sid));
  elsif kind='visit' then
    sid:=p->>'site_id'; noteid:=mid;
    insert into public.observations values(w,noteid,sid,p->>'note',(p->>'block_rating')::integer,
      coalesce((p->>'observed_at')::timestamptz,now()),now(),auth.uid(),rev);
    select to_jsonb(o) into payload from public.observations o where workspace_id=w and id=noteid;
    payload:=payload || jsonb_build_object('site',public.site_detail(w,sid));
  elsif kind='list' then
    lid:=mid;
    insert into public.saved_lists values(w,lid,p->>'name',rev);
    payload:=jsonb_build_object('id',lid,'name',p->>'name','revision',rev);
  end if;
  insert into public.sync_events(workspace_id,revision,kind,payload) values(w,rev,kind,payload);
  response:=jsonb_build_object('conflict',false,'revision',rev);
  insert into public.mutation_receipts values(w,mid,auth.uid(),mutation,response);
  return response;
end $$;

create function public.pull_changes(w uuid, after_revision bigint default 0) returns jsonb
language sql stable security definer set search_path='' as $$
  select coalesce(jsonb_agg(to_jsonb(e) order by e.revision),'[]'::jsonb) from (
    select revision,kind,payload from public.sync_events
    where workspace_id=w and revision>greatest(after_revision,0) and public.is_member(w)
    order by revision limit 250
  ) e;
$$;

create function public.browse_sites(w uuid, neighborhood_filter text default '', fit_only boolean default true,
  search_text text default '', after_site text default '', viewport double precision[] default null)
returns jsonb language sql stable security definer set search_path='' as $$
  select coalesce(jsonb_agg(to_jsonb(q) order by q.site_id),'[]'::jsonb) from (
    select r.site_id,r.address,r.neighborhood,r.area_sf,r.fits,r.status,r.geometry,
      r.details - 'layout' as details, s.accounts
    from public.screening_results r join public.workspaces w0 on w0.id=r.workspace_id and w0.active_run=r.run_id
    join public.sites s on s.workspace_id=r.workspace_id and s.id=r.site_id
    where r.workspace_id=w and public.is_member(w) and (not fit_only or r.fits)
      and (neighborhood_filter='' or r.neighborhood=neighborhood_filter)
      and (search_text='' or r.address ilike '%'||search_text||'%' or search_text=any(s.accounts))
      and r.site_id>after_site
      and (viewport is null or r.bounds && box(point(viewport[1],viewport[2]),point(viewport[3],viewport[4])))
    order by r.site_id limit 250
  ) q;
$$;
create function public.catalog_summary(w uuid) returns jsonb language sql stable security definer set search_path='' as $$
  select jsonb_build_object('run',to_jsonb(run),'neighborhoods',coalesce((
    select jsonb_agg(to_jsonb(n) order by n.name) from (
      select neighborhood as name,count(*) as sites,count(*) filter(where fits) as fits
      from public.screening_results where workspace_id=w and run_id=x.active_run group by neighborhood
    ) n),'[]'::jsonb))
  from public.workspaces x left join public.screening_runs run on run.workspace_id=x.id and run.id=x.active_run
  where x.id=w and public.is_member(w);
$$;

revoke all on function public.is_member(uuid), public.open_workspace(),public.site_detail(uuid,text),
  public.mutate(uuid,jsonb),public.pull_changes(uuid,bigint),
  public.browse_sites(uuid,text,boolean,text,text,double precision[]),public.catalog_summary(uuid) from public,anon;
grant execute on function public.is_member(uuid),public.open_workspace(),public.site_detail(uuid,text),
  public.mutate(uuid,jsonb),public.pull_changes(uuid,bigint),
  public.browse_sites(uuid,text,boolean,text,text,double precision[]),public.catalog_summary(uuid) to authenticated;
