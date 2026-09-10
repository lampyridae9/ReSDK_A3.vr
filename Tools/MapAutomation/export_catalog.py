"""Export live reflection/probes through the existing Phase 1 file gateway.

Open AI_AutomationProbe and rebuild the editor first. Does not load/save maps.
Only a complete export is published. Responses remain in the existing queue.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from transport import FileQueueClient, TransportError

OUT = Path(__file__).parent / 'catalog'


def publish(name, value):
    OUT.mkdir(exist_ok=True)
    tmp=OUT/(name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    os.replace(tmp,OUT/name)


def export(geometry=False, timeout=30, resume_reflection=False):
    client=FileQueueClient(timeout)
    def request(op, revision, args=None):
        _,r=client.request(op,revision,args)
        if r['status']!='OK' or r.get('stopped'): raise TransportError(str(r))
        return r
    cap=request('getCapabilities',-1)
    if cap['result'].get('catalogVersion')!=1:
        raise TransportError('Reload/rebuild editor with Phase 2 catalog operations first')
    revision=cap['revision']; rows=[]; total=None; product=None; generation=None; before=None; all_loaded=None
    if resume_reflection:
        saved=json.loads((OUT/'reflection.json').read_text(encoding='utf-8'))
        first=request('catalogPage',revision,dict(offset=0,limit=1))['result']
        if saved['sessionId']!=client.session_id or saved['generation']!=first['generation'] or saved['revision']!=revision:
            raise TransportError('Saved reflection belongs to another session/generation/revision; full export required')
        rows=saved['objects'];total=first['total'];generation=first['generation'];product=first['productVersion'];all_loaded=first['allOopLoadedCount']
        if len(rows)!=total: raise TransportError('Incomplete saved reflection')
        before=dict(sceneFingerprint=first['sceneFingerprint'],simpleObjectCount=first['simpleObjectCount'])
    while total is None or len(rows)<total:
        result=request('catalogPage',revision,dict(offset=len(rows),limit=min(4,total-len(rows)) if total is not None else 4))['result']
        if total is not None and total!=result['total']: raise TransportError('Class set changed during export')
        if generation is not None and generation!=result['generation']: raise TransportError('Editor recompiled during export')
        generation=result['generation']
        if before is None:
            before=dict(sceneFingerprint=result['sceneFingerprint'],simpleObjectCount=result['simpleObjectCount'])
            all_loaded=result['allOopLoadedCount']
        total=result['total']; product=result['productVersion']
        page=result['objects']
        if not page and len(rows)<total: raise TransportError('Empty page before end')
        rows.extend(page)
        if len(rows)%100==0: print(f'Reflection: {len(rows)}/{total}',flush=True)
    names=[r['classname'] for r in rows]
    if len(set(names))!=len(names): raise TransportError('Duplicate class in export')
    publish('reflection.json',dict(schemaVersion=1,sessionId=client.session_id,revision=revision,generation=generation,productVersion=product,allOopLoadedCount=all_loaded,objects=rows))
    print(f'Exported {len(rows)} classes; {sum(r["editorPlaceable"] for r in rows)} resolve for editor placement')
    if geometry:
        core=json.loads((OUT/'core_assets.json').read_text(encoding='utf-8'))['assets']
        profiles=[]
        for c in core:
            result=request('probeGeometry',revision,dict(classname=c['classname']))['result']
            if result['generation']!=generation: raise TransportError('Editor recompiled between reflection and probe')
            if not result.get('cleanupVerified') or not result.get('sceneUnchanged'): raise TransportError('Probe cleanup not verified')
            profiles.append(result)
            print('Measured '+c['classname'],flush=True)
        last=request('catalogPage',revision,dict(offset=0,limit=1))['result']
        after=dict(sceneFingerprint=last['sceneFingerprint'],simpleObjectCount=last['simpleObjectCount'])
        if before!=after or last['generation']!=generation: raise TransportError('Batch changed scene or generation')
        publish('engine_geometry.json',dict(schemaVersion=1,sessionId=client.session_id,generation=generation,profiles=profiles,batchSceneUnchanged=True,before=before,after=after))


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--geometry',action='store_true'); p.add_argument('--timeout',type=float,default=30)
    p.add_argument('--resume-reflection',action='store_true',help='Reuse complete reflection only in the exact same live generation')
    a=p.parse_args(); export(a.geometry,a.timeout,a.resume_reflection)
