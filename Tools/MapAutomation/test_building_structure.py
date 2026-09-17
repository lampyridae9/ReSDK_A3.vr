"""Independent adversarial checks for the Phase 8A structural boundary."""
import copy
from dataclasses import asdict
from types import SimpleNamespace
import unittest

from building_generator.structure import (BuildingFrame, FloorLevel, FloorAssemblyValidator,
    BuildingShellValidator, anchor_position, physical_bounds, uncovered, load_structural_assets,
    StructuralAssembler)
from building_generator.generator import _fit_wall_modules, BuildingGenerator
from building_generator import BuildingFootprint, BuildingOptions, BuildingStatus
from test_building_generator import brief, layout, FakeRoomGenerator, FakeGateway, ARTIFACTS


def asset(width, depth, height, placing=0):
    return {'dimensions':[width,depth,height], 'bounds':[[-width/2,-depth/2,0],[width/2,depth/2,height]],
        'placingPoint':[0,0,placing], 'anchors':{'bottomCenter':[0,0,0],'topCenter':[0,0,height]}}


def fixture():
    """Exact synthetic box; dimensions chosen independently from production constants."""
    assets={'wall':asset(6,.3,3), 'floor':asset(6,6,.2), 'door':asset(1,.2,2),
        'jamb':asset(2.5,.3,3), 'header':asset(1,.3,1)}
    ops=[]
    def op(name,cls,p,yaw,stage,owner='f'):
        ops.append({'arguments':{'semanticId':name,'class':cls,'position':p,'rotation':[0,0,yaw],
            'scale':1,'parentId':owner}, 'stage':stage,'floorId':owner})
    op('slab','floor',[0,0,-.2],0,'floors')
    op('roof','floor',[0,0,3],0,'floors','roof')
    walls=[]
    for i,(a,b,p,yaw) in enumerate((([-3,-3,0],[3,-3,0],[0,-3,0],0),
            ([-3,3,0],[3,3,0],[0,3,0],0),([-3,-3,0],[-3,3,0],[-3,0,0],90),
            ([3,-3,0],[3,3,0],[3,0,0],90))):
        op('wall'+str(i),'wall',p,yaw,'walls')
        walls.append({'id':'w'+str(i),'start':a,'end':b,'owners':['room'], 'exterior':True,'openings':[]})
    plan={'frame':BuildingFrame((0,0,0)).json(),'profile':{'story_height':3.2,'floor_thickness':.2,
        'wall_height':3,'wall_thickness':.3,'ceiling_offset':3},
        'floors':[{'level':asdict(FloorLevel('f',0,0)),'floorOpenings':[],'walls':walls}]}
    layout=SimpleNamespace(footprint=BuildingFootprint((0,0,0),6,6),floors=[SimpleNamespace(vertical_connections=[])])
    return assets,ops,plan,layout


class StructuralTests(unittest.TestCase):
    def codes(self, data):
        a,o,p,l=data
        return {x['code'] for x in BuildingShellValidator(a).validate(l,o,p)}

    def test_closed_shell_passes(self):
        self.assertFalse(self.codes(fixture()))

    def test_anchor_placing_point_not_bbox_center(self):
        a=asset(6,.3,3,placing=.00646)
        position=anchor_position(a,'bottomCenter',[12,20,10])
        self.assertAlmostEqual(10.00646,position[2])
        self.assertEqual([12,20,13.00646],anchor_position(a,'topCenter',[12,20,16]))

    def test_native_wall_bottom_matches_floor_datum(self):
        assets=load_structural_assets()
        for name in ('BrickThinWall','SteelThinWallSmall','MediumWoodenWall','StoneBigLadderDouble'):
            a=assets[name]
            op={'arguments':{'class':name,'position':anchor_position(a,'bottomCenter',[0,0,10],90),'rotation':[0,0,90]}}
            self.assertAlmostEqual(10,physical_bounds(op,assets)[0][2],places=5)

    def test_frame_rotation_and_translation(self):
        f=BuildingFrame((4700,4200,10),90)
        self.assertAlmostEqual(4697,f.world((2,-3,4))[0])
        for actual, expected in zip(f.local(f.world((2,-3,4))),(2,-3,4)):
            self.assertAlmostEqual(actual,expected)

    def test_floating_wrong_level_and_sunk(self):
        for z,expected in ((1.65,{'WALL_FLOATING','WALL_WRONG_LEVEL','WALL_FLOOR_GAP'}),(-.3,{'WALL_SUNK','WALL_FLOOR_OVERPENETRATION'})):
            data=fixture();data[1][2]['arguments']['position'][2]=z
            self.assertTrue(expected <= self.codes(data))

    def test_shared_wall_duplication(self):
        data=fixture();data[2]['floors'][0]['walls'].append(copy.deepcopy(data[2]['floors'][0]['walls'][0]))
        self.assertIn('SHARED_WALL_DUPLICATED',self.codes(data))

    def test_exterior_gap(self):
        data=fixture();data[1].pop(2)
        self.assertIn('WALL_CONTINUITY_GAP',self.codes(data))

    def test_story_profile_mismatch(self):
        data=fixture();data[2]['profile']['story_height']=3.5
        self.assertIn('STORY_HEIGHT_INCOMPATIBLE',self.codes(data))

    def test_floor_tiling_gap_and_overlap(self):
        v=FloorAssemblyValidator();level=FloorLevel('f',0,0)
        tiles=[{'id':'a','rect':(0,0,2,2),'top':0},{'id':'b','rect':(2,0,4,2),'top':0}]
        self.assertFalse(v.validate(level,tiles,[],(0,0,4,2)))
        tiles[1]['rect']=(2.1,0,4,2)
        self.assertIn('FLOOR_COVERAGE_GAP',{x['code'] for x in v.validate(level,tiles,[],(0,0,4,2))})
        tiles[1]['rect']=(1.9,0,4,2)
        self.assertIn('FLOOR_MODULE_OVERLAP',{x['code'] for x in v.validate(level,tiles,[],(0,0,4,2))})

    def test_opening_checks_edges_not_only_tile_center(self):
        errors=FloorAssemblyValidator().validate(FloorLevel('upper',1,3),
            [{'id':'tile','rect':(0,0,4,2),'top':3}],[(3.5,0,5,2)],(0,0,5,2))
        self.assertIn('FLOOR_OPENING_BLOCKED',{x['code'] for x in errors})

    def test_upper_floor_datum(self):
        errors=FloorAssemblyValidator().validate(FloorLevel('upper',1,3.2),
            [{'id':'tile','rect':(0,0,2,2),'top':0}],[],(0,0,2,2))
        self.assertIn('FLOOR_WRONG_DATUM',{x['code'] for x in errors})

    def portal_fixture(self):
        data=fixture();a,ops,plan,_=data
        plan['floors'][0]['walls'][0]['openings']=[{'id':'entry','offset_along_wall':2.5,
            'width':1,'height':2,'bottom':0,'spaces':['EXTERIOR','room']}]
        ops.pop(2)
        for sid,cls,pos,stage,owner in [('left','jamb',[-1.75,-3,0],'walls','f'),
                ('right','jamb',[1.75,-3,0],'walls','f'),('header','header',[0,-3,2],'walls','f'),
                ('door','door',[0,-3,0],'doors','entry')]:
            ops.append({'arguments':{'semanticId':sid,'class':cls,'position':pos,'rotation':[0,0,0],
                'parentId':owner},'stage':stage,'floorId':'f'})
        # Header is a supported member above an opening, not a floor-supported wall.
        ops[-2]['stage']='headers'
        return data

    def test_real_portal_with_header(self):
        self.assertFalse(self.codes(self.portal_fixture()))

    def test_door_inside_solid_wall_rejected(self):
        data=self.portal_fixture()
        data[1].append({'arguments':{'semanticId':'solid','class':'wall','position':[0,-3,0],
            'rotation':[0,0,0],'parentId':'f'},'stage':'walls','floorId':'f'})
        self.assertIn('DOOR_INSIDE_SOLID_WALL',self.codes(data))

    def test_door_alignment_and_size(self):
        data=self.portal_fixture();data[1][-1]['arguments']['position'][0]=.2
        self.assertIn('DOOR_NOT_CENTERED_IN_OPENING',self.codes(data))
        data[2]['floors'][0]['walls'][0]['openings'][0]['width']=.5
        self.assertIn('OPENING_TOO_SMALL',self.codes(data))

    def test_no_unbuildable_fragments_accepted(self):
        with self.assertRaises(ValueError):
            _fit_wall_modules(3.05,[{'length':3,'material':'brick','asset':'wall'}],.05,0)

    def test_material_runs_remain_grouped(self):
        modules=[{'length':3,'material':'brick','asset':'a'},{'length':1,'material':'wood','asset':'b'}]
        chosen,_=_fit_wall_modules(8,modules,.001,5)
        families=[x['material'] for x in chosen]
        self.assertLessEqual(sum(a!=b for a,b in zip(families,families[1:])),1)

    def test_invalid_shell_blocks_furnishing_and_live_apply(self):
        rooms=FakeRoomGenerator();gateway=FakeGateway()
        result=BuildingGenerator(room_generator=rooms,gateway=gateway,artifact_dir=ARTIFACTS).generate('recovery',
            BuildingFootprint((100,100,10),12,10.05624),BuildingOptions(mode='live'),building_brief=brief())
        self.assertEqual(BuildingStatus.VALIDATION_FAILED,result.status)
        self.assertEqual([],rooms.calls);self.assertEqual(1,len(gateway.objects))
        codes={x['code'] for x in result.shell_validation['diagnostics']}
        self.assertTrue({'STAIR_RISE_MISMATCH','FLOOR_OPENING_NOT_ON_MODULE_GRID'}<=codes)

    def test_structural_plan_is_local_at_any_origin(self):
        _,made=layout();g=BuildingGenerator(artifact_dir=ARTIFACTS)
        p=StructuralAssembler(g.profile).compile(made)
        self.assertAlmostEqual(0,p['floors'][0]['level']['datum_z'])
        self.assertLess(abs(p['floors'][0]['walls'][0]['start'][0]),10)


if __name__=='__main__':unittest.main()
