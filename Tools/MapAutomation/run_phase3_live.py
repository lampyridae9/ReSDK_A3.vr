#!/usr/bin/env python3
"""Run Phase 3 spatial primitives and a small non-semantic composition in Eden."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from spatial.model import PlacementIntent, ResolvedObject, SceneState, SpatialTransform, SupportSurface
from spatial.solver import PlacementSolver, load_phase3_assets
from transport import FileQueueClient, ROOT, TransportError

CURATED={"ConcretePanel","WoodenSmallFloor","ConcreteGreenWall","WoodenDoor","SingleWhiteBed","SmallWoodenTable","WoodenChair","SteelGreenCabinet","LampCeiling"}


def require_ok(step: str,response: dict[str,Any]) -> None:
    if response['status']!='OK': raise TransportError(f"{step} failed: {response['diagnostics']}")


def close(a,b,t=.02): return len(a)==len(b) and all(abs(x-y)<=t for x,y in zip(a,b))
def patch(op,args): return {'operation':op,'arguments':args}


def composition_scene(assets,base=(4600.0,4600.0,10.134262)):
    x,y,z=base
    floor=SupportSurface('floor_1','floor','p3_floor',base,(0,0,1),(1,0,0),(0,1,0),(3.3,3.3))
    south=SupportSurface('south_wall','wall','p3_south_wall',(x,y-3.3,z+1.5),(0,1,0),(1,0,0),(0,0,1),(3.3,1.5))
    ceiling=SupportSurface('ceiling_1','ceiling','room',(x,y,z+3),(0,0,-1),(1,0,0),(0,1,0),(3.3,3.3))
    region=[(x-3.3,y-3.3),(x+3.3,y-3.3),(x+3.3,y+3.3),(x-3.3,y+3.3)]
    walls=[
        ResolvedObject.create('p3_wall_a',assets['ConcreteGreenWall'],SpatialTransform((x-1.68,y-3.696442,z+2.11962))),
        ResolvedObject.create('p3_wall_b',assets['ConcreteGreenWall'],SpatialTransform((x+1.68,y-3.696442,z+2.11962))),
    ]
    door=ResolvedObject.create('p3_door',assets['WoodenDoor'],SpatialTransform((x+3.15,y+1.8,z),(0,0,90)))
    return SceneState('room_1',region,{'floor_1':floor,'south_wall':south,'ceiling_1':ceiling},walls+[door],(x+2.55,y+1.8),[]),walls,door


def resolve_composition(solver,scene):
    intents=[
        PlacementIntent('p3_bed','SingleWhiteBed','room_1','floor_1','south_wall',soft=('PreferWallCenter',),reachable=True,seed=301),
        PlacementIntent('p3_table','SmallWoodenTable','room_1','floor_1',soft=('Compact',),seed=302),
        PlacementIntent('p3_chair','WoodenChair','room_1','floor_1',soft=('Compact',),seed=303),
        PlacementIntent('p3_storage','SteelGreenCabinet','room_1','floor_1','south_wall',soft=('PreferWallCenter',),seed=304),
        PlacementIntent('p3_light','LampCeiling','room_1','ceiling_1',soft=('PreferWallCenter',),seed=305),
    ]
    results=[]
    for intent in intents:
        result=solver.resolve(intent,scene,dry_run=True)
        if result.status!='VALID': raise RuntimeError(f"offline composition failed for {intent.id}: {result.json()}")
        results.append(result);scene.objects.append(result.placement)
    return results


def create_ops(scene,walls,door,results):
    x,y,z=scene.surfaces['floor_1'].origin
    floor_bounds=(-1.91356,1.91356,-1.77017,1.77017)
    ops=[]
    for index,(dx,dy) in enumerate(((-1.85,-1.7),(1.85,-1.7),(-1.85,1.7),(1.85,1.7))):
        ops.append(patch('create',{'semanticId':f'p3_floor_{index+1}','class':'WoodenSmallFloor','position':[x+dx,y+dy,z-0.134262],'rotation':[0,0,0],'scale':1,'parentId':''}))
    # Independent structural smoke probe; it is outside the local room region and
    # exists only between the create/read-back and cleanup patches.
    ops.append(patch('create',{'semanticId':'p3_concrete_panel','class':'ConcretePanel','position':[x+8,y,z-0.0922552],'rotation':[0,0,0],'scale':1,'parentId':''}))
    for o in [*walls,door,*[r.placement for r in results]]:
        ops.append(patch('create',{'semanticId':o.id,'class':o.asset.classname,**o.transform.gateway(),'parentId':''}))
    return ops


def diagnostics_matrix(solver,scene,results,door):
    bed=next(r.placement for r in results if r.placement.id=='p3_bed')
    floor=scene.surfaces['floor_1'];codes=lambda ds:sorted({d.code for d in ds})
    floating=ResolvedObject.create('floating',bed.asset,SpatialTransform((bed.transform.position[0],bed.transform.position[1],bed.transform.position[2]+.2),bed.transform.rotation_deg))
    penetration=ResolvedObject.create('penetration',bed.asset,SpatialTransform((bed.transform.position[0],bed.transform.position[1],bed.transform.position[2]-.2),bed.transform.rotation_deg))
    wall_cross=ResolvedObject.create('wall_cross',bed.asset,SpatialTransform((bed.transform.position[0],scene.surfaces['south_wall'].origin[1]-.2,bed.transform.position[2]),bed.transform.rotation_deg))
    table_cross=ResolvedObject.create('table_cross',solver.assets['SmallWoodenTable'],SpatialTransform((bed.transform.position[0],bed.transform.position[1],floor.origin[2])))
    cabinet_sweep=ResolvedObject.create('cabinet_sweep',solver.assets['SteelGreenCabinet'],SpatialTransform((door.transform.position[0]-.7,door.transform.position[1],floor.origin[2]),(0,0,90)))
    clean_objects=[o for o in scene.objects if o.id not in {'p3_bed','p3_table','p3_chair','p3_storage','p3_light'}]
    collision_scene=SceneState(scene.region_id,scene.region_polygon,scene.surfaces,clean_objects+[bed],scene.entrance,[])
    accessible,path=solver.access.validate(scene,solver._interaction_target(bed),bed.id)
    bx,by,_=floor.origin
    barriers=[
        ResolvedObject.create('barrier_a',solver.assets['ConcreteGreenWall'],SpatialTransform((bx-1.65,by+.5,floor.origin[2]+2.11962))),
        ResolvedObject.create('barrier_b',solver.assets['ConcreteGreenWall'],SpatialTransform((bx+1.65,by+.5,floor.origin[2]+2.11962))),
    ]
    blocked_scene=SceneState(scene.region_id,scene.region_polygon,scene.surfaces,barriers,(bx,by+2.5),[])
    blocked,_=solver.access.validate(blocked_scene,(bx,by-2),"blocked_target")
    return {
        'A_floorSupport':codes(solver.support.validate(bed,floor)),
        'B_floating':codes(solver.support.validate(floating,floor)),
        'C_penetration':codes(solver.support.validate(penetration,floor)),
        'D_wallIntersection':codes(solver.geometry.validate(wall_cross,SceneState(scene.region_id,scene.region_polygon,scene.surfaces,clean_objects,scene.entrance,[]))),
        'E_againstWall':results[0].status,
        'F_objectCollision':codes(solver.geometry.validate(table_cross,collision_scene)),
        'G_clearance':codes(solver.clearance.validate(ResolvedObject.create('clearance_probe',solver.assets['WoodenChair'],SpatialTransform((bed.transform.position[0],bed.transform.position[1]+1.55,floor.origin[2]))),collision_scene)),
        'H_blockedDoor':codes(solver.clearance.validate(cabinet_sweep,SceneState(scene.region_id,scene.region_polygon,scene.surfaces,[door],scene.entrance,[]))),
        'I_accessibility':{'diagnostics':codes(accessible),'pathPoints':len(path)},
        'J_blockedAccessibility':codes(blocked),
    }


def assert_matrix(m):
    if m['A_floorSupport'] or m['E_againstWall']!='VALID': raise RuntimeError(f'A/E support placement failed: {m}')
    expected={'B_floating':'SUPPORT_GAP','C_penetration':'SUPPORT_PENETRATION','D_wallIntersection':'INTERSECTION','F_objectCollision':'INTERSECTION','H_blockedDoor':'CLEARANCE_BLOCKED','J_blockedAccessibility':'UNREACHABLE'}
    for key,value in expected.items():
        if value not in m[key]: raise RuntimeError(f'{key}: expected {value}, got {m[key]}')
    if 'CLEARANCE_BLOCKED' not in m['G_clearance']: raise RuntimeError('G_clearance did not reject')
    if m['I_accessibility']['diagnostics'] or m['I_accessibility']['pathPoints']<2: raise RuntimeError('I_accessibility failed')


def validate_actual_readback(solver,planned_scene,results,actual):
    """Rebuild validator inputs from Eden-returned transforms, never from the patch echo."""
    rebuilt={}
    for identifier,row in actual.items():
        if row['class'] in solver.assets:
            rebuilt[identifier]=ResolvedObject.create(identifier,solver.assets[row['class']],SpatialTransform(tuple(row['position']),tuple(row['rotation']),'EDEN').with_space('WORLD'))
    base=[rebuilt['p3_wall_a'],rebuilt['p3_wall_b'],rebuilt['p3_door']]
    scene=SceneState(planned_scene.region_id,planned_scene.region_polygon,planned_scene.surfaces,base,planned_scene.entrance,[])
    validation={}
    for result in results:
        candidate=rebuilt[result.placement.id];surface=scene.surfaces[result.intent.on_surface]
        diagnostics=solver.support.validate(candidate,surface)
        diagnostics+=solver.geometry.validate(candidate,scene)
        diagnostics+=solver.clearance.validate(candidate,scene)
        path=[]
        if result.intent.reachable:
            temp=SceneState(scene.region_id,scene.region_polygon,scene.surfaces,scene.objects+[candidate],scene.entrance,[])
            access,path=solver.access.validate(temp,solver._interaction_target(candidate),candidate.id);diagnostics+=access
        validation[candidate.id]={'diagnostics':[x.json() for x in diagnostics],'navigationPathPoints':len(path)}
        if diagnostics: raise TransportError(f'actual spatial validation failed for {candidate.id}: {validation[candidate.id]}')
        scene.objects.append(candidate)
    return validation


def run(timeout: float,interactive: bool=False) -> Path:
    unit=subprocess.run([sys.executable,str(ROOT/'Tools/MapAutomation/test_placement_solver.py')],cwd=ROOT,capture_output=True,text=True)
    if unit.returncode: raise RuntimeError(unit.stdout+unit.stderr)
    assets,config=load_phase3_assets();solver=PlacementSolver(assets,config,allow_candidate_assets=True)
    virtual,walls,door=composition_scene(assets);results=resolve_composition(solver,virtual)
    deterministic=resolve_composition(solver,composition_scene(assets)[0])
    k_same=[r.placement.transform for r in results]==[r.placement.transform for r in deterministic]
    if not k_same: raise RuntimeError('K deterministic placement mismatch')
    matrix=diagnostics_matrix(solver,virtual,results,door);matrix['K_deterministic']=True
    assert_matrix(matrix)

    client=FileQueueClient(timeout);transcript=[]
    def send(op,rev,args=None):
        req,res=client.request(op,rev,args);transcript.append({'request':req,'response':res});print(f'{op:16} {res["status"]:4} revision={res["revision"]}');return res
    caps=send('getCapabilities',-1);require_ok('getCapabilities',caps)
    live_classes=set(caps['result'].get('classes',[]));missing=sorted(CURATED-live_classes)
    if caps['result'].get('spatialVersion')!=1 or missing: raise TransportError(f'Eden needs recompile; spatialVersion/classes missing: {missing}')
    bad=[x for x in caps['result'].get('classDiagnostics',[]) if x[1]]
    if bad: raise TransportError(f'curated class diagnostics failed: {bad}')
    initial=send('inspectScene',caps['revision']);require_ok('initial inspectScene',initial)
    if initial.get('stopped'): raise TransportError('gateway is safe-stopped; reconcile before Phase 3 run')
    initial_scene=initial['result'];revision=initial['revision']
    dry_before=json.dumps(initial_scene,sort_keys=True,separators=(',',':'))
    dry_after=send('inspectScene',revision);require_ok('dry-run inspectScene',dry_after)
    matrix['L_dryRun']={'valid':all(r.status=='VALID' for r in results),'sceneUnchanged':dry_before==json.dumps(dry_after['result'],sort_keys=True,separators=(',',':')),'revisionUnchanged':dry_after['revision']==revision}
    if not all(matrix['L_dryRun'].values()): raise RuntimeError(f'L dry-run failed: {matrix["L_dryRun"]}')

    operations=create_ops(virtual,walls,door,results);created_ids=[x['arguments']['semanticId'] for x in operations]
    created=False
    try:
        response=send('applyPatch',revision,{'operations':operations});require_ok('composition create',response);created=True;revision=response['revision']
        actual={x['semanticId']:x for x in response['result'] if x['semanticId'] in created_ids}
        if set(actual)!=set(created_ids): raise TransportError(f'create read-back IDs mismatch: {sorted(set(created_ids)-set(actual))}')
        expected={x['arguments']['semanticId']:x['arguments'] for x in operations}
        mismatches=[]
        for identifier,row in actual.items():
            exp=expected[identifier]
            if row['class']!=exp['class'] or not close(row['position'],exp['position']) or not close(row['rotation'],exp['rotation'],.05): mismatches.append({'id':identifier,'expected':exp,'actual':row})
        if mismatches: raise TransportError(f'actual read-back mismatch: {mismatches}')
        actual_validation=validate_actual_readback(solver,virtual,results,actual)
        matrix['actualReadback']={'objects':len(actual),'classes':sorted({x['class'] for x in actual.values()}),'tolerance':config['tolerances']['actualReadback'],'valid':True,'spatialValidation':actual_validation}
        if interactive:
            print('\nINTERACTIVE CHECKPOINT: composition is present near [4600,4600,10].')
            print('Inspect it in Eden. Press Enter here only when it may be removed.')
            input()
    finally:
        if created:
            state=send('inspectScene',revision);require_ok('pre-cleanup inspectScene',state);revision=state['revision']
            present={x['semanticId'] for x in state['result']}
            deletes=[patch('delete',{'semanticId':x}) for x in reversed(created_ids) if x in present]
            if deletes:
                cleanup=send('applyPatch',revision,{'operations':deletes});require_ok('cleanup',cleanup);revision=cleanup['revision']

    final=send('inspectScene',revision);require_ok('final inspectScene',final)
    scene_unchanged=final['result']==initial_scene
    if not scene_unchanged: raise TransportError('cleanup did not restore the initial scene')
    artifact={
        'schemaVersion':1,'status':'PASS','catalogVersion':config['catalogVersion'],'createdAtUtc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'sessionId':caps['sessionId'],'startRevision':initial['revision'],'endRevision':final['revision'],
        'curatedClasses':sorted(CURATED),'classDiagnostics':caps['result']['classDiagnostics'],
        'primitiveTests':matrix,'composition':[r.json() for r in results],
        'createdObjects':len(operations),'actualReadback':matrix['actualReadback'],
        'sceneUnchanged':scene_unchanged,'productionMapsTouched':False,'unitTestCount':15,'transcript':transcript,
    }
    out=ROOT/'Tools/MapAutomation/artifacts'/f'phase3_live_{time.strftime("%Y%m%d_%H%M%S")}.json'
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(artifact,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    latest=ROOT/'Tools/MapAutomation/artifacts/phase3_live_latest.json';latest.write_text(json.dumps(artifact,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(f'PASS: Phase 3 live Eden validation; sceneUnchanged={scene_unchanged}; artifact={out}')
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--timeout',type=float,default=45)
    parser.add_argument('--interactive',action='store_true',help='pause with the verified temporary composition visible before cleanup')
    args=parser.parse_args()
    try: run(args.timeout,args.interactive)
    except (OSError,KeyError,TypeError,ValueError,RuntimeError,TransportError) as exc: parser.exit(1,f'FAIL: {exc}\n')


if __name__=='__main__': main()
