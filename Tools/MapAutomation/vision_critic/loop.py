"""Policy-only bounded repair state machine; capture/critic/apply calls stay independent."""
from __future__ import annotations

from dataclasses import dataclass,field
from enum import Enum
from typing import Any,Callable

from .model import CriticResult,CriticStatus
from .repair import RepairPlanner,RepairStatus,issue_fingerprint


class StopReason(str,Enum):
    PASS="PASS"; MAX_ITERATIONS="MAX_ITERATIONS"; NO_PROGRESS="NO_PROGRESS"; REPAIR_INFEASIBLE="REPAIR_INFEASIBLE"
    REGRESSION="REGRESSION"; LOW_CONFIDENCE="LOW_CONFIDENCE"; CRITIC_FAILED="CRITIC_FAILED"; REVIEW_ONLY="REVIEW_ONLY"


@dataclass
class LoopResult:
    stop_reason:StopReason; iterations:list[dict[str,Any]]=field(default_factory=list); repairs_applied:int=0
    def json(self)->dict[str,Any]:return {"stopReason":self.stop_reason.value,"repairsApplied":self.repairs_applied,"iterations":self.iterations}


class BoundedRepairLoop:
    SEVERITY={"info":0,"low":1,"medium":2,"high":3}
    def __init__(self,repair_planner:RepairPlanner,*,max_repairs:int=2,min_severity:str="medium",min_confidence:float=.75):
        if not 0<=max_repairs<=3:raise ValueError("max_repairs must be 0..3")
        if min_severity not in self.SEVERITY or not 0<=min_confidence<=1:raise ValueError("invalid repair threshold")
        self.repair_planner=repair_planner;self.max_repairs=max_repairs;self.min_severity=min_severity;self.min_confidence=min_confidence

    def run(self,*,review:Callable[[int,dict[str,Any]|None],CriticResult],generation:dict[str,Any],shell,apply:Callable[[list[dict[str,Any]]],dict[str,Any]]|None=None)->LoopResult:
        history={};rows=[];repairs=0;previous=None
        for iteration in range(self.max_repairs+1):
            result=review(iteration,previous);entry={"iteration":iteration,"critic":result.json()}
            if result.status!=CriticStatus.SUCCESS or result.validated_output is None:rows.append(entry);return LoopResult(StopReason.CRITIC_FAILED,rows,repairs)
            output=result.validated_output
            actionable=[x for x in output["issues"] if self.SEVERITY[x["severity"]]>=self.SEVERITY[self.min_severity] and x["confidence"]>=self.min_confidence and x["grounding"]=="GROUNDED"]
            if not actionable:
                rows.append(entry);return LoopResult(StopReason.PASS if output["overall"]=="PASS" else StopReason.LOW_CONFIDENCE,rows,repairs)
            issue=actionable[0];fp=issue_fingerprint(issue);history[fp]=history.get(fp,0)+1
            if history[fp]>=2:entry["issueFingerprint"]=fp;rows.append(entry);return LoopResult(StopReason.NO_PROGRESS,rows,repairs)
            if iteration>=self.max_repairs:rows.append(entry);return LoopResult(StopReason.MAX_ITERATIONS,rows,repairs)
            proposal=self.repair_planner.plan(issue,generation,shell);entry["proposal"]=proposal.json();rows.append(entry)
            if proposal.status!=RepairStatus.READY:return LoopResult(StopReason.REPAIR_INFEASIBLE,rows,repairs)
            if apply is None:return LoopResult(StopReason.REVIEW_ONLY,rows,repairs)
            applied=apply(proposal.operations);entry["applyResult"]=applied
            if applied.get("hardSpatialPass") is not True:return LoopResult(StopReason.REGRESSION,rows,repairs)
            if proposal.intent:
                intents=generation.get("placementIntents",[]);intents[:]=[x for x in intents if x.get("id")!=proposal.intent["id"]];intents.append(proposal.intent)
            repairs+=1;previous=issue
        return LoopResult(StopReason.MAX_ITERATIONS,rows,repairs)
