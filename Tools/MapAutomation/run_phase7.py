#!/usr/bin/env python3
"""Phase 7 review-only by default; explicit --repair enables bounded live changes."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys
import time

from room_generator import MapAutomationRoomGateway,RoomGenerator
from room_generator.gateway import _fingerprint
from run_room_generator import probe_shell
from spatial.model import PlacementIntent,ResolvedObject,SpatialTransform
from spatial.solver import SolverResult
from vision_critic import BoundedRepairLoop,CriticService,OpenAICriticProvider,RepairPlanner,build_capture_bundle
from vision_critic.config import load_critic_env

ROOT=Path(__file__).resolve().parents[2]


def _capture(generation:dict,gateway:MapAutomationRoomGateway)->None:
    revision=generation["sceneRevisionAfter"];shots=[]
    source=list(generation.get("screenshots",[]))
    for index,old in enumerate(source):
        pose=old.get("cameraPose",{});role=pose.get("name") or old.get("artifact",{}).get("cameraRole")
        if not role:continue
        if index:time.sleep(5)
        response=gateway.capture(revision,[{"positionASL":pose["positionASL"],"targetASL":pose["targetASL"],"fov":pose["fov"],
            "viewId":role,"cameraRole":role,"captureClassOverlay":True}])
        shots.append({"generationId":generation["generationId"],"roomId":generation["roomId"],"revision":revision,
            "cameraPose":pose,"artifact":response["result"][0]})
    generation["screenshots"]=shots


def main()->None:
    load_critic_env();parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation",type=Path,help="Phase 6/7 generation artifact with screenshots")
    parser.add_argument("--repair",action="store_true",help="explicitly allow bounded live repair")
    parser.add_argument("--max-repairs",type=int,default=int(os.getenv("RELICTA_MAX_VISUAL_REPAIRS","2")))
    parser.add_argument("--shell",choices=["small","medium","large"],default="medium")
    parser.add_argument("--model",default=os.getenv("RELICTA_CRITIC_MODEL","gpt-5"));parser.add_argument("--timeout",type=float,default=float(os.getenv("RELICTA_CRITIC_TIMEOUT","60")))
    parser.add_argument("--no-cache",action="store_true");parser.add_argument("--interactive",action="store_true")
    parser.add_argument("--recapture-role",action="append",choices=["entrance","opposite_corner","overview"],help="replace a requested view before review")
    parser.add_argument("--live-start-delay",type=float,default=0,help="seconds to focus Eden before recapture")
    args=parser.parse_args();key=os.getenv("OPENAI_API_KEY","")
    if not key:parser.exit(2,"CRITIC_FAILED: OPENAI_API_KEY is not set.\n")
    generation=json.loads(args.generation.read_text(encoding="utf-8"))
    if args.recapture_role:
        gateway=MapAutomationRoomGateway(args.timeout);snapshot=gateway.snapshot()
        expected=generation.get("sceneFingerprintAfter");revision=generation.get("sceneRevisionAfter")
        if snapshot.revision!=revision or snapshot.fingerprint!=expected:parser.exit(2,"RECAPTURE_REJECTED: live revision/fingerprint differs from generation.\n")
        if args.live_start_delay>0:
            print(f"Recapture starts in {args.live_start_delay:g} seconds; focus Eden now.",flush=True);time.sleep(args.live_start_delay)
        shell=probe_shell(args.shell).scene;floor=next(x for x in shell.surfaces.values() if x.type=="floor");x,y,z=floor.origin;half=max(floor.half_extents)
        by_role={(row.get("cameraPose",{}).get("name") or row.get("artifact",{}).get("cameraRole")):row for row in generation.get("screenshots",[])}
        for role in dict.fromkeys(args.recapture_role):
            old=by_role.get(role)
            if old is None:parser.exit(2,f"RECAPTURE_REJECTED: role {role} is absent.\n")
            old_pose=old["cameraPose"];dz=old_pose["targetASL"][2]-(z+.7)
            if role=="opposite_corner":pose={"name":role,"positionASL":[x+half-.6,y+half-.6,z+dz+1.8],"targetASL":[x,y,z+dz+.7],"fov":.8}
            elif role=="entrance":pose={"name":role,"positionASL":[x,y-half+.8,z+dz+1.7],"targetASL":[x,y,z+dz+.8],"fov":.8}
            else:pose={"name":role,"positionASL":[x+half+3,y-half-3,z+dz+half+3],"targetASL":[x,y,z+dz+.6],"fov":.9}
            response=gateway.capture(revision,[{"positionASL":pose["positionASL"],"targetASL":pose["targetASL"],"fov":pose["fov"],"viewId":role,"cameraRole":role,"captureClassOverlay":True}])
            old.update({"revision":revision,"cameraPose":pose,"artifact":response["result"][0]})
        args.generation.write_text(json.dumps(generation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    bundle=build_capture_bundle(generation)
    service=CriticService(OpenAICriticProvider(key,args.model),model=args.model,cache_enabled=not args.no_cache,timeout=args.timeout)
    if not args.repair:
        result=service.review_capture(bundle);print(json.dumps(result.json(),ensure_ascii=False,indent=2));raise SystemExit(0 if result.status.value=="SUCCESS" else 1)
    gateway=MapAutomationRoomGateway(args.timeout);snapshot=gateway.snapshot()
    if snapshot.revision!=bundle.revision or snapshot.fingerprint!=bundle.scene_fingerprint:
        parser.exit(2,"REPAIR_REJECTED: live revision/fingerprint differs from capture bundle.\n")
    shell=probe_shell(args.shell).scene;generator=RoomGenerator(gateway=gateway);planner=RepairPlanner(generator.pipeline)
    iteration={"value":0}
    def review(index,previous):
        current=build_capture_bundle(generation,iteration=index)
        return service.review_capture(current,iteration=index,previous_issue=previous)
    def apply(operations):
        if args.interactive: input("Press Enter to apply the proposed deterministic repair...")
        response=gateway.apply(operations,generation["sceneRevisionAfter"]);generation["sceneRevisionAfter"]=response["revision"]
        by_id={x["semanticId"]:x for x in response["result"]}
        for row in generation.get("placements",[]):
            actual=by_id.get(row["id"])
            if actual:row["transform"]={"position":actual["position"],"rotation":actual["rotation"],"scale":actual.get("scale",1)}
        placements=[]
        intents={x["id"]:PlacementIntent.from_json(x) for x in generation.get("placementIntents",[])}
        for row in generation.get("placements",[]):
            intent=intents.get(row["id"])
            if not intent:continue
            obj=ResolvedObject.create(row["id"],generator.pipeline.solver.assets[row["asset"]],SpatialTransform(tuple(row["transform"]["position"]),tuple(row["transform"]["rotation"]),"EDEN").with_space("WORLD"))
            placements.append(SolverResult("VALID",intent,obj,[],[],None,[],False,None))
        diagnostics,navigation=generator._validate_scene(shell,placements)
        generation["metrics"]["navigationResult"]=navigation;generation["sceneFingerprintAfter"]=_fingerprint(response["result"])
        _capture(generation,gateway);args.generation.write_text(json.dumps(generation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return {"revision":response["revision"],"hardSpatialPass":not diagnostics,"diagnostics":diagnostics}
    loop=BoundedRepairLoop(planner,max_repairs=args.max_repairs,
        min_severity=os.getenv("RELICTA_CRITIC_MIN_SEVERITY","medium"),min_confidence=float(os.getenv("RELICTA_CRITIC_MIN_CONFIDENCE","0.75")))
    outcome=loop.run(review=review,generation=generation,shell=shell,apply=apply)
    out_dir=ROOT/"Tools/MapAutomation/artifacts/repairs";out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/f"repair_loop_{generation['generationId']}.json").write_text(json.dumps(outcome.json(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(outcome.json(),ensure_ascii=False,indent=2))
    if args.interactive: input("Review complete. Press Enter to return to the shell; cleanup remains an explicit Phase 6 operation...")


if __name__=="__main__":main()
