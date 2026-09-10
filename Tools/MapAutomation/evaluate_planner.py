#!/usr/bin/env python3
"""Evaluate semantic properties of real Planner outputs or the offline contract fixture."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from planner import OpenAIResponsesProvider, PlannerInput, PlannerService, PlannerStatus, load_planner_env
from planner.model import ProviderResponse
from planner.provider import PlannerProvider
from semantic.pipeline import PatternPipeline, build_room_context

ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/"Tools/MapAutomation/planner_evaluation.json"


def expected_brief(expected: dict, seed: int) -> dict:
    people=expected.get("capacity",2)
    styles=expected.get("styles",["neutral"])
    return {"schemaVersion":1,"intent":"create_room","roomType":"bedroom","style":styles,
        "capacity":{"people":people},"requirements":{"sleeping":expected.get("sleeping",people),"storage":expected.get("storage",1),"lighting":expected.get("lighting",1)},
        "preferences":{k:expected.get(k,False) for k in ("workSurface","seating","compact")},"seed":seed}


class EvaluationFixtureProvider(PlannerProvider):
    name="offline-evaluation-fixture"
    def __init__(self, output: dict): self.output=output
    def plan_room(self,**kwargs): return ProviderResponse(PlannerStatus.SUCCESS,output=self.output,raw_output=json.dumps(self.output),latency_ms=0)


def score(output: dict|None, expected: dict, status: str) -> dict:
    wanted=expected["status"];success=status==wanted
    metrics={"statusCorrect":success,"schemaValid":bool(output) if wanted=="SUCCESS" else success}
    if wanted!="SUCCESS": return metrics
    if not output:
        metrics.update({key:False for key in ("roomTypeCorrect","capacityCorrect","requiredFunctionsCorrect","preferencesCorrect","forbiddenFieldsAbsent","pipelineAccepted")})
        return metrics
    req=(output or {}).get("requirements",{});prefs=(output or {}).get("preferences",{})
    forbidden={"position","rotation","classname","class","rawsqf","python","shell"}
    def has_forbidden(value):
        if isinstance(value,dict): return any(k.casefold() in forbidden or has_forbidden(v) for k,v in value.items())
        if isinstance(value,list): return any(has_forbidden(v) for v in value)
        return False
    metrics.update({"roomTypeCorrect":output.get("roomType")==expected.get("roomType","bedroom"),
        "capacityCorrect":output.get("capacity",{}).get("people")==expected.get("capacity",2),
        "requiredFunctionsCorrect":all(req.get(k)==expected[k] for k in ("sleeping","storage","lighting") if k in expected),
        "preferencesCorrect":all(prefs.get(k,False)==expected[k] for k in ("workSurface","seating","compact") if k in expected),
        "forbiddenFieldsAbsent":not has_forbidden(output)})
    try: metrics["pipelineAccepted"]=PatternPipeline().run(output,build_room_context()).status=="PASS"
    except Exception: metrics["pipelineAccepted"]=False
    return metrics


def main() -> None:
    load_planner_env()
    parser=argparse.ArgumentParser();parser.add_argument("--real",action="store_true");parser.add_argument("--model",default=os.getenv("RELICTA_PLANNER_MODEL","gpt-5.6-luna"));parser.add_argument("--no-cache",action="store_true");args=parser.parse_args()
    dataset=json.loads(DATA.read_text(encoding="utf-8"));rows=[]
    key=os.getenv("OPENAI_API_KEY","")
    if args.real and not key: parser.error("--real requires OPENAI_API_KEY")
    for index,case in enumerate(dataset["cases"],1):
        expected=case["expected"];seed=12000+index
        provider=OpenAIResponsesProvider(key,args.model) if args.real else EvaluationFixtureProvider(expected_brief(expected,seed))
        service=PlannerService(provider,model=args.model if args.real else "fixture-v1",max_attempts=2,cache_enabled=args.real and not args.no_cache)
        result=service.plan_room(PlannerInput(case["prompt"],seed));metrics=score(result.validated_output,expected,result.status.value)
        rows.append({"id":case["id"],"category":case["category"],"status":result.status.value,"expectedStatus":expected["status"],"metrics":metrics,"artifact":result.artifact_path,"usage":result.usage,"latencyMs":result.latency_ms})
    values=[v for row in rows for v in row["metrics"].values()];rate=sum(values)/len(values) if values else 0
    report={"schemaVersion":1,"mode":"real-llm" if args.real else "offline-contract-fixture","model":args.model if args.real else "fixture-v1","caseCount":len(rows),"metricCount":len(values),"passRate":rate,"threshold":dataset["threshold"],"status":"PASS" if rate>=dataset["threshold"] else "FAIL","cases":rows}
    out=ROOT/"Tools/MapAutomation/artifacts"/("phase5_evaluation_real.json" if args.real else "phase5_evaluation_offline.json");out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},ensure_ascii=False,indent=2));raise SystemExit(report["status"]!="PASS")


if __name__=="__main__": main()
