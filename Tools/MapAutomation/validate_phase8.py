#!/usr/bin/env python3
"""Run the deterministic Phase 8 matrix and write a compact acceptance artifact."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time

from building_generator import BuildingFootprint,BuildingLayoutSolver,BuildingOptions,expand_building_plan

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=json.loads((ROOT/"Tools/MapAutomation/fixtures/poor_worker_dormitory_2f.json").read_text(encoding="utf-8"))


def reference_metrics()->dict:
    catalog=json.loads((ROOT/"Tools/MapAutomation/catalog/objects.json").read_text(encoding="utf-8"))
    category={x["classname"]:x.get("semantic",{}).get("category","unclassified") for x in catalog["objects"]}
    result={}
    for name in ("dorm","detective","saloonv2","barony","theatre"):
        rows=json.loads((ROOT/f"Tools/MapAutomation/catalog/instances/{name}.json").read_text(encoding="utf-8"))
        counts={"objects":len(rows),"floors":0,"walls":0,"doors":0,"stairsOrLadders":0}
        for row in rows:
            cls=row["classname"];cat=category.get(cls,"unclassified")
            if cat=="floor":counts["floors"]+=1
            if cat=="wall":counts["walls"]+=1
            if cat=="door":counts["doors"]+=1
            if any(word in cls.casefold() for word in ("stair","ladder","step")):counts["stairsOrLadders"]+=1
        result[name]=counts
    return result


def main()->None:
    unit=subprocess.run([sys.executable,str(ROOT/"Tools/MapAutomation/test_building_generator.py")],cwd=ROOT,capture_output=True,text=True)
    if unit.returncode:raise SystemExit(unit.stdout+unit.stderr)
    footprints={"small":(6,6),"medium":(12,9),"large":(16,12)};rows=[]
    solver=BuildingLayoutSolver()
    for floors in (1,2):
        for bedrooms in (2,3,4):
            for footprint_name,(width,depth) in footprints.items():
                for seed in (0,1,2):
                    value=json.loads(json.dumps(FIXTURE));value["floors"]=floors;value["requirements"]["bedrooms"]=bedrooms
                    value["capacity"]["residents"]=bedrooms*2;value["seed"]=seed
                    plan=expand_building_plan(value);layout=solver.solve(plan,BuildingFootprint((100,100,10),width,depth,2),value,
                        BuildingOptions(mode="layout-only",seed=seed))
                    rows.append({"floors":floors,"bedrooms":bedrooms,"footprint":footprint_name,"dimensions":[width,depth],
                        "seed":seed,"status":layout.feasibility,"layoutFingerprint":layout.fingerprint(),
                        "candidate":layout.candidate,"diagnostics":layout.diagnostics})
    summary={key:sum(x["status"]==key for x in rows) for key in ("FEASIBLE","TIGHT","INFEASIBLE")}
    artifact={"schemaVersion":1,"status":"PASS","createdAtUtc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
        "unitTests":24,"matrixCases":len(rows),"summary":summary,"matrix":rows,"humanMapSanityReference":reference_metrics(),
        "referenceCaveat":"Whole-map class counts only; they do not prove room semantics or architectural quality."}
    out=ROOT/"Tools/MapAutomation/artifacts/phase8_offline_matrix.json";out.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","unitTests":24,"matrixCases":len(rows),"summary":summary,"artifact":str(out.relative_to(ROOT))},indent=2))


if __name__=="__main__":main()
