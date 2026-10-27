-- Run after migrations in a disposable Supabase/local PostgreSQL database.
-- Uses real roles, RLS, transactions and functions; rolls back every fixture.
begin;
create function pg_temp.assert(ok boolean, msg text) returns void language plpgsql as $$
begin if ok is distinct from true then raise exception 'FAIL: %',msg; end if; end $$;
insert into auth.users(id) values('10000000-0000-0000-0000-000000000001'),('10000000-0000-0000-0000-000000000002');
set local role authenticated;
select set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000001',true);
select set_config('test.workspace',public.open_workspace()->>'id',true);
select pg_temp.assert((public.open_workspace()->>'id')=current_setting('test.workspace'),'workspace is reused');
reset role;
select set_config('test.list',(select id::text from public.saved_lists where workspace_id=current_setting('test.workspace')::uuid),true);
set local role service_role;
select public.import_begin(current_setting('test.workspace')::uuid,'{
 "run_id":"20000000-0000-0000-0000-000000000001","fingerprint":"test-1","model":{"version":"test"},
 "sources":{},"scope":"test","sites":2,"parcels":2}');
select public.import_batch(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000001','[
 {"site_id":"S0000000000001","accounts":["0000000000001"],"address":"100 Test","neighborhood":"Third Ward","area_sf":10000,"fits":true,"status":"wide_5","geometry":{"type":"Polygon","coordinates":[[[-95.35,29.73],[-95.349,29.73],[-95.349,29.731],[-95.35,29.731],[-95.35,29.73]]]},"bbox":[-95.35,29.73,-95.349,29.731],"details":{}}
]');
do $$ begin
  perform public.import_finish(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000001');
  raise exception 'FAIL: incomplete import promoted';
exception when raise_exception then if SQLERRM not like 'Incomplete run:%' then raise; end if; end $$;
select public.import_batch(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000001','[
 {"site_id":"S0000000000002","accounts":["0000000000002"],"address":"200 Test","neighborhood":"Second Ward","area_sf":5000,"fits":false,"status":"below_area","geometry":null,"bbox":null,"details":{}}
]');
select public.import_finish(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000001');
set local role authenticated;
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid))=1,'default filter only fits');
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid,'',false))=2,'small parcels retained');
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid,'Second Ward',false))=1,'neighborhood filter');
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid,'',true,'','',array[-95.36,29.72,-95.34,29.74]))=1,'spatial viewport');
select set_config('test.save',jsonb_build_object('id','30000000-0000-0000-0000-000000000001','kind','save','payload',
  jsonb_build_object('list_id',current_setting('test.list'),'site_id','S0000000000001','status','saved','expected_revision',0))::text,true);
select pg_temp.assert((public.mutate(current_setting('test.workspace')::uuid,current_setting('test.save')::jsonb)->>'revision')::int=2,'save revision');
select pg_temp.assert((public.mutate(current_setting('test.workspace')::uuid,current_setting('test.save')::jsonb)->>'revision')::int=2,'lost acknowledgment retry');
select pg_temp.assert((select count(*) from public.list_items)=1,'save is idempotent');
select set_config('test.visit','{"id":"30000000-0000-0000-0000-000000000002","kind":"visit","payload":{"site_id":"S0000000000001","note":"Offline field visit","block_rating":4,"observed_at":"2026-10-26T12:00:00Z"}}',true);
select public.mutate(current_setting('test.workspace')::uuid,current_setting('test.visit')::jsonb);
select public.mutate(current_setting('test.workspace')::uuid,current_setting('test.visit')::jsonb);
select pg_temp.assert((select count(*) from public.observations)=1,'visit retry creates one observation');
select pg_temp.assert((public.mutate(current_setting('test.workspace')::uuid,
  jsonb_set(current_setting('test.save')::jsonb,'{id}','"30000000-0000-0000-0000-000000000003"'))->>'conflict')::boolean,'stale status produces conflict');
select pg_temp.assert(jsonb_array_length(public.pull_changes(current_setting('test.workspace')::uuid,0))=3,'event cursor excludes retry/conflict');
select pg_temp.assert(jsonb_array_length(public.pull_changes(current_setting('test.workspace')::uuid,3))=0,'cursor pulls only new events');
do $$ begin
  perform public.mutate(current_setting('test.workspace')::uuid,jsonb_set(current_setting('test.visit')::jsonb,'{payload,note}','"altered"'));
  raise exception 'FAIL: mutation reuse accepted';
exception when raise_exception then if SQLERRM not like 'Mutation id reused%' then raise; end if; end $$;
do $$ begin
  update public.list_items set status='pass';
  raise exception 'FAIL: direct client mutation allowed';
exception when insufficient_privilege then null; end $$;
do $$ begin
  perform public.import_finish(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000001');
  raise exception 'FAIL: client imported data';
exception when insufficient_privilege then null; end $$;
-- A second account cannot read or mutate the first account's inventory/notes.
select set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000002',true);
select public.open_workspace();
select pg_temp.assert((select count(*) from public.observations)=0,'RLS hides another workspace');
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid,'',false))=0,'RPC hides another workspace');
do $$ begin
  perform public.mutate(current_setting('test.workspace')::uuid,current_setting('test.visit')::jsonb);
  raise exception 'FAIL: cross-workspace mutation allowed';
exception when insufficient_privilege then null; end $$;
set local role anon;
do $$ begin
  perform public.open_workspace();
  raise exception 'FAIL: anonymous workspace allowed';
exception when insufficient_privilege then null; end $$;
reset role;
-- Repointing the catalog to another complete run cannot remove human records.
select set_config('request.jwt.claim.sub','10000000-0000-0000-0000-000000000001',true);
select public.import_begin(current_setting('test.workspace')::uuid,'{
 "run_id":"20000000-0000-0000-0000-000000000002","fingerprint":"test-2","model":{"version":"new"},
 "sources":{},"scope":"test","sites":2,"parcels":2}');
insert into public.screening_results select workspace_id,'20000000-0000-0000-0000-000000000002',site_id,
 address,neighborhood,area_sf,false,'no_fit',geometry,bounds,details from public.screening_results
 where run_id='20000000-0000-0000-0000-000000000001';
select public.import_finish(current_setting('test.workspace')::uuid,'20000000-0000-0000-0000-000000000002');
select pg_temp.assert((select count(*) from public.observations where workspace_id=current_setting('test.workspace')::uuid)=1,'rescreen preserves visits');
select pg_temp.assert((select count(*) from public.list_items where workspace_id=current_setting('test.workspace')::uuid)=1,'rescreen preserves saved sites');
select pg_temp.assert(jsonb_array_length(public.browse_sites(current_setting('test.workspace')::uuid))=0,'new model active atomically');
rollback;
\echo Workflow, import and RLS assertions passed.
