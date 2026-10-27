-- Only the trusted import process can write catalog data. Never expose its key.
create function public.import_begin(w uuid, manifest jsonb) returns uuid language plpgsql security definer set search_path='' as $$
declare rid uuid:=(manifest->>'run_id')::uuid; previous public.screening_runs;
begin
  select * into previous from public.screening_runs where workspace_id=w and id=rid;
  if found then
    if previous.fingerprint<>manifest->>'fingerprint' then raise exception 'Run ID has different content'; end if;
    return rid;
  end if;
  insert into public.screening_runs(workspace_id,id,fingerprint,model,sources,scope,expected_sites,expected_parcels)
    values(w,rid,manifest->>'fingerprint',manifest->'model',manifest->'sources',manifest->>'scope',
      (manifest->>'sites')::integer,(manifest->>'parcels')::integer);
  return rid;
end $$;

create function public.import_batch(w uuid, rid uuid, records jsonb) returns integer
language plpgsql security definer set search_path='' as $$
declare r jsonb; accounts text[]; known text[]; a text; b jsonb; n integer:=0; ready boolean;
begin
  select status='ready' into ready from public.screening_runs where workspace_id=w and id=rid for update;
  if not found then raise exception 'Begin the run before importing'; end if;
  if ready then raise exception 'Completed screening runs are immutable'; end if;
  if jsonb_array_length(records)>500 then raise exception 'Batch limit is 500'; end if;
  for r in select value from jsonb_array_elements(records) loop
    select array_agg(distinct value order by value) into accounts from jsonb_array_elements_text(r->'accounts');
    select s.accounts into known from public.sites s where workspace_id=w and id=r->>'site_id';
    if found and known<>accounts then raise exception 'Site membership changed for %',r->>'site_id'; end if;
    insert into public.sites values(w,r->>'site_id',accounts) on conflict do nothing;
    foreach a in array accounts loop
      insert into public.parcels values(w,a) on conflict do nothing;
      insert into public.site_parcels values(w,r->>'site_id',a) on conflict do nothing;
    end loop;
    b:=r->'bbox';
    insert into public.screening_results values(w,rid,r->>'site_id',coalesce(r->>'address',''),r->>'neighborhood',
      (r->>'area_sf')::double precision,(r->>'fits')::boolean,r->>'status',nullif(r->'geometry','null'::jsonb),
      case when jsonb_typeof(b)='array' then box(point((b->>0)::double precision,(b->>1)::double precision),
        point((b->>2)::double precision,(b->>3)::double precision)) end, r->'details')
    on conflict(workspace_id,run_id,site_id) do update set address=excluded.address,neighborhood=excluded.neighborhood,
      area_sf=excluded.area_sf,fits=excluded.fits,status=excluded.status,geometry=excluded.geometry,bounds=excluded.bounds,details=excluded.details;
    n:=n+1;
  end loop;
  return n;
end $$;

create function public.import_finish(w uuid, rid uuid) returns jsonb language plpgsql security definer set search_path='' as $$
declare run public.screening_runs; n integer; p integer;
begin
  perform 1 from public.workspaces where id=w for update;
  select * into run from public.screening_runs where workspace_id=w and id=rid for update;
  if not found then raise exception 'Unknown screening run'; end if;
  select count(*), count(*) filter(where site_id like 'S%') into n,p from public.screening_results
    where workspace_id=w and run_id=rid;
  if n<>run.expected_sites or p<>run.expected_parcels then
    raise exception 'Incomplete run: %/% sites; %/% parcels',n,run.expected_sites,p,run.expected_parcels;
  end if;
  update public.screening_runs set status='ready',completed_at=coalesce(completed_at,now()) where workspace_id=w and id=rid;
  update public.workspaces set active_run=rid where id=w;
  return jsonb_build_object('run_id',rid,'sites',n,'parcels',p,'status','ready');
end $$;

revoke all on function public.import_begin(uuid,jsonb),public.import_batch(uuid,uuid,jsonb),public.import_finish(uuid,uuid)
  from public,anon,authenticated;
grant execute on function public.import_begin(uuid,jsonb),public.import_batch(uuid,uuid,jsonb),public.import_finish(uuid,uuid)
  to service_role;
