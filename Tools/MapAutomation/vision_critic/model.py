"""Provider-independent strict Critic contract and local trust boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import copy
import re
from typing import Any

CATEGORIES={"VISUAL_FLOATING_OR_SUNK","VISUAL_CLIPPING","RELATION_MISMATCH","ORIENTATION_AWKWARD",
    "SPACING_AWKWARD","ENTRANCE_VISUALLY_BLOCKED","COMPOSITION_IMBALANCE","EXCESSIVE_EMPTY_SPACE",
    "EXCESSIVE_CROWDING","VISIBILITY_OCCLUSION","LIGHTING_PLACEMENT_AWKWARD","UNRESOLVED"}
SEVERITIES={"high","medium","low","info"}
GOALS={"REPOSITION","REORIENT","REGROUP","MOVE_AWAY","MOVE_NEAR","RETRY_PLACEMENT","DROP_OPTIONAL","REQUEST_RECAPTURE","NO_ACTION"}
FORBIDDEN={"position","positionasl","coordinates","coordinate","rotation","euler","transform","scenepatch","classname","class","sqf","python","shell","code","command"}


class CriticStatus(str,Enum):
    SUCCESS="SUCCESS"; INVALID_OUTPUT="INVALID_STRUCTURED_OUTPUT"; PROVIDER_ERROR="PROVIDER_ERROR"; TIMEOUT="TIMEOUT"; REFUSED="REFUSED"


@dataclass
class ProviderResponse:
    status: CriticStatus
    output: dict[str,Any]|None=None
    raw_output: str|None=None
    diagnostics: list[dict[str,Any]]=field(default_factory=list)
    usage: dict[str,Any]=field(default_factory=dict)
    latency_ms: int=0
    response_id: str|None=None


@dataclass
class CriticResult:
    review_id: str
    status: CriticStatus
    provider: str
    model: str
    prompt_version: str
    schema_version: int
    generation_id: str
    room_id: str
    revision: int
    iteration: int
    validated_output: dict[str,Any]|None
    diagnostics: list[dict[str,Any]]
    usage: dict[str,Any]
    latency_ms: int
    attempts: int
    image_telemetry: list[dict[str,Any]]=field(default_factory=list)
    cached: bool=False
    artifact_path: str|None=None

    def json(self)->dict[str,Any]:
        return {"schemaVersion":self.schema_version,"reviewId":self.review_id,"status":self.status.value,
            "provider":self.provider,"model":self.model,"promptVersion":self.prompt_version,
            "generationId":self.generation_id,"roomId":self.room_id,"revision":self.revision,"iteration":self.iteration,
            "validatedOutput":self.validated_output,"diagnostics":self.diagnostics,"usage":self.usage,
            "latencyMs":self.latency_ms,"attempts":self.attempts,"images":self.image_telemetry,
            "cached":self.cached,"artifactPath":self.artifact_path}


class CriticContractError(ValueError): pass


def _exact(value:dict[str,Any],keys:set[str],path:str)->None:
    if set(value)!=keys: raise CriticContractError(f"{path}: expected keys {sorted(keys)}, got {sorted(value)}")


def _scan(value:Any,path:str="$")->None:
    if isinstance(value,dict):
        for key,child in value.items():
            if key.casefold() in FORBIDDEN: raise CriticContractError(f"{path}.{key}: forbidden field")
            _scan(child,f"{path}.{key}")
    elif isinstance(value,list):
        for index,child in enumerate(value): _scan(child,f"{path}[{index}]")


def validate_critic_output(value:Any,known_semantic_ids:set[str],known_view_ids:set[str])->dict[str,Any]:
    """Validate schema plus grounding/policy invariants without trusting provider strict mode."""
    if not isinstance(value,dict): raise CriticContractError("$: expected object")
    _scan(value);_exact(value,{"schemaVersion","overall","issues","recapture"},"$")
    if type(value["schemaVersion"]) is not int or value["schemaVersion"]!=1: raise CriticContractError("schemaVersion must equal 1")
    if value["overall"] not in {"PASS","REPAIR","RECAPTURE","UNRESOLVED"}: raise CriticContractError("invalid overall")
    issues=value["issues"]
    if not isinstance(issues,list) or len(issues)>12: raise CriticContractError("issues must be array with at most 12 entries")
    issue_ids=set()
    for index,issue in enumerate(issues):
        path=f"issues[{index}]"
        if not isinstance(issue,dict): raise CriticContractError(path+": expected object")
        _exact(issue,{"issueId","category","severity","confidence","grounding","targets","views","observation","evidenceKind","repairGoal"},path)
        iid=issue["issueId"]
        if not isinstance(iid,str) or re.fullmatch(r"visual_[0-9]{3}",iid) is None or iid in issue_ids: raise CriticContractError(path+": invalid/duplicate issueId")
        issue_ids.add(iid)
        if issue["category"] not in CATEGORIES or issue["severity"] not in SEVERITIES: raise CriticContractError(path+": invalid taxonomy")
        if type(issue["confidence"]) not in {int,float} or not 0<=issue["confidence"]<=1: raise CriticContractError(path+": confidence out of range")
        if issue["grounding"] not in {"GROUNDED","UNRESOLVED"}: raise CriticContractError(path+": invalid grounding")
        targets=issue["targets"];views=issue["views"]
        if not isinstance(targets,list) or len(targets)>3 or any(type(x) is not str for x in targets): raise CriticContractError(path+": invalid targets")
        if len(targets)!=len(set(targets)): raise CriticContractError(path+": duplicate targets")
        unknown=set(targets)-known_semantic_ids
        if unknown: raise CriticContractError(path+": unknown semantic targets "+str(sorted(unknown)))
        if issue["grounding"]=="GROUNDED" and not targets: raise CriticContractError(path+": grounded issue needs a target")
        if issue["grounding"]=="UNRESOLVED" and targets: raise CriticContractError(path+": unresolved issue cannot claim targets")
        if not isinstance(views,list) or len(views)!=len(set(views)) or set(views)-known_view_ids: raise CriticContractError(path+": unknown/duplicate view ids")
        if not isinstance(issue["observation"],str) or not issue["observation"].strip() or len(issue["observation"])>500: raise CriticContractError(path+": invalid observation")
        if issue["evidenceKind"]!="VISUAL_OBSERVATION": raise CriticContractError(path+": engine facts are forbidden")
        goal=issue["repairGoal"]
        if not isinstance(goal,dict): raise CriticContractError(path+": repairGoal must be object")
        _exact(goal,{"type","subject","reference"},path+".repairGoal")
        if goal["type"] not in GOALS: raise CriticContractError(path+": invalid repair goal")
        for key in ("subject","reference"):
            if goal[key] is not None and goal[key] not in known_semantic_ids: raise CriticContractError(path+f": unknown {key}")
        if goal["type"] not in {"REQUEST_RECAPTURE","NO_ACTION"} and goal["subject"] is None: raise CriticContractError(path+": actionable goal needs subject")
        if goal["subject"] is not None and goal["subject"] not in targets: raise CriticContractError(path+": subject must be a grounded target")
    rec=value["recapture"]
    if not isinstance(rec,dict): raise CriticContractError("recapture must be object")
    _exact(rec,{"requested","cameraRoles","reason"},"recapture")
    if type(rec["requested"]) is not bool or not isinstance(rec["cameraRoles"],list): raise CriticContractError("invalid recapture")
    if set(rec["cameraRoles"])-{"entrance","opposite_corner","overview"} or len(rec["cameraRoles"])>2: raise CriticContractError("invalid recapture cameraRoles")
    if value["overall"]=="PASS" and any(x["severity"] in {"high","medium"} for x in issues): raise CriticContractError("PASS cannot contain actionable severity")
    return copy.deepcopy(value)
