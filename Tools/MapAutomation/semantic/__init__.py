"""Phase 4 room semantics public API."""

from .model import (
    Cardinality, Requirement, RoomPattern, RoomPlan, SemanticDiagnostic,
    SemanticRelation, SemanticSlot,
)
from .pipeline import (
    AssetResolver, PatternFeasibility, PatternPipeline, PatternValidator,
    PlannerContractError, build_room_context, load_patterns, validate_planner_brief,
)

__all__ = [
    "AssetResolver", "Cardinality", "PatternFeasibility", "PatternPipeline",
    "PatternValidator", "PlannerContractError",
    "Requirement", "RoomPattern", "RoomPlan", "SemanticDiagnostic",
    "SemanticRelation", "SemanticSlot", "build_room_context", "load_patterns",
    "validate_planner_brief",
]
