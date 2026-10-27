-- Neighborhood lookup does not need a unique site identifier in every key.
-- Removing it lets PostgreSQL deduplicate repeated neighborhood keys. A small
-- partial index retains ordered pagination for the default fitting-site view.
-- No records, geometry, precision, constraints or access policies change.
create index screening_neighborhood_lookup
  on public.screening_results(workspace_id,run_id,neighborhood);
create index screening_fitting_sites
  on public.screening_results(workspace_id,run_id,site_id) where fits;
drop index public.screening_neighborhood;
