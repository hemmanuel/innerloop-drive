"""Place two real-scale rectangular duplex scenarios and their access on GIS lots.

Feet in EPSG:2278. Buildings are rigid rectangles, never sheared to match a lot.
The site split follows the existing equal-area cut, but its 33-ft screen is not a gate.
"""
import math
from shapely import affinity
from shapely.geometry import box, LineString, Polygon
from shapely.ops import split, unary_union

SCENARIOS = [
    ('wide_5', '40 x 45 ft / 5-ft sides', 40, 45, 5),
    ('wide_3', '40 x 45 ft / 3-ft sides', 40, 45, 3),
    ('narrow_5', '30 x 60 ft / 5-ft sides', 30, 60, 5),
    ('narrow_3', '30 x 60 ft / 3-ft sides', 30, 60, 3),
]
MODEL = {
    'version': 'reasonable-duplex-v1',
    'basis': 'User authorized reasonable dimensions on 2026-10-26; not measured Drew structures',
    'wide': {'width_ft':40,'depth_ft':45,'stories':2,'gross_sf_per_unit':1800},
    'narrow': {'width_ft':30,'depth_ft':60,'stories':2,'gross_sf_per_unit':1800,
               'basis':'Adapted five-bedroom program; published 30-ft-wide seven-bedroom unit has 1,866 heated sq ft'},
    'parking': {'spaces_per_duplex':4,'stall_width_ft':9,'stall_depth_ft':19,
                'arrangement':'Two tandem pairs, each pair assigned to one dwelling',
                'wide_driveway_ft':18,'narrow_driveway_ft':12,'narrow_flare_depth_ft':6},
    'reservations': {'side_options_ft':[5,3],'rear_ft':5,'walk_ft':3,'entry_depth_ft':4},
    'sources': [
      'https://southernimpressionhomes.com/investment-properties/floor-plans/3732/',
      'https://southernimpressionhomes.com/investment-properties/floor-plans/4640/',
      'https://www.houstontx.gov/planning/Livable%20Places/docs_pdfs/Signed_Adopted_Ordinances_-_C42_and_C26.pdf',
      'https://www.houstonpermittingcenter.org/sites/g/files/nwywnm431/files/2025-11/Pro%20-%20Session%202%20-%20Rm%20JK%20-%20FAQ%20-%20Site%20Plan%20Review%20101.pdf'],
}

def steps(lo, hi, step=1):
    if hi < lo - 1e-6: return []
    if hi-lo > 500:
        raise ValueError('Large-site placement search: divide into project-sized blocks')
    return sorted(set([lo, hi, (lo+hi)/2]+[lo+i*step for i in range(int((hi-lo)/step)+1)]))

def place(child, street, width, depth, side, land_sf):
    # A one-foot entrance strip accommodates small GIS jogs between adjoining
    # parcel faces; all buildings, stalls and main paths still stay inside land.
    front = child.intersection(street.buffer(1, cap_style=2))
    if front.is_empty: return None
    flo, _, fhi, _ = front.bounds
    fw=fhi-flo
    if fw < 33-.025: return None
    narrow = fw < 44-.025
    if narrow and land_sf > 15000: return None
    flare=6 if narrow else 0
    front_min=1+38+flare+3+4
    x0,y0,x1,y1=child.bounds
    if x1-x0 < width+2*side-.025 or y1 < front_min+depth+5-.025: return None
    allowed=child.buffer(.025)
    # Parking lies entirely on private land. Entry tapers are outside the stalls.
    parking_options=[]
    for px in steps(flo+3,fhi-18-3):
        curb=LineString([(px+(3 if narrow else 0),0),(px+18-(3 if narrow else 0),0)])
        if not narrow and max(curb.bounds[0]-flo,fhi-curb.bounds[2]) < 20-.025: continue
        stalls=[box(px+c*9,1+flare+r*19,px+(c+1)*9,1+flare+(r+1)*19) for c in range(2) for r in range(2)]
        entrance=box(px+(3 if narrow else 0),-1,px+18-(3 if narrow else 0),1).intersection(child)
        drive=unary_union([entrance,Polygon([(px+3,1),(px+15,1),(px+18,7),(px,7)])]) if narrow else entrance
        paved=unary_union(stalls+[drive])
        if allowed.covers(paved): parking_options.append((px,stalls,drive,curb,paved))
    if not parking_options:return None
    for y in steps(front_min,y1-depth-5):
        for x in steps(x0+side,x1-width-side):
            body=box(x,y,x+width,y+depth)
            reserve=unary_union([body.buffer(side,join_style=2),box(x-side,y+depth,x+width+side,y+depth+5)])
            if not allowed.covers(reserve):continue
            crosswalk=box(x-3,y-7,x+width+3,y-4)
            sidepaths=[box(x-3,y-4,x,y+depth),box(x+width,y-4,x+width+3,y+depth)]
            entries=[box(x+width*q-1.5,y-4,x+width*q+1.5,y) for q in (.25,.75)]
            if not all(allowed.covers(s) for s in [crosswalk,*sidepaths,*entries]):continue
            for px,stalls,drive,curb,paved in parking_options:
                for wx in (px-3,px+18):
                    walk=box(wx,1,wx+3,y-4)
                    street_link=box(wx,-1,wx+3,1).intersection(child)
                    connector=box(min(wx,x-3),y-7,max(wx+3,x+width+3),y-4)
                    if not allowed.covers(walk) or not allowed.covers(connector):continue
                    if walk.intersection(paved).area>.01 or connector.intersection(paved).area>.01:continue
                    return {'building':body,'parking':stalls,'drive':drive,'curb':curb,
                            'walks':[street_link,walk,connector,*sidepaths],'entries':entries,
                            'clearance':reserve,'front_building_ft':round(y,1),'frontage_ft':round(fw,1),
                            'driveway_ft':12 if narrow else 18}
    return None

def screen(g, front, cut, land_sf, *, ownership_ok=True):
    out={'fits':False,'status':'no_fit','reason':'No complete building / parking layout fits',
         'scenario':None,'children':[],'overlays':[],'tested_scenarios':[]}
    if land_sf<10000:out.update(status='below_area',reason='Below 10,000 sq ft');return out
    if not ownership_ok:out.update(status='owner_review',reason='Owner match unresolved');return out
    if front is None or cut is None or g.geom_type!='Polygon':
        out.update(status='geometry_review',reason='Street face or continuous split unresolved');return out
    a,b=front.coords;w=front.length;ux=(b[0]-a[0])/w;uy=(b[1]-a[1])/w
    vx,vy=-uy,ux
    if (g.centroid.x-a[0])*vx+(g.centroid.y-a[1])*vy<0:vx,vy=-vx,-vy
    def local(h):return affinity.affine_transform(h,[ux,uy,vx,vy,-a[0]*ux-a[1]*uy,-a[0]*vx-a[1]*vy])
    def world(h):return affinity.affine_transform(h,[ux,vx,uy,vy,a[0],a[1]])
    if cut.geom_type!='LineString':out.update(status='geometry_review',reason='Split has multiple pieces');return out
    ca,cb=cut.coords[0],cut.coords[-1];dx=cb[0]-ca[0];dy=cb[1]-ca[1]
    longcut=LineString([(ca[0]-dx*100,ca[1]-dy*100),(cb[0]+dx*100,cb[1]+dy*100)])
    children=list(split(g,longcut).geoms)
    if len(children)!=2 or any(c.geom_type!='Polygon' for c in children):
        out.update(status='geometry_review',reason='Equal-area cut does not produce two continuous lots');return out
    children=sorted([local(c) for c in children],key=lambda c:c.centroid.x)
    street=LineString([(0,0),(w,0)])
    for key,label,bw,bd,side in SCENARIOS:
        placements=[place(c,street,bw,bd,side,land_sf) for c in children]
        ok=all(p is not None for p in placements)
        out['tested_scenarios'].append({'id':key,'fits':ok})
        if not ok:continue
        out.update(fits=True,status=key,reason=label,scenario={'id':key,'width_ft':bw,'depth_ft':bd,'side_ft':side})
        for i,p in enumerate(placements):
            out['children'].append({'frontage_ft':p['frontage_ft'],'building_front_ft':p['front_building_ft'],
              'driveway_ft':p['driveway_ft'],'parking_spaces':4,'recorded_area_sf':round(land_sf/2)})
            objects=[('building',p['building']),('clearance',p['clearance']),('curb',p['curb'])]
            objects += [('parking',h) for h in p['parking']]+[('walk',h) for h in p['walks']]+[('entry',h) for h in p['entries']]
            if p['drive'] is not None:objects.append(('drive',p['drive']))
            out['overlays'] += [{'kind':k,'child':i+1,'geometry':world(h)} for k,h in objects]
        return out
    return out
