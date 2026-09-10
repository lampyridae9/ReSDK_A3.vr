#!/usr/bin/env python3
"""Validate Phase 3 policy, spatial contracts and optional live Eden evidence."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
POLICY=ROOT/'Tools/MapAutomation/phase3_assets.json'
CATALOG=ROOT/'Tools/MapAutomation/catalog'
LIVE=ROOT/'Tools/MapAutomation/artifacts/phase3_live_latest.json'
EXPECTED={'ConcretePanel','WoodenSmallFloor','ConcreteGreenWall','WoodenDoor','SingleWhiteBed','SmallWoodenTable','WoodenChair','SteelGreenCabinet','LampCeiling'}
PROVENANCE={'engineMeasured','humanVerified','engineMeasured+humanVerified','approximate','unknown'}


def load(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(require_live=False):
    errors=[];warnings=[];check=lambda ok,msg: errors.append(msg) if not ok else None
    policy=load(POLICY);rows=policy.get('assets',[]);names=[x.get('classname') for x in rows]
    check(set(names)==EXPECTED and len(names)==len(EXPECTED),'Phase 3 subset must contain exactly nine unique classes')
    geometry={x['classname']:x for x in load(CATALOG/'geometry.json')['profiles']}
    core={x['classname']:x for x in load(CATALOG/'core_assets.json')['assets']}
    for row in rows:
        name=row.get('classname','?');check(name in geometry and name in core,name+': absent from live Core geometry/catalog')
        check(row.get('placementType') in {'floor','wall','ceiling','free','attached','terrain'},name+': invalid placementType')
        for key in ('semanticFront','semanticBack'):
            value=row.get(key,{}).get('value');prov=row.get(key,{}).get('provenance')
            check(prov in PROVENANCE,name+': invalid '+key+' provenance')
            if value is not None: check(len(value)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in value),name+': invalid '+key)
        support=row.get('support',{});check(support.get('provenance') in PROVENANCE,name+': invalid support provenance')
        if support.get('surfaceTypes'):
            check(isinstance(support.get('localPlaneZ'),(int,float)) and math.isfinite(support['localPlaneZ']),name+': invalid support plane')
        for volume in row.get('clearanceVolumes',[]):
            check(len(volume.get('localCenter',[]))==3 and len(volume.get('halfExtents',[]))==3,name+': invalid clearance shape')
            check(all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in volume.get('halfExtents',[])),name+': invalid clearance extents')
            check(volume.get('provenance') in PROVENANCE,name+': invalid clearance provenance')
        for surface in row.get('providedSurfaces',[]):
            check(surface.get('type') in {'floor','wall','ceiling'} and surface.get('provenance') in PROVENANCE,name+': invalid provided surface')
            check(len(surface.get('halfExtents',[]))==2 and all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in surface.get('halfExtents',[])),name+': invalid provided surface bounds')
        if name in geometry:
            dims=geometry[name]['dimensions']['value'];check(len(dims)==3 and all(math.isfinite(v) and v>0 for v in dims),name+': invalid live dimensions')
    allowed_policy={r['classname'] for r in rows if r.get('generatorAllowed')}
    allowed_core={n for n,r in core.items() if r.get('generatorAllowed')}
    check(allowed_policy==allowed_core,'generatorAllowed differs between policy and Core Asset Set')
    check(allowed_policy in (set(),EXPECTED),'generatorAllowed must be none before live PASS or exactly the verified subset')
    unit=subprocess.run([sys.executable,str(ROOT/'Tools/MapAutomation/test_placement_solver.py')],cwd=ROOT,capture_output=True,text=True)
    check(unit.returncode==0,'spatial primitive unit tests failed')
    live=None
    if LIVE.exists():
        live=load(LIVE)
        check(live.get('status')=='PASS','latest live evidence is not PASS')
        check(live.get('sceneUnchanged') is True,'live cleanup did not preserve scene')
        check(live.get('productionMapsTouched') is False,'live evidence touched a production map')
        check(set(live.get('curatedClasses',[]))==EXPECTED,'live curated class set mismatch')
        check(set(live.get('actualReadback',{}).get('classes',[]))==EXPECTED,'not all curated classes received actual read-back')
        check(live.get('actualReadback',{}).get('valid') is True,'actual read-back validation failed')
        p=live.get('primitiveTests',{})
        check(p.get('A_floorSupport')==[] and p.get('E_againstWall')=='VALID','live positive placement primitives failed')
        for key,code in {'B_floating':'SUPPORT_GAP','C_penetration':'SUPPORT_PENETRATION','D_wallIntersection':'INTERSECTION','F_objectCollision':'INTERSECTION','G_clearance':'CLEARANCE_BLOCKED','H_blockedDoor':'CLEARANCE_BLOCKED','J_blockedAccessibility':'UNREACHABLE'}.items():
            check(code in p.get(key,[]),f'live {key} lacks {code}')
        check(p.get('I_accessibility',{}).get('diagnostics')==[],'live accessibility positive test failed')
        check(p.get('K_deterministic') is True and all(p.get('L_dryRun',{}).values()),'live deterministic/dry-run test failed')
    elif require_live: errors.append('live Eden evidence missing')
    else: warnings.append('live Eden evidence pending')
    if require_live: check(allowed_policy==EXPECTED,'verified subset has not been enabled after live PASS')
    result={'schemaVersion':1,'status':'PASS' if not errors else 'FAIL','requireLive':require_live,'errors':errors,'warnings':warnings,
        'counts':{'curatedAssets':len(rows),'generatorAllowed':len(allowed_policy),'unitTests':15,'liveReadbackObjects':0 if not live else live.get('createdObjects',0)},
        'liveEvidence':str(LIVE.relative_to(ROOT)).replace('\\','/') if live else None}
    (CATALOG/'phase3_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-live',action='store_true');a=p.parse_args();result=validate(a.require_live)
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result['errors']))
