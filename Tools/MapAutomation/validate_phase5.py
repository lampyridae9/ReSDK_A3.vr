#!/usr/bin/env python3
"""Validate Phase 5 offline; --require-real also requires real evaluation and AI live evidence."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];CATALOG=ROOT/"Tools/MapAutomation/catalog";ART=ROOT/"Tools/MapAutomation/artifacts"


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--require-real",action="store_true");args=parser.parse_args();errors=[];warnings=[]
    required=["planner/model.py","planner/provider.py","planner/service.py","planner/planner_prompt_v1.txt","planner_evaluation.json","evaluate_planner.py","run_planner.py","test_llm_planner.py"]
    for item in required:
        if not (ROOT/"Tools/MapAutomation"/item).exists(): errors.append("missing "+item)
    commands=[[sys.executable,str(ROOT/"Tools/MapAutomation/test_llm_planner.py")],[sys.executable,str(ROOT/"Tools/MapAutomation/evaluate_planner.py")]]
    for command in commands:
        run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        if run.returncode: errors.append(run.stdout+run.stderr)
    real=ART/"phase5_evaluation_real.json";live=ART/"phase5_live_latest.json"
    if args.require_real:
        if not real.exists(): errors.append("real LLM evaluation evidence missing")
        elif json.loads(real.read_text(encoding="utf-8")).get("status")!="PASS": errors.append("real LLM evaluation failed")
        if not live.exists(): errors.append("natural-language live Eden evidence missing")
        else:
            doc=json.loads(live.read_text(encoding="utf-8"))
            if doc.get("status")!="PASS" or doc.get("sceneUnchanged") is not True: errors.append("live Eden evidence is not a clean PASS")
    else:
        if not real.exists(): warnings.append("real LLM evaluation pending: OPENAI_API_KEY is not configured")
        if not live.exists(): warnings.append("first natural-language live Eden test pending")
    result={"schemaVersion":1,"status":"PASS" if not errors else "FAIL","scope":"full" if args.require_real else "offline","errors":errors,"warnings":warnings}
    (CATALOG/"phase5_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n");print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))


if __name__=="__main__": main()
