"""Prepare an isolated Eden fixture; NOT an external Automation transport.

Never modifies mission.sqm or overwrites an existing map. Python 3.10+; stdlib only.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MAP_NAME = "AI_AutomationProbe"
MARKER = "MapAutomation-v1"
TEMPLATE = Path("Src/Editor/Bin/ProtoMap/TEMP_MAP.cpp")
DESTINATION = Path(f"Src/Editor/Bin/Maps/{MAP_NAME}.cpp")


def build_fixture(template: str) -> str:
    token = '[""missionName"",""TEMP""]'
    if template.count(token) != 1:
        raise ValueError("Expected exactly one TEMP common-storage record; refusing to guess")
    replacement = (
        f'[""missionName"",""{MAP_NAME}""],'
        f'[""__automationProbe"",""{MARKER}""],'
        '[""version"",5]'
    )
    return template.replace(token, replacement)


def prepare(repo: Path) -> Path:
    repo = repo.resolve()
    source = (repo / TEMPLATE).resolve()
    target = (repo / DESTINATION).resolve()
    artifacts = (repo / "Tools/MapAutomation/artifacts").resolve()
    if not all(p.is_relative_to(repo) for p in (source, target, artifacts)):
        raise ValueError("Fixture paths must remain inside the repository")
    text = build_fixture(source.read_text(encoding="utf-8-sig"))
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}; use the existing probe map")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    artifacts.mkdir(parents=True, exist_ok=True)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        target = prepare(args.repo)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"NOT PREPARED: {exc}\n")
    print(f"PREPARED: {target}")
    print("REQUIRES MANUAL ENGINE TEST; open the fixture through ReSDK MapsManager.")
    print("External transport is deferred until internal Eden smoke tests pass.")


if __name__ == "__main__":
    main()
