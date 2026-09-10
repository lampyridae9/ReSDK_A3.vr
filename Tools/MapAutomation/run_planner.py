#!/usr/bin/env python3
"""Phase 5 developer CLI: plan-only by default, deterministic dry-run, explicit live."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

from planner import OpenAIResponsesProvider, PlannerInput, PlannerService, PlannerStatus, load_planner_env
from semantic.pipeline import PatternPipeline, build_room_context, validate_planner_brief

ROOT=Path(__file__).resolve().parents[2]


def load_brief(path: Path) -> dict:
    doc=json.loads(path.read_text(encoding="utf-8"))
    return validate_planner_brief(doc.get("validatedOutput",doc))


def main() -> None:
    load_planner_env()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt",nargs="?",help="natural-language room request")
    modes=parser.add_mutually_exclusive_group();modes.add_argument("--plan-only",action="store_true");modes.add_argument("--dry-run",action="store_true");modes.add_argument("--live",action="store_true")
    parser.add_argument("--fixture",type=Path,help="validated brief/artifact replay; skips the LLM call")
    parser.add_argument("--seed",type=int);parser.add_argument("--model",default=os.getenv("RELICTA_PLANNER_MODEL","gpt-5.6-luna"))
    parser.add_argument("--timeout",type=float,default=float(os.getenv("RELICTA_PLANNER_TIMEOUT","30")))
    parser.add_argument("--no-cache",action="store_true");parser.add_argument("--interactive",action="store_true")
    args=parser.parse_args()
    if not args.fixture and not args.prompt: parser.error("prompt is required unless --fixture is used")
    planner_artifact=None
    if args.fixture:
        brief=load_brief(args.fixture);source=f"saved brief {args.fixture}"
    else:
        key=os.getenv("OPENAI_API_KEY","")
        if not key: parser.exit(2,"PROVIDER_ERROR: OPENAI_API_KEY is not set. Use --fixture for offline replay.\n")
        provider=OpenAIResponsesProvider(key,args.model)
        cache_default=os.getenv("RELICTA_PLANNER_CACHE","1").strip().casefold() not in {"0","false","no","off"}
        service=PlannerService(provider,model=args.model,cache_enabled=cache_default and not args.no_cache,timeout=args.timeout)
        planned=service.plan_room(PlannerInput(args.prompt,args.seed))
        print(json.dumps(planned.json(),ensure_ascii=False,indent=2))
        if planned.status != PlannerStatus.SUCCESS: raise SystemExit(1)
        brief=planned.validated_output;planner_artifact=planned.artifact_path;source=f"LLM Planner {planner_artifact}"
    if not args.dry_run and not args.live:
        if args.fixture: print(json.dumps(brief,ensure_ascii=False,indent=2))
        return
    pipeline=PatternPipeline();scene=build_room_context();before=scene.fingerprint();result=pipeline.run(brief,scene)
    status="SUCCESS" if result.status=="PASS" else ("PATTERN_INFEASIBLE" if result.feasibility=="INFEASIBLE" else "SPATIAL_FAILURE")
    output={"schemaVersion":1,"status":status,"plannerArtifact":planner_artifact,"brief":brief,"pipeline":result.json(),"sceneUnchanged":scene.fingerprint()==before}
    out=ROOT/"Tools/MapAutomation/artifacts"/f"phase5_dry_run_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(output,ensure_ascii=False,indent=2))
    if status!="SUCCESS" or not output["sceneUnchanged"]: raise SystemExit(1)
    if args.live:
        from run_phase4_live import run
        live=run(args.timeout,args.interactive,brief=brief,source=source)
        phase5_latest=ROOT/"Tools/MapAutomation/artifacts/phase5_live_latest.json"
        shutil.copyfile(live,phase5_latest)
        print(f"LIVE PASS: {live}")


if __name__=="__main__": main()
