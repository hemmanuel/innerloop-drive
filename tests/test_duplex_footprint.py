import unittest
from shapely.geometry import box, LineString, Polygon
from shapely import affinity
from screening.site_shape import audit_shape
from screening.duplex_footprint import screen

def run(g,front,area):
    a=audit_shape(g,front,area)
    return screen(g,front,a['split_geometry'],area)

class PlacementTest(unittest.TestCase):
    def test_wide_and_narrow_sites(self):
        for w,d,expected in [(100,100,True),(94,110,True),(88,114,True),(80,125,True),(74,150,True),(72,140,True),(70,150,False),(66,160,False),(50,200,False),(200,50,False)]:
            with self.subTest(w=w,d=d):
                r=run(box(0,0,w,d),LineString([(0,0),(w,0)]),w*d)
                self.assertEqual(r['fits'],expected)
                if expected:
                    self.assertEqual(sum(x['kind']=='parking' for x in r['overlays']),8)
                    for x in r['overlays']:self.assertTrue(box(0,0,w,d).buffer(.03).covers(x['geometry']))
    def test_rotated_buildings_keep_dimensions(self):
        g=affinity.rotate(box(0,0,100,100),31,origin=(0,0))
        front=affinity.rotate(LineString([(0,0),(100,0)]),31,origin=(0,0))
        r=run(g,front,10000)
        self.assertTrue(r['fits'])
        for x in r['overlays']:
            if x['kind']=='building':self.assertAlmostEqual(x['geometry'].area,1800,places=5)
    def test_pinched_polygon_does_not_pass_bounding_box(self):
        g=Polygon([(0,0),(100,0),(100,25),(60,25),(60,160),(40,160),(40,25),(0,25)])
        self.assertFalse(run(g,LineString([(0,0),(100,0)]),10000)['fits'])
    def test_area_gate(self):
        self.assertFalse(run(box(0,0,100,100),LineString([(0,0),(100,0)]),9999)['fits'])
    def test_wentworth_skew(self):
        g=Polygon([(51.81,145.49),(0,0),(74.15,0),(122.26,122.23)])
        self.assertFalse(run(g,LineString([(0,0),(74.15,0)]),10232)['fits'])
    def test_jogged_assembled_front(self):
        g=Polygon([(0,0),(50,.22),(100,0),(100,100),(0,100)])
        self.assertTrue(run(g,LineString([(0,0),(100,0)]),10000)['fits'])
    def test_walks_do_not_cross_parking_or_buildings(self):
        r=run(box(0,0,74,150),LineString([(0,0),(74,0)]),11100)
        self.assertTrue(r['fits'])
        self.assertEqual([c['driveway_ft'] for c in r['children']],[12,12])
        obstacles=[x['geometry'] for x in r['overlays'] if x['kind'] in ('building','parking','drive')]
        for x in r['overlays']:
            if x['kind'] in ('walk','entry'):
                for g in obstacles:self.assertLess(x['geometry'].intersection(g).area,.01)

if __name__=='__main__':unittest.main()
