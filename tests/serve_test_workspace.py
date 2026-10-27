"""LOCAL TEST FIXTURE ONLY. Simulated auth, real migration RPCs in disposable PG.

Binds 127.0.0.1 and only connects to a caller-specified local test database.
Never deploy this file. The production app talks directly to Supabase Auth/REST.
"""
import argparse,json,subprocess,uuid
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
USER='f0000000-0000-0000-0000-000000000001'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--psql',required=True);ap.add_argument('--pg-port',required=True)
    ap.add_argument('--database',required=True);ap.add_argument('--port',type=int,default=18781);a=ap.parse_args()
    def sql(command,auth=False):
        prefix=f"begin; set local role authenticated; set local request.jwt.claim.sub='{USER}'; " if auth else ''
        end='; commit;' if auth else ''
        p=subprocess.run([a.psql,'-h','127.0.0.1','-p',a.pg_port,'-U','postgres','-d',a.database,
            '-X','-qAt','-v','ON_ERROR_STOP=1','-c',prefix+command+end],capture_output=True,text=True,encoding='utf-8')
        if p.returncode:raise RuntimeError(p.stderr.strip())
        raw=p.stdout.strip()
        try:return json.loads(raw or 'null')
        except json.JSONDecodeError:return raw
    def literal(value):return "'"+str(value).replace("'","''")+"'"
    sql(f"insert into auth.users(id) values('{USER}') on conflict do nothing")
    w=sql('select public.open_workspace()',True)['id']
    rid='f1000000-0000-0000-0000-000000000001'
    manifest={'run_id':rid,'fingerprint':'browser-test-v1','model':{'version':'browser-test'},'sources':{},'scope':'Synthetic browser fixture','sites':2,'parcels':2}
    sql(f"select public.import_begin('{w}',{literal(json.dumps(manifest))}::jsonb)")
    ready=sql(f"select to_jsonb(status) from public.screening_runs where workspace_id='{w}' and id='{rid}'")=='ready'
    if not ready:
        fixtures=[]
        for i,lon in enumerate([-95.351,-95.353],1):
            fixtures.append({'site_id':f'S999999999999{i}','accounts':[f'999999999999{i}'],
              'address':f'{i}00 Workflow Test St','neighborhood':'Third Ward','area_sf':10500,'fits':True,'status':'wide_5',
              'geometry':{'type':'Polygon','coordinates':[[[lon,29.730],[lon+.0003,29.730],[lon+.0003,29.7303],[lon,29.7303],[lon,29.730]]]},
              'bbox':[lon,29.730,lon+.0003,29.7303],
              'details':{'transit_distance_ft':600,'campaign_area':'Third Ward','layout':{'reason':'40 × 45 ft / 5-ft sides','overlays':[]}}})
        sql(f"select public.import_batch('{w}','{rid}',{literal(json.dumps(fixtures))}::jsonb)")
    sql(f"select public.import_finish('{w}','{rid}')")
    allowed={'open_workspace','browse_sites','site_detail','pull_changes','mutate','catalog_summary'}
    def arg(name,value):
        if not name.replace('_','').isalnum():raise ValueError('Invalid argument')
        if value is None:return name+'=>null'
        if isinstance(value,bool):return name+'=>'+str(value).lower()
        if isinstance(value,(int,float)):return name+'=>'+str(value)
        if isinstance(value,dict):return name+'=>'+literal(json.dumps(value))+'::jsonb'
        if isinstance(value,list):return name+'=>array['+','.join(str(float(x)) for x in value)+']::double precision[]'
        return name+'=>'+literal(value)
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'web/workspace'),**kwargs)
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin','*');self.send_header('Access-Control-Allow-Headers','authorization,apikey,content-type');super().end_headers()
        def do_OPTIONS(self):self.send_response(204);self.end_headers()
        def do_POST(self):
            try:
                body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
                if self.path.startswith('/auth/v1/token'):
                    result={'access_token':'fixture-token','refresh_token':'fixture-refresh','expires_in':3600,
                        'user':{'id':USER,'email':'fixture@example.test'}}
                else:
                    name=urlparse(self.path).path.rsplit('/',1)[-1]
                    if name not in allowed:raise ValueError('RPC not exposed by fixture')
                    result=sql('select public.'+name+'('+','.join(arg(k,v) for k,v in body.items())+')',True)
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({'message':str(e)}).encode())
        def log_message(self,format,*args):pass
    print(f'Test workspace at http://127.0.0.1:{a.port} (synthetic auth; real PostgreSQL)',flush=True)
    ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()

if __name__=='__main__':main()
