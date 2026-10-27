import gzip,json,struct,tempfile,unittest
from pathlib import Path
from site_identity import accounts,site_id
from build_native_data import snapshot


class IdentityAndBundleTest(unittest.TestCase):
    def test_membership_order_and_duplicates_do_not_change_identity(self):
        a='0000000000001';b='0000000000002'
        self.assertEqual(site_id(a),'S'+a)
        self.assertEqual(site_id([a,b,a]),site_id([b,a]))
        self.assertNotEqual(site_id([a,b]),site_id([a,'0000000000003']))
        with self.assertRaises(ValueError):accounts('123')

    def test_binary_keeps_ids_holes_and_exact_record_count(self):
        outer=[[-95.35,29.73],[-95.349,29.73],[-95.349,29.731],[-95.35,29.731],[-95.35,29.73]]
        hole=[[-95.3498,29.7302],[-95.3497,29.7302],[-95.3497,29.7303],[-95.3498,29.7302]]
        members=['0000000000001','0000000000002']
        row={'site_id':site_id(members),'accounts':members,'address':'Workflow fixture','area_sf':10000,
             'neighborhood':'Third Ward','status':'wide_5','fits':True,
             'geometry':{'type':'Polygon','coordinates':[outer,hole]}}
        test_root=Path('.local').resolve();test_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=test_root) as tmp:
            self.assertTrue(Path(tmp).resolve().is_relative_to(test_root))
            source=Path(tmp)/'sites.jsonl.gz';dest=Path(tmp)/'parcels.bin'
            with gzip.open(source,'wt') as out:
                out.write(json.dumps(row)+'\n');out.write(json.dumps({**row,'geometry':None})+'\n')
            snapshot(str(source),str(dest))
            with dest.open('rb') as f:
                self.assertEqual(f.read(4),b'ILP3')
                count,lon,lat=struct.unpack('>Idd',f.read(20));self.assertEqual(count,1)
                kind,priority,picked,reserved,area,*bounds=struct.unpack('>BBBBfffff',f.read(24))
                self.assertEqual((kind,priority,area),(1,3,10000))
                strings=[]
                for i in range(5):
                    n=struct.unpack('>I',f.read(4))[0];strings.append(f.read(n).decode())
                self.assertEqual(strings,[row['address'],row['site_id'],' '.join(members),'Third Ward','wide_5'])
                rings=struct.unpack('>I',f.read(4))[0];self.assertEqual(rings,2)
                for ring in [outer,hole]:
                    n=struct.unpack('>I',f.read(4))[0];self.assertEqual(n,len(ring));f.read(n*8)
                self.assertEqual(f.read(),b'')

if __name__=='__main__':unittest.main()
