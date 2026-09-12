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
    candidates=[];max_count=min(9,max(1,math.ceil(length/min(m["length"] for m in modules))+1))
    for count in range(1,max_count+1):
        for indexes in itertools.combinations_with_replacement(range(len(modules)),count):
            chosen=[modules[i] for i in indexes];total=sum(m["length"] for m in chosen)
            adjustment=abs(length-total)/(count-1 if count>1 else 2)
            if adjustment<=max_adjustment+1e-9:
                materials=len({m["material"] for m in chosen})
                candidates.append(((round(adjustment,8),count,-materials,tuple(indexes)),chosen,(length-total)/(count-1) if count>1 else 0.0))
    if not candidates:raise ValueError(f"WALL_RUN_UNTILABLE length={length:.3f} tolerance={max_adjustment:.3f}")
    _,chosen,seam=min(candidates,key=lambda row:row[0])
    chosen=list(chosen)
    if len(chosen)>1:
        shift=variant%len(chosen);chosen=chosen[shift:]+chosen[:shift]
    return chosen,seam


def _room_shell(room:SpacePlan,portal:PortalPlan,elevation:float,storey_height:float)->ExistingRoomShell:
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
        gateway:MapAutomationRoomGateway|None=None,artifact_dir:Path=ARTIFACTS):
        self.planner_service=planner_service;self.gateway=gateway;self.room_generator=room_generator or RoomGenerator()
        self.artifact_dir=artifact_dir;self.profile=load_profile();self.layout_solver=BuildingLayoutSolver(self.profile)
        self.accessibility=BuildingAccessibilityValidator()

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
        operations=[];warnings=[];structure=self.profile["structure"];floor_w,floor_d=structure["floorModule"]
        # Pick the unscaled panel orientation with the smallest boundary error,
        # then keep native pitch. This removes the previous coplanar floor overlap.
        outer=layout.floors[0].footprint
        floor_candidates=[]
        for yaw,mw,md in ((0,floor_w,floor_d),(90,floor_d,floor_w)):
            nx=max(1,round(outer.width/mw));ny=max(1,round(outer.depth/md))
            floor_candidates.append((max(abs(nx*mw-outer.width),abs(ny*md-outer.depth)),yaw,mw,md,nx,ny))
        edge_error,floor_yaw,mw,md,nx,ny=min(floor_candidates)
        if edge_error>.15:raise ValueError(f"FLOOR_GRID_UNTILABLE edgeError={edge_error:.3f}")
        levels=[(f.id,f.elevation) for f in layout.floors]+[("roof",layout.floors[-1].elevation+self.profile["storeyHeight"])]
        grid_x0=outer.center[0]-nx*mw/2+mw/2;grid_y0=outer.center[1]-ny*md/2+md/2
        for level_id,z in levels:
            opening=next((v.occupied_region for f in layout.floors for v in f.vertical_connections if v.to_floor==level_id),None)
            for ix in range(nx):
                for iy in range(ny):
                    cx=grid_x0+ix*mw;cy=grid_y0+iy*md
                    if opening and opening.contains(cx,cy):
                        warnings.append({"code":"STAIRWELL_OPENING_APPROXIMATE","owner":level_id,"moduleGridIndex":[ix,iy]})
                        continue
                    sid=f"building_001__{level_id}__floor_module_{ix*ny+iy+1:03d}"
                    operations.append({"operation":"create","arguments":{"semanticId":sid,"class":structure["floorAsset"],
                        "position":[cx,cy,z-.0922552],"rotation":[0,0,floor_yaw],"scale":1,"parentId":level_id},"stage":"floors"})
        modules=structure["wallModules"];max_adjustment=structure["maxWallJointAdjustment"]
        for floor in layout.floors:
            portals={p.wall_segment:p for p in floor.portals}
            for run_index,run in enumerate(_physical_wall_runs(floor),1):
                associated=[portals[w.id] for w in run["walls"] if w.id in portals]
                if len(associated)>1:raise ValueError("MULTIPLE_PORTALS_ON_PHYSICAL_WALL_RUN")
                portal=associated[0] if associated else None;length=run["end"]-run["start"]
                intervals=[(run["start"],run["end"])]
                if portal:
                    along=portal.center[0] if run["axis"]=="H" else portal.center[1]
                    half=structure["doorClearWidth"]/2
                    intervals=[(run["start"],along-half),(along+half,run["end"])]
                module_index=0
                for interval_index,(start,end) in enumerate(intervals):
                    span=end-start
                    if span<=.25:continue
                    chosen,seam=_fit_wall_modules(span,modules,max_adjustment,
                        floor.index*31+run_index*7+interval_index)
                    cursor=start
                    for item_index,item in enumerate(chosen):
                        module_index+=1;center=cursor+item["length"]/2
                        asset=item["asset"]
                        if run["exterior"] and not portal and item["length"]==6.0 and structure.get("windowModules"):
                            windows=structure["windowModules"];asset=windows[(floor.index+run_index+item_index)%len(windows)]["asset"]
                        x=center if run["axis"]=="H" else run["fixed"]
                        y=run["fixed"] if run["axis"]=="H" else center
                        run_id=f"{floor.id}.physical_wall_{run_index:03d}"
                        sid=_gateway_id(f"building_001__{run_id}__module_{module_index:03d}")
                        operations.append({"operation":"create","arguments":{"semanticId":sid,"class":asset,
                            # GOLib's structure placement frame is floor-based;
                            # applying the raw model AABB minZ here lifts walls twice.
                            "position":[x,y,floor.elevation+item.get("positionZOffset",0)],"rotation":[0,0,0 if run["axis"]=="H" else 90],"scale":1,
                            "parentId":_gateway_id(run_id)},"stage":"walls"})
                        cursor+=item["length"]+seam
            for portal in floor.portals:
                horizontal=abs(next(w for w in floor.walls if w.id==portal.wall_segment).start[1]-next(w for w in floor.walls if w.id==portal.wall_segment).end[1])<1e-6
                operations.append({"operation":"create","arguments":{"semanticId":f"building_001__{portal.id}","class":portal.door_asset,
                    "position":[portal.center[0],portal.center[1],floor.elevation],"rotation":[0,0,0 if horizontal else 90],"scale":1,
                    "parentId":portal.id},"stage":"doors"})
        for vertical in layout.floors[0].vertical_connections:
            operations.append({"operation":"create","arguments":{"semanticId":f"building_001__{vertical.id}","class":vertical.asset,
                "position":[*vertical.occupied_region.center,layout.floors[0].elevation+vertical.model_origin_z_offset],"rotation":[0,0,vertical.yaw],"scale":1,
                "parentId":vertical.id},"stage":"stairs","applyAllowed":self.profile["structure"]["stairGeneratorAllowed"]})
        return operations,warnings

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
        result.reproducibility={"seed":brief["seed"],"buildingProfile":"sha256:"+hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest(),
            "catalogVersion":phase3["catalogVersion"],"solverVersion":"building-layout-v1",
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
        if options.mode=="layout-only":
            result.status=BuildingStatus.SUCCESS;result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        furnishing=[];room_started=time.perf_counter();room_backtracks=0
        if not options.shell_only:
            for slot in plan.room_slots:
                if slot["type"]!="bedroom":continue
                floor=next(x for x in layout.floors if x.id==slot["floorId"]);room=next(x for x in floor.spaces if x.id==slot["id"])
                portal=next(x for x in floor.portals if x.to_space==room.id)
                room_result=self.room_generator.generate_room("deterministic building bedroom",_room_shell(room,portal,floor.elevation,plan.storey_height),
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
        order={"floors":0,"walls":1,"doors":2,"stairs":3,"furniture":4,"lights":5};operations=sorted(shell_ops+furnishing,key=lambda x:order[x["stage"]])
        catalog=json.loads(CATALOG.read_text(encoding="utf-8"));chunks={x["classname"]:x.get("chunkType","UNKNOWN") for x in catalog["objects"]}
        result.budget=budget_report(operations,chunks);result.diagnostics.extend(result.budget["warnings"])
        ids=[x["arguments"]["semanticId"] for x in operations]
        result.ownership={"generationId":gid,"buildingId":plan.id,"objects":[{"semanticId":x["arguments"]["semanticId"],
            "floorId":next((f.id for f in layout.floors if x["arguments"]["position"][2]>=f.elevation-.2 and x["arguments"]["position"][2]<f.elevation+plan.storey_height),None),
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
            result.transaction.update({"state":"COMMITTED","revisionCommitted":revision})
            if options.capture:
                anchor=next((row for row in applied["result"] if row.get("positionASL") and row.get("position")),None)
                dz=anchor["positionASL"][2]-anchor["position"][2] if anchor else 0.0
                x,y,z=footprint.origin;room=next(s for s in layout.floors[0].spaces if s.kind=="bedroom")
                rx,ry=room.rect.center
                poses=[("exterior",[x,y-footprint.depth*1.8,z+dz+5],[x,y,z+dz+2]),
                    ("floor_001",[x+footprint.width,y-footprint.depth,z+dz+10],[x,y,z+dz+1]),
                    ("representative_room",[room.rect.x2-1.2,ry,z+dz+1.6],[room.rect.x+1,ry,z+dz+1.3])]
                if len(layout.floors)>1:
                    upper=layout.floors[1].elevation
                    poses.extend([("floor_002",[x+footprint.width,y-footprint.depth,upper+dz+10],[x,y,upper+dz+1]),
                        ("stairs",[x,y+footprint.depth,z+dz+4],[x,y,z+dz+2])])
                for name,pos,target in poses:
                    try:
                        captured=self.gateway.capture(revision,[{"viewId":name,"cameraRole":name,"positionASL":pos,
                            "targetASL":target,"fov":.9,"captureClassOverlay":name=="representative_room"}])
                        result.screenshots.append({"viewId":name,"revision":revision,"artifact":captured["result"][0]})
                    except TransportError as exc:
                        # Capture is a post-commit review aid.  A transient OS
                        # screenshot failure must not roll back a structurally
                        # valid building or masquerade as an Eden apply failure.
                        result.diagnostics.append({"code":"BUILDING_CAPTURE_FAILED","viewId":name,"message":str(exc)})
            final=self.gateway.inspect(revision);result.transaction["sceneFingerprintAfter"]=_fingerprint(final["result"])
            result.status=BuildingStatus.SUCCESS
            if not options.keep_result:self.cleanup(result)
            result.metrics["totalGenerationLatencyMs"]=self._ms()-started;return self._save(result)
        except TransactionApplyError as exc:
            partial=bool({x.get("semanticId") for x in exc.actual}&set(ids))
            return self._fail(result,BuildingStatus.PARTIAL_FAILURE if partial else BuildingStatus.APPLY_FAILED,"BUILDING_APPLY_FAILED",{"response":exc.response})
        except (TransportError,OSError,KeyError,TypeError,ValueError) as exc:
            cleanup="NOT_APPLIED"
            revision=result.transaction.get("currentRevision")
            if revision is not None:
                try:
                    cleaned=self.gateway.cleanup(ids,revision);cleanup="CLEAN" if _fingerprint(cleaned["result"])==result.transaction["sceneFingerprintBefore"] else "DIVERGED"
                except Exception as cleanup_exc:cleanup="FAILED: "+str(cleanup_exc)
            result.transaction["failureCleanup"]=cleanup
            return self._fail(result,BuildingStatus.PARTIAL_FAILURE if cleanup not in {"NOT_APPLIED","CLEAN"} else BuildingStatus.APPLY_FAILED,
                "BUILDING_TRANSACTION_FAILED",{"message":str(exc),"failureCleanup":cleanup})

    def cleanup(self,result:BuildingResult)->None:
        if self.gateway is None or "revisionCommitted" not in result.transaction:raise ValueError("no committed live building")
        ids=[x["semanticId"] for x in result.ownership["objects"]];cleaned=self.gateway.cleanup(ids,result.transaction["revisionCommitted"])
        after=_fingerprint(cleaned["result"]);clean=after==result.transaction.get("sceneFingerprintBefore")
        result.ownership["cleanupStatus"]="CLEAN" if clean else "DIVERGED";result.transaction["cleanupRevision"]=cleaned["revision"]
        if not clean:raise TransportError("building cleanup did not restore scene fingerprint")
