#!/usr/bin/env python3
"""Phase 3 deterministic spatial primitive tests (A-L)."""
from __future__ import annotations

import copy
import math
import unittest

from spatial.model import OBB, PlacementIntent, ResolvedObject, SceneState, SpatialTransform, SupportSurface
from spatial.solver import AccessibilityValidator, ClearanceValidator, GeometryValidator, NavigationAgentProfile, PlacementSolver, SupportValidator, load_phase3_assets


ASSETS, CONFIG = load_phase3_assets()
T = CONFIG['tolerances']


def room(*, objects=None, entrance=(0.0, 3.0)) -> SceneState:
    surfaces={
        'floor_1':SupportSurface('floor_1','floor','WoodenSmallFloor',(0,0,0),(0,0,1),(1,0,0),(0,1,0),(3.5,3.5)),
        'south_wall':SupportSurface('south_wall','wall','ConcreteGreenWall',(0,-3,1.5),(0,1,0),(1,0,0),(0,0,1),(3.3,1.5)),
        'ceiling_1':SupportSurface('ceiling_1','ceiling','room',(0,0,3),(0,0,-1),(1,0,0),(0,1,0),(3.5,3.5)),
    }
    return SceneState('room_1',[(-3.5,-3.5),(3.5,-3.5),(3.5,3.5),(-3.5,3.5)],surfaces,list(objects or []),entrance,[])


def obj(identifier, classname, position, yaw=0):
    return ResolvedObject.create(identifier,ASSETS[classname],SpatialTransform(position,(0,0,yaw)))


class SpatialPrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.solver=PlacementSolver(ASSETS,CONFIG,allow_candidate_assets=True)

    def codes(self,diagnostics): return {x.code for x in diagnostics}

    def test_a_floor_support_pass(self):
        bed=obj('bed','SingleWhiteBed',(0,0,0))
        self.assertEqual([],self.solver.support.validate(bed,room().surfaces['floor_1']))

    def test_b_floating_fails(self):
        bed=obj('bed','SingleWhiteBed',(0,0,0.2))
        self.assertIn('SUPPORT_GAP',self.codes(self.solver.support.validate(bed,room().surfaces['floor_1'])))

    def test_c_penetration_fails(self):
        bed=obj('bed','SingleWhiteBed',(0,0,-0.2))
        self.assertIn('SUPPORT_PENETRATION',self.codes(self.solver.support.validate(bed,room().surfaces['floor_1'])))

    def test_d_wall_intersection_fails(self):
        wall=obj('wall','ConcreteGreenWall',(0,-3.396442,2.11962))
        bed=obj('bed','SingleWhiteBed',(0,-2.8,0))
        self.assertIn('INTERSECTION',self.codes(self.solver.geometry.validate(bed,room(objects=[wall]))))

    def test_e_against_wall_resolves(self):
        wall=obj('wall','ConcreteGreenWall',(0,-3.396442,2.11962))
        state=room(objects=[wall])
        intent=PlacementIntent('bed','SingleWhiteBed','room_1','floor_1','south_wall',soft=('PreferWallCenter',),seed=7)
        result=self.solver.resolve(intent,state)
        self.assertEqual('VALID',result.status)
        self.assertAlmostEqual(0.0,result.placement.transform.position[2],places=6)
        self.assertAlmostEqual(0.0,min(p[2] for p in result.placement.occupied.corners()),places=6)
        self.assertEqual([],self.solver.support.validate(result.placement,state.surfaces['floor_1']))
        self.assertNotIn('INTERSECTION',self.codes(self.solver.geometry.validate(result.placement,state)))

    def test_f_object_collision_rejected(self):
        bed=obj('bed','SingleWhiteBed',(0,0,0))
        table=obj('table','SmallWoodenTable',(0,0,0))
        self.assertIn('INTERSECTION',self.codes(self.solver.geometry.validate(table,room(objects=[bed]))))

    def test_g_clearance_rejected_without_collision(self):
        bed=obj('bed','SingleWhiteBed',(0,0,0))
        chair=obj('chair','WoodenChair',(0,1.55,0.000001))
        state=room(objects=[bed])
        self.assertNotIn('INTERSECTION',self.codes(self.solver.geometry.validate(chair,state)))
        self.assertIn('CLEARANCE_BLOCKED',self.codes(self.solver.clearance.validate(chair,state)))

    def test_h_door_sweep_rejects_storage(self):
        door=obj('door','WoodenDoor',(0,0,0))
        cabinet=obj('cabinet','SteelGreenCabinet',(-0.7,0,0))
        self.assertIn('CLEARANCE_BLOCKED',self.codes(self.solver.clearance.validate(cabinet,room(objects=[door]))))

    def test_i_accessible_entrance_to_bed_usable_side(self):
        bed=obj('bed','SingleWhiteBed',(0,-1.5,0))
        state=room(objects=[bed])
        diagnostics,path=self.solver.access.validate(state,(0,0.2),'bed')
        self.assertEqual([],diagnostics)
        self.assertGreater(len(path),2)

    def test_j_blocked_accessibility_fails(self):
        barriers=[obj('barrier1','ConcreteGreenWall',(-1.65,0,2.11962),0),obj('barrier2','ConcreteGreenWall',(1.65,0,2.11962),0)]
        state=room(objects=barriers,entrance=(0,3))
        diagnostics,_=self.solver.access.validate(state,(0,-2),'target')
        self.assertIn('UNREACHABLE',self.codes(diagnostics))

    def test_k_deterministic_same_input_seed(self):
        state=room()
        intent=PlacementIntent('table','SmallWoodenTable','room_1','floor_1',seed=193)
        a=self.solver.resolve(intent,state);b=self.solver.resolve(intent,copy.deepcopy(state))
        self.assertEqual(a.placement.transform,b.placement.transform)
        self.assertEqual(a.score,b.score)

    def test_l_dry_run_does_not_mutate_scene(self):
        state=room();before=state.fingerprint()
        result=self.solver.resolve(PlacementIntent('bed','SingleWhiteBed','room_1','floor_1',seed=3),state,dry_run=True)
        self.assertEqual('VALID',result.status)
        self.assertIsNotNone(result.scene_patch)
        self.assertEqual(before,state.fingerprint())

    def test_obb_sat_rotation_and_separation(self):
        bounds=((-1,-.2,-.5),(1,.2,.5))
        a=OBB.from_local_bounds(bounds,SpatialTransform((0,0,0),(0,0,45)))
        b=OBB.from_local_bounds(bounds,SpatialTransform((0.5,0,0),(0,0,-45)))
        c=OBB.from_local_bounds(bounds,SpatialTransform((4,0,0),(0,0,-45)))
        self.assertTrue(a.intersects(b));self.assertFalse(a.intersects(c))

    def test_coordinate_conversion_requires_explicit_offset(self):
        with self.assertRaises(ValueError): SpatialTransform((0,0,0),space='ATL').with_space('ASL')
        self.assertEqual(12,SpatialTransform((0,0,2),space='ATL').with_space('ASL',asl_minus_atl=10).position[2])

    def test_intent_contract_rejects_transforms(self):
        with self.assertRaises(ValueError):
            PlacementIntent.from_json({'id':'x','asset':'SingleWhiteBed','region':'room_1','onSurface':'floor_1','position':[0,0,0]})

    def test_preferred_near_scores_target_object(self):
        state=room(objects=[obj('table','SmallWoodenTable',(1.5,1.5,0))])
        intent=PlacementIntent('chair','WoodenChair','room_1','floor_1',soft=('Compact',),seed=7,preferred_near='table')
        result=self.solver.resolve(intent,state)
        self.assertEqual('VALID',result.status)
        self.assertLess(math.dist(result.placement.transform.position[:2],(1.5,1.5)),2.0)


if __name__=='__main__': unittest.main(verbosity=2)
