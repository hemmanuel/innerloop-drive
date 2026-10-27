"""Exercise the real import RPCs at full scale in a disposable local test DB.

Apply the migrations and bootstrap_local.sql first. This test never connects to
hosted Supabase, creates no real users, and leaves its fixture for inspection.
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import time
from pathlib import Path


USER = 'f0000000-0000-0000-0000-000000000002'


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snapshot', type=Path)
    ap.add_argument('--psql', required=True)
    ap.add_argument('--pg-port', required=True)
    ap.add_argument('--database', required=True)
    args = ap.parse_args()
    if not args.database.endswith('_test'):
        raise SystemExit('Use a disposable local database with a name ending in _test')
    manifest = json.loads((args.snapshot / 'manifest.json').read_text())
    source = args.snapshot / 'sites.jsonl.gz'
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest['fingerprint']:
        raise SystemExit('Snapshot checksum differs from manifest')
    command = [args.psql, '-h', '127.0.0.1', '-p', args.pg_port, '-U', 'postgres',
               '-d', args.database, '-X', '-qAt', '-v', 'ON_ERROR_STOP=1']

    def sql(statement, authenticated=False):
        if authenticated:
            statement = (f"begin; set local role authenticated; set local request.jwt.claim.sub='{USER}'; "
                         + statement + '; commit;')
        result = subprocess.run(command, input=statement, capture_output=True,
                                text=True, encoding='utf-8')
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout.strip() or 'null')

    sql(f"insert into auth.users(id) values('{USER}') on conflict do nothing")
    workspace = sql('select public.open_workspace()', True)['id']
    run = manifest['run_id']
    sql(f"set role service_role; select to_jsonb(public.import_begin('{workspace}',{literal(json.dumps(manifest))}::jsonb))")
    ready = sql(f"select to_jsonb(status='ready') from public.screening_runs where workspace_id='{workspace}' and id='{run}'")
    started = time.monotonic()
    if not ready:
        # One psql connection; each batch commits independently just like REST.
        # A file sink prevents either pipe from filling while the producer writes.
        with (args.snapshot / 'local-import.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log,
                                       stderr=log, text=True, encoding='utf-8')
            try:
                process.stdin.write('set standard_conforming_strings=on; set role service_role;\n')
                batch = []
                count = 0

                def send():
                    nonlocal count
                    payload = literal(json.dumps(batch, separators=(',', ':'), allow_nan=False))
                    process.stdin.write(f"select public.import_batch('{workspace}','{run}',{payload}::jsonb);\n")
                    process.stdin.flush()
                    count += len(batch)
                    if count % 15000 == 0:
                        print(f'Imported {count:,}/{manifest["sites"]:,}', flush=True)
                    batch.clear()

                with gzip.open(source, 'rt', encoding='utf-8') as records:
                    for line in records:
                        batch.append(json.loads(line))
                        if len(batch) == 150:
                            send()
                    if batch:
                        send()
                process.stdin.close()
                if process.wait() != 0:
                    raise RuntimeError('Import failed; inspect local-import.log')
            except BaseException:
                process.terminate()
                process.wait()
                raise
    activation = sql(f"set role service_role; select public.import_finish('{workspace}','{run}')")
    sql('analyze public.screening_results; analyze public.sites; analyze public.site_parcels;')
    timings = {}
    summary = None
    for name, query in [
        ('summary', f"select public.catalog_summary('{workspace}')"),
        ('first_page', f"select public.browse_sites('{workspace}')"),
        ('third_ward', f"select public.browse_sites('{workspace}',area_filter=>'Third Ward')")
    ]:
        before = time.monotonic()
        result = sql(query, True)
        timings[name] = round(time.monotonic() - before, 3)
        if name == 'summary':
            summary = result
        elif name == 'first_page' and not result:
            raise AssertionError('Expected qualifying sites in the full-Loop catalog')
    special = sql(f"select public.site_detail('{workspace}','S1155890110007')", True)
    if special and (special['fits'] or special['area_sf'] != 0):
        raise AssertionError('Condominium common-land false positive returned')
    size = sql("select jsonb_build_object('database_bytes',pg_database_size(current_database()),"
               "'public_table_bytes',(select sum(pg_total_relation_size(c.oid)) from pg_class c "
               "join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relkind='r'))")
    report = {'activation': activation, 'seconds': round(time.monotonic()-started, 1),
              'workspace': workspace, 'size': size, 'query_seconds_including_psql_startup': timings,
              'areas': summary['areas'], 'neighborhoods': len(summary['neighborhoods'])}
    (args.snapshot / 'local-import-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
