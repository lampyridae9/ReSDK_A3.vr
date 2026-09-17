"""Native measured fixture regressions, independent of orchestration stubs."""
import copy
import json
from pathlib import Path
import unittest

from building_generator import BuildingFootprint,BuildingOptions,BuildingLayoutSolver,expand_building_plan
from building_generator.structure import (StructuralAssembler,BuildingShellValidator,load_structural_assets,
    tile_native_floor,rotate,anchor_position,physical_bounds,FloorAssemblyValidator,FloorLevel)
from building_generator.generator import validate_transform_readback
from building_generator.generator import BuildingGenerator, _room_shell
from room_generator import RoomGenerator, GenerationOptions
from transport import TransportError

BASE=Path(__file__).resolve().parent


def native_shell():
    profile=json.loads((BASE/'worker_house_profile.json').read_text())
    brief=json.loads((BASE/'fixtures/poor_worker_dormitory_2f.json').read_text())
    brief['requirements'].update(bedrooms=2,storage=True);brief['capacity']['residents']=4
    plan=expand_building_plan(brief,profile)
    layout=BuildingLayoutSolver(profile).solve(plan,BuildingFootprint((5040,4700,10),12,12),brief,BuildingOptions())
    ops,errors,structure=StructuralAssembler(profile).assemble(layout)
    assert not errors,errors
    return layout,ops,structure,BuildingShellValidator(tolerance=profile['contactTolerance'])


class NativeGridTests(unittest.TestCase):
    def test_bounded_strategy_fallback_preserves_seed_and_required_beds(self):
        layout,_,_,_=native_shell();floor=layout.floors[1]
        room=next(s for s in floor.spaces if s.kind=='bedroom')
        portal=next(p for p in floor.portals if p.to_space==room.id)
        brief=json.loads((BASE/'fixtures/poor_bedroom_two_workers.json').read_text())
        brief['seed']=1236
        result=RoomGenerator().generate_room('fallback regression',_room_shell(room,portal,floor.elevation,3),
            GenerationOptions(seed=1236,capture=False),planner_brief=brief,room_id=room.id,slot_namespace=room.id)
        self.assertEqual(result.status.value,'SUCCESS')
        self.assertEqual([a['strategy'] for a in result.metrics['strategyAttempts']],['opposite_beds','parallel_beds'])
        self.assertEqual(result.planner_brief['seed'],1236)
        self.assertEqual(sum(p['asset']=='SingleWhiteBed' for p in result.placements),2)
        self.assertLessEqual(result.metrics['searchNodes'],128)
        self.assertTrue(result.metrics['navigationResult']['reachable'])

    def test_furnished_worker_house_with_wall_bearing_clearance(self):
        profile=json.loads((BASE/'worker_house_profile.json').read_text())
        brief=json.loads((BASE/'fixtures/worker_house_recovery_2f.json').read_text())
        result=BuildingGenerator(profile=profile).generate('recovery regression',
            BuildingFootprint((5040,4700,10),12,12),BuildingOptions(),building_brief=brief)
        self.assertEqual(result.status.value,'SUCCESS')
        self.assertEqual(sum(p['asset']=='SingleWhiteBed' for r in result.room_generations for p in r['placements']),4)
        self.assertEqual(sum(op['stage']=='guards' for op in result.shell_operations),5)
        layout,_,_,_=native_shell()
        for floor in layout.floors:
            for room in (s for s in floor.spaces if s.kind=='bedroom'):
                portal=next(p for p in floor.portals if p.to_space==room.id)
                shell=_room_shell(room,portal,floor.elevation,3,.3)
                self.assertAlmostEqual(min(x for x,y in shell.scene.region_polygon),room.rect.x+.3)
                self.assertAlmostEqual(max(x for x,y in shell.scene.region_polygon),room.rect.x2-.3)

    def test_measured_euler_axes(self):
        expected=[[.719727,-.425781,.548295],[.604004,.773438,-.192630],[-.341797,.469727,.813798]]
        for point,target in zip(([1,0,0],[0,1,0],[0,0,1]),expected):
            for a,b in zip(rotate(point,[30,20,40]),target):self.assertAlmostEqual(a,b,delta=.0006)

    def test_lintel_top_uses_unrotated_placing_offset(self):
        assets=load_structural_assets();a=assets['ConcreteSmallPole']
        for rotation,anchor in (([0,90,0],'lintelTop'),([90,0,0],'lintelTopY')):
            position=anchor_position(a,anchor,[5000,4700,13],rotation)
            self.assertAlmostEqual(position[2],11.75687,places=5)
            op={'arguments':{'class':'ConcreteSmallPole','position':position,'rotation':rotation,'scale':1}}
            self.assertAlmostEqual(physical_bounds(op,assets)[1][2],13,places=6)

    def test_rotated_tiles_preserve_internal_opening_and_perimeter(self):
        holes=[(0,-3,3,3)];tiles=tile_native_floor(12,12,(3,6),holes)
        self.assertEqual(len(tiles),7)
        self.assertEqual({0,90},{v[2] for v in tiles})
        rectangles=[]
        for i,(x,y,yaw) in enumerate(tiles):
            w,d=(3,6) if yaw==0 else (6,3)
            rectangles.append({'id':str(i),'rect':(x-w/2,y-d/2,x+w/2,y+d/2),'top':0})
        self.assertFalse(FloorAssemblyValidator().validate(FloorLevel('f',0,0),rectangles,holes,(-6,-6,6,6)))

    def test_partial_tile_hole_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'FLOOR_OPENING_NOT_ON_MODULE_GRID'):
            tile_native_floor(12,12,(3,6),[(0,-3,3.1,3)])

    def test_two_floor_native_shell_passes(self):
        layout,ops,plan,validator=native_shell()
        self.assertFalse(validator.validate(layout,ops,plan))

    def test_missing_lintel_is_a_real_gap(self):
        layout,ops,plan,validator=native_shell();ops=[o for o in ops if o['stage']!='headers']
        self.assertIn('WALL_CONTINUITY_GAP',{d['code'] for d in validator.validate(layout,ops,plan)})

    def test_moved_stair_is_rejected_using_actual_landings(self):
        layout,ops,plan,validator=native_shell()
        stairs=next(o for o in ops if o['stage']=='stairs');stairs['arguments']['position'][2]+=.3
        codes={d['code'] for d in validator.validate(layout,ops,plan)}
        self.assertTrue({'STAIR_BOTTOM_LANDING_WRONG_DATUM','STAIR_TOP_LANDING_WRONG_DATUM'}<=codes)

    def test_rotated_stair_is_rejected(self):
        layout,ops,plan,validator=native_shell()
        next(o for o in ops if o['stage']=='stairs')['arguments']['rotation'][2]=180
        self.assertIn('STAIR_DIRECTION_MISMATCH',{d['code'] for d in validator.validate(layout,ops,plan)})

    def test_serialization_tolerance_does_not_allow_centimetre_drift(self):
        expected={'semanticId':'s','class':'wall','position':[5003.78228,4700,10],'rotation':[0,0,0],'scale':1}
        row=copy.deepcopy(expected);row['position'][0]=5003.78
        validate_transform_readback(expected,row)
        row['position'][0]=5003.80
        with self.assertRaises(TransportError):validate_transform_readback(expected,row)
        for field,value in [('position',[0]),('rotation',[0,float('nan'),0]),('scale',.9)]:
            row=copy.deepcopy(expected);row[field]=value
            with self.assertRaises(TransportError):validate_transform_readback(expected,row)


if __name__=='__main__':unittest.main()
