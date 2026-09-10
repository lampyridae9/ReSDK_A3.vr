#!/usr/bin/env python3
"""Validate Phase 4 data contracts, tests, dry-run and optional live evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"Tools/MapAutomation/catalog"
LIVE=ROOT/"Tools/MapAutomation/artifacts/phase4_live_latest.json"


def validate(require_live: bool=False):
    errors=[];warnings=[]
    for relative in ["semantic/model.py","semantic/pipeline.py","patterns/poor_bedroom.json","semantic_assets.json",
        "planner_room_brief.schema.json","fixtures/poor_bedroom_two_workers.json","test_pattern_system.py"]:
        if not (ROOT/"Tools/MapAutomation"/relative).exists(): errors.append("missing "+relative)
    test=subprocess.run([sys.executable,str(ROOT/"Tools/MapAutomation/test_pattern_system.py")],cwd=ROOT,capture_output=True,text=True)
    if test.returncode: errors.append("Phase 4 tests failed: "+test.stdout+test.stderr)
    else:
        if "Ran 15 tests" not in test.stderr: errors.append("unexpected Phase 4 test count")
    live=None
    if LIVE.exists():
        live=json.loads(LIVE.read_text(encoding="utf-8"))
        policy=json.loads((ROOT/"Tools/MapAutomation/phase3_assets.json").read_text(encoding="utf-8"))
        if live.get("status")!="PASS" or live.get("sceneUnchanged") is not True or live.get("productionMapsTouched") is not False:
            errors.append("Phase 4 live evidence is not a clean PASS")
        if live.get("roomPlan",{}).get("catalogVersion") != policy.get("catalogVersion"):
            errors.append("Phase 4 live evidence belongs to an older spatial catalog version")
    elif require_live: errors.append("Phase 4 live Eden evidence missing")
    else: warnings.append("Phase 4 live Eden demonstration pending")
    result={"schemaVersion":1,"status":"PASS" if not errors else "FAIL","requireLive":require_live,"errors":errors,"warnings":warnings,
        "counts":{"tests":15,"liveReadbackObjects":0 if not live else live.get("actualReadback",{}).get("objects",0)},
        "liveEvidence":str(LIVE.relative_to(ROOT)).replace("\\","/") if live else None}
    (CATALOG/"phase4_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--require-live",action="store_true");args=parser.parse_args();result=validate(args.require_live)
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result["errors"]))
