#!/usr/bin/env python3
"""Build, and optionally launch, a kept Phase 8 live generation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from room_generator.gateway import MapAutomationRoomGateway


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generation", type=Path)
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args()
    generation_path = args.generation if args.generation.is_absolute() else ROOT / args.generation
    generation = json.loads(generation_path.read_text(encoding="utf-8"))
    expected = {row["semanticId"] for row in generation["ownership"]["objects"]}

    gateway = MapAutomationRoomGateway(args.timeout)
    before = gateway.snapshot()
    present = {row["semanticId"] for row in before.objects}
    missing = sorted(expected - present)
    if missing:
        raise SystemExit(f"kept generation is incomplete; missing {len(missing)} owned objects")
    built = gateway.build_probe(before.revision)
    launched = gateway.launch_runtime_probe(before.revision) if args.launch else None
    artifact = {
        "schemaVersion": 1,
        "status": "LAUNCH_SCHEDULED" if launched else "BUILD_PASS",
        "generationArtifact": str(generation_path.relative_to(ROOT)).replace("\\", "/"),
        "ownedObjectsVerified": len(expected),
        "build": built["result"],
        "launch": launched["result"] if launched else None,
        "runtimeVerification": "PENDING_VISUAL_AND_PLAYER_TRAVERSAL" if launched else "NOT_LAUNCHED",
        "timestamp": int(time.time()),
    }
    output = ROOT / "Tools/MapAutomation/artifacts/phase8_runtime_latest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
