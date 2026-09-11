"""MapAutomation adapter and transaction boundary for Phase 6."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from transport import FileQueueClient, TransportError


@dataclass(frozen=True)
class SceneSnapshot:
    revision: int
    objects: list[dict[str, Any]]
    fingerprint: str
    session_id: str


def _fingerprint(objects: list[dict[str, Any]]) -> str:
    return hashlib.sha256(json.dumps(objects,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


class MapAutomationRoomGateway:
    """No orchestration policy lives here; it only maps room transactions to Phase 1."""
    def __init__(self, timeout: float=45.0, client: FileQueueClient|None=None):
        self.client=client or FileQueueClient(timeout); self.transcript=[]

    def _send(self, operation: str, revision: int, arguments: dict[str,Any]|None=None) -> dict[str,Any]:
        request,response=self.client.request(operation,revision,arguments);self.transcript.append({"request":request,"response":response})
        return response

    @staticmethod
    def _ok(label: str,response: dict[str,Any]) -> None:
        if response.get("status")!="OK": raise TransportError(f"{label}: {response.get('diagnostics')}")

    def snapshot(self) -> SceneSnapshot:
        caps=self._send("getCapabilities",-1);self._ok("capabilities",caps)
        state=self._send("inspectScene",caps["revision"]);self._ok("inspectScene",state)
        if state.get("stopped"): raise TransportError("gateway is safe-stopped; explicit reconcile is required")
        return SceneSnapshot(state["revision"],state["result"],_fingerprint(state["result"]),caps["sessionId"])

    def apply(self, operations: list[dict[str,Any]], expected_revision: int) -> dict[str,Any]:
        response=self._send("applyPatch",expected_revision,{"operations":operations})
        if response.get("status")!="OK":
            actual=response.get("result",{}).get("actual") if isinstance(response.get("result"),dict) else response.get("result")
            raise TransactionApplyError(response,actual or [])
        return response

    def inspect(self, revision: int) -> dict[str,Any]:
        response=self._send("inspectScene",revision);self._ok("inspectScene",response);return response

    def capture(self, revision: int, views: list[dict[str,Any]]) -> dict[str,Any]:
        response=self._send("captureViews",revision,{"views":views});self._ok("captureViews",response);return response

    def probe_geometry(self, revision: int, classname: str) -> dict[str,Any]:
        response=self._send("probeGeometry",revision,{"classname":classname});self._ok("probeGeometry",response);return response

    def build_probe(self, revision: int) -> dict[str,Any]:
        response=self._send("buildProbe",revision);self._ok("buildProbe",response);return response

    def launch_runtime_probe(self, revision: int) -> dict[str,Any]:
        response=self._send("launchRuntimeProbe",revision);self._ok("launchRuntimeProbe",response);return response

    def cleanup(self, semantic_ids: list[str], expected_revision: int) -> dict[str,Any]:
        state=self.inspect(expected_revision);present={row["semanticId"] for row in state["result"]}
        operations=[{"operation":"delete","arguments":{"semanticId":sid}} for sid in reversed(semantic_ids) if sid in present]
        if not operations: return state
        # The Phase 1 gateway accepts at most 32 operations per patch.  Cleanup
        # must obey the same physical transport limit as creation while keeping
        # the logical transaction revision-monotonic.
        response=state
        for offset in range(0,len(operations),32):
            response=self.apply(operations[offset:offset+32],response["revision"])
        return response


class TransactionApplyError(TransportError):
    def __init__(self,response: dict[str,Any],actual: list[dict[str,Any]]):
        super().__init__(f"applyPatch failed: {response.get('diagnostics')}")
        self.response=response;self.actual=actual
