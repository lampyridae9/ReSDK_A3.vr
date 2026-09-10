"""Overlay complete live evidence on the existing catalog without mining maps.

Preserves models.json (historical M2C), source declarations and all usage data.
Manifest is marked incomplete before writes so interrupted ingestion cannot pass.
"""
from __future__ import annotations
import copy
import json
import math
from build_catalog import OUT,ROOT,digest,norm,fact,classify
from catalog_parser import literal
from compare_live_catalog import compare


def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def write(name,value):
    target=OUT/name;temporary=target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    temporary.replace(target)


def capabilities(row):
    chain=set([row['classname']]+row['inheritance'])
    families=dict(container=['SContainer','Container','IContainerStruct'],seating=['IChair','IChairAsItem'],
        door=['DoorDynamic','DoorStatic'],light=['ILightible','ILightibleStruct'],
        electronic=['ElectronicDevice','BaseElectronicDeviceLighting','ElectronicDeviceDoor'],item=['Item'])
    result={}
    for key,bases in families.items():
        matches=sorted(chain&set(bases))
        result[key]=fact(True if matches else None,'ruleDerived',status='APPROXIMATE' if matches else 'UNKNOWN',
            confidence=0.85 if matches else 0,evidence={'liveInheritanceMatches':matches,
            'meaning':'Capability family, not functional interaction test; absence of match does not prove absence'})
    result['interactive']=fact(None,'ruleDerived',status='UNKNOWN',confidence=0,
        evidence='Methods exported in reflection.json; method existence alone does not establish usable interaction')
    return result


def ingest():
    state=read('build_state.json')
    if state['status']!='COMPLETE': raise ValueError('Incomplete catalog: inspect interrupted writes before ingestion')
    for name,expected in state['outputs'].items():
        if digest(OUT/name)!=expected: raise ValueError('Existing output changed: '+name)
    for name,expected in state['inputs'].items():
        if digest(ROOT/name)!=expected: raise ValueError('Existing input changed: '+name)
    write('build_state.json',{**state,'status':'INGESTING_LIVE'})
    result=compare()
    if result['errors']: raise ValueError(result['errors'])
    doc=read('objects.json');old={r['classname']:r for r in doc['objects']}
    reflection=read('reflection.json');engine=read('engine_geometry.json')
    live={r['classname']:r for r in engine['profiles']}
    core=read('core_assets.json');geometry=read('geometry.json')
    historical={r['model']:r for r in read('models.json')['models']}
    rows=[]
    for r in reflection['objects']:
        name=r['classname']; row=copy.deepcopy(old.get(name,{}))
        row.update({k:v for k,v in r.items() if k!='effectiveProperties'})
        row['availability']='REFLECTION_RESOLVED' if r['editorPlaceable'] else 'NOT_PLACEABLE'
        row['resolvedModel']=norm(r['engineResolvedModel']) if r['engineResolvedModel'] else None
        row['modelResolution']=fact(row['resolvedModel'],'engineMeasured',status='VERIFIED',evidence='live CfgVehicles lookup; full creation tested only for Core')
        row['semanticId']='relicta:'+name.lower()
        row.setdefault('semantic',classify(row))
        row.setdefault('usage',dict(totalCount=0,mapCount=0,mapsUsedIn=[],perMapCounts={},frequencyRank=None,source='mapUsageDerived'))
        row.setdefault('modelOverrides',[])
        row['effectivePropertiesRef']=dict(file='reflection.json',classname=name,field='effectiveProperties')
        for key,field in [('displayName','name'),('description','desc')]:
            try: row[key]=literal(r['effectiveProperties'].get(field,{}).get('expression',''))
            except ValueError: row[key]=None
        row['capabilities']=capabilities(r)
        row['provenance']={**row.get('provenance',{}),'availability':'engineMeasured','capabilities':'ruleDerived',
            **{k:'source' for k in ['classname','inheritance','parent','model','chunkType','editorAttributes']}}
        rows.append(row)
    doc.update(authority='reflection',objects=rows,editorPlaceableCount=result['editorPlaceableClasses'],
        liveLoadedCount=result['liveGameObjectClasses'],allOopLoadedCount=result['allOopLoadedCount'])
    byclass={r['classname']:r for r in rows}
    profiles=[]
    for c in core['assets']:
        name=c['classname'];r=live[name];h=copy.deepcopy(historical[c['model']])
        dims=fact(r['dimensions'],'engineMeasured',status='VERIFIED',meaning='Fresh boundingBoxReal AABB dimensions; not collision mesh')
        support=fact(r['visualBounds'][0][2],'ruleDerived',status='APPROXIMATE',confidence=0.4,
            meaning='AABB minimum Z in canonical model basis; assumed support plane, not measured contact')
        c.update(availability='LIVE_PROBE_VERIFIED',historicalDimensions=h['dimensions'],dimensions=dims,
            semanticFront=fact(None,'ruleDerived',status='UNKNOWN',confidence=0),supportAssumptions=support,
            reviewRequired=['contact and semantic orientation','functional clearance'])
        c['placementType'].update(status='APPROXIMATE',evidence='Curated intended attachment; fresh bounds do not verify contact',reviewed=False)
        if c['orientation']['value'] is None: c['orientation']['confidence']=0
        gb=r['geometryBounds'][:2]
        valid=len(gb)==2 and all(len(v)==3 for v in gb) and all(math.isfinite(b-a) and b>a for a,b in zip(*gb))
        profiles.append(dict(classname=name,model=norm(r['model']),chunkType=byclass[name]['chunkType'],
            historical=h,liveProbe=r,dimensions=dims,
            visualBounds=fact(r['visualBounds'][:2],'engineMeasured',status='VERIFIED',freshness='LIVE_PROBE'),
            geometryBounds=fact(gb,'engineMeasured',status='VERIFIED' if valid else 'UNKNOWN',meaning='Geometry LOD AABB only, not collision mesh'),
            pivot=fact([0,0,0],'engineMeasured',status='VERIFIED',worldReadback=r['modelOriginASL'],meaning='Model origin; not contact pivot'),
            orientation=fact(dict(vectorDir=r['vectorDir'],vectorUp=r['vectorUp']),'engineMeasured',status='VERIFIED',meaning='Probe basis, not semantic front'),
            semanticFront=c['semanticFront'],supportPlane=support,
            occupiedVolume=fact(math.prod(r['dimensions']),'ruleDerived',status='APPROXIMATE',meaning='AABB volume, not collision volume'),
            lodEvidence=r.get('lodEvidence',{}),placementType=c['placementType']))
    core['status']='LIVE_VERIFIED_CORE_WITH_CURATED_PLACEMENT_ASSUMPTIONS'
    geometry.update(profiles=profiles,unknown=['contact pivot/support mesh','exact collision mesh','continuous door swept volume',
        'interaction clearance','semantic front','wall/ceiling attachment','ROADWAY support surface'])
    summary=read('build_summary.json');summary.update(status='PASS',pending=[],manualReview=['contact and semantic orientation','functional clearance'])
    changed={'objects.json':doc,'core_assets.json':core,'geometry.json':geometry,'build_summary.json':summary}
    for name,value in changed.items(): write(name,value)
    for name in [*changed,'m2c_comparison.json','live_validation.json']: state['outputs'][name]=digest(OUT/name)
    for path in [OUT/'reflection.json',OUT/'engine_geometry.json',OUT.parent/'ingest_live_catalog.py',OUT.parent/'compare_live_catalog.py',OUT.parent/'export_catalog.py',ROOT/'Src/Editor/MapAutomation/MapAutomation_catalog.sqf']:
        state['inputs'][path.relative_to(ROOT).as_posix()]=digest(path)
    state['status']='COMPLETE';state['liveGeneration']=reflection['generation']
    write('build_state.json',state)
    return result


if __name__=='__main__':
    result=ingest();print(json.dumps({k:v for k,v in result.items() if k!='door'},ensure_ascii=False,indent=2))
