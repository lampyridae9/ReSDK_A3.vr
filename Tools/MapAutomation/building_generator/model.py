"""Phase 8 contracts. Geometry is explicit only after BuildingBrief expansion."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any


class BuildingStatus(str, Enum):
    SUCCESS="SUCCESS"
    INFEASIBLE="INFEASIBLE"
    PLANNER_FAILED="PLANNER_FAILED"
    LAYOUT_FAILED="LAYOUT_FAILED"
    ROOM_GENERATION_FAILED="ROOM_GENERATION_FAILED"
    VALIDATION_FAILED="VALIDATION_FAILED"
    APPLY_FAILED="APPLY_FAILED"
    PARTIAL_FAILURE="PARTIAL_FAILURE"


@dataclass(frozen=True)
class BuildingFootprint:
    origin: tuple[float,float,float]
    width: float
    depth: float
    max_floors: int=2

    def __post_init__(self) -> None:
        if self.width<=0 or self.depth<=0: raise ValueError("footprint dimensions must be positive")
        if not 1<=self.max_floors<=8: raise ValueError("max_floors must be 1..8")

    def json(self) -> dict[str,Any]:
        return {"origin":list(self.origin),"width":self.width,"depth":self.depth,"maxFloors":self.max_floors}


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    depth: float

    @property
    def x2(self)->float:return self.x+self.width
    @property
    def y2(self)->float:return self.y+self.depth
    @property
    def area(self)->float:return self.width*self.depth
    @property
    def center(self)->tuple[float,float]:return (self.x+self.width/2,self.y+self.depth/2)
    def contains(self,x:float,y:float,tolerance:float=1e-6)->bool:
        return self.x-tolerance<=x<=self.x2+tolerance and self.y-tolerance<=y<=self.y2+tolerance
    def json(self)->dict[str,float]:return {"x":self.x,"y":self.y,"width":self.width,"depth":self.depth}


@dataclass(frozen=True)
class SpacePlan:
    id: str
    kind: str
    floor_id: str
    required: bool
    capacity: int
    rect: Rect

    def json(self)->dict[str,Any]:
        return {"id":self.id,"kind":self.kind,"floorId":self.floor_id,"required":self.required,
            "capacity":self.capacity,"rect":self.rect.json()}


@dataclass(frozen=True)
class WallSegment:
    id: str
    floor_id: str
    start: tuple[float,float]
    end: tuple[float,float]
    owners: tuple[str,...]
    exterior: bool

    @property
    def length(self)->float:return abs(self.end[0]-self.start[0])+abs(self.end[1]-self.start[1])
    def json(self)->dict[str,Any]:
        return {"id":self.id,"floorId":self.floor_id,"start":list(self.start),"end":list(self.end),
            "owners":list(self.owners),"exterior":self.exterior,"length":self.length}


@dataclass(frozen=True)
class PortalPlan:
    id: str
    floor_id: str
    from_space: str
    to_space: str
    wall_segment: str
    center: tuple[float,float]
    width: float
    door_asset: str
    exterior: bool=False

    def json(self)->dict[str,Any]:
        return {"portalId":self.id,"floorId":self.floor_id,"fromSpace":self.from_space,"toSpace":self.to_space,
            "wallSegment":self.wall_segment,"opening":{"center":list(self.center),"width":self.width},
            "doorAsset":self.door_asset,"exterior":self.exterior}


@dataclass(frozen=True)
class VerticalConnectionPlan:
    id: str
    type: str
    from_floor: str
    to_floor: str
    occupied_region: Rect
    entry_region_lower: Rect
    entry_region_upper: Rect
    asset: str
    clearance: float
    yaw: float=0
    model_origin_z_offset: float=0
    verification: str="APPROXIMATE"
    opening_region: Rect|None=None

    def json(self)->dict[str,Any]:
        return {"id":self.id,"type":self.type,"fromFloor":self.from_floor,"toFloor":self.to_floor,
            "occupiedRegion":self.occupied_region.json(),
            "entryRegionLower":self.entry_region_lower.json(),"entryRegionUpper":self.entry_region_upper.json(),
            "asset":self.asset,"clearance":self.clearance,"yaw":self.yaw,
            "modelOriginZOffset":self.model_origin_z_offset,"verification":self.verification,
            "floorOpening":self.opening_region.json() if self.opening_region else None}


@dataclass
class FloorPlan:
    id: str
    index: int
    elevation: float
    footprint: Rect
    spaces: list[SpacePlan]
    walls: list[WallSegment]
    portals: list[PortalPlan]
    vertical_connections: list[VerticalConnectionPlan]=field(default_factory=list)

    def json(self)->dict[str,Any]:
        return {"floorId":self.id,"index":self.index,"elevation":self.elevation,"footprint":self.footprint.json(),
            "spaces":[x.json() for x in self.spaces],"walls":[x.json() for x in self.walls],
            "portals":[x.json() for x in self.portals],"verticalConnections":[x.json() for x in self.vertical_connections]}


@dataclass
class BuildingGraph:
    nodes: list[dict[str,Any]]=field(default_factory=list)
    edges: list[dict[str,Any]]=field(default_factory=list)

    def add_node(self,id:str,type:str,**data:Any)->None:self.nodes.append({"id":id,"type":type,**data})
    def add_edge(self,source:str,target:str,type:str,**data:Any)->None:self.edges.append({"source":source,"target":target,"type":type,**data})
    def json(self)->dict[str,Any]:return {"nodes":self.nodes,"edges":self.edges}


@dataclass
class BuildingPlan:
    id: str
    building_type: str
    styles: tuple[str,...]
    seed: int
    storey_height: float
    room_slots: list[dict[str,Any]]
    graph: BuildingGraph
    versions: dict[str,str]

    def json(self)->dict[str,Any]:
        return {"schemaVersion":1,"buildingId":self.id,"buildingType":self.building_type,"style":list(self.styles),
            "seed":self.seed,"storeyHeight":self.storey_height,"roomSlots":self.room_slots,"graph":self.graph.json(),
            "versions":self.versions}


@dataclass
class BuildingLayout:
    building_id: str
    footprint: BuildingFootprint
    floors: list[FloorPlan]
    graph: BuildingGraph
    candidate: dict[str,Any]
    feasibility: str
    diagnostics: list[dict[str,Any]]=field(default_factory=list)

    def json(self)->dict[str,Any]:
        return {"schemaVersion":1,"buildingId":self.building_id,"footprint":self.footprint.json(),
            "floors":[x.json() for x in self.floors],"graph":self.graph.json(),"candidate":self.candidate,
            "feasibility":self.feasibility,"diagnostics":self.diagnostics}

    def fingerprint(self)->str:
        return hashlib.sha256(json.dumps(self.json(),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class BuildingOptions:
    mode: str="dry-run"
    seed: int|None=None
    shell_only: bool=False
    capture: bool=True
    keep_result: bool=False
    max_layout_candidates: int=4
    max_partition_attempts: int=4
    time_budget_ms: int=1000

    def __post_init__(self)->None:
        if self.mode not in {"plan-only","layout-only","dry-run","live"}:raise ValueError("invalid building mode")
        if self.seed is not None and not 0<=self.seed<=2147483647:raise ValueError("seed out of range")
        if not 1<=self.max_layout_candidates<=16 or not 1<=self.max_partition_attempts<=16 or self.time_budget_ms<1:
            raise ValueError("invalid layout search budget")


@dataclass
class BuildingResult:
    generation_id: str
    status: BuildingStatus
    request: str
    building_brief: dict[str,Any]|None=None
    building_plan: dict[str,Any]|None=None
    building_layout: dict[str,Any]|None=None
    room_generations: list[dict[str,Any]]=field(default_factory=list)
    shell_operations: list[dict[str,Any]]=field(default_factory=list)
    diagnostics: list[dict[str,Any]]=field(default_factory=list)
    budget: dict[str,Any]=field(default_factory=dict)
    metrics: dict[str,Any]=field(default_factory=dict)
    ownership: dict[str,Any]=field(default_factory=dict)
    transaction: dict[str,Any]=field(default_factory=dict)
    screenshots: list[dict[str,Any]]=field(default_factory=list)
    reproducibility: dict[str,Any]=field(default_factory=dict)
    artifact_path: str|None=None
    structural_plan: dict[str,Any]|None=None
    shell_validation: dict[str,Any]=field(default_factory=dict)

    def json(self)->dict[str,Any]:
        return {"schemaVersion":2,"generationId":self.generation_id,"status":self.status.value,"request":self.request,
            "buildingBrief":self.building_brief,"buildingPlan":self.building_plan,"buildingLayout":self.building_layout,
            "roomGenerations":self.room_generations,"shellOperations":self.shell_operations,"diagnostics":self.diagnostics,
            "buildingBudgetReport":self.budget,"metrics":self.metrics,"ownership":self.ownership,
            "transaction":self.transaction,"screenshots":self.screenshots,"reproducibility":self.reproducibility,
            "artifactPath":self.artifact_path,"structuralPlan":self.structural_plan,"shellValidation":self.shell_validation}
