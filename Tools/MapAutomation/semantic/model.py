"""World-coordinate-free types for Phase 4 room semantics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FUNCTIONAL_ROLES = {
    "entrance", "sleeping", "storage", "lighting", "work_surface", "seating", "circulation"
}
PRIORITIES = {"required", "preferred", "optional"}
RELATIONS = {"againstWall", "near", "awayFrom", "groupedWith", "accessibleFrom", "mustNotBlock", "faces"}
STYLES = {"poor", "utilitarian", "neutral"}


@dataclass(frozen=True)
class Cardinality:
    minimum: int
    preferred: int
    maximum: int

    def __post_init__(self) -> None:
        if not 0 <= self.minimum <= self.preferred <= self.maximum:
            raise ValueError("cardinality must satisfy 0 <= min <= preferred <= max")


@dataclass(frozen=True)
class Requirement:
    function: str
    priority: str
    cardinality: Cardinality

    def __post_init__(self) -> None:
        if self.function not in FUNCTIONAL_ROLES: raise ValueError("unknown functional role: "+self.function)
        if self.priority not in PRIORITIES: raise ValueError("unknown priority: "+self.priority)
        if self.priority == "required" and self.cardinality.minimum < 1:
            raise ValueError("required function must have min >= 1")


@dataclass(frozen=True)
class SemanticRelation:
    kind: str
    target: str
    hard: bool = False

    def __post_init__(self) -> None:
        if self.kind not in RELATIONS: raise ValueError("unknown semantic relation: "+self.kind)
        if not self.target: raise ValueError("semantic relation target is empty")


@dataclass(frozen=True)
class RoomPattern:
    id: str
    room_type: str
    styles: tuple[str, ...]
    people: Cardinality
    requirements: tuple[Requirement, ...]
    strategies: tuple[str, ...]
    relations: dict[str, tuple[SemanticRelation, ...]]
    provenance: dict[str, Any]


@dataclass
class SemanticSlot:
    id: str
    function: str
    priority: str
    index: int
    placement: str
    relations: tuple[SemanticRelation, ...]
    style: tuple[str, ...]
    asset: str | None = None
    status: str = "PLANNED"

    def json(self) -> dict[str, Any]:
        return {"id": self.id, "function": self.function, "priority": self.priority,
            "index": self.index, "placement": self.placement, "style": list(self.style),
            "relations": [{"kind": r.kind, "target": r.target, "hard": r.hard} for r in self.relations],
            "asset": self.asset, "status": self.status}


@dataclass(frozen=True)
class SemanticDiagnostic:
    code: str
    subjects: tuple[str, ...]
    severity: str
    details: dict[str, Any]
    repair_hint: str | None = None

    def json(self) -> dict[str, Any]:
        return {"code": self.code, "subjects": list(self.subjects), "severity": self.severity,
            "details": self.details, "repairHint": self.repair_hint}


@dataclass
class RoomPlan:
    id: str
    pattern_id: str
    room_type: str
    styles: tuple[str, ...]
    capacity: int
    seed: int
    catalog_version: str
    region: str
    entrance: str
    surfaces: tuple[str, ...]
    strategy: str
    slots: list[SemanticSlot]
    diagnostics: list[SemanticDiagnostic] = field(default_factory=list)

    def json(self) -> dict[str, Any]:
        return {"schemaVersion": 1, "id": self.id, "pattern": self.pattern_id,
            "roomType": self.room_type, "style": list(self.styles), "capacity": {"people": self.capacity},
            "seed": self.seed, "catalogVersion": self.catalog_version, "region": self.region,
            "entrance": self.entrance, "surfaces": list(self.surfaces), "strategy": self.strategy,
            "slots": [s.json() for s in self.slots], "diagnostics": [d.json() for d in self.diagnostics]}
