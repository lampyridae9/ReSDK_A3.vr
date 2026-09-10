"""Validate Phase 2 data integrity separately from engine/semantic readiness."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path
from build_catalog import OUT, ROOT, MAP_NAMES, digest, norm


def load(name): return json.loads((OUT/name).read_text(encoding='utf-8'))


def probe_errors(profile):
    errors=[]
    dims=profile.get('dimensions',[]); bounds=profile.get('visualBounds',[])
    valid_dims=len(dims)==3 and all(type(v) in (float,int) and math.isfinite(v) and v>0 for v in dims)
    valid_bounds=len(bounds)>=2 and all(isinstance(v,list) and len(v)==3 and all(type(x) in (float,int) and math.isfinite(x) for x in v) for v in bounds[:2])
    if not valid_dims: errors.append('invalid dimensions')
    if not valid_bounds: errors.append('invalid visual bounds')
    # Eden JSON rounds large coordinates; allow two units of the observed 0.1 mm
    # serialization quantum while still rejecting materially inconsistent data.
    if valid_dims and valid_bounds and any(abs(dims[i]-(bounds[1][i]-bounds[0][i]))>2e-4 for i in range(3)): errors.append('dimensions disagree with bounds')
    if profile.get('source')!='engineMeasured' or profile.get('status')!='VERIFIED': errors.append('missing engine provenance')
    return errors


def validate(require_engine=False):
    errors=[]; warnings=[]
    def check(ok,msg):
        if not ok: errors.append(msg)
    state=load('build_state.json')
    check(state['status']=='COMPLETE','Interrupted build: rebuild before using catalog')
    for name,expected in state.get('outputs',{}).items():
        check((OUT/name).exists() and digest(OUT/name)==expected,'Generated output changed: '+name)
    for name,expected in state.get('inputs',{}).items():
        check((ROOT/name).exists() and digest(ROOT/name)==expected,'Input changed: '+name)
    check(not load('build_summary.json')['sourceDuplicates'],'Ambiguous source declarations')
    doc=load('objects.json'); objects=doc['objects']; byclass={r['classname']:r for r in objects}
    maps=load('maps.json'); usage=load('usage.json'); core=load('core_assets.json')['assets']
    models={r['model']:r for r in load('models.json')['models']}
    check(len(byclass)==len(objects),'Duplicate classname')
    check(len({r['semanticId'] for r in objects})==len(objects),'Duplicate semantic ID')
    check(set(maps)==set(MAP_NAMES),'Map manifest mismatch')
    totals=Counter(); actual_permap={}
    for name,m in maps.items():
        check(digest(ROOT/m['source'])==m['sha256'],f'{name}: source changed')
        rt=m['runtimeComparison']; check(digest(ROOT/rt['source'])==rt['sha256'],f'{name}: runtime changed')
        rows=load('instances/'+name+'.json'); counts=Counter(r['classname'] for r in rows)
        actual_permap[name]=counts; totals.update(counts)
        check(len(rows)==m['parsedRelevantObjects'],f'{name}: instance count mismatch')
        check(len(rows)+len(m['excludedObjects'])==m['sourceObjectCount'],f'{name}: object conservation')
        check(all(r['declared']==r['parsed'] for r in m['entitiesContainers']),f'{name}: Entities count mismatch')
        check(len({r['entityId'] for r in rows})==len(rows),f'{name}: duplicate entity ID')
        check(not m['unknownClasses'],f'{name}: unknown classes {m["unknownClasses"]}')
        check(not m['chunkDisagreements'],f'{name}: chunk mismatch with compiled map')
        if rt['classCountDifferences']: warnings.append(name+': runtime differs; see maps.json')
        for r in rows:
            check(r['classname'] in byclass,f'{name}: missing class {r["classname"]}')
            check(len(r['position'])==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in r['position']),f'{name}: invalid position')
    check(dict(totals)=={c:u['totalCount'] for c,u in usage.items()},'Global usage mismatch')
    order=sorted(totals,key=lambda c:(-totals[c],c))
    for i,c in enumerate(order,1):
        u=usage[c]; expected={m:n[c] for m,n in actual_permap.items() if n[c]}
        check(u['perMapCounts']==expected,c+': per map count mismatch')
        check(u['frequencyRank']==i,c+': invalid rank')
        check(set(u['mapsUsedIn'])==set(expected) and u['mapCount']==len(expected),c+': map refs mismatch')
    for r in objects:
        c=r['classname']; chain=r['inheritance']
        check(c not in chain and len(chain)==len(set(chain)),c+': cyclic inheritance')
        check(not chain or chain[0]==r['parent'],c+': parent mismatch')
        if r['parent'] in byclass: check(chain==[r['parent']]+byclass[r['parent']]['inheritance'],c+': inconsistent chain')
        if r['chunkType'] not in ['ITEM','STRUCTURE','DECOR']: warnings.append(c+': chunk unknown (nonphysical/base class)')
        if not r['resolvedModel']: warnings.append(c+': model absent from M2C')
    for m in models.values():
        dims=m['dimensions']['value']; bounds=m['visualBounds']['value']
        check(len(dims)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) and v>=0 for v in dims),m['model']+': invalid bounds')
        check(all(abs(dims[i]-(bounds[1][i]-bounds[0][i]))<1e-8 for i in range(3)),m['model']+': inconsistent dimensions')
    check(len({c['classname'] for c in core})==len(core),'Duplicate core class')
    for c in core:
        check(c['classname'] in byclass,'Core missing class')
        check(c['model'] in models,c['classname']+': core unresolved model')
        check(c['chunkType'] in ['ITEM','STRUCTURE','DECOR'],c['classname']+': invalid core chunk')
        check(all(v>0 and math.isfinite(v) for v in c['dimensions']['value']),c['classname']+': invalid core dimensions')
        check(c['usage']['totalCount']>0,c['classname']+': core not used')
        check('confidence' in c['semantic'] and 'source' in c['semantic'],c['classname']+': missing provenance')
        check(c['availability']!='NOT_PLACEABLE',c['classname']+': not placeable')
    pending=[]
    if doc['editorPlaceableCount'] is None: pending.append('Live assembled reflection not exported; availability UNKNOWN')
    engine_path=OUT/'engine_geometry.json'
    if not engine_path.exists(): pending.append('Fresh engine geometry probes missing')
    else:
        engine=load('engine_geometry.json'); profiles={r['classname']:r for r in engine['profiles']}
        check(len(profiles)==len(engine['profiles']),'Duplicate engine profile')
        check(engine.get('batchSceneUnchanged') is True and engine.get('before')==engine.get('after'),'Batch scene preservation unverified')
        if (OUT/'reflection.json').exists():
            reflection=load('reflection.json')
            check(engine.get('generation')==reflection.get('generation') and engine.get('sessionId')==reflection.get('sessionId'),'Reflection/probe generation mismatch')
            reflected={r['classname']:r for r in reflection['objects']}
            check(doc['editorPlaceableCount']==sum(r['editorPlaceable'] for r in reflected.values()),'Incorrect editorPlaceableCount')
            for c in core: check(reflected.get(c['classname'],{}).get('editorPlaceable') is True,c['classname']+': core not engine-resolved')
        for c in core:
            if c['classname'] not in profiles: pending.append('Engine geometry missing: '+c['classname'])
            else:
                r=profiles[c['classname']]
                errors.extend(c['classname']+': '+e for e in probe_errors(r))
                check(r.get('cleanupVerified') is True and r.get('sceneUnchanged') is True,c['classname']+': cleanup unverified')
                check(norm(r['model'])==c['model'],c['classname']+': engine model mismatch')
                check(r['dimensions']==c['dimensions']['value'],c['classname']+': ingest fresh engine dimensions')
        if not (OUT/'live_validation.json').exists(): pending.append('Historical/live comparison missing')
        else: check(load('live_validation.json')['status']=='PASS','Live evidence comparison failed')
    if any(not c['semantic']['reviewed'] for c in core): warnings.append('Core contact/orientation/semantics remain curated assumptions; manual review required for functional placement')
    if require_engine and pending: errors.extend(pending)
    result=dict(integrity='PASS' if not errors else 'FAIL',phase2Status='PARTIAL' if pending and not errors else ('FAIL' if errors else 'PASS'),
                errors=errors,warnings=warnings,pending=pending, counts=dict(classes=len(objects),maps=len(maps),objects=sum(totals.values()),core=len(core)))
    (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-engine',action='store_true');a=p.parse_args()
    result=validate(a.require_engine);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(result['errors']))
