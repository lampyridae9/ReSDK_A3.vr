"""Phase 8 building orchestration: plan, shell, room dry-runs, validate, then apply."""
from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
import uuid
from typing import Any

from planner import PlannerInput,PlannerStatus
from room_generator import ExistingRoomShell,GenerationOptions,GenerationStatus,RoomGenerator
from room_generator.gateway import MapAutomationRoomGateway,TransactionApplyError,_fingerprint
from spatial.model import ResolvedObject,SceneState,SpatialTransform,SupportSurface
from spatial.solver import load_phase3_assets
from transport import TransportError

from .layout import BuildingLayoutSolver,PROFILE_PATH,expand_building_plan,load_profile
from .model import BuildingFootprint,BuildingLayout,BuildingOptions,BuildingResult,BuildingStatus,PortalPlan,Rect,SpacePlan
from .planner import validate_building_brief
from .validator import BuildingAccessibilityValidator,budget_report
from .structure import StructuralAssembler, BuildingShellValidator, load_structural_assets, ASSETS_PATH
from .capture import render_building_overlay


def validate_transform_readback(requested, actual):
    sid=requested['semanticId']
    for field in ('position','rotation'):
        values=actual.get(field)
        if not isinstance(values,(list,tuple)) or len(values)!=3 or any(
                not isinstance(v,(int,float)) or not math.isfinite(v) for v in values):
            raise TransportError('BUILDING_TRANSFORM_READBACK_INVALID: '+sid)
    # Engine JSON numbers retain six significant digits. At world x=5000,
    # quantisation alone is +/-5 mm; at a z datum of 10 it is +/-0.00005 m.
    def position_tolerance(value):
        quantum=10**(math.floor(math.log10(abs(value)))-5) if value else 0
        return max(.002,quantum/2+.0005)
    if actual.get('class')!=requested['class'] or any(abs(x-y)>position_tolerance(x) for x,y in zip(requested['position'],actual['position'])):
        raise TransportError('BUILDING_TRANSFORM_READBACK_MISMATCH: '+sid)
    if any(abs((x-y+180)%360-180)>.02 for x,y in zip(requested['rotation'],actual['rotation'])):
        raise TransportError('BUILDING_ROTATION_READBACK_MISMATCH: '+sid)
    scale=actual.get('scale')
    if not isinstance(scale,(int,float)) or not math.isfinite(scale) or abs(scale-requested['scale'])>.0001:
        raise TransportError('BUILDING_SCALE_READBACK_MISMATCH: '+sid)

ROOT=Path(__file__).resolve().parents[3]
ARTIFACTS=ROOT/"Tools/MapAutomation/artifacts/buildings"
CATALOG=ROOT/"Tools/MapAutomation/catalog/objects.json"


def _gateway_id(value:str)->str:return value.replace(".","__")


def _physical_wall_runs(floor:Any)->list[dict[str,Any]]:
    """Merge semantic wall fragments into buildable collinear envelope runs."""
    groups:dict[tuple[str,float,bool],list[Any]]={}
    for wall in floor.walls:
        horizontal=abs(wall.start[1]-wall.end[1])<1e-6
        key=("H" if horizontal else "V",round(wall.start[1] if horizontal else wall.start[0],6),wall.exterior)
        groups.setdefault(key,[]).append(wall)
    runs=[]
    for (axis,fixed,exterior),walls in sorted(groups.items()):
        walls.sort(key=lambda w:w.start[0] if axis=="H" else w.start[1])
        current=[];start=end=None
        for wall in walls:
            a=wall.start[0] if axis=="H" else wall.start[1];b=wall.end[0] if axis=="H" else wall.end[1]
            if current and abs(a-end)>1e-5:
                runs.append({"axis":axis,"fixed":fixed,"start":start,"end":end,"exterior":exterior,"walls":current})
                current=[];start=None
            if not current:start=a
            current.append(wall);end=b
        if current:runs.append({"axis":axis,"fixed":fixed,"start":start,"end":end,"exterior":exterior,"walls":current})
    return runs


def _fit_wall_modules(length:float,modules:list[dict[str,Any]],max_adjustment:float,variant:int)->tuple[list[dict[str,Any]],float]:
    """Bounded exact-ish one-dimensional packing; never overhangs a wall run."""
    if not modules:raise ValueError('NO_COMPATIBLE_WALL_MODULES')
    candidates=[];max_count=min(9,max(1,math.ceil(length/min(m["length"] for m in modules))+1))
    for count in range(1,max_count+1):
        for indexes in itertools.combinations_with_replacement(range(len(modules)),count):
            chosen=[modules[i] for i in indexes];total=sum(m["length"] for m in chosen)
            # No positive seams (holes) and no single-module overhang.
            if total < length-1e-6 or (count==1 and abs(total-length)>1e-6):continue
            adjustment=abs(length-total)/max(1,count-1)
            if adjustment<=max_adjustment+1e-9:
                materials=len({m["material"] for m in chosen})
                candidates.append(((materials,round(adjustment,8),count,tuple(indexes)),chosen,(length-total)/(count-1) if count>1 else 0.0))
    if not candidates:raise ValueError(f"WALL_RUN_UNTILABLE length={length:.3f} tolerance={max_adjustment:.3f}")
    _,chosen,seam=min(candidates,key=lambda row:row[0])
    chosen=list(chosen)
    chosen.sort(key=lambda m:(m['material'],m['asset']))
    return chosen,seam


def _room_shell(room:SpacePlan,portal:PortalPlan,elevation:float,storey_height:float,wall_clearance:float=0)->ExistingRoomShell:
    r=room.rect;x,y=r.center;z=elevation
    owner=room.id
    px,py=portal.center
    # Keep the navigation seed a full approach-clearance inside the room.
    # The former 0.45 m inset could round onto an inflated boundary cell for
    # module-derived room widths such as 4.35 m, rejecting every candidate.
    approach_inset=.8
    if abs(px-r.x)<1e-6:entrance=(px+approach_inset,py);door_position=(px-.08,py,z);yaw=90;portal_side="west"
    elif abs(px-r.x2)<1e-6:entrance=(px-approach_inset,py);door_position=(px+.08,py,z);yaw=90;portal_side="east"
    elif abs(py-r.y)<1e-6:entrance=(px,py+approach_inset);door_position=(px,py-.08,z);yaw=0;portal_side="south"
    else:entrance=(px,py-approach_inset);door_position=(px,py+.08,z);yaw=0;portal_side="north"
    # Reserve the full wall bearing width before solving furniture placement.
    if wall_clearance:
        r=Rect(r.x+wall_clearance,r.y+wall_clearance,r.width-2*wall_clearance,r.depth-2*wall_clearance)
        x,y=r.center
    surfaces={
        f"{owner}.floor":SupportSurface(f"{owner}.floor","floor",owner,(x,y,z),(0,0,1),(1,0,0),(0,1,0),(r.width/2,r.depth/2)),
        f"{owner}.ceiling":SupportSurface(f"{owner}.ceiling","ceiling",owner,(x,y,z+storey_height),(0,0,-1),(1,0,0),(0,1,0),(r.width/2,r.depth/2)),
    }
    wall_specs={
        "east":((r.x2,y,z+storey_height/2),(-1,0,0),(0,1,0),(max(.1,r.depth/2-.2),storey_height/2)),
        "north":((x,r.y2,z+storey_height/2),(0,-1,0),(1,0,0),(max(.1,r.width/2-.2),storey_height/2)),
        "south":((x,r.y,z+storey_height/2),(0,1,0),(1,0,0),(max(.1,r.width/2-.2),storey_height/2)),
        "west":((r.x,y,z+storey_height/2),(1,0,0),(0,1,0),(max(.1,r.depth/2-.2),storey_height/2)),
    }
    # Phase 4's parallel-bed pattern targets the first wall deterministically.
    # Keep the same world-facing wall on mirrored rooms: the curated bed's
    # interaction clearance is not proven mirror-symmetric in model space.
    ordered=["west","east","north","south"]
    for index,side in enumerate(ordered,1):
        origin,normal,u_axis,half=wall_specs[side];sid=f"{owner}.wall_{index}_{side}"
        surfaces[sid]=SupportSurface(sid,"wall",owner,origin,normal,u_axis,(0,0,1),half)
    assets,_=load_phase3_assets();door=ResolvedObject.create(portal.id,assets[portal.door_asset],SpatialTransform(door_position,(0,0,yaw),"WORLD"))
    scene=SceneState(f"{owner}.region",[(r.x,r.y),(r.x2,r.y),(r.x2,r.y2),(r.x,r.y2)],surfaces,[door],entrance,[])
    return ExistingRoomShell(f"{owner}.shell",scene,[],True)


class BuildingGenerator:
    def __init__(self,*,planner_service:Any|None=None,room_generator:RoomGenerator|None=None,
        gateway:MapAutomationRoomGateway|None=None,artifact_dir:Path=ARTIFACTS,review_callback:Any|None=None,profile=None):
        self.planner_service=planner_service;self.gateway=gateway;self.room_generator=room_generator or RoomGenerator()
        self.artifact_dir=artifact_dir;self.profile=copy.deepcopy(profile) if profile is not None else load_profile();self.layout_solver=BuildingLayoutSolver(self.profile)
        self.accessibility=BuildingAccessibilityValidator()
        self.structural_assets=load_structural_assets()
        self.shell_validator=BuildingShellValidator(self.structural_assets,self.profile.get('contactTolerance',.02))
        self.review_callback=review_callback

    @staticmethod
    def _ms()->int:return int(time.time()*1000)

    def _save(self,result:BuildingResult)->BuildingResult:
        self.artifact_dir.mkdir(parents=True,exist_ok=True);path=self.artifact_dir/(result.generation_id+".json")
        try:result.artifact_path=str(path.relative_to(ROOT)).replace("\\","/")
        except ValueError:result.artifact_path=str(path)
        path.write_text(json.dumps(result.json(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return result

    def _fail(self,result:BuildingResult,status:BuildingStatus,code:str,details:dict[str,Any]|None=None)->BuildingResult:
        result.status=status;result.diagnostics.append({"code":code,"details":details or {}});return self._save(result)

    def _shell_operations(self,layout:BuildingLayout)->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
        operations,diagnostics,_=StructuralAssembler(self.profile,self.structural_assets).assemble(layout)
        return operations,diagnostics

    def generate(self,request:str,footprint:BuildingFootprint,options:BuildingOptions=BuildingOptions(),*,
        building_brief:dict[str,Any]|None=None)->BuildingResult:
        started=self._ms();gid="building_generation_"+uuid.uuid4().hex[:16]
        result=BuildingResult(gid,BuildingStatus.PLANNER_FAILED,request);planning=time.perf_counter()
        if building_brief is None:
            if self.planner_service is None:return self._fail(result,BuildingStatus.PLANNER_FAILED,"BUILDING_PLANNER_NOT_CONFIGURED")
            planned=self.planner_service.plan_building(PlannerInput(request,options.seed));result.metrics["llmCalls"]=1
            result.metrics["planningLatencyMs"]=planned.latency_ms
            if planned.status!=PlannerStatus.SUCCESS or planned.validated_output is None:
                return self._fail(result,BuildingStatus.PLANNER_FAILED,planned.status.value,{"diagnostics":planned.diagnostics})
            brief=planned.validated_output
        else:
            try:brief=validate_building_brief(building_brief)
            except ValueError as exc:return self._fail(result,BuildingStatus.PLANNER_FAILED,"BUILDING_BRIEF_INVALID",{"message":str(exc)})
            if options.seed is not None:brief=copy.deepcopy(brief);brief["seed"]=options.seed
            result.metrics["llmCalls"]=0;result.metrics["planningLatencyMs"]=int((time.perf_counter()-planning)*1000)
        result.building_brief=copy.deepcopy(brief);plan=expand_building_plan(brief,self.profile);result.building_plan=plan.json()
        _,phase3=load_phase3_assets()
        result.reproducibility={"seed":brief["seed"],"buildingProfile":"sha256:"+hashlib.sha256(json.dumps(self.profile,sort_keys=True).encode()).hexdigest(),
            "catalogVersion":phase3["catalogVersion"],"solverVersion":"building-layout-v1+structural-assembly-v2",
            "structuralAssets":"sha256:"+hashlib.sha256(ASSETS_PATH.read_bytes()).hexdigest(),
            "footprint":footprint.json()}
        if options.mode=="plan-only":
            result.status=BuildingStatus.SUCCESS;result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        layout_started=time.perf_counter();layout=self.layout_solver.solve(plan,footprint,brief,options)
        result.metrics["layoutLatencyMs"]=int((time.perf_counter()-layout_started)*1000);result.building_layout=layout.json()
        result.metrics["layoutAttempts"]=layout.candidate.get("attemptsUsed",0)
        if layout.feasibility=="INFEASIBLE":return self._fail(result,BuildingStatus.INFEASIBLE,"BUILDING_INFEASIBLE",{"diagnostics":layout.diagnostics})
        access=self.accessibility.validate(layout,plan)
        if access:return self._fail(result,BuildingStatus.VALIDATION_FAILED,"BUILDING_ACCESSIBILITY_FAILED",{"diagnostics":access})
        try:shell_ops,shell_warnings=self._shell_operations(layout)
        except ValueError as exc:return self._fail(result,BuildingStatus.VALIDATION_FAILED,"BUILDING_SHELL_INVALID",{"message":str(exc)})
        result.shell_operations=shell_ops;result.diagnostics.extend(shell_warnings)
        result.structural_plan=StructuralAssembler(self.profile,self.structural_assets).compile(layout)
        structural_errors=shell_warnings+self.shell_validator.validate(layout,shell_ops,result.structural_plan)
        result.shell_validation={'status':'FAIL' if structural_errors else 'PASS',
            'scope':'calibrated envelope; collision and walkthrough not certified','diagnostics':structural_errors}
        if structural_errors:
            return self._fail(result,BuildingStatus.VALIDATION_FAILED,'BUILDING_SHELL_INVALID',{'diagnostics':structural_errors})
        if options.mode=="layout-only":
            result.status=BuildingStatus.SUCCESS;result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        furnishing=[];room_started=time.perf_counter();room_backtracks=0
        if not options.shell_only:
            for slot in plan.room_slots:
                if slot["type"]!="bedroom":continue
                floor=next(x for x in layout.floors if x.id==slot["floorId"]);room=next(x for x in floor.spaces if x.id==slot["id"])
                portal=next(x for x in floor.portals if x.to_space==room.id)
                room_result=self.room_generator.generate_room("deterministic building bedroom",_room_shell(room,portal,floor.elevation,self.profile['ceilingOffset'],self.profile.get('furnitureWallClearance',0)),
                    GenerationOptions("dry-run",slot["roomBrief"]["seed"],capture=False),planner_brief=slot["roomBrief"],room_id=room.id,slot_namespace=room.id)
                result.room_generations.append({"roomId":room.id,"status":room_result.status.value,"roomPlan":room_result.room_plan,
                    "placements":room_result.placements,"droppedOptional":room_result.dropped_optional,"metrics":room_result.metrics,
                    "diagnostics":room_result.diagnostics})
                room_backtracks+=int(room_result.metrics.get("backtracks",0))
                if room_result.status!=GenerationStatus.SUCCESS:
                    result.metrics["roomGenerationLatencyMs"]=int((time.perf_counter()-room_started)*1000)
                    return self._fail(result,BuildingStatus.ROOM_GENERATION_FAILED,"ROOM_GENERATION_FAILED",{"roomId":room.id,"status":room_result.status.value})
                for placement in room_result.placements:
                    furnishing.append({"operation":"create","arguments":{"semanticId":placement["id"],"class":placement["asset"],
                        "position":placement["transform"]["position"],"rotation":placement["transform"]["rotation"],"scale":1,
                        "parentId":room.id},"stage":"lights" if placement["asset"]=="LampCeiling" else "furniture"})
        result.metrics["roomGenerationLatencyMs"]=int((time.perf_counter()-room_started)*1000);result.metrics["roomBacktracks"]=room_backtracks
        order={"floors":0,"walls":1,"headers":2,"doors":3,"stairs":4,"guards":5,"furniture":6,"lights":7};operations=sorted(shell_ops+furnishing,key=lambda x:order[x["stage"]])
        # Distinct generations can coexist; cleanup never targets another building.
        def scoped(value):
            value=_gateway_id(value.removeprefix('building_001__'))
            if len(value)>48:value=value[:35]+'_'+hashlib.sha256(value.encode()).hexdigest()[:12]
            return 'b'+gid[-12:]+'__'+value
        for op in operations:
            op['arguments']['semanticId']=scoped(op['arguments']['semanticId'])
            op['arguments']['parentId']=scoped(op['arguments']['parentId'])
        catalog=json.loads(CATALOG.read_text(encoding="utf-8"));chunks={x["classname"]:x.get("chunkType","UNKNOWN") for x in catalog["objects"]}
        result.budget=budget_report(operations,chunks);result.diagnostics.extend(result.budget["warnings"])
        ids=[x["arguments"]["semanticId"] for x in operations]
        result.ownership={"generationId":gid,"buildingId":plan.id,"objects":[{"semanticId":x["arguments"]["semanticId"],
            "floorId":x.get('floorId') or next((f.id for f in layout.floors if x["arguments"]["position"][2]>=f.elevation-.2 and x["arguments"]["position"][2]<f.elevation+plan.storey_height),None),
            "ownerId":x["arguments"]["parentId"],"stage":x["stage"]} for x in operations],"cleanupStatus":"NOT_REQUIRED" if options.mode!="live" else "PENDING"}
        result.metrics.update({"roomCount":len(plan.room_slots),"portalCount":sum(len(f.portals) for f in layout.floors),
            "objectsGenerated":len(operations),"visionCalls":0})
        if options.mode=="dry-run":
            result.status=BuildingStatus.SUCCESS;result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        if self.gateway is None:return self._fail(result,BuildingStatus.APPLY_FAILED,"LIVE_GATEWAY_NOT_CONFIGURED")
        blocked=[x for x in operations if x.get("applyAllowed") is False]
        if blocked:return self._fail(result,BuildingStatus.APPLY_FAILED,"VERTICAL_ASSET_NOT_GENERATOR_ALLOWED",
            {"assets":sorted({x["arguments"]["class"] for x in blocked}),"policy":"fail-closed before Eden mutation"})
        clean_ops=[{"operation":x["operation"],"arguments":x["arguments"]} for x in operations]
        try:
            snapshot=self.gateway.snapshot();result.transaction={"state":"PREFLIGHT_COMPLETE","revisionBefore":snapshot.revision,
                "sceneFingerprintBefore":snapshot.fingerprint,"commitBoundary":"one logical building transaction",
                "physicalBatchLimit":32,"applyOrder":list(order),"batches":[]}
            revision=snapshot.revision;applied={"revision":revision,"result":snapshot.objects}
            for stage in order:
                stage_ops=[x for x in clean_ops if next(raw["stage"] for raw in operations if raw["arguments"]["semanticId"]==x["arguments"]["semanticId"])==stage]
                for offset in range(0,len(stage_ops),32):
                    batch=stage_ops[offset:offset+32];applied=self.gateway.apply(batch,revision);revision=applied["revision"]
                    expected={x["arguments"]["semanticId"] for x in batch};actual={x["semanticId"] for x in applied["result"]}
                    missing=expected-actual
                    result.transaction["batches"].append({"stage":stage,"count":len(batch),"revision":revision})
                    result.transaction["currentRevision"]=revision
                    if missing:raise TransportError("building batch read-back missing semantic IDs: "+str(sorted(missing)))
                    rows={x['semanticId']:x for x in applied['result']}
                    for requested in batch:
                        a=requested['arguments'];actual_row=rows[a['semanticId']]
                        validate_transform_readback(a,actual_row)
                if self.review_callback and stage in {'walls','stairs','lights'}:
                    result.transaction['reviewStage']=stage;self._save(result)
                    self.review_callback({'walls':'shell-only','stairs':'portals/stairs','lights':'furnished building'}[stage],result)
            result.transaction.update({"state":"COMMITTED","revisionCommitted":revision})
            if options.capture:
                anchor=next((row for row in applied["result"] if row.get("positionASL") and row.get("position")),None)
                dz=anchor["positionASL"][2]-anchor["position"][2] if anchor else 0.0
                x,y,z=footprint.origin;room=next(s for s in layout.floors[0].spaces if s.kind=="bedroom")
                rx,ry=room.rect.center
                circulation=next(s for s in layout.floors[0].spaces if s.kind=='corridor').rect
                cx,cy=circulation.center
                entrance=next(p for p in layout.floors[0].portals if p.exterior)
                ex,ey=entrance.center
                outward=(ex-x,ey-y);norm=math.hypot(*outward)
                poses=[("exterior_front",[x,y-footprint.depth*1.8,z+dz+5],[x,y,z+dz+2]),
                    ("exterior_corner",[x+footprint.width,y-footprint.depth,z+dz+6],[x,y,z+dz+2]),
                    ("entrance",[ex+outward[0]/norm*4,ey+outward[1]/norm*4,z+dz+1.6],[ex,ey,z+dz+1.3]),
                    ("floor_0_overview",[circulation.x2-1,circulation.y+1,z+dz+2.5],[cx,cy,z+dz+1.4]),
                    ("representative_room",[room.rect.x2-1.2,ry,z+dz+1.6],[room.rect.x+1,ry,z+dz+1.3])]
                if len(layout.floors)>1:
                    upper=layout.floors[1].elevation
                    stair=layout.floors[0].vertical_connections[0];sx,sy=stair.occupied_region.center
                    poses.extend([("floor_1_overview",[circulation.x2-1,circulation.y+1,upper+dz+1.7],[sx,sy,upper+dz-.4]),
                        ("stairs",[sx-1,sy-3.8,z+dz+1.6],[sx-1,sy,z+dz+1.1])])
                for name,pos,target in poses:
                    try:
                        captured=self.gateway.capture(revision,[{"viewId":name,"cameraRole":name,"positionASL":pos,
                            "targetASL":target,"fov":.9,"captureClassOverlay":name=="representative_room"}])
                        capture_artifact=captured['result'][0]
                        result.screenshots.append({"viewId":name,"revision":revision,"artifact":capture_artifact})
                        clean=capture_artifact.get('cleanPath',capture_artifact.get('path'))
                        if clean and Path(clean).is_file():
                            overlay=self.artifact_dir/(gid+'_'+name+'_semantic.png')
                            render_building_overlay(clean,str(overlay),result.structural_plan,
                                {'positionASL':pos,'targetASL':target,'fov':.9},dz)
                            capture_artifact['semanticOverlayPath']=str(overlay)
                    except (TransportError,OSError) as exc:
                        # Capture is a post-commit review aid.  A transient OS
                        # screenshot failure must not roll back a structurally
                        # valid building or masquerade as an Eden apply failure.
                        result.diagnostics.append({"code":"BUILDING_CAPTURE_FAILED","viewId":name,"message":str(exc)})
            final=self.gateway.inspect(revision);result.transaction["sceneFingerprintAfter"]=_fingerprint(final["result"])
            result.status=BuildingStatus.SUCCESS
            if self.review_callback:self.review_callback('screenshots',result)
            if not options.keep_result:self.cleanup(result)
            result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        except TransactionApplyError as exc:
            partial=bool({x.get("semanticId") for x in exc.actual}&set(ids))
            return self._fail(result,BuildingStatus.PARTIAL_FAILURE if partial else BuildingStatus.APPLY_FAILED,"BUILDING_APPLY_FAILED",{"response":exc.response})
        except (TransportError,OSError,KeyError,TypeError,ValueError) as exc:
            cleanup="NOT_APPLIED"
            revision=result.transaction.get("currentRevision")
            if revision is not None and not options.keep_result:
                try:
                    cleaned=self.gateway.cleanup(ids,revision);cleanup="CLEAN" if _fingerprint(cleaned["result"])==result.transaction["sceneFingerprintBefore"] else "DIVERGED"
                except Exception as cleanup_exc:cleanup="FAILED: "+str(cleanup_exc)
            elif revision is not None:
                cleanup='KEPT_FOR_REVIEW';result.ownership['cleanupStatus']=cleanup
            result.transaction["failureCleanup"]=cleanup
            return self._fail(result,BuildingStatus.PARTIAL_FAILURE if cleanup not in {"NOT_APPLIED","CLEAN"} else BuildingStatus.APPLY_FAILED,
                "BUILDING_TRANSACTION_FAILED",{"message":str(exc),"failureCleanup":cleanup})

    def cleanup(self,result:BuildingResult)->None:
        if self.gateway is None or "revisionCommitted" not in result.transaction:raise ValueError("no committed live building")
        ids=[x["semanticId"] for x in result.ownership["objects"]];cleaned=self.gateway.cleanup(ids,result.transaction["revisionCommitted"])
        after=_fingerprint(cleaned["result"]);clean=after==result.transaction.get("sceneFingerprintBefore")
        result.ownership["cleanupStatus"]="CLEAN" if clean else "DIVERGED";result.transaction["cleanupRevision"]=cleaned["revision"]
        if not clean:raise TransportError("building cleanup did not restore scene fingerprint")
