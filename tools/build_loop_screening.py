"""Screen every inside-610 account and conservative same-owner assemblies.

Read-only on the study. Writes a private, resumable snapshot for both Supabase
and the native app. No owner names or mailing addresses leave this process.
"""
import argparse,csv,gzip,hashlib,io,json,math,re,time,uuid,zipfile
from pathlib import Path
from collections import Counter,defaultdict
import duckdb
from shapely import STRtree,contains_xy,make_valid
from shapely.geometry import shape,Polygon,Point,mapping
from shapely.ops import transform,unary_union,snap
from pyproj import Transformer
from site_identity import site_id
from screening.streets import StreetScreen,norm
from screening.duplex_footprint import MODEL
from screening.land_scope import reported_area,scope_issue


def readjs(p):return json.loads(p.read_text(encoding='utf-8-sig').split('=',1)[1].strip().removesuffix(';'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    for name in ['study','geometry','roads','gtfs','output']:ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--enrichment',type=Path)
    ap.add_argument('--layout-cache',type=Path,help='Reuse proven identical placement inputs; always rescreen land scope')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    tofeet=Transformer.from_crs(4326,2278,always_xy=True).transform
    toll=Transformer.from_crs(2278,4326,always_xy=True).transform
    data=readjs(a.study/'out/app/data.js');loop=transform(tofeet,Polygon(data['ring']))
    manifest=json.loads((a.geometry/'manifest.json').read_text())
    pages=sorted(a.geometry.glob('parcels-*.json'))
    if len(pages)!=manifest['pages']:raise RuntimeError('Finish the parcel download first')
    print('Loading inside-610 accounts from the full study',flush=True)
    db=duckdb.connect(str(a.study/'houston.duckdb'),read_only=True)
    query='''select trim(r.acct) account,coalesce(r.site_addr_1,'') address,
      try_cast(r.land_ar as double) area_sf,coalesce(r.state_class,'') state_class,
      coalesce(r.lgl_1,'')||' '||coalesce(r.lgl_2,'')||' '||coalesce(r.lgl_3,'') legal_text,
      try_cast(r.land_val as double) land_value,try_cast(r.bld_val as double) building_value,
      trim(r.mailto) owner,trim(r.mail_addr_1) mail_addr,trim(r.mail_city) mail_city,trim(r.mail_state) mail_state,
      coalesce(n.dscr,'HCAD neighborhood '||trim(r.Neighborhood_Code)) neighborhood,
      g.x,g.y,g.fld_zone,g.in_sfha
      from raw_real_acct r join parcel_geo g on trim(g.acct)=trim(r.acct)
      left join raw_nbhd n on trim(n.cd)=trim(r.Neighborhood_Code)
      where g.x between ? and ? and g.y between ? and ?'''
    xmin,ymin,xmax,ymax=loop.bounds
    res=db.execute(query,[xmin,xmax,ymin,ymax]);cols=[d[0] for d in res.description]
    accounts={}
    for row in res.fetchall():
        r=dict(zip(cols,row))
        if loop.contains(Point(r['x'],r['y'])):
            if r['account'] in accounts and r!=accounts[r['account']]:raise RuntimeError('Conflicting study rows for '+r['account'])
            accounts[r['account']]=r
    db.close();print(f'{len(accounts):,} accounts inside the Loop',flush=True)
    # Add the campaign-area names alongside HCAD subdivision neighborhoods.
    areas={r['acct']:r['area'] for r in csv.DictReader((a.study/'out/coliving/hidden/area_by_account.csv').open(encoding='utf-8-sig'))}
    polys={};years=Counter();raw_count=0;geometry_hash=hashlib.sha256()
    for file in pages:
        raw=file.read_bytes();geometry_hash.update(raw)
        for f in json.loads(raw)['features']:
            raw_count+=1;p=f['properties'];years[str(p.get('tax_year'))]+=1
            acct=str(p.get('HCAD_NUM') or p.get('acct_num') or '').strip().zfill(13)
            if acct not in accounts or not f.get('geometry'):continue
            g=make_valid(transform(tofeet,shape(f['geometry'])))
            if g.geom_type not in ('Polygon','MultiPolygon') or g.is_empty:continue
            polys[acct]=unary_union([polys[acct],g]) if acct in polys else g
    if raw_count!=manifest['object_count']:raise RuntimeError('Geometry page counts disagree with manifest')
    print(f'{len(polys):,} matched polygons; {len(accounts)-len(polys):,} unmatched accounts',flush=True)
    geometry_groups=defaultdict(list)
    for acct,g in polys.items():geometry_groups[hashlib.sha256(g.normalize().wkb).digest()].append(acct)
    for group in geometry_groups.values():
        for acct in group:accounts[acct]['shared_geometry_accounts']=len(group)
    # Strict full-name + mailing-address match. Never group confidential owners
    # by one shared mailing address, and never strip entity-name suffixes.
    ownership={}
    for acct,r in accounts.items():
        name=norm(r['owner']);mail=norm(r['mail_addr'])
        issue=scope_issue(r)
        if issue and issue['status'] in ('condominium_interest','shared_geometry_review'):continue
        if name and mail and not any(x in name for x in ('CURRENT OWNER','CONFIDENTIAL','UNKNOWN')):
            ownership[acct]=(name,mail,norm(r['mail_city']),norm(r['mail_state']))
    keys=sorted(polys);geoms=[polys[k] for k in keys];tree=STRtree(geoms);parent=list(range(len(keys)))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,g in enumerate(geoms):
        if keys[i] not in ownership:continue
        for j0 in tree.query(g,predicate='dwithin',distance=1):
            j=int(j0)
            if j<=i or ownership.get(keys[j])!=ownership[keys[i]]:continue
            other=geoms[j]
            if g.intersection(other).area>min(g.area,other.area)*.05:continue
            shared=g.boundary.intersection(other.boundary.buffer(1)).length
            if shared<20:continue
            parent[root(i)]=root(j)
    groups=defaultdict(list)
    for i,k in enumerate(keys):groups[root(i)].append(k)
    groups=[sorted(v) for v in groups.values() if len(v)>1]
    # All singles are retained, even 5k lots and excluded former state classes.
    sites=[([k],polys.get(k)) for k in sorted(accounts)]
    for members in groups:
        total=sum(reported_area(accounts[k]) for k in members)
        unknown_area=any(reported_area(accounts[k])==0 for k in members)
        if total<10000 and not unknown_area:continue
        joined=polys[members[0]]
        for k in members[1:]:joined=unary_union([joined,snap(polys[k],joined,1)])
        if total<10000 and joined.area<10000:continue
        sites.append((members,joined))
    print(f'{len(sites):,} sites including {len(sites)-len(accounts):,} same-owner assemblies',flush=True)
    enrichment={}
    if a.enrichment:
        enrichment={site_id(r['accts']):r for r in json.loads(a.enrichment.read_text())}
    # Scheduled stop records, using a dated GTFS snapshot; nearest straight-line
    # stop distance is preserved independently from the geometry outcome.
    with zipfile.ZipFile(a.gtfs) as z:
        stops=list(csv.DictReader(io.TextIOWrapper(z.open('stops.txt'),encoding='utf-8-sig')))
    stop_points=[Point(*tofeet(float(s['stop_lon']),float(s['stop_lat']))) for s in stops]
    stop_tree=STRtree(stop_points)
    screener=StreetScreen(json.loads(a.roads.read_text()),geoms,tofeet,toll)
    placement_code={n:digest(Path(__file__).parent/'screening'/n) for n in ['duplex_footprint.py','site_shape.py','streets.py']}
    layout_cache={};cache_source=None
    if a.layout_cache:
        cache_meta=json.loads((a.layout_cache.parent/'layout-cache-meta.json').read_text())
        if cache_meta['geometry_sha256']!=geometry_hash.hexdigest() or cache_meta['roads_sha256']!=digest(a.roads) or cache_meta['placement_code']!=placement_code:
            raise RuntimeError('Placement-cache geometry, roads or model differ')
        with a.layout_cache.open(encoding='utf-8') as f:
            for line in f:
                try:r=json.loads(line)
                except json.JSONDecodeError:break
                layout_cache[r['site_id']]={k:r[k] for k in ['accounts','address','area_sf','geometry']}
                layout_cache[r['site_id']]['layout']=r['details']['layout']
        cache_source={'sha256':digest(a.layout_cache),'provenance':cache_meta,'records':len(layout_cache)}
        print(f'{len(layout_cache):,} cached layouts available; every land-interest check will be rerun',flush=True)
    codefiles=[Path(__file__),Path(__file__).parent/'site_identity.py',*sorted((Path(__file__).parent/'screening').glob('*.py'))]
    sources={'study':str(a.study),'study_size':(a.study/'houston.duckdb').stat().st_size,
      'study_modified_ns':(a.study/'houston.duckdb').stat().st_mtime_ns,
      'loop_boundary_sha256':hashlib.sha256(json.dumps(data['ring']).encode()).hexdigest(),
      'geometry':manifest,'geometry_tax_years':dict(years),'geometry_matches':len(polys),
      'missing_geometry':len(accounts)-len(polys),'roads_sha256':digest(a.roads),'gtfs_sha256':digest(a.gtfs),
      'geometry_sha256':geometry_hash.hexdigest(),'layout_cache':cache_source,
      'enrichment_sha256':digest(a.enrichment) if a.enrichment else None,
      'code':{p.name:digest(p) for p in codefiles}}
    model={**MODEL,'version':'loop-duplex-v2','frontage_rule':'street-occluded; corner/major access queue',
      'land_scope':'recorded land area only; condominium interests and shared-boundary aliases retained outside primary fits',
      'assemblies':'exact full owner and mailing address; shared boundary >=20 ft; <=5% overlap',
      'transit':'nearest GTFS stop; straight-line <=2640 ft','large_search_span_ft':500}
    signature=hashlib.sha256(json.dumps([model,sources],sort_keys=True).encode()).hexdigest()
    signature_file=a.output/'resume-signature.txt'
    partial=a.output/'sites.partial.jsonl'
    if signature_file.exists() and signature_file.read_text()!=signature and partial.exists():
        raise RuntimeError('Inputs changed; use a new output directory')
    signature_file.write_text(signature)
    done=set();counts=Counter()
    if partial.exists():
        # A trailing interrupted write is discarded; completed records survive.
        with partial.open('rb+') as f:
            while True:
                start=f.tell();line=f.readline()
                if not line:break
                try:r=json.loads(line)
                except json.JSONDecodeError:f.truncate(start);break
                done.add(r['site_id']);counts[r['status']]+=1
    anchors={'UH':(-95.3444,29.7199),'TSU':(-95.3607,29.7216),'TMC':(-95.3975,29.7080)}
    with partial.open('a',encoding='utf-8',newline='\n') as out:
        for number,(members,g) in enumerate(sites,1):
            sid=site_id(members)
            if sid in done:continue
            rr=[accounts[k] for k in members];area=sum(reported_area(r) for r in rr)
            address='; '.join(dict.fromkeys(r['address'] for r in rr));c=g.representative_point() if g is not None else Point(rr[0]['x'],rr[0]['y'])
            ll_geometry=transform(toll,g) if g is not None else None
            geo=json.loads(json.dumps(mapping(ll_geometry))) if ll_geometry is not None else None
            bb=list(ll_geometry.bounds) if ll_geometry is not None else None
            ni=int(stop_tree.nearest(c));dist=c.distance(stop_points[ni])
            issues=[issue for r in rr if (issue:=scope_issue(r)) is not None]
            cached=layout_cache.pop(sid,None)
            if issues:layout=issues[0]
            elif cached and cached['accounts']==members and cached['address']==address and cached['area_sf']==area and cached['geometry']==geo:
                layout=cached['layout']
            else:layout=screener.layout(g,address,area)
            fits=layout['fits'] and dist<=2640
            status='outside_transit' if layout['fits'] and not fits else layout['status']
            old=enrichment.get(sid,{})
            # HCAD neighborhoods remain filterable across the entire Loop; the
            # older campaign groups are a separate field (many say Other).
            neighborhoods=sorted(set(r['neighborhood'] or 'Unassigned' for r in rr))
            details={'layout':layout,'campaign_area':areas.get(members[0],'Other inside 610'),
              'neighborhoods':neighborhoods,'site_type':'single' if len(members)==1 else 'same_owner_assembly',
              'flood_zone':' / '.join(sorted(set(str(r['fld_zone'] or 'unknown') for r in rr))),
              'land_value':sum(r['land_value'] or 0 for r in rr),'building_value':sum(r['building_value'] or 0 for r in rr),
              'state_classes':sorted(set(r['state_class'] for r in rr)),
              'recorded_area_complete':all(reported_area(r)>0 for r in rr),
              'polygon_area_sf':round(g.area,2) if g is not None else None,
              'shared_geometry_account_count':max(r.get('shared_geometry_accounts',1) for r in rr),
              'transit_distance_ft':round(dist,1),'nearest_stop_id':stops[ni]['stop_id'],'nearest_stop_name':stops[ni]['stop_name'],
              'anchor_straight_line_mi':{k:round(c.distance(Point(*tofeet(*v)))/5280,2) for k,v in anchors.items()},
              'geometry_source':manifest['url'],'geometry_matched_accounts':sum(k in polys for k in members)}
            for key in ['owner_type','mail_matches_site','mail_within_half_mile_site','houston_mail','block_quality',
                        'building_line_overlays','minimum_lot_overlays','minimum_lot_above_equal_half','recorded_sfr_overlay']:
                if key in old:details[key]=old[key]
            r={'site_id':sid,'accounts':members,'address':address,'neighborhood':' / '.join(neighborhoods),
               'area_sf':area,'fits':fits,'status':status,'geometry':geo,'bbox':bb,'details':details}
            out.write(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n');out.flush();counts[status]+=1
            if number%2000==0:print(f'{number:,}/{len(sites):,} screened; {sum(counts[k] for k in ("wide_5","wide_3","narrow_5","narrow_3")):,} fits',flush=True)
    target=a.output/'sites.jsonl.gz'
    with partial.open('rb') as inp, target.open('wb') as dest:
        with gzip.GzipFile(filename='',fileobj=dest,mode='wb',mtime=0) as gz:
            for line in inp:gz.write(line)
    fingerprint=digest(target)
    result={'run_id':str(uuid.uuid5(uuid.NAMESPACE_URL,'innerloop:'+fingerprint)),'fingerprint':fingerprint,
      'scope':'Every HCAD account with centroid inside Loop 610; same-owner contiguous assemblies',
      'parcels':len(accounts),'sites':len(sites),'model':model,'sources':sources,'counts':dict(counts)}
    (a.output/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'parcels':len(accounts),'sites':len(sites),'counts':dict(counts),'snapshot':str(target)},indent=2),flush=True)

if __name__=='__main__':main()
