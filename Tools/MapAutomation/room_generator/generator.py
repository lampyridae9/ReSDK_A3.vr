"""Phase 6 orchestration: one brief, bounded spatial search, one scene patch."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import time
import uuid
from dataclasses import replace
from typing import Any

from planner import PlannerInput, PlannerStatus
from semantic.model import SemanticDiagnostic, SemanticSlot
from semantic.pipeline import PatternPipeline, validate_planner_brief
from spatial.model import ResolvedObject, SceneState, SpatialTransform
from spatial.solver import SolverResult
from transport import TransportError
from .gateway import MapAutomationRoomGateway, TransactionApplyError, _fingerprint
from .model import ExistingRoomShell, GenerationLifecycle, GenerationOptions, GenerationResult, GenerationStatus

ROOT=Path(__file__).resolve().parents[3]
ARTIFACTS=ROOT/"Tools/MapAutomation/artifacts/generations"
PATTERN_PATH=ROOT/"Tools/MapAutomation/patterns/poor_bedroom.json"

# This is semantic dependency order, not geometry: circulation/entrance are reserved
# by the shell, core required furniture precedes ambience, and seating depends on a
# work surface. Explicit slot-to-slot relations are additionally topologically sorted.
ROLE_PHASE={"sleeping":10,"storage":20,"lighting":30,"work_surface":40,"seating":50}


class RoomGenerator:
    def __init__(self, *, planner_service: Any|None=None, pipeline: PatternPipeline|None=None,
        gateway: MapAutomationRoomGateway|None=None, artifact_dir: Path=ARTIFACTS):
        self.planner_service=planner_service;self.pipeline=pipeline or PatternPipeline();self.gateway=gateway
        self.artifact_dir=artifact_dir

    @staticmethod
    def _now_ms() -> int: return int(time.time()*1000)

    def _transition(self,result: GenerationResult,state: GenerationLifecycle) -> None:
        result.lifecycle=state;result.lifecycle_history.append({"state":state.value,"atMs":self._now_ms()})

    def _save(self,result: GenerationResult) -> GenerationResult:
        self.artifact_dir.mkdir(parents=True,exist_ok=True)
        path=self.artifact_dir/f"{result.generation_id}.json"
        try: result.artifact_path=str(path.relative_to(ROOT)).replace("\\","/")
        except ValueError: result.artifact_path=str(path)
        path.write_text(json.dumps(result.json(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
        return result

    def _fail(self,result: GenerationResult,status: GenerationStatus,code: str,details: dict[str,Any]|None=None) -> GenerationResult:
        result.status=status;result.diagnostics.append({"code":code,"stage":result.lifecycle.value,"details":details or {}})
        self._transition(result,GenerationLifecycle.FAILED);result.timings["totalMs"]=self._now_ms()-result.lifecycle_history[0]["atMs"]
        return self._save(result)

    @staticmethod
    def _ordered_slots(slots: list[SemanticSlot]) -> list[SemanticSlot]:
        furnishing=[s for s in slots if s.placement!="virtual"]
        by_id={s.id:s for s in furnishing};deps={s.id:{r.target for r in s.relations if r.target in by_id} for s in furnishing}
        result=[];remaining=set(by_id)
        while remaining:
            ready=[by_id[sid] for sid in remaining if not (deps[sid]&remaining)]
            if not ready: raise ValueError("cyclic semantic placement dependencies")
            ready.sort(key=lambda s:({"required":0,"preferred":1,"optional":2}[s.priority],ROLE_PHASE.get(s.function,99),s.id))
            chosen=ready[0];result.append(chosen);remaining.remove(chosen.id)
        return result

    def _validate_scene(self, base: SceneState, placements: list[SolverResult]) -> tuple[list[dict[str,Any]],dict[str,Any]]:
        working=copy.deepcopy(base);diagnostics=[];reachable=[]
        for placed in placements:
            obj=placed.placement;intent=placed.intent
            if obj is None: continue
            current=[]
            current+=self.pipeline.solver.support.validate(obj,working.surfaces[intent.on_surface])
            current+=self.pipeline.solver.geometry.validate(obj,working)
            current+=self.pipeline.solver.clearance.validate(obj,working)
            diagnostics += [d.json() for d in current];working.objects.append(obj)
            if intent.reachable: reachable.append(obj)
        path_points={}
        for obj in reachable:
            ds,path=self.pipeline.solver.access.validate(working,self.pipeline.solver._interaction_target(obj),obj.id)
            diagnostics += [d.json() for d in ds];path_points[obj.id]=len(path)
        return diagnostics,{"requiredTargets":len(reachable),"reachable":not diagnostics,"pathPoints":path_points}

    def _place(self, plan, shell: ExistingRoomShell, options: GenerationOptions, result: GenerationResult) -> list[SolverResult]|None:
        ordered=self._ordered_slots(plan.slots);required=[s for s in ordered if s.priority=="required"]
        optional=[s for s in ordered if s.priority!="required"]
        for slot in ordered:
            try: slot.asset=self.pipeline.asset_resolver.resolve(slot);slot.status="RESOLVED"
            except ValueError as exc:
                if slot.priority=="required":
                    result.diagnostics.append({"code":"UNRESOLVED_ASSET","subjects":[slot.id],"message":str(exc)});return None
                slot.status="DROPPED_OPTIONAL" if slot.priority=="optional" else "DROPPED_PREFERRED"
                result.dropped_optional.append({"slotId":slot.id,"status":slot.status,"reason":"UNRESOLVED_ASSET"})
        result.resolved_assets=[{"slotId":s.id,"asset":s.asset,"priority":s.priority} for s in ordered if s.asset]
        deadline=time.perf_counter()+options.search_timeout_ms/1000
        metrics=result.metrics;metrics.update({"candidateAttempts":0,"generatedCandidates":0,"backtracks":0,"searchNodes":0,
            "candidateLimit":options.candidate_limit,"maxBacktracks":options.max_backtracks,"maxSearchNodes":options.max_search_nodes,
            "searchTimeoutMs":options.search_timeout_ms,"searchBudgetExhausted":False})

        def accessible_after(state: SceneState, placements: list[SolverResult]) -> bool:
            for placed in placements:
                if placed.intent.reachable and placed.placement:
                    ds,_=self.pipeline.solver.access.validate(state,self.pipeline.solver._interaction_target(placed.placement),placed.placement.id)
                    if ds:return False
            return True

        def search(index: int,state: SceneState,placed: list[SolverResult]) -> list[SolverResult]|None:
            if index==len(required):return placed
            if time.perf_counter()>deadline or metrics["searchNodes"]>=options.max_search_nodes or metrics["backtracks"]>options.max_backtracks:
                metrics["searchBudgetExhausted"]=True;return None
            slot=required[index]
            if not slot.asset:return None
            intent=self.pipeline.placement_intent(slot,plan,state)
            batch=self.pipeline.solver.resolve_candidates(intent,state,limit=options.candidate_limit,dry_run=True)
            result.placement_intents.append(intent.json());metrics["generatedCandidates"]+=batch.generated
            for candidate in batch.candidates:
                metrics["candidateAttempts"]+=1;metrics["searchNodes"]+=1
                next_state=copy.deepcopy(state);next_state.objects.append(candidate.placement)
                next_placed=placed+[candidate]
                if not accessible_after(next_state,next_placed):continue
                found=search(index+1,next_state,next_placed)
                if found is not None:slot.status="PLACED";return found
                metrics["backtracks"]+=1
                if metrics["backtracks"]>options.max_backtracks:metrics["searchBudgetExhausted"]=True;break
            return None

        started=time.perf_counter();placements=search(0,copy.deepcopy(shell.scene),[])
        result.timings["solverMs"]=int((time.perf_counter()-started)*1000)
        if placements is None:return None
        working=copy.deepcopy(shell.scene)
        for placed in placements:working.objects.append(placed.placement)
        # Preferred/optional elements degrade locally and never cause backtracking of
        # an already valid required solution.
        for slot in optional:
            if not slot.asset:continue
            intent=self.pipeline.placement_intent(slot,plan,working);result.placement_intents.append(intent.json())
            if intent.preferred_near and intent.preferred_near not in {x.id for x in working.objects}:
                slot.status="DROPPED_OPTIONAL" if slot.priority=="optional" else "DROPPED_PREFERRED"
                drop={"slotId":slot.id,"status":slot.status,"reason":"SEMANTIC_DEPENDENCY_UNAVAILABLE","target":intent.preferred_near}
                result.dropped_optional.append(drop);result.diagnostics.append({"code":"OPTIONAL_DROPPED",**drop});continue
            batch=self.pipeline.solver.resolve_candidates(intent,working,limit=options.candidate_limit,dry_run=True)
            metrics["generatedCandidates"]+=batch.generated;chosen=None
            for candidate in batch.candidates:
                metrics["candidateAttempts"]+=1
                tentative=copy.deepcopy(working);tentative.objects.append(candidate.placement)
                if accessible_after(tentative,placements):chosen=candidate;working=tentative;break
            if chosen is None:
                slot.status="DROPPED_OPTIONAL" if slot.priority=="optional" else "DROPPED_PREFERRED"
                drop={"slotId":slot.id,"status":slot.status,"reason":"NO_VALID_CANDIDATE_OR_ACCESSIBILITY_REGRESSION"}
                result.dropped_optional.append(drop);result.diagnostics.append({"code":"OPTIONAL_DROPPED",**drop})
            else:slot.status="PLACED";placements.append(chosen)
        return placements

    def generate_room(self, request: str, shell: ExistingRoomShell, options: GenerationOptions=GenerationOptions(),
        *, planner_brief: dict[str,Any]|None=None, room_id: str="room_001", slot_namespace: str|None=None) -> GenerationResult:
        generation_id="generation_"+uuid.uuid4().hex[:16];started=self._now_ms()
        result=GenerationResult(generation_id,room_id,GenerationStatus.PLACEMENT_FAILED,GenerationLifecycle.CREATED,
            [{"state":"CREATED","atMs":started}],request)
        self._transition(result,GenerationLifecycle.INSPECTING);inspection=shell.inspect()
        result.scene_fingerprint_before=shell.scene.fingerprint()
        if not inspection.supported:return self._fail(result,GenerationStatus.UNSUPPORTED_ROOM_GEOMETRY,"UNSUPPORTED_ROOM_GEOMETRY",{"diagnostics":list(inspection.diagnostics)})
        self._transition(result,GenerationLifecycle.PLANNING);planner_started=time.perf_counter()
        if planner_brief is None:
            if self.planner_service is None:return self._fail(result,GenerationStatus.PLANNER_FAILED,"PLANNER_NOT_CONFIGURED")
            planned=self.planner_service.plan_room(PlannerInput(request,options.seed))
            result.planner_result=planned.json();result.token_usage=dict(planned.usage);result.timings["llmMs"]=planned.latency_ms
            if planned.status!=PlannerStatus.SUCCESS or planned.validated_output is None:
                return self._fail(result,GenerationStatus.PLANNER_FAILED,planned.status.value,{"diagnostics":planned.diagnostics})
            brief=planned.validated_output
        else:
            try:brief=validate_planner_brief(planner_brief)
            except ValueError as exc:return self._fail(result,GenerationStatus.PLANNER_FAILED,"SCHEMA_VALIDATION_FAILED",{"message":str(exc)})
            if options.seed is not None:brief=copy.deepcopy(brief);brief["seed"]=options.seed
            result.planner_result={"status":"REPLAYED","attemptCount":0,"validatedOutput":brief}
        result.timings.setdefault("llmMs",int((time.perf_counter()-planner_started)*1000));result.planner_brief=copy.deepcopy(brief)
        self._transition(result,GenerationLifecycle.PLANNED)
        try:plan=self.pipeline.create_plan(brief,shell.scene,room_id=room_id,slot_namespace=slot_namespace)
        except (ValueError,KeyError) as exc:return self._fail(result,GenerationStatus.PATTERN_FAILED,"PATTERN_FAILED",{"message":str(exc)})
        result.room_plan=plan.json();pattern_hash=hashlib.sha256(PATTERN_PATH.read_bytes()).hexdigest()
        result.reproducibility={"plannerBrief":copy.deepcopy(brief),"seed":brief["seed"],"patternId":plan.pattern_id,
            "patternVersion":"sha256:"+pattern_hash,"catalogVersion":plan.catalog_version,"solverVersion":self.pipeline.asset_resolver.phase3.get("catalogVersion"),
            "roomShellFingerprint":shell.fingerprint()}
        if options.mode=="plan-only":
            result.status=GenerationStatus.SUCCESS;self._transition(result,GenerationLifecycle.COMPLETE);result.timings["totalMs"]=self._now_ms()-started
            return self._save(result)
        self._transition(result,GenerationLifecycle.RESOLVING)
        feasibility=self.pipeline.feasibility(plan,shell.scene);result.metrics["feasibility"]=feasibility
        if feasibility=="INFEASIBLE":return self._fail(result,GenerationStatus.INFEASIBLE,"PATTERN_INFEASIBLE",{"stage":"preflight"})
        self._transition(result,GenerationLifecycle.PLACING)
        # Try each declared pattern at most once, sharing the original search budget.
        strategies=[plan.strategy]+[s for s in self.pipeline.select_pattern(brief).strategies if s!=plan.strategy]
        deadline=time.perf_counter()+options.search_timeout_ms/1000
        attempts=[];nodes=0;backtracks=0;placements=None
        for strategy in strategies:
            remaining=int((deadline-time.perf_counter())*1000)
            if remaining<1 or nodes>=options.max_search_nodes or backtracks>options.max_backtracks:break
            plan=self.pipeline.create_plan(brief,shell.scene,room_id=room_id,slot_namespace=slot_namespace,strategy=strategy)
            result.placement_intents=[];result.dropped_optional=[];result.resolved_assets=[]
            placements=self._place(plan,shell,replace(options,search_timeout_ms=remaining,
                max_search_nodes=options.max_search_nodes-nodes,max_backtracks=options.max_backtracks-backtracks),result)
            attempt={"strategy":strategy,"status":"SUCCESS" if placements is not None else "INFEASIBLE",
                "searchNodes":result.metrics.get("searchNodes",0),"backtracks":result.metrics.get("backtracks",0)}
            attempts.append(attempt);nodes+=attempt["searchNodes"];backtracks+=attempt["backtracks"]
            if placements is not None:break
        result.metrics.update({"strategyAttempts":attempts,"searchNodes":nodes,"backtracks":backtracks})
        result.reproducibility["selectedStrategy"]=plan.strategy
        result.room_plan=plan.json()
        if placements is None:
            code="SEARCH_BUDGET_EXHAUSTED" if result.metrics.get("searchBudgetExhausted") else "REQUIRED_PLACEMENT_INFEASIBLE"
            return self._fail(result,GenerationStatus.INFEASIBLE,code,{"metrics":result.metrics})
        result.dry_run_placements=[x.json() for x in placements]
        self._transition(result,GenerationLifecycle.VALIDATING);validation,navigation=self._validate_scene(shell.scene,placements)
        result.metrics["navigationResult"]=navigation;result.metrics["numberOfObjects"]=len(placements)
        if validation:return self._fail(result,GenerationStatus.VALIDATION_FAILED,"FINAL_PREFLIGHT_VALIDATION_FAILED",{"diagnostics":validation})
        semantic=self.pipeline.validate_plan(plan)
        errors=[d.json() for d in semantic if d.severity=="ERROR"]
        if errors:return self._fail(result,GenerationStatus.VALIDATION_FAILED,"ROOM_PLAN_VALIDATION_FAILED",{"diagnostics":errors})
        result.semantic_ids=[x.intent.id for x in placements]
        result.placements=[x.json()["placement"] for x in placements]
        owned_ids=[op["arguments"]["semanticId"] for op in shell.materialization_operations]+result.semantic_ids
        result.ownership={"generationId":generation_id,"roomId":room_id,"patternId":plan.pattern_id,"seed":plan.seed,
            "objects":[{"semanticId":sid,"slotId":sid if sid in result.semantic_ids else None} for sid in owned_ids],"cleanupStatus":"NOT_REQUIRED" if options.mode!="live" else "PENDING"}
        if options.mode=="dry-run":
            result.status=GenerationStatus.SUCCESS;result.scene_fingerprint_after=shell.scene.fingerprint()
            self._transition(result,GenerationLifecycle.COMPLETE);result.timings["totalMs"]=self._now_ms()-started
            return self._save(result)
        if self.gateway is None:return self._fail(result,GenerationStatus.APPLY_FAILED,"LIVE_GATEWAY_NOT_CONFIGURED")
        try:
            snapshot=self.gateway.snapshot();result.scene_revision_before=snapshot.revision;result.scene_fingerprint_before=snapshot.fingerprint
            result.transaction={"state":"PREFLIGHT_COMPLETE","revisionBefore":snapshot.revision,
                "sceneFingerprintBefore":snapshot.fingerprint,"sceneStateBefore":snapshot.objects,
                "semanticStateBefore":[row for row in snapshot.objects if row.get("semanticId") in owned_ids],
                "commitBoundary":"single applyPatch","safeStopOnApplyFailure":True}
            operations=copy.deepcopy(shell.materialization_operations)
            for placed in placements:
                op=copy.deepcopy(placed.scene_patch["operations"][0]);op["arguments"]["parentId"]=room_id;operations.append(op)
            self._transition(result,GenerationLifecycle.APPLYING);applied=self.gateway.apply(operations,snapshot.revision)
            result.scene_revision_after=applied["revision"]
            self._transition(result,GenerationLifecycle.READBACK);actual=[row for row in applied["result"] if row["semanticId"] in owned_ids]
            if {row["semanticId"] for row in actual}!=set(owned_ids):raise TransportError("owned semantic IDs differ from apply read-back")
            actual_placements=[]
            intended={x.intent.id:x.intent for x in placements}
            for row in actual:
                if row["semanticId"] not in intended:continue
                obj=ResolvedObject.create(row["semanticId"],self.pipeline.solver.assets[row["class"]],
                    SpatialTransform(tuple(row["position"]),tuple(row["rotation"]),"EDEN").with_space("WORLD"))
                source=next(x for x in placements if x.intent.id==row["semanticId"])
                actual_placements.append(SolverResult("VALID",source.intent,obj,[],[],source.score,[],False,None))
            actual_validation,navigation=self._validate_scene(shell.scene,actual_placements)
            if actual_validation:raise TransportError("actual read-back failed spatial validation: "+json.dumps(actual_validation))
            result.metrics["navigationResult"]=navigation;result.placements=[x.json()["placement"] for x in actual_placements]
            if options.capture:
                self._transition(result,GenerationLifecycle.CAPTURING)
                anchor=next((row for row in actual if row.get("positionASL") and row.get("position")),None)
                dz=anchor["positionASL"][2]-anchor["position"][2] if anchor else 0.0
                floor=next(s for s in shell.scene.surfaces.values() if s.type=="floor");x,y,z=floor.origin
                half=max(floor.half_extents);poses=[
                    {"name":"entrance","positionASL":[x,y-half+0.8,z+dz+1.7],"targetASL":[x,y,z+dz+0.8],"fov":0.8},
                    {"name":"opposite_corner","positionASL":[x+half-0.6,y+half-0.6,z+dz+1.8],"targetASL":[x,y,z+dz+0.7],"fov":0.8},
                    {"name":"overview","positionASL":[x+half+3,y-half-3,z+dz+half+3],"targetASL":[x,y,z+dz+0.6],"fov":0.9}]
                # One view per transport response keeps the duplicate SQF test artifact
                # below FileManager's bounded Read buffer and isolates capture failures.
                result.screenshots=[]
                for pose_index,pose in enumerate(poses):
                    capture=self.gateway.capture(applied["revision"],[{"positionASL":pose["positionASL"],"targetASL":pose["targetASL"],"fov":pose["fov"],
                        "viewId":pose["name"],"cameraRole":pose["name"],"captureClassOverlay":True}])
                    if len(capture["result"])!=1:raise TransportError("capture did not return exactly one view")
                    result.screenshots.append({"generationId":generation_id,"roomId":room_id,"revision":applied["revision"],
                        "cameraPose":pose,"artifact":capture["result"][0]})
                    # Arma may reject an immediately following screenshot command even
                    # after the paired files exist. Keep Eden requests independent and
                    # allow the engine capture pipeline to drain between camera roles.
                    if pose_index+1<len(poses) and capture["result"][0].get("classOverlayPath"):time.sleep(5)
            final=self.gateway.inspect(applied["revision"]);result.scene_fingerprint_after=_fingerprint(final["result"])
            result.transaction["state"]="COMMITTED";result.transaction["revisionCommitted"]=applied["revision"]
            result.status=GenerationStatus.SUCCESS;self._transition(result,GenerationLifecycle.COMPLETE)
            if not options.keep_result:self.cleanup(result)
            result.timings["totalMs"]=self._now_ms()-started;return self._save(result)
        except TransactionApplyError as exc:
            partial=bool({row.get("semanticId") for row in exc.actual}&set(owned_ids))
            return self._fail(result,GenerationStatus.PARTIAL_FAILURE if partial else GenerationStatus.APPLY_FAILED,
                "APPLY_PARTIAL_SAFE_STOP" if partial else "APPLY_FAILED",{"response":exc.response,"automaticReconcile":False})
        except (TransportError,OSError,KeyError,TypeError,ValueError) as exc:
            cleanup="NOT_APPLIED"
            if result.scene_revision_after is not None:
                try:
                    cleaned=self.gateway.cleanup(owned_ids,result.scene_revision_after);result.scene_revision_after=cleaned["revision"]
                    result.scene_fingerprint_after=_fingerprint(cleaned["result"])
                    cleanup="CLEAN" if result.scene_fingerprint_after==result.scene_fingerprint_before else "DIVERGED"
                except Exception as cleanup_exc: cleanup="FAILED: "+str(cleanup_exc)
            result.transaction["failureCleanup"]=cleanup
            partial=result.scene_revision_after is not None and cleanup!="CLEAN"
            return self._fail(result,GenerationStatus.PARTIAL_FAILURE if partial else GenerationStatus.APPLY_FAILED,
                "LIVE_TRANSACTION_FAILED",{"message":str(exc),"failureCleanup":cleanup})

    def regenerate_room(self, previous: GenerationResult, shell: ExistingRoomShell, new_seed: int,
        options: GenerationOptions|None=None) -> GenerationResult:
        if previous.planner_brief is None:raise ValueError("previous result has no saved planner brief")
        chosen=options or GenerationOptions(seed=new_seed)
        chosen=GenerationOptions(chosen.mode,new_seed,chosen.candidate_limit,chosen.max_backtracks,chosen.max_search_nodes,
            chosen.search_timeout_ms,chosen.capture,chosen.keep_result)
        return self.generate_room(previous.original_request,shell,chosen,planner_brief=previous.planner_brief,room_id=previous.room_id)

    def cleanup(self,result: GenerationResult) -> None:
        if self.gateway is None or result.scene_revision_after is None:raise ValueError("live generation has no cleanup context")
        ids=[row["semanticId"] for row in result.ownership.get("objects",[])]
        response=self.gateway.cleanup(ids,result.scene_revision_after);result.scene_revision_after=response["revision"]
        result.scene_fingerprint_after=_fingerprint(response["result"])
        clean=result.scene_fingerprint_before is None or result.scene_fingerprint_after==result.scene_fingerprint_before
        result.ownership["cleanupStatus"]="CLEAN" if clean else "DIVERGED"
        result.transaction["cleanupRevision"]=response["revision"]
        if not clean:raise TransportError("cleanup removed generation-owned objects but did not restore the initial scene fingerprint")
