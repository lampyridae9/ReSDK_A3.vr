"""Deterministic Phase 3 spatial placement layer."""

from .model import (
    AssetProfile, ClearanceVolume, Diagnostic, OBB, PlacementIntent,
    ResolvedObject, SceneState, SpatialTransform, SupportSurface,
)
from .solver import CandidateBatch, PlacementSolver, SolverResult, load_phase3_assets

__all__ = [
    "AssetProfile", "ClearanceVolume", "Diagnostic", "OBB", "PlacementIntent",
    "CandidateBatch", "PlacementSolver", "ResolvedObject", "SceneState", "SolverResult",
    "SpatialTransform", "SupportSurface", "load_phase3_assets",
]
