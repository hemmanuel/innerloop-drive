import unittest
from frontage_policy import DuplexEnvelope, access_route


class FrontagePolicyTests(unittest.TestCase):
    def test_access_rules_and_gis_boundary(self):
        self.assertEqual(access_route(90,10000),'test_two_front_lots_44_plus')
        self.assertEqual(access_route(80,10000),'test_two_narrow_front_lots_33_to_44')
        self.assertEqual(access_route(70,15000),'test_two_narrow_front_lots_33_to_44')
        self.assertEqual(access_route(70,15001),'test_shared_access_over_15000')
        self.assertEqual(access_route(66,10000),'measure_near_access_threshold')
        self.assertEqual(access_route(60,15000),'test_shared_access_or_alternative_split')
        self.assertEqual(access_route(None,10000),'measure_street_frontage')
        self.assertEqual(access_route(100,10000,street_class='MAJOR'),'test_thoroughfare_access')

    def test_access_alternatives_preserve_narrow_sites(self):
        self.assertEqual(access_route(50,10000,through=True),'test_opposite_street_split')
        self.assertEqual(access_route(50,10000,corner=True),'test_corner_split_and_side_access')
        self.assertEqual(access_route(50,10000,usable_alley=True),'test_alley_loaded_split')
        self.assertEqual(access_route(60,10000,subdividing=False),'test_existing_lots_and_access')

    def test_envelope_requires_width_and_depth(self):
        # User-supplied design dimensions; not a default buyer prototype.
        p=DuplexEnvelope(34,60,3,3,40,5)
        self.assertTrue(p.fits(40,125))
        self.assertFalse(p.fits(39,150))
        self.assertFalse(p.fits(40,100))


if __name__=='__main__': unittest.main()
