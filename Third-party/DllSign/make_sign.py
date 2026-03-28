#!/usr/bin/env python3
"""Generate SHA-1 signatures for `_allowed_extensions.h`.

Usage:
    python make_sign.py                   # regenerate `Src/client/ClientInit/_allowed_extensions.h`
    python make_sign.py debug_console url_fetch  # print signatures for provided extensions
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
import sys
from typing import Iterable, List, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

DEFAULT_HEADER_CANDIDATES = [
    PROJECT_ROOT / "client" / "ClientInit" / "_allowed_extensions.h",
    PROJECT_ROOT / "Src" / "client" / "ClientInit" / "_allowed_extensions.h",
]
DEFAULT_HEADER_PATH = next((path for path in DEFAULT_HEADER_CANDIDATES if path.exists()), DEFAULT_HEADER_CANDIDATES[-1])

DEFAULT_MOD_PATH = Path(r"D:\Relicta\from_launcher\Arma 3\@RLCT")
ENTRY_RE = re.compile(r'^\s*\["(?P<name>[^"]+)"\s*,\s*"(?P<hash>[0-9A-Fa-f]{40})"\]\s*,?\s*\\?\s*$')
HEADER_COMMENT = "// Generated from make_sign.py"
DEFINE_NAME = "#define CLIENTSIDE_LIST_ALLOWED_EXTENSIONS [ \\"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate extension signatures."
    )
    parser.add_argument(
        "extensions",
        nargs="*",
        help="Extension names to process. If omitted, uses names from the header file.",
    )
    parser.add_argument(
        "--mod-path",
        default=DEFAULT_MOD_PATH,
        type=Path,
        help=f"Base path where extension DLLs are located (default: {DEFAULT_MOD_PATH}).",
    )
    parser.add_argument(
        "--header-path",
        default=DEFAULT_HEADER_PATH,
        type=Path,
        help="Path to _allowed_extensions.h (used in no-argument mode).",
    )
    return parser.parse_args()


def normalize_extension_name(raw_name: str) -> str:
    normalized = Path(raw_name).stem if raw_name.lower().endswith(".dll") else raw_name
    return Path(normalized).name


def parse_extensions_from_header(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Header file not found: {path}")

    names: List[str] = []
    collecting = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "CLIENTSIDE_LIST_ALLOWED_EXTENSIONS" in line:
            collecting = True
            continue
        if collecting:
            if line.strip().startswith("]"):
                break
            match = ENTRY_RE.match(line)
            if match:
                names.append(match.group("name"))
    return names


def sha1_hex(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def resolve_file_path(base_path: Path, extension_name: str) -> Path:
    if not base_path.exists():
        raise FileNotFoundError(f"Mod path not found: {base_path}")

    stem = normalize_extension_name(extension_name)
    candidates = [f"{stem}_x64.dll", f"{stem}.dll"]
    for candidate in candidates:
        candidate_path = base_path / candidate
        if candidate_path.is_file():
            return candidate_path

    # Fallback search for nested paths.
    for candidate in candidates:
        matches = list(base_path.rglob(candidate))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FileNotFoundError(
                f"Ambiguous file lookup for '{extension_name}' in '{base_path}': "
                f"{', '.join(str(m) for m in matches)}"
            )

    raise FileNotFoundError(
        f"Cannot find extension DLL for '{extension_name}' in '{base_path}'. "
        f"Expected names: {', '.join(candidates)}"
    )


def generate_signatures(extensions: Iterable[str], mod_path: Path) -> List[Tuple[str, str]]:
    signatures: List[Tuple[str, str]] = []
    for ext in extensions:
        normalized = normalize_extension_name(ext)
        file_path = resolve_file_path(mod_path, normalized)
        signatures.append((normalized, sha1_hex(file_path)))
    return signatures


def emit_entries(signatures: Iterable[Tuple[str, str]]) -> List[str]:
    rows = list(signatures)
    if not rows:
        return []

    result: List[str] = []
    for idx, (name, digest) in enumerate(rows):
        if idx + 1 == len(rows):
            suffix = " \\"
        else:
            suffix = ", \\"
        result.append(f'\t["{name}", "{digest}"]{suffix}')
    return result


def rewrite_header(path: Path, signatures: List[Tuple[str, str]]) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Header file not found: {path}")

    source_lines = path.read_text(encoding="utf-8-sig").splitlines()
    output_lines: List[str] = []

    inserted = False
    for line in source_lines:
        if line.startswith("macro_const("):
            output_lines.append(line.rstrip())
            output_lines.append(HEADER_COMMENT)
            output_lines.append(DEFINE_NAME)
            output_lines.extend(emit_entries(signatures))
            output_lines.append(" ]")
            inserted = True
            break
        output_lines.append(line.rstrip())

    if not inserted:
        raise RuntimeError(f"Could not find macro_const block in {path}")

    output = "\n".join(output_lines) + "\n"
    path.write_text(output, encoding="utf-8")


def print_signatures(signatures: List[Tuple[str, str]]) -> None:
    for line in emit_entries(signatures):
        print(line)


def parse_extension_or_default(args: argparse.Namespace) -> List[str]:
    if args.extensions:
        return args.extensions
    return parse_extensions_from_header(args.header_path)


def main() -> int:
    args = parse_args()
    try:
        extensions = parse_extension_or_default(args)
        signatures = generate_signatures(extensions, args.mod_path)
        if args.extensions:
            print_signatures(signatures)
        else:
            rewrite_header(args.header_path, signatures)
            print(f"Updated {args.header_path}")
        return 0
    except Exception as exc:
        print(f"make_sign: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
