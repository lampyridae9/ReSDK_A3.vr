#!/usr/bin/env python3
"""Phase 4 semantic contract and end-to-end dry-run tests."""
from __future__ import annotations

import copy
from dataclasses import replace
import json
from pathlib import Path
import unittest

from semantic.model import SemanticSlot
from semantic.pipeline import AssetResolver, PatternPipeline, PlannerContractError, build_room_context, validate_planner_brief

ROOT = Path(__file__).resolve().parents[2]


class PatternSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json"
        cls.brief = json.loads(fixture.read_text(encoding="utf-8"))

    def setUp(self): self.pipeline = PatternPipeline()

    def test_01_valid_bedroom(self):
        result = self.pipeline.run(self.brief, build_room_context())
        self.assertEqual("PASS", result.status)
        self.assertEqual(2, sum(s.function == "sleeping" and s.status == "PLACED" for s in result.plan.slots))

    def test_02_one_person_cardinality(self):
        brief=copy.deepcopy(self.brief);brief["capacity"]["people"]=1;brief["requirements"]["sleeping"]=1
        result=self.pipeline.run(brief,build_room_context())
        self.assertEqual("PASS",result.status)
        self.assertEqual(1,sum(s.function=="sleeping" for s in result.plan.slots))

    def test_03_missing_required_sleeping(self):
        plan=self.pipeline.create_plan(self.brief,build_room_context());plan.slots=[s for s in plan.slots if s.function!="sleeping"]
        self.assertIn("REQUIRED_FUNCTION_MISSING",{d.code for d in self.pipeline.validate_plan(plan)})

    def test_04_unknown_room_type(self):
        brief=copy.deepcopy(self.brief);brief["roomType"]="kitchen"
        with self.assertRaises(PlannerContractError): validate_planner_brief(brief)

    def test_05_unknown_style(self):
        brief=copy.deepcopy(self.brief);brief["style"]=["baroque"]
        with self.assertRaises(PlannerContractError): validate_planner_brief(brief)

    def test_06_generator_allowed_hard_gate(self):
        resolver=AssetResolver();resolver.assets["SingleWhiteBed"]=replace(resolver.assets["SingleWhiteBed"],generator_allowed=False)
        slot=SemanticSlot("sleeping_001","sleeping","required",1,"floor",(),("poor",))
        with self.assertRaisesRegex(ValueError,"UNRESOLVED_ASSET"): resolver.resolve(slot)

    def test_07_optional_table_cannot_fit(self):
        brief=copy.deepcopy(self.brief);brief["requirements"]["sleeping"]=1;brief["capacity"]["people"]=1
        result=self.pipeline.run(brief,build_room_context(half=2.0))
        self.assertEqual("PASS",result.status)
        self.assertIn("OPTIONAL_DROPPED",{d.code for d in result.diagnostics})
        table=next(s for s in result.plan.slots if s.function=="work_surface")
        self.assertEqual("DROPPED_PREFERRED",table.status)

    def test_08_required_bed_cannot_fit(self):
        result=self.pipeline.run(self.brief,build_room_context(half=.8))
        self.assertEqual("INFEASIBLE",result.status)
        self.assertIn("PATTERN_INFEASIBLE",{d.code for d in result.diagnostics})

    def test_09_same_seed_identical_plan(self):
        a=self.pipeline.create_plan(self.brief,build_room_context()).json();b=self.pipeline.create_plan(self.brief,build_room_context()).json()
        self.assertEqual(a,b)

    def test_10_different_seed_strategy(self):
        strategies=set()
        for seed in range(20):
            brief=copy.deepcopy(self.brief);brief["seed"]=seed
            strategies.add(self.pipeline.create_plan(brief,build_room_context()).strategy)
        self.assertGreaterEqual(len(strategies),2)

    def test_11_coordinates_rejected(self):
        brief=copy.deepcopy(self.brief);brief["position"]=[0,0,0]
        with self.assertRaisesRegex(PlannerContractError,"forbidden"): validate_planner_brief(brief)

    def test_12_arbitrary_classname_rejected(self):
        brief=copy.deepcopy(self.brief);brief["preferences"]["classname"]="Anything"
        with self.assertRaisesRegex(PlannerContractError,"forbidden"): validate_planner_brief(brief)

    def test_13_semantic_to_intent(self):
        result=self.pipeline.run(self.brief,build_room_context())
        required={s.id for s in result.plan.slots if s.priority=="required" and s.placement!="virtual"}
        self.assertEqual(required,{i.id for i in result.intents if i.id in required})
        self.assertTrue(all("InsideRegion" in i.hard and "AvoidIntersection" in i.hard for i in result.intents))

    def test_14_full_phase3_dry_run(self):
        scene=build_room_context();before=scene.fingerprint();result=self.pipeline.run(self.brief,scene)
        self.assertEqual("PASS",result.status)
        self.assertEqual(before,scene.fingerprint())
        self.assertTrue(all(p.status=="VALID" and p.dry_run for p in result.placements))

    def test_contract_schema_matches_fixture(self):
        schema=json.loads((ROOT/"Tools/MapAutomation/planner_room_brief.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(1,schema["properties"]["schemaVersion"]["const"])
        self.assertEqual(self.brief,validate_planner_brief(self.brief))


if __name__ == "__main__": unittest.main(verbosity=2)
