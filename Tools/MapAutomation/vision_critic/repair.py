"""Bounded semantic goals translated back into Phase 3 deterministic placement."""
from __future__ import annotations

import copy
from dataclasses import dataclass,field
from enum import Enum
import math
from typing import Any

from semantic.model import RoomPlan,SemanticRelation,SemanticSlot
from spatial.model import PlacementIntent,ResolvedObject,SceneState,SpatialTransform


class RepairStatus(str,Enum):
    READY="READY"; NO_ACTION="NO_ACTION"; REPAIR_INFEASIBLE="REPAIR_INFEASIBLE"; REJECTED="REJECTED"


@dataclass
class RepairProposal:
    status:RepairStatus; issue_fingerprint:str; goal:dict[str,Any]; intent:dict[str,Any]|None=None
    operations:list[dict[str,Any]]=field(default_factory=list); diagnostics:list[dict[str,Any]]=field(default_factory=list)

    def json(self)->dict[str,Any]:
        return {"status":self.status.value,"issueFingerprint":self.issue_fingerprint,"goal":self.goal,
            "placementIntent":self.intent,"operations":self.operations,"diagnostics":self.diagnostics}


def issue_fingerprint(issue:dict[str,Any])->str:
    goal=issue.get("repairGoal",{})
    return "|".join([str(issue.get("category")),",".join(sorted(issue.get("targets",[]))),str(goal.get("type")),str(goal.get("reference"))])


class RepairPlanner:
    """Never consumes free prose: only a locally validated issue and existing generation state."""
    def __init__(self,pipeline): self.pipeline=pipeline

    @staticmethod
    def _slot(room_plan:dict[str,Any],sid:str)->dict[str,Any]|None:
        return next((x for x in room_plan.get("slots",[]) if x.get("id")==sid),None)

    def _scene(self,shell:SceneState,generation:dict[str,Any],exclude:str)->SceneState:
        scene=copy.deepcopy(shell);assets=self.pipeline.solver.assets
        for row in generation.get("placements",[]):
            if row.get("id")==exclude or row.get("asset") not in assets: continue
            t=row.get("transform",{});scene.objects.append(ResolvedObject.create(row["id"],assets[row["asset"]],
                SpatialTransform(tuple(t["position"]),tuple(t["rotation"]),"EDEN").with_space("WORLD")))
        return scene

    def plan(self,issue:dict[str,Any],generation:dict[str,Any],shell:SceneState)->RepairProposal:
        fp=issue_fingerprint(issue);goal=copy.deepcopy(issue["repairGoal"]);kind=goal["type"];subject=goal["subject"];reference=goal["reference"]
        if kind in {"NO_ACTION","REQUEST_RECAPTURE"}: return RepairProposal(RepairStatus.NO_ACTION,fp,goal)
        slot=self._slot(generation.get("roomPlan") or {},subject)
        if slot is None:return RepairProposal(RepairStatus.REJECTED,fp,goal,diagnostics=[{"code":"UNKNOWN_SUBJECT"}])
        if kind=="DROP_OPTIONAL":
            if slot.get("priority")!="optional": return RepairProposal(RepairStatus.REJECTED,fp,goal,diagnostics=[{"code":"REQUIRED_SEMANTICS_PROTECTED","priority":slot.get("priority")}])
            return RepairProposal(RepairStatus.READY,fp,goal,operations=[{"operation":"delete","arguments":{"semanticId":subject}}])
        previous=next((x for x in generation.get("placementIntents",[]) if x.get("id")==subject),None)
        placement=next((x for x in generation.get("placements",[]) if x.get("id")==subject),None)
        if previous is None or placement is None:return RepairProposal(RepairStatus.REJECTED,fp,goal,diagnostics=[{"code":"MISSING_GENERATION_STATE"}])
        intent=PlacementIntent.from_json(previous);soft=list(intent.soft);facing=intent.facing_direction;near=intent.preferred_near
        if kind in {"REGROUP","MOVE_NEAR"}:
            if not reference:return RepairProposal(RepairStatus.REJECTED,fp,goal,diagnostics=[{"code":"REFERENCE_REQUIRED"}])
            near=reference
            if "Compact" not in soft:soft.append("Compact")
        elif kind=="MOVE_AWAY":
            near=None
            soft=[x for x in soft if x!="Compact"]
            if "MaximizeCirculation" not in soft:soft.append("MaximizeCirculation")
        elif kind=="REORIENT" and reference:
            ref=next((x for x in generation.get("placements",[]) if x.get("id")==reference),None)
            if ref:
                a=placement["transform"]["position"];b=ref["transform"]["position"];dx,dy=b[0]-a[0],b[1]-a[1]
                if math.hypot(dx,dy)>1e-6:facing=(dx,dy)
        intent=PlacementIntent(intent.id,intent.asset,intent.region,intent.on_surface,intent.against_wall,intent.hard,tuple(soft),intent.reachable,facing,intent.seed+7919,near)
        scene=self._scene(shell,generation,subject)
        try: solved=self.pipeline.solver.resolve(intent,scene,dry_run=True)
        except (ValueError,KeyError) as exc:return RepairProposal(RepairStatus.REPAIR_INFEASIBLE,fp,goal,intent.json(),diagnostics=[{"code":"SOLVER_REJECTED","message":str(exc)}])
        if solved.status!="VALID" or solved.placement is None:
            return RepairProposal(RepairStatus.REPAIR_INFEASIBLE,fp,goal,intent.json(),diagnostics=[x.json() for x in solved.diagnostics])
        op={"operation":"setTransform","arguments":{"semanticId":subject,**solved.placement.transform.gateway()}}
        return RepairProposal(RepairStatus.READY,fp,goal,intent.json(),[op],[{"code":"PHASE3_DRY_RUN_PASS","authority":"ENGINE_SOLVER_FACT"}])
