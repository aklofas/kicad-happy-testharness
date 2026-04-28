"""Promote a gate-passed extraction to gold (A7).

Reads a v1.4 datasheet extraction cache file, re-runs the A6 acceptance gate,
re-runs the sanity-vector diff, validates the cache against the current
extraction schema, prompts the user, and writes gold + meta on confirm.

Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.1.

Exit codes:
    0  promoted (gold + meta written)
    1  aborted by user at confirmation prompt
    2  blocked: gate failed / sanity-vector mismatch / schema-validation failed
    3  blocked: cache file not found / malformed
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# regression/ → harness root
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS_ROOT))

from regression._mpn_slug import mpn_slug  # noqa: E402


def _resolve_kicad_happy_dir() -> Path:
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        return Path(env)
    return _HARNESS_ROOT.parent / "kicad-happy"


def _resolve_cache_dir(arg: Optional[str]) -> Path:
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "datasheets" / "extracted"


def _load_cache(cache_path: Path) -> dict:
    if not cache_path.exists():
        print(f"ERROR: cache file not found: {cache_path}", file=sys.stderr)
        sys.exit(3)
    try:
        return json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cache file unreadable: {e}", file=sys.stderr)
        sys.exit(3)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote a gate-passed extraction to v1.4 gold.",
    )
    parser.add_argument("--mpn", required=True, help="MPN to promote (e.g. LM2596-ADJ)")
    parser.add_argument("--cache-dir", default=None,
                        help="Path to <kicad-happy>/datasheets/extracted/ "
                             "(default: $KICAD_HAPPY_DIR/datasheets/extracted/)")
    parser.add_argument("--pdf-dir", default=None,
                        help="Where PDFs live for SHA computation "
                             "(default: $KICAD_HAPPY_DIR/datasheets/pdfs/)")
    parser.add_argument("--yes", action="store_true",
                        help="Non-interactive; promote without prompt")
    parser.add_argument("--no-gate", action="store_true",
                        help="Skip A6 gate re-run (sanity-vector diff still runs)")
    parser.add_argument("--re-curate-from", default=None,
                        help="Re-curation sweep mode; previous schema base version")
    args = parser.parse_args(argv)

    cache_dir = _resolve_cache_dir(args.cache_dir)
    cache_path = cache_dir / f"{args.mpn}.json"
    cache = _load_cache(cache_path)

    # Stub: subsequent task steps fill in gate / sanity / write.
    print(f"Loaded cache for {args.mpn} ({len(json.dumps(cache))} bytes)")
    return 2  # placeholder until rest of pipeline lands (Tasks 2b/2c)


if __name__ == "__main__":
    sys.exit(main())
