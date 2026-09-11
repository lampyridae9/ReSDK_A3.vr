#!/usr/bin/env python3
"""Curated live geometry/orientation review for Phase 8 vertical assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from room_generator.gateway import MapAutomationRoomGateway, _fingerprint


ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = {"SteelRustyStairs", "StoneBigLadderDouble"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--class", dest="classname", choices=sorted(CANDIDATES), default="SteelRustyStairs")
    parser.add_argument("--origin", nargs=3, type=float, default=(4725, 4700, 10.134262), metavar=("X", "Y", "Z"))
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    artifact = ROOT / f"Tools/MapAutomation/artifacts/phase8_vertical_{args.classname.lower()}_latest.json"

    gateway = MapAutomationRoomGateway(args.timeout)
    before = gateway.snapshot()
    measured = gateway.probe_geometry(before.revision, args.classname)["result"]
    bounds = measured["visualBounds"]
    x, y, floor_z = args.origin
    origin_z = floor_z - bounds[0][2]
    sid = "phase8__vertical_review__001"
    operation = {"operation": "create", "arguments": {"semanticId": sid, "class": args.classname,
        "position": [x, y, origin_z], "rotation": [0, 0, 0], "scale": 1, "parentId": "stairs_001"}}
    applied = gateway.apply([operation], before.revision)
    actual = next(row for row in applied["result"] if row["semanticId"] == sid)
    dz = actual["positionASL"][2] - actual["position"][2]
    width, depth, height = measured["dimensions"]
    target = [x, y, floor_z + dz + height / 2]
    views = [
        {"viewId": "vertical_side", "cameraRole": "vertical_side",
            "positionASL": [x + max(7, width * 3), y, floor_z + dz + height / 2], "targetASL": target, "fov": .8,
            "captureClassOverlay": True},
        {"viewId": "vertical_lower", "cameraRole": "vertical_lower",
            "positionASL": [x, y - depth / 2 - 3, floor_z + dz + 1.7], "targetASL": [x, y, floor_z + dz + 1.8], "fov": .8,
            "captureClassOverlay": False},
        {"viewId": "vertical_upper", "cameraRole": "vertical_upper",
            "positionASL": [x, y + depth / 2 + 3, floor_z + dz + height - .7],
            "targetASL": [x, y, floor_z + dz + height - 1.2], "fov": .8, "captureClassOverlay": False},
    ]
    captures = []
    for view in views:
        response = gateway.capture(applied["revision"], [view])
        captures.append({"view": view, "artifact": response["result"][0]})
    inspected = gateway.inspect(applied["revision"])
    cleanup = None
    if not args.keep:
        cleanup = gateway.cleanup([sid], inspected["revision"])
    scene_after = cleanup["result"] if cleanup else inspected["result"]
    result = {
        "schemaVersion": 1,
        "status": "PASS_PENDING_VISUAL_REVIEW",
        "classname": args.classname,
        "geometry": measured,
        "placement": {"floorElevation": floor_z, "modelOriginZOffset": -bounds[0][2], "actual": actual},
        "captures": captures,
        "sceneFingerprintBefore": before.fingerprint,
        "sceneFingerprintAfter": _fingerprint(scene_after),
        "sceneUnchanged": not args.keep and _fingerprint(scene_after) == before.fingerprint,
        "kept": args.keep,
        "revision": (cleanup or inspected)["revision"],
        "timestamp": int(time.time()),
    }
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
