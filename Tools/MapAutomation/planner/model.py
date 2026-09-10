"""Small provider-independent result model for the Phase 5 planner."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlannerStatus(str, Enum):
    SUCCESS = "SUCCESS"
    INVALID_OUTPUT = "INVALID_STRUCTURED_OUTPUT"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    SEMANTIC_VALIDATION_FAILED = "SEMANTIC_VALIDATION_FAILED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    TIMEOUT = "TIMEOUT"
    REFUSED = "REFUSED"
    UNSUPPORTED_REQUEST = "UNSUPPORTED_REQUEST"
    PATTERN_INFEASIBLE = "PATTERN_INFEASIBLE"
    SPATIAL_FAILURE = "SPATIAL_FAILURE"


@dataclass(frozen=True)
class PlannerInput:
    user_prompt: str
    seed: int | None = None
    room_context: str | None = None

    def __post_init__(self) -> None:
        if not self.user_prompt.strip(): raise ValueError("user prompt is empty")
        if len(self.user_prompt) > 8000: raise ValueError("user prompt exceeds 8000 characters")
        if self.seed is not None and not 0 <= self.seed <= 2147483647: raise ValueError("seed out of range")


@dataclass
class ProviderResponse:
    status: PlannerStatus
    output: dict[str, Any] | None = None
    raw_output: str | None = None
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    latency_ms: int = 0
    response_id: str | None = None


@dataclass
class PlannerResult:
    request_id: str
    status: PlannerStatus
    provider: str
    model: str
    prompt_version: str
    schema_version: int
    planner_input: PlannerInput
    validated_output: dict[str, Any] | None
    attempt_count: int
    diagnostics: list[dict[str, Any]]
    usage: dict[str, Any]
    latency_ms: int
    cached: bool = False
    artifact_path: str | None = None

    def json(self) -> dict[str, Any]:
        return {
            "requestId": self.request_id, "status": self.status.value, "provider": self.provider,
            "model": self.model, "promptVersion": self.prompt_version, "schemaVersion": self.schema_version,
            "input": {"userPrompt": self.planner_input.user_prompt, "seed": self.planner_input.seed,
                "roomContext": self.planner_input.room_context},
            "validatedOutput": self.validated_output, "attemptCount": self.attempt_count,
            "diagnostics": self.diagnostics, "usage": self.usage, "latencyMs": self.latency_ms,
            "cached": self.cached, "artifactPath": self.artifact_path,
        }
