#!/usr/bin/env python3
"""Phase 8 worker-dormitory generator. Safe default: full dry-run."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from building_generator import (BuildingFootprint,BuildingGenerator,BuildingOptions,BuildingPlannerService,
    BuildingStatus,validate_building_brief)
from planner import OpenAIResponsesProvider,load_planner_env
from room_generator import MapAutomationRoomGateway

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_BRIEF=ROOT/"Tools/MapAutomation/fixtures/poor_worker_dormitory_2f.json"


def _brief(path:Path)->dict:
    doc=json.loads(path.read_text(encoding="utf-8"));return validate_building_brief(doc.get("buildingBrief",doc))


def main()->None:
    load_planner_env();parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt",nargs="?",help="natural-language worker dormitory request")
    modes=parser.add_mutually_exclusive_group();modes.add_argument("--plan-only",action="store_true");modes.add_argument("--layout-only",action="store_true")
    modes.add_argument("--dry-run",action="store_true");modes.add_argument("--live",action="store_true")
    parser.add_argument("--brief",type=Path,help="BuildingBrief or saved building artifact; skips LLM")
    parser.add_argument("--origin",type=float,nargs=3,default=(4700,4700,10.134262),metavar=("X","Y","Z"))
    parser.add_argument("--width",type=float,default=12);parser.add_argument("--depth",type=float,default=10.05624);parser.add_argument("--max-floors",type=int,default=2)
    parser.add_argument("--seed",type=int);parser.add_argument("--shell-only",action="store_true")
    parser.add_argument("--max-layout-candidates",type=int,default=4);parser.add_argument("--max-partition-attempts",type=int,default=4)
    parser.add_argument("--time-budget-ms",type=int,default=1000);parser.add_argument("--timeout",type=float,default=45)
    parser.add_argument("--model",default=os.getenv("RELICTA_PLANNER_MODEL","gpt-5.6-luna"));parser.add_argument("--no-cache",action="store_true")
    parser.add_argument("--interactive",action="store_true",help="keep a successful live building until Enter, then clean it up")
    parser.add_argument("--keep",action="store_true");parser.add_argument("--cleanup-generation",type=Path)
    args=parser.parse_args();mode="live" if args.live else "plan-only" if args.plan_only else "layout-only" if args.layout_only else "dry-run"
    gateway=MapAutomationRoomGateway(args.timeout) if mode=="live" or args.cleanup_generation else None
    if args.cleanup_generation:
        result_doc=json.loads(args.cleanup_generation.read_text(encoding="utf-8"));ids=[x["semanticId"] for x in result_doc.get("ownership",{}).get("objects",[])]
        if not ids:parser.exit(2,"building artifact has no owned IDs\n")
        snap=gateway.snapshot();cleaned=gateway.cleanup(ids,snap.revision)
        print(json.dumps({"status":"SUCCESS","removedIds":ids,"revision":cleaned["revision"]},ensure_ascii=False,indent=2));return
    brief=_brief(args.brief) if args.brief else None;planner_service=None
    if brief is None:
        if not args.prompt:parser.error("prompt is required unless --brief is used")
        key=os.getenv("OPENAI_API_KEY","")
        if not key:parser.exit(2,"BUILDING_PLANNER_FAILED: OPENAI_API_KEY is not set; use --brief for replay.\n")
        planner_service=BuildingPlannerService(OpenAIResponsesProvider(key,args.model),model=args.model,timeout=args.timeout,cache_enabled=not args.no_cache)
    generator=BuildingGenerator(planner_service=planner_service,gateway=gateway)
    options=BuildingOptions(mode,args.seed,args.shell_only,True,args.keep or args.interactive,args.max_layout_candidates,
        args.max_partition_attempts,args.time_budget_ms)
    result=generator.generate(args.prompt or "replay saved worker dormitory brief",
        BuildingFootprint(tuple(args.origin),args.width,args.depth,args.max_floors),options,building_brief=brief)
    print(json.dumps(result.json(),ensure_ascii=False,indent=2))
    if args.interactive and result.status==BuildingStatus.SUCCESS:
        input("Building is visible in AI_AutomationProbe. Press Enter to clean up...");generator.cleanup(result);generator._save(result)
    if result.status not in {BuildingStatus.SUCCESS,BuildingStatus.INFEASIBLE}:raise SystemExit(1)


if __name__=="__main__":main()
