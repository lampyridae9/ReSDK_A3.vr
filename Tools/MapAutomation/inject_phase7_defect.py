#!/usr/bin/env python3
"""Inject one deterministic, solver-valid visual acceptance defect."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import time

from room_generator import MapAutomationRoomGateway,RoomGenerator
from room_generator.gateway import _fingerprint
from run_phase7 import _capture
from run_room_generator import probe_shell
from spatial.model import PlacementIntent,ResolvedObject,SpatialTransform
from spatial.solver import SolverResult
from vision_critic import RepairPlanner


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation",type=Path)
    parser.add_argument("--shell",choices=["small","medium","large"],default="medium")
    parser.add_argument("--timeout",type=float,default=60)
    parser.add_argument("--live-start-delay",type=float,default=0)
    args=parser.parse_args();generation=json.loads(args.generation.read_text(encoding="utf-8"))
    gateway=MapAutomationRoomGateway(args.timeout);snapshot=gateway.snapshot()
    if snapshot.revision!=generation.get("sceneRevisionAfter") or snapshot.fingerprint!=generation.get("sceneFingerprintAfter"):
        parser.exit(2,"DEFECT_REJECTED: live revision/fingerprint differs from generation.\n")
    shell=probe_shell(args.shell).scene;generator=RoomGenerator(gateway=gateway);planner=RepairPlanner(generator.pipeline)
    issue={"category":"RELATION_MISMATCH","targets":["seating_001","work_surface_001"],
        "repairGoal":{"type":"MOVE_AWAY","subject":"seating_001","reference":"work_surface_001"}}
    proposal=planner.plan(issue,generation,shell)
    if proposal.status.value!="READY":parser.exit(2,"DEFECT_REJECTED: deterministic solver found no valid separated chair position.\n")
    old=next(x for x in generation["placements"] if x["id"]=="seating_001")["transform"]
    response=gateway.apply(proposal.operations,generation["sceneRevisionAfter"]);by_id={x["semanticId"]:x for x in response["result"]}
    for row in generation.get("placements",[]):
        actual=by_id.get(row["id"])
        if actual:row["transform"]={"position":actual["position"],"rotation":actual["rotation"],"scale":actual.get("scale",1)}
    intents=generation.get("placementIntents",[]);intents[:]=[x for x in intents if x.get("id")!="seating_001"]+[proposal.intent]
    placements=[];intent_by_id={x["id"]:PlacementIntent.from_json(x) for x in intents}
    for row in generation.get("placements",[]):
        intent=intent_by_id.get(row["id"])
        if not intent:continue
        obj=ResolvedObject.create(row["id"],generator.pipeline.solver.assets[row["asset"]],
            SpatialTransform(tuple(row["transform"]["position"]),tuple(row["transform"]["rotation"]),"EDEN").with_space("WORLD"))
        placements.append(SolverResult("VALID",intent,obj,[],[],None,[],False,None))
    diagnostics,navigation=generator._validate_scene(shell,placements)
    if diagnostics:parser.exit(2,"DEFECT_REJECTED: post-apply hard validation failed; manual cleanup is required.\n")
    generation["sceneRevisionAfter"]=response["revision"];generation["sceneFingerprintAfter"]=_fingerprint(response["result"])
    generation["transaction"]["revisionCommitted"]=response["revision"];generation["metrics"]["navigationResult"]=navigation
    current=next(x for x in generation["placements"] if x["id"]=="seating_001")["transform"]
    generation["visualDefectFixture"]={"type":"SEATING_SEPARATED_FROM_WORK_SURFACE","subject":"seating_001",
        "reference":"work_surface_001","originalTransform":copy.deepcopy(old),"defectTransform":copy.deepcopy(current),
        "hardSpatialPass":True,"revision":response["revision"]}
    if args.live_start_delay>0:
        print(f"Defect capture starts in {args.live_start_delay:g} seconds; focus Eden now.",flush=True);time.sleep(args.live_start_delay)
    _capture(generation,gateway);args.generation.write_text(json.dumps(generation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"SUCCESS","revision":response["revision"],"defect":generation["visualDefectFixture"]},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
