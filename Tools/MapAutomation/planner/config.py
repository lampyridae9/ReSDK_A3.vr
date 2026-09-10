"""Load the small Phase 5 planner configuration from local .env files."""
from __future__ import annotations
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ALLOWED={"OPENAI_API_KEY","RELICTA_PLANNER_MODEL","RELICTA_PLANNER_TIMEOUT","RELICTA_PLANNER_CACHE"}


def load_planner_env() -> list[Path]:
    """Load known keys without overriding the process environment."""
    loaded=[]
    for path in (ROOT/".env",ROOT/"Tools/MapAutomation/.env"):
        if not path.is_file(): continue
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line=raw.strip()
            if not line or line.startswith("#"): continue
            if line.startswith("export "): line=line[7:].lstrip()
            if "=" not in line: continue
            key,value=line.split("=",1);key=key.strip()
            if key not in ALLOWED: continue
            value=value.strip()
            if len(value)>=2 and value[0]==value[-1] and value[0] in {"'",'"'}: value=value[1:-1]
            os.environ.setdefault(key,value)
        loaded.append(path)
    return loaded
