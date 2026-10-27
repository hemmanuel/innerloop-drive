"""Resume a public Harris County parcel download inside the study's 610 envelope.

Only public account IDs and polygon geometry are requested. Each page is atomic
and cached; the screening builder applies the precise Loop boundary afterwards.
"""
import argparse
import concurrent.futures
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

URL = 'https://www.gis.hctx.net/arcgis/rest/services/HCAD/Parcels/MapServer/0'


def request(params, endpoint='/query'):
    encoded = urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            req = urllib.request.Request(URL + endpoint + '?' + encoded,
                                         headers={'User-Agent':'InnerLoopDrive/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            if 'error' in data:
                raise RuntimeError(data['error'])
            return data
        except Exception:
            if attempt == 5:
                raise
            time.sleep(min(2**attempt, 20))


def atomic_json(path, obj):
    temp = path.with_suffix('.part')
    temp.write_text(json.dumps(obj,separators=(',',':')),encoding='utf-8')
    temp.replace(path)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--study',type=Path,required=True)
    ap.add_argument('--cache',type=Path,required=True)
    a=ap.parse_args(); a.cache.mkdir(parents=True,exist_ok=True)
    data=json.loads((a.study/'out/app/data.js').read_text(encoding='utf-8-sig').split('=',1)[1].strip().removesuffix(';'))
    ring=data['ring']; xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
    meta=a.cache/'service.json'
    if not meta.exists(): atomic_json(meta,request({'f':'json'},''))
    idfile=a.cache/'ids.json'
    if not idfile.exists():
        ids=request({'f':'json','where':'1=1','returnIdsOnly':'true','inSR':4326,
          'geometryType':'esriGeometryEnvelope','spatialRel':'esriSpatialRelIntersects',
          'geometry':f'{min(xs)},{min(ys)},{max(xs)},{max(ys)}'})
        if not ids.get('objectIds'):raise RuntimeError('No parcel IDs returned')
        atomic_json(idfile,ids)
    ids=sorted(json.loads(idfile.read_text())['objectIds'])
    # IIS rejects long GET query strings; 100 IDs stays below its URL limit.
    size=100
    chunks=[ids[i:i+size] for i in range(0,len(ids),size)]
    def page(pair):
        i,chunk=pair; out=a.cache/f'parcels-{i:05d}.json'
        if out.exists():return i,len(json.loads(out.read_text())['features'])
        result=request({'f':'geojson','objectIds':','.join(map(str,chunk)),
            'outFields':'OBJECTID,HCAD_NUM,acct_num,tax_year,parcel_type','returnGeometry':'true','outSR':4326})
        if len(result.get('features',[]))!=len(chunk):
            raise RuntimeError(f'Incomplete page {i}: {len(result.get("features",[]))}/{len(chunk)}')
        atomic_json(out,result)
        return i,len(chunk)
    print(f'{len(ids):,} parcel polygons; {len(chunks)} resumable pages',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for done,(i,n) in enumerate(pool.map(page,enumerate(chunks)),1):
            if done%25==0 or done==len(chunks):print(f'{done}/{len(chunks)} pages',flush=True)
    atomic_json(a.cache/'manifest.json',{'url':URL,'downloaded_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'object_count':len(ids),'pages':len(chunks),'envelope':[min(xs),min(ys),max(xs),max(ys)]})

if __name__=='__main__':main()
