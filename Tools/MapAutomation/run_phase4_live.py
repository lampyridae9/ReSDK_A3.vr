#!/usr/bin/env python3
"""Apply the Phase 4 manual bedroom fixture to AI_AutomationProbe and clean it up."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from semantic.pipeline import PatternPipeline, build_room_context
from spatial.model import ResolvedObject, SceneState, SpatialTransform
from transport import FileQueueClient, ROOT, TransportError

FIXTURE = ROOT/"Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json"


def require_ok(label: str, response: dict[str,Any]) -> None:
    if response["status"] != "OK": raise TransportError(f"{label}: {response['diagnostics']}")


def create_operations(result, scene):
    x,y,z=scene.surfaces["floor_1"].origin
    operations=[]
    for index,(dx,dy) in enumerate(((-1.85,-1.7),(1.85,-1.7),(-1.85,1.7),(1.85,1.7)),1):
        operations.append({"operation":"create","arguments":{"semanticId":f"phase4_floor_{index:03d}","class":"WoodenSmallFloor",
            "position":[x+dx,y+dy,z-.134262],"rotation":[0,0,0],"scale":1,"parentId":"room_001"}})
    door=scene.objects[0]
    operations.append({"operation":"create","arguments":{"semanticId":door.id,"class":door.asset.classname,
        **door.transform.gateway(),"parentId":"room_001"}})
    for operation in result.scene_patch["operations"]:
        op=json.loads(json.dumps(operation));op["arguments"]["parentId"]="room_001";operations.append(op)
    return operations


def validate_readback(pipeline, planned, result, actual):
    rebuilt={row["semanticId"]:ResolvedObject.create(row["semanticId"],pipeline.solver.assets[row["class"]],
        SpatialTransform(tuple(row["position"]),tuple(row["rotation"]),"EDEN").with_space("WORLD"))
        for row in actual if row["class"] in pipeline.solver.assets}
    scene=SceneState(planned.region_id,planned.region_polygon,planned.surfaces,[rebuilt["entrance_shell_001"]],planned.entrance,[])
    checks={}
    required_targets=[]
    for intent in result.intents:
        candidate=rebuilt[intent.id];diagnostics=[]
        diagnostics += pipeline.solver.support.validate(candidate,scene.surfaces[intent.on_surface])
        diagnostics += pipeline.solver.geometry.validate(candidate,scene)
        diagnostics += pipeline.solver.clearance.validate(candidate,scene)
        scene.objects.append(candidate)
        if intent.reachable: required_targets.append(candidate)
        checks[intent.id]={"diagnostics":[d.json() for d in diagnostics]}
        if diagnostics: raise TransportError(f"actual geometry failed for {intent.id}: {checks[intent.id]}")
    for candidate in required_targets:
        diagnostics,path=pipeline.solver.access.validate(scene,pipeline.solver._interaction_target(candidate),candidate.id)
        checks[candidate.id]["accessibility"]={"diagnostics":[d.json() for d in diagnostics],"pathPoints":len(path)}
        if diagnostics: raise TransportError(f"actual accessibility failed for {candidate.id}")
    return checks


def run(timeout: float, interactive: bool = False, *, brief: dict[str,Any] | None = None, source: str = "manual fixture") -> Path:
    tests=subprocess.run([sys.executable,str(ROOT/"Tools/MapAutomation/test_pattern_system.py")],cwd=ROOT,capture_output=True,text=True)
    if tests.returncode: raise RuntimeError(tests.stdout+tests.stderr)
    brief=brief or json.loads(FIXTURE.read_text(encoding="utf-8"));pipeline=PatternPipeline();scene=build_room_context()
    before_fingerprint=scene.fingerprint();result=pipeline.run(brief,scene)
    if result.status != "PASS" or scene.fingerprint() != before_fingerprint: raise RuntimeError("semantic dry-run failed or mutated input scene")
    operations=create_operations(result,scene);created_ids=[x["arguments"]["semanticId"] for x in operations]
    client=FileQueueClient(timeout);transcript=[]
    def send(op,rev,args=None):
        request,response=client.request(op,rev,args);transcript.append({"request":request,"response":response})
        print(f"{op:16} {response['status']:4} revision={response['revision']}");return response
    caps=send("getCapabilities",-1);require_ok("capabilities",caps)
    initial=send("inspectScene",caps["revision"]);require_ok("initial scene",initial)
    if initial.get("stopped"): raise TransportError("gateway is safe-stopped")
    revision=initial["revision"];initial_scene=initial["result"];created=False;screenshots=[]
    try:
        response=send("applyPatch",revision,{"operations":operations});require_ok("create bedroom",response);created=True;revision=response["revision"]
        actual=[x for x in response["result"] if x["semanticId"] in created_ids]
        if {x["semanticId"] for x in actual} != set(created_ids): raise TransportError("created semantic IDs differ from read-back")
        checks=validate_readback(pipeline,scene,result,actual)
        x,y,z=scene.surfaces["floor_1"].origin
        reference_floor=next(row for row in actual if row["semanticId"]=="phase4_floor_001")
        asl_z=z+(reference_floor["positionASL"][2]-reference_floor["position"][2])
        capture=send("captureViews",revision,{"views":[
            {"positionASL":[x+7,y-9,asl_z+6],"targetASL":[x,y,asl_z+0.8],"fov":0.8},
            {"positionASL":[x+4,y-5,asl_z+2.2],"targetASL":[x,y,asl_z+0.5],"fov":0.7}
        ]});require_ok("capture bedroom",capture);screenshots=capture["result"]
        if interactive:
            print("Bedroom is visible near [4700,4700,10]. Press Enter to clean it up.");input()
    finally:
        if created:
            state=send("inspectScene",revision);require_ok("pre-cleanup",state);revision=state["revision"]
            present={x["semanticId"] for x in state["result"]}
            deletes=[{"operation":"delete","arguments":{"semanticId":identifier}} for identifier in reversed(created_ids) if identifier in present]
            if deletes:
                cleanup=send("applyPatch",revision,{"operations":deletes});require_ok("cleanup",cleanup);revision=cleanup["revision"]
    final=send("inspectScene",revision);require_ok("final scene",final)
    if final["result"] != initial_scene: raise TransportError("cleanup did not restore initial scene")
    artifact={"schemaVersion":1,"status":"PASS","createdAtUtc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "sessionId":caps["sessionId"],"plannerSource":source,"fixture":str(FIXTURE.relative_to(ROOT)).replace("\\","/") if source=="manual fixture" else None,"roomPlan":result.plan.json(),
        "semanticDryRun":result.json(),"actualReadback":{"objects":len(actual),"validation":checks},
        "screenshots":screenshots,"sceneUnchanged":True,"productionMapsTouched":False,"transcript":transcript}
    out=ROOT/"Tools/MapAutomation/artifacts"/f"phase4_live_{time.strftime('%Y%m%d_%H%M%S')}.json"
    latest=ROOT/"Tools/MapAutomation/artifacts/phase4_live_latest.json"
    raw=json.dumps(artifact,ensure_ascii=False,indent=2)+"\n";out.write_text(raw,encoding="utf-8",newline="\n");latest.write_text(raw,encoding="utf-8",newline="\n")
    print(f"PASS: Phase 4 live bedroom; sceneUnchanged=True; artifact={out}");return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--timeout",type=float,default=45);parser.add_argument("--interactive",action="store_true")
    args=parser.parse_args()
    try: run(args.timeout,args.interactive)
    except (OSError,KeyError,TypeError,ValueError,RuntimeError,TransportError) as exc: parser.exit(1,f"FAIL: {exc}\n")


if __name__ == "__main__": main()
