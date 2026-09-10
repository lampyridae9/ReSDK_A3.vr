#!/usr/bin/env python3
"""Enable only the curated subset after a complete live Eden PASS artifact exists."""
from __future__ import annotations

import json
import os
from pathlib import Path
from validate_phase3 import EXPECTED, LIVE, POLICY, CATALOG, ROOT, digest


def write_atomic(path,data):
    temporary=path.with_suffix(path.suffix+'.phase3.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');os.replace(temporary,path)


def main():
    if not LIVE.exists(): raise SystemExit('FAIL: live Eden artifact missing')
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    if live.get('status')!='PASS' or live.get('sceneUnchanged') is not True or set(live.get('actualReadback',{}).get('classes',[]))!=EXPECTED:
        raise SystemExit('FAIL: live artifact is not a complete nine-class scene-preserving PASS')
    policy=json.loads(POLICY.read_text(encoding='utf-8'));policy['status']='LIVE_VERIFIED_PHASE3'
    policy['liveEvidence']='Tools/MapAutomation/artifacts/phase3_live_latest.json'
    for row in policy['assets']: row['generatorAllowed']=row['classname'] in EXPECTED
    write_atomic(POLICY,policy)
    core_path=CATALOG/'core_assets.json';core=json.loads(core_path.read_text(encoding='utf-8'))
    for row in core['assets']:
        row['generatorAllowed']=row['classname'] in EXPECTED
        if row['classname'] in EXPECTED:
            row['phase3SpatialProfile']='Tools/MapAutomation/phase3_assets.json'
            row['phase3LiveEvidence']='Tools/MapAutomation/artifacts/phase3_live_latest.json'
    write_atomic(core_path,core)
    state_path=CATALOG/'build_state.json';state=json.loads(state_path.read_text(encoding='utf-8'))
    state['outputs']['core_assets.json']=digest(core_path);write_atomic(state_path,state)
    print('PASS: generatorAllowed enabled for exactly 9 live-verified Phase 3 assets')


if __name__=='__main__': main()
