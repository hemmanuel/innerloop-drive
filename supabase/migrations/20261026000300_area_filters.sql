-- Broad campaign areas (Third Ward, Fifth Ward, etc.) and HCAD neighborhoods
-- are separate filters. Neither changes the Loop-wide inventory.
drop function public.browse_sites(uuid,text,boolean,text,text,double precision[]);
create function public.browse_sites(w uuid, neighborhood_filter text default '', fit_only boolean default true,
  search_text text default '', after_site text default '', viewport double precision[] default null, area_filter text default '')
returns jsonb language sql stable security definer set search_path='' as $$
  select coalesce(jsonb_agg(to_jsonb(q) order by q.site_id),'[]'::jsonb) from (
    select r.site_id,r.address,r.neighborhood,r.area_sf,r.fits,r.status,r.geometry,
      r.details - 'layout' as details, s.accounts
    from public.screening_results r join public.workspaces w0 on w0.id=r.workspace_id and w0.active_run=r.run_id
    join public.sites s on s.workspace_id=r.workspace_id and s.id=r.site_id
    where r.workspace_id=w and public.is_member(w) and (not fit_only or r.fits)
      and (neighborhood_filter='' or r.neighborhood=neighborhood_filter)
      and (area_filter='' or r.details->>'campaign_area'=area_filter)
      and (search_text='' or r.address ilike '%'||search_text||'%' or search_text=any(s.accounts))
      and r.site_id>after_site
      and (viewport is null or r.bounds && box(point(viewport[1],viewport[2]),point(viewport[3],viewport[4])))
    order by r.site_id limit 250
  ) q;
$$;
create or replace function public.catalog_summary(w uuid) returns jsonb language sql stable security definer set search_path='' as $$
  select jsonb_build_object('run',to_jsonb(run),'neighborhoods',coalesce((
    select jsonb_agg(to_jsonb(n) order by n.name) from (
      select neighborhood as name,count(*) as sites,count(*) filter(where fits) as fits
      from public.screening_results where workspace_id=w and run_id=x.active_run group by neighborhood
    ) n),'[]'::jsonb),'areas',coalesce((
    select jsonb_agg(to_jsonb(n) order by n.name) from (
      select details->>'campaign_area' as name,count(*) as sites,count(*) filter(where fits) as fits
      from public.screening_results where workspace_id=w and run_id=x.active_run group by details->>'campaign_area'
    ) n),'[]'::jsonb))
  from public.workspaces x left join public.screening_runs run on run.workspace_id=x.id and run.id=x.active_run
  where x.id=w and public.is_member(w);
$$;
revoke all on function public.browse_sites(uuid,text,boolean,text,text,double precision[],text) from public,anon;
grant execute on function public.browse_sites(uuid,text,boolean,text,text,double precision[],text) to authenticated;
