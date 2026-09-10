"""Parser adversarial fixtures and dataset accounting. No engine certification."""
import unittest
from catalog_parser import literal,parse_config,parse_hashdata
from build_catalog import read_map, ROOT, spatial
from validate_catalog import validate,probe_errors


class ParserTests(unittest.TestCase):
    def test_strings_do_not_create_classes(self):
        cfg=parse_config('class Entities {items=1; class Item0 {dataType="Object"; init="class Item7 {}; [""class"",""Fake""]";};};')
        self.assertEqual(len(cfg['children']['Entities']['children']),1)
        self.assertEqual(literal('["]","}","class"]'),[']','}','class'])

    def test_nested_container_class_not_placed_object(self):
        hd=parse_hashdata('{createHashMapFromArray [["class","Box"],["containerContent",[["Paper",3]]],["customProps",createHashMapFromArray [["desc","[\'class\',\'Fake\']"]]]]}')
        self.assertEqual(hd['class'],'Box')
        self.assertEqual(hd['containerContent'],[['Paper',3]])

    def test_historical_wrapper(self):
        self.assertEqual(parse_hashdata('call{{createHashMapFromArray [["class","Pipe"]]}}')['class'],'Pipe')

    def test_multiline_and_unicode(self):
        cfg=parse_config('x="Земля" \\n "Камень";')
        self.assertEqual(cfg['properties']['x'],'Земля\nКамень')

    def test_reject_code_and_ambiguous_data(self):
        for s in ['call compile "bad"','[1,2] call bad','{1}','createHashMapFromArray [["a",1],["a",2]]','[1,2','"unfinished']:
            with self.subTest(s=s),self.assertRaises(ValueError): literal(s)

    def test_signed_exponents(self):
        self.assertEqual(literal('[-1e-3,2,true,any]'),[-0.001,2,True,{'sqfUndefined':True}])

    def test_dataset_small_and_large_counts(self):
        # Independently confirmed against compiled direct Init* calls.
        for name,n,excluded in [('Hunt',423,3),('Minimap',3164,4),('SaloonV2',3707,3)]:
            rows,meta=read_map(ROOT/f'Src/Editor/Bin/Maps/{name}.cpp')
            self.assertEqual(len(rows),n)
            self.assertEqual(len(meta['excludedObjects']),excluded)

    def test_spatial_vertical_separation_and_pairs_once(self):
        rows=[dict(entityId=i,classname=c,position=p,anglesRadians=[0,0,0],atlOffset=0) for i,(c,p) in enumerate([('A',[0,0,0]),('B',[3,4,0]),('B',[0,0,6])])]
        pairs,_,_=spatial(rows)
        self.assertEqual(pairs[('A','B')],1)
        self.assertEqual(sum(pairs.values()),1)

    def test_catalog_integrity(self):
        self.assertEqual(validate()['errors'],[])

    def test_probe_does_not_verify_invalid_or_inconsistent_bounds(self):
        p=dict(dimensions=[1,1,1],visualBounds=[[0,0,0],[1,1,1]],source='engineMeasured',status='VERIFIED')
        self.assertEqual(probe_errors(p),[])
        for dims in [[float('nan'),1,1],[0,1,1],[-1,1,1],[2,1,1]]:
            self.assertTrue(probe_errors({**p,'dimensions':dims}))


if __name__=='__main__': unittest.main()
