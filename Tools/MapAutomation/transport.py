"""Client for the MapAutomation data-only JSON file queue."""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUESTS = ROOT / "Tools/MapAutomation/queue/requests"
RESPONSES = ROOT / "Tools/MapAutomation/queue/responses"


class TransportError(RuntimeError):
    pass


class FileQueueClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.session_id = ""
        REQUESTS.mkdir(parents=True, exist_ok=True)
        RESPONSES.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def new_request_id(label: str) -> str:
        return f"{label}_{uuid.uuid4().hex}"

    def envelope(
        self,
        operation: str,
        expected_revision: int,
        arguments: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "protocolVersion": 1,
            "requestId": request_id or self.new_request_id(operation),
            "sessionId": self.session_id,
            "expectedRevision": expected_revision,
            "operation": operation,
            "arguments": arguments or {},
        }

    def deliver(self, request: dict[str, Any], *, force_redelivery: bool = False) -> dict[str, Any]:
        request_id = request["requestId"]
        request_path = REQUESTS / f"{request_id}.json"
        response_path = RESPONSES / f"{request_id}.json"
        if force_redelivery and response_path.exists():
            response_path.unlink()
        elif response_path.exists():
            raise TransportError(f"Response already exists for new delivery: {response_path}")
        raw = json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        temporary = request_path.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(raw, encoding="utf-8", newline="\n")
        os.replace(temporary, request_path)
        deadline = time.monotonic() + self.timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if response_path.exists():
                try:
                    response = json.loads(response_path.read_text(encoding="utf-8-sig"))
                    self._validate_response(request_id, response)
                    if request["operation"] == "getCapabilities" and response["status"] == "OK":
                        self.session_id = response["sessionId"]
                    return response
                except (OSError, json.JSONDecodeError, TransportError) as exc:
                    last_error = exc
            time.sleep(0.1)
        raise TransportError(
            f"Timed out waiting for {response_path}. Is AI_AutomationProbe open and READY in Eden?"
            + (f" Last read error: {last_error}" if last_error else "")
        )

    @staticmethod
    def _validate_response(request_id: str, response: Any) -> None:
        if not isinstance(response, dict):
            raise TransportError("Response must be a JSON object")
        required = {"requestId", "status", "revision", "result", "diagnostics"}
        missing = required - response.keys()
        if missing:
            raise TransportError(f"Response misses fields: {sorted(missing)}")
        if response["requestId"] != request_id:
            raise TransportError("Response requestId mismatch")
        if response["status"] not in {"OK", "FAIL"}:
            raise TransportError(f"Unexpected response status: {response['status']!r}")

    def request(
        self,
        operation: str,
        expected_revision: int,
        arguments: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        envelope = self.envelope(operation, expected_revision, arguments, request_id)
        return envelope, self.deliver(envelope)

