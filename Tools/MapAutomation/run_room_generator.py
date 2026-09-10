#!/usr/bin/env python3
"""Phase 6 one-command room generator. Safe default: dry-run."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

from planner import OpenAIResponsesProvider, PlannerService, load_planner_env
from room_generator import ExistingRoomShell, GenerationOptions, MapAutomationRoomGateway, RoomGenerator
from room_generator.gateway import _fingerprint
from semantic.pipeline import build_room_context, validate_planner_brief

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE=ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json"
SHELL_SIZES={"too-small":0.8,"small":2.0,"medium":3.5,"large":4.5}


def probe_shell(name: str) -> ExistingRoomShell:
    scene=build_room_context(half=SHELL_SIZES[name]);x,y,z=scene.surfaces["floor_1"].origin;half=SHELL_SIZES[name]
    spacing=max(.45,half/2+.1);operations=[]
    # The medium acceptance fixture uses low-profile concrete panels.  The
    # wooden floor model has raised metal edge strips; when four tiles meet in
    # the room centre those strips look like furniture clipping in screenshots.
    if name=="medium":
        floor_index=0
        for dx in (-3*half/4,-half/4,half/4,3*half/4):
            for dy in (-half/2,half/2):
                floor_index+=1
                operations.append({"operation":"create","arguments":{"semanticId":f"phase7_floor_{floor_index:03d}","class":"ConcretePanel",
                    "position":[x+dx,y+dy,z-.0922552],"rotation":[0,0,0],"scale":1,"parentId":"room_001"}})
    else:
        for index,(dx,dy) in enumerate(((-spacing,-spacing),(spacing,-spacing),(-spacing,spacing),(spacing,spacing)),1):
            operations.append({"operation":"create","arguments":{"semanticId":f"phase6_floor_{index:03d}","class":"WoodenSmallFloor",
                "position":[x+dx,y+dy,z-.134262],"rotation":[0,0,0],"scale":1,"parentId":"room_001"}})
    for index,(dx,dy) in enumerate(((-spacing,-spacing),(spacing,-spacing),(-spacing,spacing),(spacing,spacing)),1):
        operations.append({"operation":"create","arguments":{"semanticId":f"phase7_ceiling_{index:03d}","class":"WoodenSmallFloor",
            "position":[x+dx,y+dy,z+3+.134262],"rotation":[0,0,0],"scale":1,"parentId":"room_001"}})
    # Materialize the same planes used by the solver. ConcreteGreenWall's measured
    # thickness is shifted outside each abstract inner wall surface, so furnishing
    # remains governed by the unchanged Phase 3 room geometry.
    thickness=.396442;wall_z=z+2.11962;offsets=(-2*half/3,0,2*half/3);wall_index=0
    for side in ("north","east","west"):
        for along in offsets:
            wall_index+=1
            if side=="north":position=[x+along,y+half+thickness,wall_z];yaw=0
            elif side=="east":position=[x+half+thickness,y+along,wall_z];yaw=90
            else:position=[x-half-thickness,y+along,wall_z];yaw=90
            operations.append({"operation":"create","arguments":{"semanticId":f"phase7_wall_{wall_index:03d}","class":"ConcreteGreenWall",
                "position":position,"rotation":[0,0,yaw],"scale":1,"parentId":"room_001"}})
    # South leaves a centered 1m+ visual doorway around entrance_shell_001.
    for along in (offsets[0],offsets[2]):
        wall_index+=1;operations.append({"operation":"create","arguments":{"semanticId":f"phase7_wall_{wall_index:03d}","class":"ConcreteGreenWall",
            "position":[x+along,y-half-thickness,wall_z],"rotation":[0,0,0],"scale":1,"parentId":"room_001"}})
    door=scene.objects[0]
    operations.append({"operation":"create","arguments":{"semanticId":door.id,"class":door.asset.classname,
        **door.transform.gateway(),"parentId":"room_001"}})
    return ExistingRoomShell(f"probe_{name}",scene,operations)


def load_brief(path: Path) -> dict:
    doc=json.loads(path.read_text(encoding="utf-8"))
    candidate=doc.get("plannerBrief",doc.get("validatedOutput",doc))
    return validate_planner_brief(candidate)


def main() -> None:
    load_planner_env();parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt",nargs="?",help="natural-language bedroom request")
    modes=parser.add_mutually_exclusive_group();modes.add_argument("--plan-only",action="store_true");modes.add_argument("--dry-run",action="store_true");modes.add_argument("--live",action="store_true")
    parser.add_argument("--brief",type=Path,help="saved planner brief/generation artifact; skips LLM")
    parser.add_argument("--shell",choices=sorted(SHELL_SIZES),default="medium");parser.add_argument("--seed",type=int)
    parser.add_argument("--model",default=os.getenv("RELICTA_PLANNER_MODEL","gpt-5.6-luna"));parser.add_argument("--timeout",type=float,default=45)
    parser.add_argument("--candidate-limit",type=int,default=4);parser.add_argument("--max-backtracks",type=int,default=32)
    parser.add_argument("--max-search-nodes",type=int,default=128);parser.add_argument("--search-timeout-ms",type=int,default=5000)
    parser.add_argument("--interactive",action="store_true",help="keep the live room until Enter, then clean up")
    parser.add_argument("--live-start-delay",type=float,default=0,help="seconds to wait before live work so Eden can be focused")
    parser.add_argument("--keep",action="store_true",help="leave this generation in the probe for later inspection")
    parser.add_argument("--cleanup-generation",type=Path,help="delete only IDs owned by a saved generation artifact")
    parser.add_argument("--no-cache",action="store_true")
    args=parser.parse_args();mode="live" if args.live else ("plan-only" if args.plan_only else "dry-run")
    if args.cleanup_generation:
        doc=json.loads(args.cleanup_generation.read_text(encoding="utf-8"));ids=[x["semanticId"] for x in doc.get("ownership",{}).get("objects",[])]
        if not ids:parser.exit(2,"Cleanup artifact has no owned semantic IDs.\n")
        gateway=MapAutomationRoomGateway(args.timeout);snapshot=gateway.snapshot();cleaned=gateway.cleanup(ids,snapshot.revision)
        after=_fingerprint(cleaned["result"]);expected=doc.get("transaction",{}).get("sceneFingerprintBefore")
        clean=not expected or after==expected
        doc.setdefault("ownership",{})["cleanupStatus"]="CLEAN" if clean else "DIVERGED";doc["sceneRevisionAfter"]=cleaned["revision"];doc["sceneFingerprintAfter"]=after
        args.cleanup_generation.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
        print(json.dumps({"status":"SUCCESS" if clean else "PARTIAL_FAILURE","revision":cleaned["revision"],"removedIds":ids,"sceneRestored":clean},ensure_ascii=False,indent=2))
        raise SystemExit(0 if clean else 1)
    if not args.brief and not args.prompt:parser.error("prompt is required unless --brief is used")
    brief=load_brief(args.brief) if args.brief else None
    planner_service=None
    if brief is None:
        key=os.getenv("OPENAI_API_KEY","")
        if not key:parser.exit(2,"PLANNER_FAILED: OPENAI_API_KEY is not set; use --brief for replay.\n")
        planner_service=PlannerService(OpenAIResponsesProvider(key,args.model),model=args.model,cache_enabled=not args.no_cache,timeout=args.timeout)
    gateway=MapAutomationRoomGateway(args.timeout) if mode=="live" else None
    generator=RoomGenerator(planner_service=planner_service,gateway=gateway)
    if mode=="live" and args.live_start_delay>0:
        print(f"Live run starts in {args.live_start_delay:g} seconds; focus Eden now.",flush=True);time.sleep(args.live_start_delay)
    options=GenerationOptions(mode,args.seed,args.candidate_limit,args.max_backtracks,args.max_search_nodes,args.search_timeout_ms,True,args.keep or args.interactive)
    result=generator.generate_room(args.prompt or "replay saved bedroom brief",probe_shell(args.shell),options,planner_brief=brief)
    print(json.dumps(result.json(),ensure_ascii=False,indent=2))
    if args.interactive and result.status.value=="SUCCESS":
        print("Room is visible in AI_AutomationProbe. Press Enter to clean up...");input();generator.cleanup(result);generator._save(result)
        print("Cleanup complete; only objects owned by this generation were removed.")
    if result.status.value not in {"SUCCESS","INFEASIBLE"}:raise SystemExit(1)


if __name__=="__main__":main()
