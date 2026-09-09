"""Run the Phase 1 external Python -> Eden -> Python acceptance test."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from transport import FileQueueClient, ROOT, TransportError


def require_ok(step: str, response: dict[str, Any]) -> None:
    if response["status"] != "OK":
        raise TransportError(f"{step} failed: {response['diagnostics']}")


def find_object(response: dict[str, Any], semantic_id: str) -> dict[str, Any]:
    require_ok("inspectObjects", response)
    matches = [item for item in response["result"] if item["semanticId"] == semantic_id]
    if len(matches) != 1:
        raise TransportError(f"Expected exactly one {semantic_id!r}, got {len(matches)}")
    return matches[0]


def patch(operation: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"operation": operation, "arguments": arguments}


def vec_close(actual: list[float], expected: list[float], tolerance: float = 0.02) -> bool:
    return len(actual) == len(expected) and all(abs(a - b) <= tolerance for a, b in zip(actual, expected))


def run(timeout: float, interactive: bool = False) -> Path:
    client = FileQueueClient(timeout)
    transcript: list[dict[str, Any]] = []

    def observe(message: str) -> None:
        if interactive:
            input(f"\nOBSERVE IN EDEN: {message}\nPress Enter to continue... ")

    def send(operation: str, revision: int, arguments: dict[str, Any] | None = None, request_id: str | None = None):
        request, response = client.request(operation, revision, arguments, request_id)
        transcript.append({"request": request, "response": response})
        print(f"{operation:16} {response['status']:4} revision={response['revision']} requestId={request['requestId']}")
        return request, response

    _, capabilities = send("getCapabilities", -1)
    require_ok("getCapabilities", capabilities)
    if not capabilities["result"].get("transport"):
        raise TransportError("Eden reports transport=false; reload/recompile the editor module")

    _, initial = send("inspectScene", capabilities["revision"])
    require_ok("inspectScene", initial)
    if initial.get("stopped"):
        raise TransportError("Probe is in stopped state; inspect it and run call ma_reconcile before this test")
    initial_ids = sorted(item["semanticId"] for item in initial["result"])
    revision = initial["revision"]
    semantic_id = "external_probe_" + client.new_request_id("obj").split("_", 1)[1][:12]
    create_position = [4004, 4004, 10] if interactive else [4050, 4050, 10]
    moved_position = [4006, 4005, 10.5] if interactive else [4052, 4051, 10.5]
    created = False
    create_request: dict[str, Any] | None = None
    create_response: dict[str, Any] | None = None
    try:
        create_id = client.new_request_id("create")
        create_request, create_response = send(
            "applyPatch",
            revision,
            {"operations": [patch("create", {
                "semanticId": semantic_id,
                "class": "WoodenArch",
                "position": create_position,
                "rotation": [0, 0, 15],
                "scale": 1,
                "parentId": "",
            })]},
            create_id,
        )
        require_ok("create", create_response)
        created = True
        revision = create_response["revision"]

        duplicate_response = client.deliver(create_request, force_redelivery=True)
        transcript.append({"request": create_request, "response": duplicate_response, "redelivery": True})
        print(f"duplicate delivery {duplicate_response['status']:4} revision={duplicate_response['revision']} requestId={create_id}")
        if duplicate_response != create_response:
            raise TransportError("Duplicate requestId did not return the original response")

        _, inspected = send("inspectObjects", revision, {"semanticIds": [semantic_id]})
        created_object = find_object(inspected, semantic_id)
        if not vec_close(created_object["position"], create_position):
            raise TransportError(f"Create read-back mismatch: {created_object['position']}")
        observe(f"created {semantic_id} (WoodenArch) at {create_position}")

        _, moved = send("applyPatch", revision, {"operations": [patch("setTransform", {
            "semanticId": semantic_id,
            "position": moved_position,
            "rotation": [5, 0, 75],
            "scale": 1,
        })]})
        require_ok("setTransform", moved)
        stale_revision = revision
        revision = moved["revision"]

        _, inspected = send("inspectObjects", revision, {"semanticIds": [semantic_id]})
        moved_object = find_object(inspected, semantic_id)
        if not vec_close(moved_object["position"], moved_position):
            raise TransportError(f"Transform read-back mismatch: {moved_object['position']}")
        observe(f"moved {semantic_id} to {moved_position}, rotation [5, 0, 75]")

        target = moved_object["positionASL"]
        views = [
            {"positionASL": [target[0] + 18, target[1] - 24, target[2] + 16], "targetASL": target, "fov": 0.85},
            {"positionASL": [target[0] - 18, target[1] - 20, target[2] + 12], "targetASL": target, "fov": 0.85},
        ]
        _, captured = send("captureViews", revision, {"views": views})
        require_ok("captureViews", captured)
        if len(captured["result"]) != 2 or any(item["revision"] != revision for item in captured["result"]):
            raise TransportError("Capture metadata count/revision mismatch")
        for item in captured["result"]:
            print(f"  PNG: {item['path']} — REQUIRES MANUAL PNG REVIEW")
        observe("two PNG files were captured; their exact paths are printed above")

        _, stale = send("applyPatch", stale_revision, {"operations": [patch("setTransform", {
            "semanticId": semantic_id,
            "position": [4099, 4099, 99],
            "rotation": [0, 0, 0],
            "scale": 1,
        })]})
        if stale["status"] != "FAIL" or not any(d and d[0] == "REVISION_MISMATCH" for d in stale["diagnostics"]):
            raise TransportError(f"Stale revision was not rejected correctly: {stale}")
        if stale["revision"] != revision:
            raise TransportError("Stale request changed revision")
        _, inspected = send("inspectObjects", revision, {"semanticIds": [semantic_id]})
        if not vec_close(find_object(inspected, semantic_id)["position"], moved_position):
            raise TransportError("Stale request changed the scene")

        observe(f"stale revision was rejected; {semantic_id} must still be at {moved_position}. Next step deletes it")

        _, deleted = send("applyPatch", revision, {"operations": [patch("delete", {"semanticId": semantic_id})]})
        require_ok("delete", deleted)
        created = False
        revision = deleted["revision"]
        _, final_scene = send("inspectScene", revision)
        require_ok("final inspectScene", final_scene)
        final_ids = sorted(item["semanticId"] for item in final_scene["result"])
        if final_ids != initial_ids:
            raise TransportError(f"Scene was not restored: before={initial_ids}, after={final_ids}")
        if final_scene["result"] != initial["result"]:
            raise TransportError("Pre-existing object state changed during the external cycle")
    finally:
        if created:
            try:
                _, state = send("inspectScene", revision)
                current_revision = state["revision"]
                current_ids = [item["semanticId"] for item in state.get("result", [])]
                if semantic_id in current_ids and not state.get("stopped"):
                    _, cleanup = send("applyPatch", current_revision, {"operations": [patch("delete", {"semanticId": semantic_id})]})
                    print(f"cleanup          {cleanup['status']}")
            except Exception as cleanup_error:  # preserve the primary failure
                print(f"WARNING: cleanup failed: {cleanup_error}", file=sys.stderr)

    artifacts = ROOT / "Tools/MapAutomation/artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    output = artifacts / time.strftime("external_e2e_%Y%m%d_%H%M%S.json")
    output.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"PASS: external Phase 1 cycle completed. Transcript: {output}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds per request")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="pause at visible Eden checkpoints and place the temporary object near the probe fixture",
    )
    args = parser.parse_args()
    try:
        run(args.timeout, args.interactive)
    except (OSError, KeyError, TypeError, TransportError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
