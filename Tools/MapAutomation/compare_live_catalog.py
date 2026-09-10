"""Compare preserved offline data to real gateway exports; never re-parse maps.

No synthetic measurements. Missing files stop comparison. Thresholds are review
policy, not claims about collision tolerance.
"""
from __future__ import annotations
from collections import Counter
import json
import math
from pathlib import Path
from build_catalog import OUT,norm
from validate_catalog import probe_errors


def compare_geometry(historical, live):
    if not historical or not live or probe_errors(live):
        return dict(classification='MISSING_DATA',reason='Missing or invalid measurement')
    if norm(historical['model'])!=norm(live['model']):
        return dict(classification='SIGNIFICANT_DIFFERENCE',reason='Model identity changed',
                    historicalModel=historical['model'],liveModel=live['model'])
    bounds=historical['visualBounds']['value'];fresh=live['visualBounds'][:2]
    dimensions=historical['dimensions']['value']
    deltas=[abs(fresh[j][i]-bounds[j][i]) for j in range(2) for i in range(3)]
    tolerances=[max(0.02,dimensions[i]*0.01) for j in range(2) for i in range(3)]
    category='MATCH' if max(deltas)<=0.005 else ('MINOR_DIFFERENCE' if all(d<=t for d,t in zip(deltas,tolerances)) else 'SIGNIFICANT_DIFFERENCE')
    return dict(classification=category,boundsMaxAbsDelta=max(deltas),
        dimensionsDelta=[a-b for a,b in zip(live['dimensions'],dimensions)],
        source='ruleDerived',historicalBounds=bounds,liveBounds=fresh,
        policy='MATCH <=5mm on every AABB coordinate; MINOR <=max(2cm,1% corresponding historical dimension); else SIGNIFICANT')


def door_summary(profile):
    samples=profile.get('doorSamples',[]) if profile else []
    if len(samples)!=8:
        return dict(status='UNKNOWN',reason='Eight fresh WoodenDoor animation samples required')
    errors=[]
    for i,r in enumerate(samples):
        if abs(r['actualPhase']-i/10)>0.005: errors.append('Animation read-back mismatch at '+str(i))
    bounds=[r['visualBounds'] for r in samples]
    lo=[min(b[0][i] for b in bounds) for i in range(3)]
    hi=[max(b[1][i] for b in bounds) for i in range(3)]
    positions=[dict(r.get('selectionPositions',[])).get('xlamdoor') for r in samples]
    tracked=all(isinstance(p,list) and len(p)==3 for p in positions)
    axis=dict(profile.get('lodEvidence',{}).get('Memory',{}).get('namedPositions',[])).get('xlamdoor_axis')
    tracked_motion=[positions[-1][i]-positions[0][i] for i in range(3)] if tracked else None
    hinge_side=None
    if isinstance(axis,list) and len(axis)==3:
        hinge_side='negativeX' if abs(axis[0]-bounds[0][0][0]) < abs(axis[0]-bounds[0][1][0]) else 'positiveX'
    return dict(status='VERIFIED_PHASES' if not errors else 'FAIL',errors=errors,
        sourceContract=dict(animation='xlamdoor',closed=0,open=0.7,source='source',evidence='WoodenDoors.sqf / DoorDynamic.animateSource'),
        closedState=dict(sample=samples[0],status='VERIFIED',source='engineMeasured'),
        openState=dict(sample=samples[-1],status='VERIFIED',source='engineMeasured',meaning='Configured phase read back; functional passage not tested'),
        hingeAxisSelection=dict(value=axis,status='VERIFIED' if axis else 'UNKNOWN',source='engineMeasured',selection='xlamdoor_axis'),
        hingeSide=dict(value=hinge_side,status='APPROXIMATE' if hinge_side else 'UNKNOWN',source='ruleDerived',confidence=0.7 if hinge_side else 0,
            meaning='Axis selection proximity to closed visual AABB edge; requires human orientation review'),
        trackedSelectionMotion=dict(value=tracked_motion,status='VERIFIED' if tracked else 'UNKNOWN',source='engineMeasured',
            meaning='xlamdoor Geometry named-position delta from phase 0 to 0.7; not a leaf transform or angle'),
        sampledOpeningEnvelope=dict(bounds=[lo,hi],source='ruleDerived',status='APPROXIMATE',
            meaning='Union of eight sampled AABBs; not exact collision or guaranteed continuous sweep; not human passage clearance'),
        semanticFront=dict(value=None,status='UNKNOWN'),
        openingDirection=dict(value=None,status='UNKNOWN',reason='Requires tracking geometry/axis, phase value is not an angle'))


def compare():
    def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
    reflection=read('reflection.json');engine=read('engine_geometry.json')
    source=read('objects.json');core=read('core_assets.json')['assets']
    historical={r['model']:r for r in read('models.json')['models']}
    live={r['classname']:r for r in engine['profiles']};loaded={r['classname']:r for r in reflection['objects']}
    source_names=set(read('source_declarations.json')['classes']);errors=[]
    if len(loaded)!=len(reflection['objects']) or len(live)!=len(engine['profiles']): errors.append('Duplicate live identities')
    if engine['sessionId']!=reflection['sessionId'] or engine['generation']!=reflection['generation']: errors.append('Mixed engine generations')
    if not engine.get('batchSceneUnchanged') or engine.get('before')!=engine.get('after'): errors.append('Batch scene preservation unverified')
    comparisons=[]
    for c in core:
        name=c['classname'];r=live.get(name)
        if not loaded.get(name,{}).get('editorPlaceable'): errors.append(name+': not live editor-placeable')
        if r:
            errors.extend(name+': '+e for e in probe_errors(r))
            if not r.get('cleanupVerified') or not r.get('sceneUnchanged'): errors.append(name+': cleanup unverified')
            if norm(r['model'])!=norm(loaded.get(name,{}).get('engineResolvedModel','')): errors.append(name+': reflection/probe model mismatch')
        else: errors.append(name+': core probe missing')
        comparisons.append(dict(classname=name,**compare_geometry(historical.get(c['model']),r)))
    door=door_summary(live.get('WoodenDoor'))
    if door['status']!='VERIFIED_PHASES': errors.append('WoodenDoor state read-back not verified')
    result=dict(sourceCandidates=source['sourceCandidateCount'],allOopLoadedCount=reflection.get('allOopLoadedCount'),
        liveGameObjectClasses=len(loaded),editorPlaceableClasses=sum(r['editorPlaceable'] for r in loaded.values()),
        sourceOnly=sorted(source_names-loaded.keys()),liveOnly=sorted(loaded.keys()-source_names),
        coreProbed=len(set(live)&{c['classname'] for c in core}),coreExpected=len(core),
        m2cComparisonCounts=dict(Counter(r['classification'] for r in comparisons)),
        errors=errors,status='FAIL' if errors else 'PASS',door=door)
    for name,value in [('m2c_comparison.json',comparisons),('live_validation.json',result)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    result=compare();print(json.dumps({k:v for k,v in result.items() if k!='door'},ensure_ascii=False,indent=2))
    raise SystemExit(bool(result['errors']))
