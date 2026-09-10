#!/usr/bin/env python3
"""Phase 7 offline contract, grounding, repair-policy, and transport regression tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from PIL import Image

from room_generator import ExistingRoomShell,GenerationOptions,RoomGenerator
from run_room_generator import probe_shell
from semantic.pipeline import build_room_context
from vision_critic import BoundedRepairLoop,CriticResult,CriticStatus,RepairPlanner,RepairStatus,StopReason,build_capture_bundle,validate_critic_output
from vision_critic.model import CriticContractError
from vision_critic.capture import render_semantic_overlay

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=json.loads((ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json").read_text(encoding="utf-8"))


def output(*,overall="PASS",issues=None):
    return {"schemaVersion":1,"overall":overall,"issues":issues or [],"recapture":{"requested":False,"cameraRoles":[],"reason":None}}


def issue(goal="REGROUP",subject="seating_001",reference="work_surface_001",confidence=.95,severity="medium"):
    targets=[x for x in (subject,reference) if x]
    return {"issueId":"visual_001","category":"RELATION_MISMATCH","severity":severity,"confidence":confidence,
        "grounding":"GROUNDED","targets":targets,"views":["entrance"],"observation":"The chair appears visually disconnected from the table.",
        "evidenceKind":"VISUAL_OBSERVATION","repairGoal":{"type":goal,"subject":subject,"reference":reference}}


def generated():
    brief=copy.deepcopy(FIXTURE);brief["seed"]=100
    result=RoomGenerator(artifact_dir=ROOT/"Tools/MapAutomation/artifacts/test_phase7_generations").generate_room("bedroom",
        ExistingRoomShell("test",build_room_context()),GenerationOptions(seed=100),planner_brief=brief)
    doc=result.json();doc["sceneRevisionAfter"]=10;doc["sceneFingerprintAfter"]="fingerprint"
    doc["screenshots"]=[{"cameraPose":{"name":"entrance","positionASL":[1,2,3],"targetASL":[4,5,6],"fov":.8},
        "artifact":{"path":"missing.png","viewId":"entrance","cameraRole":"entrance"}}]
    return doc


class VisionCriticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.base_doc=generated()
    def setUp(self):
        self.doc=copy.deepcopy(self.base_doc);self.ids={x["id"] for x in self.doc["roomPlan"]["slots"] if x["placement"]!="virtual" and not x["status"].startswith("DROPPED")}
    def test_01_pass_schema(self):self.assertEqual("PASS",validate_critic_output(output(),self.ids,{"entrance"})["overall"])
    def test_02_unknown_target_rejected(self):
        bad=issue(subject="invented_001",reference=None)
        with self.assertRaises(CriticContractError):validate_critic_output(output(overall="REPAIR",issues=[bad]),self.ids,{"entrance"})
    def test_03_coordinates_rejected(self):
        bad=issue();bad["repairGoal"]["position"]=[1,2,3]
        with self.assertRaises(CriticContractError):validate_critic_output(output(overall="REPAIR",issues=[bad]),self.ids,{"entrance"})
    def test_04_engine_fact_rejected(self):
        bad=issue();bad["evidenceKind"]="ENGINE_SOLVER_FACT"
        with self.assertRaises(CriticContractError):validate_critic_output(output(overall="REPAIR",issues=[bad]),self.ids,{"entrance"})
    def test_05_unresolved_is_explicit(self):
        row=issue(goal="REQUEST_RECAPTURE",subject=None,reference=None);row.update({"grounding":"UNRESOLVED","targets":[],"category":"UNRESOLVED"})
        self.assertEqual([],validate_critic_output(output(overall="RECAPTURE",issues=[row]),self.ids,{"entrance"})["issues"][0]["targets"])
    def test_06_capture_bundle_manifest_uses_semantic_ids(self):
        bundle=build_capture_bundle(self.doc);self.assertTrue(bundle.scene_manifest["objects"])
        self.assertIn("semanticId",bundle.scene_manifest["objects"][0]);self.assertNotIn("transform",bundle.scene_manifest["objects"][0])
    def test_07_regroup_goes_through_solver(self):
        proposal=RepairPlanner(RoomGenerator().pipeline).plan(issue(),self.doc,build_room_context())
        self.assertEqual(RepairStatus.READY,proposal.status);self.assertEqual("setTransform",proposal.operations[0]["operation"])
        self.assertTrue(any(x["code"]=="PHASE3_DRY_RUN_PASS" for x in proposal.diagnostics))
    def test_08_required_drop_is_rejected(self):
        proposal=RepairPlanner(RoomGenerator().pipeline).plan(issue("DROP_OPTIONAL","sleeping_001",None),self.doc,build_room_context())
        self.assertEqual(RepairStatus.REJECTED,proposal.status);self.assertEqual("REQUIRED_SEMANTICS_PROTECTED",proposal.diagnostics[0]["code"])
    def test_09_impossible_reference_is_rejected(self):
        row=issue();row["repairGoal"]["reference"]=None
        proposal=RepairPlanner(RoomGenerator().pipeline).plan(row,self.doc,build_room_context())
        self.assertEqual(RepairStatus.REJECTED,proposal.status)
    def _critic(self,value):
        return CriticResult("x",CriticStatus.SUCCESS,"fake","fake","v1",1,"g","r",1,0,value,[],{},0,1)
    def test_10_clean_baseline_noop(self):
        loop=BoundedRepairLoop(RepairPlanner(RoomGenerator().pipeline));result=loop.run(review=lambda i,p:self._critic(output()),generation=self.doc,shell=build_room_context())
        self.assertEqual(StopReason.PASS,result.stop_reason);self.assertEqual(0,result.repairs_applied)
    def test_11_low_confidence_does_not_repair(self):
        value=output(overall="REPAIR",issues=[issue(confidence=.4)])
        result=BoundedRepairLoop(RepairPlanner(RoomGenerator().pipeline)).run(review=lambda i,p:self._critic(value),generation=self.doc,shell=build_room_context())
        self.assertEqual(StopReason.LOW_CONFIDENCE,result.stop_reason)
    def test_12_review_only_is_default(self):
        value=output(overall="REPAIR",issues=[issue()]);result=BoundedRepairLoop(RepairPlanner(RoomGenerator().pipeline)).run(review=lambda i,p:self._critic(value),generation=self.doc,shell=build_room_context())
        self.assertEqual(StopReason.REVIEW_ONLY,result.stop_reason)
    def test_13_no_progress_stops_repeat(self):
        value=output(overall="REPAIR",issues=[issue()]);calls=[]
        result=BoundedRepairLoop(RepairPlanner(RoomGenerator().pipeline),max_repairs=2).run(review=lambda i,p:self._critic(value),generation=self.doc,shell=build_room_context(),apply=lambda ops:(calls.append(ops) or {"hardSpatialPass":True}))
        self.assertEqual(StopReason.NO_PROGRESS,result.stop_reason);self.assertEqual(1,len(calls))
    def test_14_regression_stops(self):
        value=output(overall="REPAIR",issues=[issue()]);result=BoundedRepairLoop(RepairPlanner(RoomGenerator().pipeline)).run(review=lambda i,p:self._critic(value),generation=self.doc,shell=build_room_context(),apply=lambda ops:{"hardSpatialPass":False})
        self.assertEqual(StopReason.REGRESSION,result.stop_reason)
    def test_15_png_never_read_by_sqf_queue(self):
        transport=(ROOT/"Src/Editor/MapAutomation/MapAutomation_transport.sqf").read_text(encoding="utf-8")
        capture=(ROOT/"Src/Editor/MapAutomation/MapAutomation_capture.sqf").read_text(encoding="utf-8")
        self.assertNotIn("file_read _path",capture);self.assertIn("classOverlayPath",capture);self.assertIn("[_overlayStateBefore] call ma_setClassOverlay",capture)
        self.assertNotIn("base64",transport.casefold())
    def test_16_semantic_overlay_changes_only_output_copy(self):
        clean=ROOT/"Tools/MapAutomation/artifacts/test_overlay_clean.png"
        overlay=ROOT/"Tools/MapAutomation/artifacts/test_overlay_result.png"
        try:
            Image.new("RGB",(640,360),(64,64,64)).save(clean)
            doc={"placements":[{"id":"seating_001","asset":"WoodenChair","transform":{"position":[0,4,0]}},
                {"id":"work_surface_001","asset":"SmallWoodenTable","transform":{"position":[1,4,0]}}]}
            pose={"positionASL":[0,0,1],"targetASL":[0,4,0],"fov":.8}
            render_semantic_overlay(str(clean),str(overlay),doc,pose)
            self.assertTrue(overlay.is_file())
            with Image.open(overlay) as rendered:self.assertEqual((640,360),rendered.size)
            self.assertNotEqual(clean.read_bytes(),overlay.read_bytes())
        finally:
            clean.unlink(missing_ok=True);overlay.unlink(missing_ok=True)
    def test_17_move_away_removes_compact_preference(self):
        proposal=RepairPlanner(RoomGenerator().pipeline).plan(issue("MOVE_AWAY","seating_001","work_surface_001"),self.doc,build_room_context())
        self.assertEqual(RepairStatus.READY,proposal.status)
        self.assertNotIn("Compact",proposal.intent["softPreferences"]);self.assertIn("MaximizeCirculation",proposal.intent["softPreferences"])


if __name__=="__main__":unittest.main(verbosity=2)
