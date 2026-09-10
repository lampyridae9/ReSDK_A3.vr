"""Strict Phase 6 result, lifecycle, options, and existing-shell contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any

from spatial.model import SceneState


class GenerationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INFEASIBLE = "INFEASIBLE"
    PLANNER_FAILED = "PLANNER_FAILED"
    PATTERN_FAILED = "PATTERN_FAILED"
    PLACEMENT_FAILED = "PLACEMENT_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    APPLY_FAILED = "APPLY_FAILED"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"
    UNSUPPORTED_ROOM_GEOMETRY = "UNSUPPORTED_ROOM_GEOMETRY"


class GenerationLifecycle(str, Enum):
    CREATED = "CREATED"
    INSPECTING = "INSPECTING"
    PLANNING = "PLANNING"
    PLANNED = "PLANNED"
    RESOLVING = "RESOLVING"
    PLACING = "PLACING"
    VALIDATING = "VALIDATING"
    APPLYING = "APPLYING"
    READBACK = "READBACK"
    CAPTURING = "CAPTURING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ShellInspection:
    supported: bool
    diagnostics: tuple[dict[str, Any], ...]


@dataclass
class ExistingRoomShell:
    """An inspected, externally supplied upright rectangular room shell.

    ``materialization_operations`` is only for the isolated probe fixture: production
    callers normally pass a shell that already exists in Eden.
    """
    id: str
    scene: SceneState
    materialization_operations: list[dict[str, Any]] = field(default_factory=list)
    requires_ceiling: bool = True

    def fingerprint(self) -> str:
        payload={"id":self.id,"scene":self.scene.fingerprint(),"requiresCeiling":self.requires_ceiling,
            "materialization":self.materialization_operations}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=list).encode()).hexdigest()

    def inspect(self) -> ShellInspection:
        diagnostics=[]; polygon=self.scene.region_polygon
        floors=[s for s in self.scene.surfaces.values() if s.type=="floor"]
        walls=[s for s in self.scene.surfaces.values() if s.type=="wall"]
        ceilings=[s for s in self.scene.surfaces.values() if s.type=="ceiling"]
        if not floors: diagnostics.append({"code":"MISSING_FLOOR"})
        if len(polygon)!=4 or len(set(polygon))!=4: diagnostics.append({"code":"NON_RECTANGULAR_REGION","vertices":len(polygon)})
        else:
            edges=[(polygon[(i+1)%4][0]-polygon[i][0],polygon[(i+1)%4][1]-polygon[i][1]) for i in range(4)]
            if any(abs(edges[i][0]*edges[(i+1)%4][0]+edges[i][1]*edges[(i+1)%4][1])>1e-5 for i in range(4)):
                diagnostics.append({"code":"NON_ORTHOGONAL_REGION"})
        if self.scene.entrance is None: diagnostics.append({"code":"MISSING_ENTRANCE"})
        if len(walls)<2: diagnostics.append({"code":"MISSING_WALLS","actual":len(walls),"minimum":2})
        if self.requires_ceiling and not ceilings: diagnostics.append({"code":"MISSING_CEILING"})
        for surface in floors+ceilings:
            if abs(abs(surface.normal[2])-1)>1e-6: diagnostics.append({"code":"UNSUPPORTED_SURFACE_ORIENTATION","surface":surface.id})
        for wall in walls:
            if abs(wall.normal[2])>1e-6: diagnostics.append({"code":"UNSUPPORTED_WALL_ORIENTATION","surface":wall.id})
        return ShellInspection(not diagnostics,tuple(diagnostics))


@dataclass(frozen=True)
class GenerationOptions:
    mode: str = "dry-run"
    seed: int | None = None
    candidate_limit: int = 4
    max_backtracks: int = 32
    max_search_nodes: int = 128
    search_timeout_ms: int = 5000
    capture: bool = True
    keep_result: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"plan-only","dry-run","live"}: raise ValueError("mode must be plan-only, dry-run, or live")
        if self.seed is not None and not 0<=self.seed<=2147483647: raise ValueError("seed out of range")
        if not 1<=self.candidate_limit<=16: raise ValueError("candidate_limit must be 1..16")
        if self.max_backtracks<0 or self.max_search_nodes<1 or self.search_timeout_ms<1: raise ValueError("invalid search budget")


@dataclass
class GenerationResult:
    generation_id: str
    room_id: str
    status: GenerationStatus
    lifecycle: GenerationLifecycle
    lifecycle_history: list[dict[str, Any]]
    original_request: str
    planner_result: dict[str, Any] | None = None
    planner_brief: dict[str, Any] | None = None
    room_plan: dict[str, Any] | None = None
    resolved_assets: list[dict[str, Any]] = field(default_factory=list)
    placement_intents: list[dict[str, Any]] = field(default_factory=list)
    dry_run_placements: list[dict[str, Any]] = field(default_factory=list)
    placements: list[dict[str, Any]] = field(default_factory=list)
    dropped_optional: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    scene_revision_before: int | None = None
    scene_revision_after: int | None = None
    scene_fingerprint_before: str | None = None
    scene_fingerprint_after: str | None = None
    semantic_ids: list[str] = field(default_factory=list)
    screenshots: list[dict[str, Any]] = field(default_factory=list)
    timings: dict[str, int] = field(default_factory=dict)
    token_usage: dict[str, Any] = field(default_factory=dict)
    reproducibility: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    ownership: dict[str, Any] = field(default_factory=dict)
    transaction: dict[str, Any] = field(default_factory=dict)
    artifact_path: str | None = None

    def json(self) -> dict[str, Any]:
        return {"schemaVersion":1,"generationId":self.generation_id,"roomId":self.room_id,
            "status":self.status.value,"lifecycle":self.lifecycle.value,"lifecycleHistory":self.lifecycle_history,
            "originalRequest":self.original_request,"plannerResult":self.planner_result,"plannerBrief":self.planner_brief,
            "roomPlan":self.room_plan,"resolvedAssets":self.resolved_assets,"placementIntents":self.placement_intents,
            "dryRunPlacements":self.dry_run_placements,"placements":self.placements,
            "droppedOptional":self.dropped_optional,"diagnostics":self.diagnostics,
            "sceneRevisionBefore":self.scene_revision_before,"sceneRevisionAfter":self.scene_revision_after,
            "sceneFingerprintBefore":self.scene_fingerprint_before,"sceneFingerprintAfter":self.scene_fingerprint_after,
            "semanticIds":self.semantic_ids,"screenshots":self.screenshots,"timings":self.timings,
            "tokenUsage":self.token_usage,"reproducibility":self.reproducibility,"metrics":self.metrics,
            "ownership":self.ownership,"transaction":self.transaction,"artifactPath":self.artifact_path}
