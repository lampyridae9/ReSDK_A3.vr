#!/usr/bin/env python3
"""Run the Phase 6 offline generation matrix and emit aggregate metrics."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

from room_generator import ExistingRoomShell, GenerationOptions, GenerationStatus, RoomGenerator
from semantic.pipeline import build_room_context

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=json.loads((ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json").read_text(encoding="utf-8"))
SIZES={"small":2.0,"medium":3.5,"large":4.5};SEEDS=(100,200,300,400,500)


def main() -> None:
    suite=subprocess.run([sys.executable,str(ROOT/"Tools/MapAutomation/test_room_generator.py")],cwd=ROOT,capture_output=True,text=True)
    if suite.returncode:raise SystemExit(suite.stdout+suite.stderr)
    rows=[];run_dir=ROOT/"Tools/MapAutomation/artifacts/phase6_matrix_runs";generator=RoomGenerator(artifact_dir=run_dir)
    for capacity in range(1,5):
        for size,half in SIZES.items():
            for seed in SEEDS:
                brief=copy.deepcopy(FIXTURE);brief["capacity"]["people"]=capacity;brief["requirements"]["sleeping"]=capacity;brief["seed"]=seed
                result=generator.generate_room("offline matrix fixture",ExistingRoomShell(f"matrix_{size}",build_room_context(half=half)),
                    GenerationOptions(seed=seed,candidate_limit=4,max_backtracks=32,max_search_nodes=128,search_timeout_ms=5000),planner_brief=brief)
                rows.append({"capacity":capacity,"roomSize":size,"halfExtent":half,"seed":seed,"status":result.status.value,
                    "strategy":result.room_plan.get("strategy") if result.room_plan else None,"optionalDrops":len(result.dropped_optional),
                    "layoutFingerprint":hashlib.sha256(json.dumps(result.placements,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
                    "candidateAttempts":result.metrics.get("candidateAttempts",0),"backtracks":result.metrics.get("backtracks",0),
                    "latencyMs":result.timings.get("totalMs",0),"objects":result.metrics.get("numberOfObjects",0),
                    "navigationResult":result.metrics.get("navigationResult")})
    total=len(rows);success=[x for x in rows if x["status"]=="SUCCESS"];infeasible=[x for x in rows if x["status"]=="INFEASIBLE"]
    variants={(x["roomSize"],x["capacity"]):len({r["layoutFingerprint"] for r in success if r["roomSize"]==x["roomSize"] and r["capacity"]==x["capacity"]}) for x in rows}
    summary={"schemaVersion":1,"status":"PASS" if len(success)+len(infeasible)==total else "FAIL","createdAtUtc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "matrix":{"capacities":[1,2,3,4],"roomSizes":SIZES,"seeds":list(SEEDS),"cases":total},
        "metrics":{"successRate":len(success)/total,"infeasibleRate":len(infeasible)/total,
            "optionalDropRate":sum(x["optionalDrops"] for x in rows)/max(1,sum(x["objects"]+x["optionalDrops"] for x in rows)),
            "candidateAttempts":sum(x["candidateAttempts"] for x in rows),"backtracks":sum(x["backtracks"] for x in rows),
            "generationLatencyMs":{"min":min(x["latencyMs"] for x in rows),"mean":round(statistics.mean(x["latencyMs"] for x in rows),2),"max":max(x["latencyMs"] for x in rows)},
            "objects":sum(x["objects"] for x in rows),"allSuccessfulNavigationValid":all(x["navigationResult"] and x["navigationResult"]["reachable"] for x in success),
            "variantCounts":{f"{key[0]}-capacity-{key[1]}":value for key,value in sorted(variants.items())}},"rows":rows}
    out=ROOT/"Tools/MapAutomation/artifacts/phase6_generation_matrix.json"
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":summary["status"],"matrix":summary["matrix"],"metrics":summary["metrics"]},ensure_ascii=False,indent=2))
    if summary["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
