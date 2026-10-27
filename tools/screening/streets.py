"""Street frontage with intervening-parcel occlusion and complete layout results."""
import re
from collections import defaultdict
from shapely.geometry import LineString, mapping
from shapely.strtree import STRtree
from shapely.ops import transform
from .site_shape import front_run,audit_shape
from .duplex_footprint import screen


def norm(s):return re.sub(r'[^A-Z0-9]+',' ',str(s or '').upper()).strip()


class StreetScreen:
    def __init__(self,roads,parcels,to_feet,to_ll):
        self.to_ll=to_ll;self.segments=[];self.attrs=[]
        for f in roads['features']:
            for path in f['geometry']['paths']:
                points=[to_feet(*p) for p in path]
                for p,q in zip(points,points[1:]):
                    line=LineString([p,q])
                    if line.length>=5:self.segments.append(line);self.attrs.append(f['attributes'])
        self.tree=STRtree(self.segments)
        self.obstacles=list(parcels);self.obstacle_tree=STRtree(self.obstacles)

    def frontages(self,g,address):
        matches=defaultdict(list);meta={};classes={}
        for poly in (g.geoms if g.geom_type=='MultiPolygon' else [g]):
            cs=list(poly.exterior.coords)
            for a,b in zip(cs,cs[1:]):
                edge=LineString([a,b]);length=edge.length
                if length<8:continue
                mid=edge.interpolate(.5,normalized=True);dx=(b[0]-a[0])/length;dy=(b[1]-a[1])/length;opts=[]
                for j in self.tree.query(mid.buffer(85)):
                    road=self.segments[j];at=self.attrs[j]
                    if at.get('roadclass') in ('FREEWAY','HIGHWAY','HOV','RAMP'):continue
                    rp,rq=road.coords;rn=road.length
                    cosine=abs(dx*(rq[0]-rp[0])/rn+dy*(rq[1]-rp[1])/rn);dist=mid.distance(road)
                    if cosine<.966 or not 8<=dist<=85:continue
                    near=road.interpolate(road.project(mid));line=LineString([mid,near])
                    if g.buffer(-1).intersection(line).length>1:continue
                    sight=line.difference(g.buffer(1))
                    if any(self.obstacles[int(k)].buffer(-1).intersection(sight).length>2
                           for k in self.obstacle_tree.query(sight,predicate='intersects')):continue
                    u=[(r[0]-a[0])*dx+(r[1]-a[1])*dy for r in (rp,rq)]
                    if max(0,min(length,max(u))-max(0,min(u)))<min(20,length*.5):continue
                    name=norm(at.get('roadname'))
                    if name:opts.append((dist,int(j),name))
                if opts:
                    _,j,name=min(opts);matches[name].append(edge)
                    meta[name]=self.attrs[j].get('fullname') or name;classes[name]=self.attrs[j].get('roadclass')
        return sorted([{'street':meta[n],'road_class':classes[n],'feet':round(front_run(es).length,1),
            'situs':bool(re.search(r'\b'+re.escape(n)+r'\b',norm(address))),'_edge':front_run(es)}
            for n,es in matches.items()],key=lambda f:(f['situs'],f['feet']),reverse=True)

    def layout(self,g,address,sf):
        if sf<10000:return {'fits':False,'status':'below_area','reason':'Below 10,000 sq ft; retained for assemblies'}
        if g is None:return {'fits':False,'status':'missing_geometry','reason':'No polygon matched to this HCAD account'}
        if g.geom_type!='Polygon':return {'fits':False,'status':'geometry_review','reason':'Disconnected parcel geometry'}
        fronts=self.frontages(g,address);chosen=next((f for f in fronts if f['situs']),None)
        front=chosen['_edge'] if chosen else None
        if len(fronts)>1 or (chosen and chosen['road_class']=='MAJOR'):
            result={'fits':False,'status':'street_layout','reason':'Corner, through-street or major-road access layout'}
        else:
            audit=audit_shape(g,front,sf)
            try:result=screen(g,front,audit['split_geometry'],sf)
            except ValueError as e:result={'fits':False,'status':'large_layout','reason':str(e)}
            result['frontage_ft']=audit['frontage_ft'];result['depth_ft']=audit['depth_ft']
            result['split_geometry']=self.geo(audit['split_geometry'])
            for item in result.get('overlays',[]):item['geometry']=self.geo(item['geometry'])
        result['frontages']=[{k:v for k,v in f.items() if k!='_edge'} for f in fronts]
        return result

    def geo(self,g):return mapping(transform(self.to_ll,g)) if g is not None else None
