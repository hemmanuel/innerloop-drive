"""Validate identities, membership, counts and actual placed geometry in a snapshot."""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
from site_identity import site_id


def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);a=ap.parse_args()
    path=a.source/'sites.jsonl.gz' if a.source.is_dir() else a.source
    open_file=gzip.open if path.suffix=='.gz' else open
    tofeet=Transformer.from_crs(4326,2278,always_xy=True).transform
    ids=set();single_accounts=set();all_members=set();counts=Counter();fits=0;errors=[];overlay_count=0
    with open_file(path,'rt',encoding='utf-8') as f:
        for line in f:
            r=json.loads(line);sid=r['site_id'];members=r['accounts'];all_members.update(members)
            if sid in ids:errors.append((sid,'duplicate site'))
            ids.add(sid)
            if site_id(members)!=sid:errors.append((sid,'identity does not match members'))
            if len(members)==1:single_accounts.add(members[0])
            counts[r['status']]+=1
            layout=r['details']['layout']
            if r['fits'] and (not layout['fits'] or r['details']['transit_distance_ft']>2640):errors.append((sid,'fit/transit mismatch'))
            if r['fits'] and r['details'].get('recorded_area_complete') is not True:errors.append((sid,'fit without recorded land area'))
            if r['fits'] and r['details'].get('shared_geometry_account_count',1)>1:errors.append((sid,'shared parcel geometry passed'))
            if not layout['fits']:continue
            fits+=1
            if r['area_sf']<10000:errors.append((sid,'small site passed'))
            g=transform(tofeet,shape(r['geometry']));allowed=g.buffer(.05)
            overlays=layout['overlays'];kinds=Counter(o['kind'] for o in overlays)
            if kinds['building']!=2 or kinds['parking']!=8:errors.append((sid,'wrong building/parking count'))
            obstacles=[];walks=[]
            for item in overlays:
                geom=transform(tofeet,shape(item['geometry']));overlay_count+=1
                # The curb marker is a reference line within the model's one-foot
                # entrance strip. Actual paving, buildings and paths stay inside.
                boundary=g.buffer(1.05) if item['kind']=='curb' else allowed
                if not boundary.covers(geom):errors.append((sid,'outside site: '+item['kind']))
                if item['kind']=='building' and abs(geom.area-1800)>.05:errors.append((sid,'building area changed'))
                if item['kind']=='parking' and abs(geom.area-171)>.05:errors.append((sid,'parking dimensions changed'))
                if item['kind'] in ('building','parking','drive'):obstacles.append(geom)
                if item['kind'] in ('walk','entry'):walks.append(geom)
            if any(w.intersection(o).area>.03 for w in walks for o in obstacles):errors.append((sid,'walking path crosses building/parking'))
    manifest=None
    if a.source.is_dir():
        manifest=json.loads((a.source/'manifest.json').read_text())
        if len(ids)!=manifest['sites'] or len(single_accounts)!=manifest['parcels']:errors.append(('manifest','counts differ'))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest['fingerprint']:errors.append(('manifest','checksum differs'))
        if not all_members.issubset(single_accounts):errors.append(('members','assembly member lacks single-parcel record'))
    report={'sites':len(ids),'parcels':len(single_accounts),'placed_layouts':fits,'checked_overlays':overlay_count,'counts':dict(counts),'errors':errors}
    print(json.dumps(report,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
