#!/usr/bin/env python3
"""Phase 6 room-generator orchestration, search, transaction, and replay tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from planner import PlannerStatus
from room_generator import ExistingRoomShell, GenerationOptions, GenerationStatus, RoomGenerator
from room_generator.gateway import SceneSnapshot, _fingerprint
from run_room_generator import probe_shell
from semantic.pipeline import build_room_context

ROOT=Path(__file__).resolve().parents[2]
TEST_ARTIFACTS=ROOT/"Tools/MapAutomation/artifacts/test_phase6"
FIXTURE=json.loads((ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json").read_text(encoding="utf-8"))


def brief(capacity: int=2, seed: int=100) -> dict:
    value=copy.deepcopy(FIXTURE);value["capacity"]["people"]=capacity;value["requirements"]["sleeping"]=capacity;value["seed"]=seed
    return value


class FakePlanner:
    def __init__(self,value: dict):self.value=value;self.calls=0
    def plan_room(self,planner_input):
        self.calls+=1;value=copy.deepcopy(self.value);value["seed"]=planner_input.seed if planner_input.seed is not None else value["seed"]
        data={"status":"SUCCESS","attemptCount":1,"validatedOutput":value}
        return SimpleNamespace(status=PlannerStatus.SUCCESS,validated_output=value,usage={"totalTokens":10},latency_ms=7,
            diagnostics=[],json=lambda:data)


class FakeGateway:
    def __init__(self):
        self.revision=10;self.objects=[{"semanticId":"user_keep","class":"UserObject","position":[1,2,3],"rotation":[0,0,0]}]
        self.applies=0;self.captures=0
    def snapshot(self):return SceneSnapshot(self.revision,copy.deepcopy(self.objects),_fingerprint(self.objects),"fake_probe")
    def apply(self,operations,expected_revision):
        assert expected_revision==self.revision;self.applies+=1
        for op in operations:
            args=op["arguments"]
            if op["operation"]=="create":
                self.objects.append({"semanticId":args["semanticId"],"class":args["class"],"position":args["position"],
                    "positionASL":[args["position"][0],args["position"][1],args["position"][2]+100],"rotation":args["rotation"],
                    "scale":args.get("scale",1),"parentId":args.get("parentId","")})
            elif op["operation"]=="delete":self.objects=[row for row in self.objects if row["semanticId"]!=args["semanticId"]]
        self.revision+=1;return {"status":"OK","revision":self.revision,"result":copy.deepcopy(self.objects),"diagnostics":[]}
    def inspect(self,revision):
        assert revision==self.revision;return {"status":"OK","revision":self.revision,"result":copy.deepcopy(self.objects),"diagnostics":[]}
    def capture(self,revision,views):
        assert revision==self.revision;self.captures+=1
        return {"status":"OK","revision":revision,"result":[{"path":f"shot_{i}.png"} for i in range(len(views))],"diagnostics":[]}
    def cleanup(self,ids,expected_revision):
        operations=[{"operation":"delete","arguments":{"semanticId":sid}} for sid in ids if any(x["semanticId"]==sid for x in self.objects)]
        return self.apply(operations,expected_revision) if operations else self.inspect(expected_revision)


class RoomGeneratorTests(unittest.TestCase):
    def generator(self,**kwargs):return RoomGenerator(artifact_dir=TEST_ARTIFACTS,**kwargs)
    def dry(self,capacity=2,half=3.5,seed=100,**options):
        return self.generator().generate_room("bedroom",ExistingRoomShell("test",build_room_context(half=half)),
            GenerationOptions(seed=seed,**options),planner_brief=brief(capacity,seed))

    def test_01_capacity_one(self):self.assertEqual(GenerationStatus.SUCCESS,self.dry(1).status)
    def test_02_capacity_two(self):self.assertEqual(GenerationStatus.SUCCESS,self.dry(2).status)
    def test_03_capacity_three(self):self.assertEqual(GenerationStatus.SUCCESS,self.dry(3).status)
    def test_04_capacity_four(self):
        result=self.dry(4);self.assertEqual(GenerationStatus.SUCCESS,result.status)
        self.assertEqual(4,sum(x["slotId"].startswith("sleeping_") for x in result.resolved_assets))
    def test_05_small_valid_shell(self):self.assertEqual(GenerationStatus.SUCCESS,self.dry(1,2.0).status)
    def test_06_too_small_controlled_infeasible(self):
        result=self.dry(2,.8);self.assertEqual(GenerationStatus.INFEASIBLE,result.status);self.assertEqual([],result.semantic_ids)
    def test_07_optional_furniture_dropped(self):
        result=self.dry(1,2.0);self.assertEqual(GenerationStatus.SUCCESS,result.status);self.assertTrue(result.dropped_optional)
    def test_08_required_search_backtracks_with_bounded_alternatives(self):
        result=self.dry(2,2.0,0,candidate_limit=4,max_backtracks=8)
        self.assertEqual(GenerationStatus.INFEASIBLE,result.status);self.assertGreater(result.metrics["backtracks"],0)
        self.assertLessEqual(result.metrics["backtracks"],9)
    def test_09_same_seed_reproducible(self):
        a=self.dry(2,3.5,200);b=self.dry(2,3.5,200)
        self.assertEqual(a.room_plan,b.room_plan);self.assertEqual(a.placements,b.placements)
    def test_10_different_seed_variation(self):
        values=[self.dry(2,3.5,seed) for seed in (100,200,300)]
        self.assertTrue(all(x.status==GenerationStatus.SUCCESS for x in values))
        self.assertGreater(len({(x.room_plan["strategy"],json.dumps(x.placements,sort_keys=True)) for x in values}),1)
    def test_11_dry_run_changes_nothing(self):
        shell=ExistingRoomShell("test",build_room_context());before=shell.scene.fingerprint()
        result=self.generator().generate_room("bedroom",shell,GenerationOptions(seed=100),planner_brief=brief())
        self.assertEqual(before,shell.scene.fingerprint());self.assertEqual(before,result.scene_fingerprint_after)
    def test_12_live_generation_readback_and_screenshots(self):
        gateway=FakeGateway();result=self.generator(gateway=gateway).generate_room("bedroom",probe_shell("medium"),
            GenerationOptions("live",100,keep_result=True),planner_brief=brief())
        self.assertEqual(GenerationStatus.SUCCESS,result.status);self.assertEqual(3,len(result.screenshots));self.assertEqual(1,gateway.applies)
        self.assertTrue(result.metrics["navigationResult"]["reachable"])
    def test_13_preflight_failure_leaves_live_scene_clean(self):
        gateway=FakeGateway();before=copy.deepcopy(gateway.objects)
        result=self.generator(gateway=gateway).generate_room("bedroom",probe_shell("too-small"),GenerationOptions("live",100),planner_brief=brief())
        self.assertEqual(GenerationStatus.INFEASIBLE,result.status);self.assertEqual(before,gateway.objects);self.assertEqual(0,gateway.applies)
    def test_14_cleanup_only_generation_owned_objects(self):
        gateway=FakeGateway();generator=self.generator(gateway=gateway)
        result=generator.generate_room("bedroom",probe_shell("medium"),GenerationOptions("live",100,keep_result=True),planner_brief=brief())
        generator.cleanup(result);self.assertEqual(["user_keep"],[x["semanticId"] for x in gateway.objects]);self.assertEqual("CLEAN",result.ownership["cleanupStatus"])
    def test_15_planner_invoked_once_during_spatial_search(self):
        planner=FakePlanner(brief(2,0));result=self.generator(planner_service=planner).generate_room("bedroom",ExistingRoomShell("test",build_room_context(half=2.0)),
            GenerationOptions(seed=0,candidate_limit=4,max_backtracks=8))
        self.assertEqual(1,planner.calls);self.assertGreater(result.metrics["backtracks"],0)
    def test_16_unsupported_shell_is_controlled(self):
        scene=build_room_context();scene.surfaces={k:v for k,v in scene.surfaces.items() if v.type!="ceiling"}
        result=self.generator().generate_room("bedroom",ExistingRoomShell("bad",scene),GenerationOptions(),planner_brief=brief())
        self.assertEqual(GenerationStatus.UNSUPPORTED_ROOM_GEOMETRY,result.status)
    def test_17_regenerate_reuses_brief_without_planner(self):
        generator=self.generator();first=self.dry(2,3.5,100);second=generator.regenerate_room(first,ExistingRoomShell("test",build_room_context()),200)
        self.assertEqual("REPLAYED",second.planner_result["status"]);self.assertEqual(200,second.planner_brief["seed"])


if __name__=="__main__":unittest.main(verbosity=2)
