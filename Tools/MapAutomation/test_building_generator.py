#!/usr/bin/env python3
"""Phase 8 contract, layout, accessibility, orchestration, and transaction tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from building_generator import (BuildingAccessibilityValidator,BuildingFootprint,BuildingGenerator,BuildingLayoutSolver,
    BuildingOptions,BuildingStatus,expand_building_plan,validate_building_brief)
from room_generator import GenerationStatus
from room_generator.gateway import SceneSnapshot,_fingerprint

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=json.loads((ROOT/"Tools/MapAutomation/fixtures/poor_worker_dormitory_2f.json").read_text(encoding="utf-8"))
ARTIFACTS=ROOT/"Tools/MapAutomation/artifacts/test_phase8"


def brief(floors:int=2,bedrooms:int=4,residents:int=8,seed:int=1234,storage:bool=False)->dict:
    value=copy.deepcopy(FIXTURE);value["floors"]=floors;value["requirements"]["bedrooms"]=bedrooms
    value["requirements"]["storage"]=storage;value["capacity"]["residents"]=residents;value["seed"]=seed;return value


def layout(value:dict|None=None,width:float=12,depth:float=10.05624):
    value=value or brief();plan=expand_building_plan(value)
    return plan,BuildingLayoutSolver().solve(plan,BuildingFootprint((100,100,10),width,depth,2),value,BuildingOptions(mode="layout-only",seed=value["seed"]))


class FakeRoomGenerator:
    def __init__(self,fail_at:int|None=None):self.calls=[];self.fail_at=fail_at
    def generate_room(self,request,shell,options,*,planner_brief,room_id,slot_namespace=None):
        self.calls.append((room_id,slot_namespace,planner_brief))
        if self.fail_at==len(self.calls):return SimpleNamespace(status=GenerationStatus.INFEASIBLE,room_plan=None,placements=[],dropped_optional=[],metrics={},diagnostics=[])
        sid=f"{room_id}__sleeping_001"
        return SimpleNamespace(status=GenerationStatus.SUCCESS,room_plan={"id":room_id,"slots":[{"id":sid}]},
            placements=[{"id":sid,"asset":"SingleWhiteBed","transform":{"position":[100,100,10],"rotation":[0,0,0]}}],
            dropped_optional=[],metrics={"backtracks":0,"navigationResult":{"reachable":True}},diagnostics=[])


class FakeGateway:
    def __init__(self,fail=False):self.revision=5;self.objects=[{"semanticId":"user_keep","class":"UserObject","position":[0,0,0]}];self.fail=fail
    def snapshot(self):return SceneSnapshot(self.revision,copy.deepcopy(self.objects),_fingerprint(self.objects),"fake")
    def apply(self,operations,expected_revision):
        if self.fail:raise RuntimeError("injected")
        self.objects.extend({"semanticId":x["arguments"]["semanticId"],"class":x["arguments"]["class"],"position":x["arguments"]["position"]} for x in operations)
        self.revision+=1;return {"status":"OK","revision":self.revision,"result":copy.deepcopy(self.objects)}
    def inspect(self,revision):return {"status":"OK","revision":self.revision,"result":copy.deepcopy(self.objects)}
    def capture(self,revision,views):return {"status":"OK","revision":revision,"result":[{"path":"fake.png"}]}
    def cleanup(self,ids,expected_revision):
        self.objects=[x for x in self.objects if x["semanticId"] not in set(ids)];self.revision+=1
        return {"status":"OK","revision":self.revision,"result":copy.deepcopy(self.objects)}


class Phase8Tests(unittest.TestCase):
    def test_01_building_brief_schema(self):self.assertEqual("poor_worker_dormitory",validate_building_brief(brief())["buildingType"])
    def test_02_forbidden_coordinates_and_classname(self):
        for field in ("position","classname","rawSQF","python"):
            value=brief();value[field]=[1,2,3]
            with self.assertRaises(ValueError):validate_building_brief(value)
    def test_03_deterministic_building_plan(self):self.assertEqual(expand_building_plan(brief()).json(),expand_building_plan(brief()).json())
    def test_04_different_seed_variation(self):
        variants=set()
        for seed in range(8):
            _,made=layout(brief(seed=seed));variants.add(json.dumps(made.candidate,sort_keys=True))
        self.assertGreater(len(variants),1)
    def test_05_partition_no_overlap(self):
        _,made=layout()
        for floor in made.floors:
            for i,a in enumerate(floor.spaces):
                for b in floor.spaces[i+1:]:
                    overlap=max(0,min(a.rect.x2,b.rect.x2)-max(a.rect.x,b.rect.x))*max(0,min(a.rect.y2,b.rect.y2)-max(a.rect.y,b.rect.y))
                    self.assertEqual(0,overlap)
    def test_06_rooms_inside_footprint(self):
        _,made=layout();outer=made.floors[0].footprint
        self.assertTrue(all(outer.contains(x,y) for f in made.floors for s in f.spaces for x,y in ((s.rect.x,s.rect.y),(s.rect.x2,s.rect.y2))))
    def test_07_corridor_width(self):
        _,made=layout();self.assertTrue(all(min(f.spaces[0].rect.width,f.spaces[0].rect.depth)>=1.5 for f in made.floors))
    def test_08_portal_on_shared_wall(self):
        _,made=layout()
        for floor in made.floors:
            walls={x.id:x for x in floor.walls}
            for portal in floor.portals:self.assertEqual({portal.to_space} if portal.exterior else {portal.from_space,portal.to_space},set(walls[portal.wall_segment].owners))
    def test_09_exterior_entrance_connectivity(self):
        plan,made=layout();self.assertFalse(BuildingAccessibilityValidator().validate(made,plan));self.assertTrue(any(p.exterior for p in made.floors[0].portals))
    def test_10_required_rooms_connected(self):
        plan,made=layout();self.assertFalse(any(x["code"]=="ROOM_DISCONNECTED" for x in BuildingAccessibilityValidator().validate(made,plan)))
    def test_11_room_generator_reuse_without_llm_per_room(self):
        rooms=FakeRoomGenerator();result=BuildingGenerator(room_generator=rooms,artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        self.assertEqual(BuildingStatus.SUCCESS,result.status);self.assertEqual(4,len(rooms.calls));self.assertEqual(0,result.metrics["llmCalls"])
    def test_12_hierarchical_ids_and_ownership(self):
        result=BuildingGenerator(room_generator=FakeRoomGenerator(),artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        ids=[x["semanticId"] for x in result.ownership["objects"]];self.assertEqual(len(ids),len(set(ids)));self.assertTrue(any(x.startswith("bedroom_001__") for x in ids))
    def test_13_required_room_failure_is_infeasible(self):
        _,made=layout(width=5,depth=5);self.assertEqual("INFEASIBLE",made.feasibility)
    def test_14_optional_room_degradation(self):
        _,made=layout(brief(floors=1,bedrooms=2,residents=4,storage=True),width=12,depth=7)
        self.assertNotEqual("INFEASIBLE",made.feasibility);self.assertTrue(any(x["code"]=="OPTIONAL_ROOM_DROPPED" for x in made.diagnostics))
    def test_15_single_floor_building(self):
        _,made=layout(brief(floors=1,bedrooms=2,residents=4));self.assertEqual(1,len(made.floors));self.assertEqual(2,len([x for x in made.floors[0].spaces if x.kind=="bedroom"]))
    def test_16_two_floor_representation(self):
        _,made=layout();self.assertEqual([0,1],[x.index for x in made.floors])
    def test_17_vertical_connection_validation(self):
        plan,made=layout();self.assertEqual(1,len(made.floors[0].vertical_connections));self.assertFalse(BuildingAccessibilityValidator().validate(made,plan))
        vertical=made.floors[0].vertical_connections[0];corridor=made.floors[0].spaces[0].rect
        self.assertTrue(corridor.contains(vertical.occupied_region.x,vertical.occupied_region.y))
        self.assertTrue(corridor.contains(vertical.occupied_region.x2,vertical.occupied_region.y2))
        self.assertEqual("StoneBigLadderDouble",vertical.asset)
    def test_18_same_seed_reproducibility(self):
        _,a=layout();_,b=layout();self.assertEqual(a.fingerprint(),b.fingerprint())
    def test_19_dry_run_does_not_call_gateway(self):
        gateway=FakeGateway();before=copy.deepcopy(gateway.objects)
        result=BuildingGenerator(room_generator=FakeRoomGenerator(),gateway=gateway,artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        self.assertEqual(before,gateway.objects);self.assertEqual(BuildingStatus.SUCCESS,result.status)
    def test_20_required_partial_room_failure_aborts_before_apply(self):
        gateway=FakeGateway();before=copy.deepcopy(gateway.objects)
        result=BuildingGenerator(room_generator=FakeRoomGenerator(4),gateway=gateway,artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),BuildingOptions(mode="live"),building_brief=brief())
        self.assertEqual(BuildingStatus.ROOM_GENERATION_FAILED,result.status);self.assertEqual(before,gateway.objects)
    def test_21_budget_report(self):
        result=BuildingGenerator(room_generator=FakeRoomGenerator(),artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        self.assertGreater(result.budget["totalObjects"],0);self.assertIn("objectsPerChunk",result.budget)
    def test_22_single_floor_live_shell_and_cleanup(self):
        gateway=FakeGateway();generator=BuildingGenerator(room_generator=FakeRoomGenerator(),gateway=gateway,artifact_dir=ARTIFACTS)
        result=generator.generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),BuildingOptions(mode="live",shell_only=True,keep_result=True,capture=False),building_brief=brief(1,2,4))
        self.assertEqual(BuildingStatus.SUCCESS,result.status);generator.cleanup(result);self.assertEqual(["user_keep"],[x["semanticId"] for x in gateway.objects])
    def test_23_two_floor_live_shell_and_cleanup(self):
        gateway=FakeGateway();generator=BuildingGenerator(room_generator=FakeRoomGenerator(),gateway=gateway,artifact_dir=ARTIFACTS)
        result=generator.generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),BuildingOptions(mode="live",shell_only=True,keep_result=True,capture=False),building_brief=brief())
        self.assertEqual(BuildingStatus.SUCCESS,result.status)
        self.assertTrue(any(x["arguments"]["class"]=="StoneBigLadderDouble" for x in result.shell_operations))
        generator.cleanup(result);self.assertEqual(["user_keep"],[x["semanticId"] for x in gateway.objects])
    def test_24_room_failure_is_not_success(self):
        result=BuildingGenerator(room_generator=FakeRoomGenerator(1),artifact_dir=ARTIFACTS).generate("fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        self.assertEqual(BuildingStatus.ROOM_GENERATION_FAILED,result.status)

    def test_25_shell_uses_real_module_palette_and_aligned_floors(self):
        result=BuildingGenerator(room_generator=FakeRoomGenerator(),artifact_dir=ARTIFACTS).generate(
            "fixture",BuildingFootprint((100,100,10),12,10.05624,2),building_brief=brief())
        self.assertEqual(BuildingStatus.SUCCESS,result.status)
        walls=[x for x in result.shell_operations if x["stage"]=="walls"]
        classes={x["arguments"]["class"] for x in walls}
        self.assertTrue({"BrickThinWallSmall","SteelThinWallSmall","MediumWoodenWall"}&classes)
        self.assertTrue(any("Window" in name for name in classes))
        self.assertEqual({10,13.3},{round(x["arguments"]["position"][2],4) for x in walls})
        floors=[x for x in result.shell_operations if x["stage"]=="floors" and "floor_001" in x["arguments"]["semanticId"]]
        xs=sorted({round(x["arguments"]["position"][0],5) for x in floors})
        ys=sorted({round(x["arguments"]["position"][1],5) for x in floors})
        self.assertTrue(all(abs((b-a)-4.01182)<1e-4 for a,b in zip(xs,xs[1:])))
        self.assertTrue(all(abs((b-a)-2.03604)<1e-4 for a,b in zip(ys,ys[1:])))

    def test_26_door_openings_are_wider_than_the_measured_door(self):
        profile=BuildingGenerator(room_generator=FakeRoomGenerator(),artifact_dir=ARTIFACTS).profile
        self.assertGreaterEqual(profile["structure"]["doorClearWidth"],profile["structure"]["doorWidth"]+.04)


if __name__=="__main__":unittest.main(verbosity=2)
