"""Audit a same-street, equal-area split using the actual parcel polygon.

The 66-ft combined / 33-ft child frontage screen is the existing research policy.
Long-side frontage on a thin strip is routed to a separate layout lane.
Coordinates and distances supplied to this module must be in feet.
"""
import math
from shapely import affinity
from shapely.geometry import LineString, box
from shapely.ops import unary_union


def front_run(edges):
    """Return the longest continuous, substantially collinear street face.

    Never add opposite ends, disconnected frontages, or perpendicular faces.
    The one-foot join tolerance matches the source parcel simplification.
    """
    groups=[]
    for edge in edges:
        a,b=edge.coords; ux=(b[0]-a[0])/edge.length;uy=(b[1]-a[1])/edge.length
        joined=[]
        for i,group in enumerate(groups):
            for other in group:
                c,d=other.coords;vx=(d[0]-c[0])/other.length;vy=(d[1]-c[1])/other.length
                if abs(ux*vx+uy*vy)>.966 and edge.distance(other)<=1:
                    joined.append(i);break
        merged=[edge]
        for i in reversed(joined):merged+=groups.pop(i)
        groups.append(merged)
    def collapse(group):
        points=[p for edge in group for p in edge.coords]
        a,b=max(((a,b) for a in points for b in points),key=lambda pair:math.dist(*pair))
        return LineString([a,b])
    return max((collapse(group) for group in groups),key=lambda e:e.length)


def audit_shape(g,front,land_sf,*,ownership_ok=True):
    result={'primary_geometry':False,'status':'unmeasured','reason':'Street face unresolved',
            'frontage_ft':None,'depth_ft':None,'child_frontages_ft':[],
            'child_area_sf':round(land_sf/2), 'front_geometry':None,'split_geometry':None}
    if front is None:return result
    a,b=front.coords;w=front.length;ux=(b[0]-a[0])/w;uy=(b[1]-a[1])/w
    # Follow the parcel's depth axis, allowing skewed street grids. A cut forced
    # perpendicular to the road can wrongly reject an ordinary parallelogram.
    corners=list(g.minimum_rotated_rectangle.exterior.coords)
    axes=[((d[0]-c[0])/math.dist(c,d),(d[1]-c[1])/math.dist(c,d),math.dist(c,d)) for c,d in zip(corners,corners[1:])]
    vx,vy,_=min(axes,key=lambda v:abs(v[0]*ux+v[1]*uy))
    if (g.centroid.x-a[0])*vx+(g.centroid.y-a[1])*vy<0:vx,vy=-vx,-vy
    det=ux*vy-uy*vx
    ix,iy,jx,jy=vy/det,-vx/det,-uy/det,ux/det
    local=affinity.affine_transform(g,[ix,iy,jx,jy,-a[0]*ix-a[1]*iy,-a[0]*jx-a[1]*jy])
    x0,y0,x1,y1=local.bounds
    lo,hi=x0,x1
    for _ in range(45):
        cut=(lo+hi)/2
        if local.intersection(box(x0-1,y0-1,cut,y1+1)).area<local.area/2:lo=cut
        else:hi=cut
    cut=(lo+hi)/2
    widths=[max(0,min(w,cut)),max(0,w-max(0,cut))]
    children=[local.intersection(box(x0-1,y0-1,cut,y1+1)),local.intersection(box(cut,y0-1,x1+1,y1+1))]
    split=local.intersection(LineString([(cut,y0-1),(cut,y1+1)]))
    split=affinity.affine_transform(split,[ux,vx,uy,vy,a[0],a[1]])
    fill=g.area/g.minimum_rotated_rectangle.area
    result.update(frontage_ft=round(w,1),depth_ft=round(y1-y0,1),
                  equivalent_depth_ft=round(g.area/w,1),child_frontages_ft=[round(x,1) for x in widths],
                  rectangle_fill=round(fill,3),front_geometry=front,split_geometry=split)
    if land_sf<10000:status,reason='below_area','Below 10,000 sq ft'
    elif not ownership_ok:status,reason='owner_match','Owner match unresolved'
    elif w<66:status,reason='narrow_front','Needs adjoining frontage'
    elif g.geom_type!='Polygon' or fill<.85:status,reason='irregular','Irregular or disconnected shape'
    elif min(widths)<33:status,reason='unequal_front','Equal-area split leaves one street face below 33 ft'
    elif any(c.geom_type!='Polygon' for c in children):status,reason='irregular_split','Equal-area cut creates disconnected pieces'
    elif w>2*(y1-y0) and min(v[2] for v in axes)<66:
        status,reason='shallow_layout','Thin corner / through-street strip — separate layout'
    else:status,reason='primary','Two side-by-side street faces'
    result.update(status=status,reason=reason,primary_geometry=status=='primary')
    return result
