import unittest
from screening.land_scope import reported_area,scope_issue


class LandScopeTest(unittest.TestCase):
    def test_condo_never_inherits_parent_area(self):
        row={'area_sf':0,'legal_text':'UNIT 11G FLR 11 .557099 INT COMMON LAND & ELE THE PARKLANE CONDO'}
        self.assertEqual(reported_area(row),0)
        self.assertEqual(scope_issue(row)['status'],'condominium_interest')
        row['area_sf']=12000
        self.assertEqual(scope_issue(row)['status'],'condominium_interest')

    def test_missing_area_is_review_not_gis_fallback(self):
        for area in [None,0,-1,float('nan')]:
            self.assertEqual(reported_area({'area_sf':area}),0)
            self.assertEqual(scope_issue({'area_sf':area})['status'],'land_area_review')

    def test_fee_simple_townhome_and_shared_geometry(self):
        row={'area_sf':10500,'legal_text':'LT 1 BLK 1 TOWNHOME DEVELOPMENT'}
        self.assertIsNone(scope_issue(row))
        row['shared_geometry_accounts']=2
        self.assertEqual(scope_issue(row)['status'],'shared_geometry_review')

if __name__=='__main__':unittest.main()
