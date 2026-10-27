"""Idempotently upload a complete private snapshot; promote only after validation.

Credentials are read from the environment. Completed runs can be reselected
without rewriting results or any acquisition records.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('snapshot',type=Path);a=ap.parse_args()
    manifest=json.loads((a.snapshot/'manifest.json').read_text())
    source=a.snapshot/'sites.jsonl.gz'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['fingerprint']:
        raise SystemExit('Snapshot checksum does not match manifest')
    url=os.environ['SUPABASE_URL'].rstrip('/')
    key=os.environ.get('SUPABASE_SECRET_KEY') or os.environ.get('SUPABASE_SERVICE_ROLE_KEY','')
    w=os.environ['INNERLOOP_WORKSPACE_ID']
    if not url.startswith('https://'):raise SystemExit('SUPABASE_URL must use HTTPS')
    headers={'apikey':key,'Content-Type':'application/json'}
    if not key.startswith('sb_secret_'):
        try:
            encoded=key.split('.')[1]
            role=json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4))).get('role')
        except (ValueError,IndexError):role=None
        if role!='service_role':raise SystemExit('Set SUPABASE_SECRET_KEY (or a legacy SUPABASE_SERVICE_ROLE_KEY) in the import environment')
        headers['Authorization']='Bearer '+key
    def rpc(name,payload):
        raw=json.dumps(payload,allow_nan=False,separators=(',',':')).encode()
        for retry in range(5):
            try:
                req=urllib.request.Request(url+'/rest/v1/rpc/'+name,data=raw,
                    headers=headers)
                with urllib.request.urlopen(req,timeout=120) as r:return json.load(r)
            except urllib.error.HTTPError as e:
                body=e.read().decode().replace(key,'[redacted]')
                if e.code<500 and e.code!=429:raise RuntimeError(f'{name} HTTP {e.code}: {body}') from None
                if retry==4:raise RuntimeError(f'{name} HTTP {e.code}') from None
            except OSError:
                if retry==4:raise
            time.sleep(2**retry)
    rid=rpc('import_begin',{'w':w,'manifest':manifest})
    # A previous successful run needs no writes. Only the finish procedure can
    # expose it as current, and its counts are rechecked on every invocation.
    req=urllib.request.Request(url+f'/rest/v1/screening_runs?workspace_id=eq.{w}&id=eq.{rid}&select=status',
        headers=headers)
    with urllib.request.urlopen(req,timeout=30) as response:state=json.load(response)
    if state[0]['status']!='ready':
        batch=[];n=0
        with gzip.open(source,'rt',encoding='utf-8') as f:
            for line in f:
                batch.append(json.loads(line))
                if len(batch)==150:
                    rpc('import_batch',{'w':w,'rid':rid,'records':batch});n+=len(batch);batch=[]
                    if n%3000==0:print(f'Uploaded {n:,}/{manifest["sites"]:,}',flush=True)
        if batch:rpc('import_batch',{'w':w,'rid':rid,'records':batch})
    print(json.dumps(rpc('import_finish',{'w':w,'rid':rid}),indent=2))

if __name__=='__main__':main()
