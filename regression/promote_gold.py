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
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# regression/ → harness root
_HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS_ROOT))

from regression._mpn_slug import mpn_slug  # noqa: E402


def _resolve_kicad_happy_dir() -> Path:
    """Resolve kicad-happy directory from KICAD_HAPPY_DIR env or sibling repo."""
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        return Path(env)
    return _HARNESS_ROOT.parent / "kicad-happy"


def _resolve_cache_dir(arg: Optional[str]) -> Path:
    """Resolve cache dir from --cache-dir or kicad-happy/datasheets/extracted/."""
    if arg:
        return Path(arg)
    return _resolve_kicad_happy_dir() / "datasheets" / "extracted"


def _load_cache(cache_path: Path) -> dict:
    """Load and parse JSON cache file. Exits 3 on missing or malformed file."""
    if not cache_path.exists():
        print(f"ERROR: cache file not found: {cache_path}", file=sys.stderr)
        sys.exit(3)
    try:
        return json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cache file unreadable: {e}", file=sys.stderr)
        sys.exit(3)


def _resolve_sanity_dir(arg: Optional[Path] = None) -> Path:
    """Sanity-vector directory, with env override hook for tests.

    Priority: HARNESS_SANITY_DIR_OVERRIDE env var → --sanity-dir arg →
    reference/datasheets/sanity_vectors/ (harness default).
    """
    env = os.environ.get("HARNESS_SANITY_DIR_OVERRIDE")
    if env:
        return Path(env)
    if arg:
        return arg
    return _HARNESS_ROOT / "reference" / "datasheets" / "sanity_vectors"


def _run_a6_gate(mpn: str, cache_dir: Path) -> tuple[bool, str]:
    """Re-run A6 acceptance gate against an extraction cache directory.

    Invokes validate/check_acceptance_gate.py as a subprocess and returns
    (all_pass, combined_stdout_stderr). Exit code 0 → all 4 checks passed.
    Any other exit code is treated as a gate failure.
    """
    gate_cli = _HARNESS_ROOT / "validate" / "check_acceptance_gate.py"
    cmd = [sys.executable, str(gate_cli), "--mpn", mpn, "--extract-dir", str(cache_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return (proc.returncode == 0, proc.stdout + proc.stderr)


def _walk_path(obj: Any, path: str) -> Any:
    """Walk a dotted path through nested dicts.

    Returns None if any segment is missing or the traversal hits a non-dict.
    Example: _walk_path(cache, "base.package.pin_count") → 5
    """
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _coerce_specvalue(v: Any) -> Optional[dict]:
    """Coerce a cache field value to a comparable SpecValue-shaped dict.

    Mirrors validate/check_acceptance_gate.py:_resolve_actual to keep
    comparison semantics identical without a cross-module import.

    Coercion rules:
      list  → first element (or None if empty)
      bool  → {"typ": v}  (must precede int check; bool is int subclass)
      int/float → {"typ": v}
      str   → {"name": v, "code": v}
      dict  → returned as-is
      None/other → None
    """
    if v is None:
        return None
    if isinstance(v, list):
        return v[0] if v else None
    if isinstance(v, bool):
        return {"typ": v}
    if isinstance(v, (int, float)):
        return {"typ": v}
    if isinstance(v, str):
        return {"name": v, "code": v}
    if isinstance(v, dict):
        return v
    return None


def _compare_sanity_field(expected: dict, actual: Optional[dict],
                           tolerance_pct: float) -> Optional[str]:
    """Compare a single sanity-vector field against the actual cache value.

    Returns None if within tolerance, or a human-readable reason string if
    the field diverges. Mirrors _compare_field in check_acceptance_gate.py.

    Tolerance: |actual - expected| / |expected| * 100 <= tolerance_pct.
    Unit must match string-equal. Missing expected numeric keys in actual
    are divergences.
    """
    if actual is None:
        return "path not found in cache"
    if "unit" in expected and expected["unit"] != actual.get("unit"):
        return (f"unit_mismatch (expected {expected['unit']!r}, "
                f"got {actual.get('unit')!r})")
    for key in ("min", "typ", "max"):
        if key not in expected:
            continue
        exp = expected[key]
        act = actual.get(key)
        if act is None:
            return f"key_missing_in_cache: {key}"
        if (isinstance(exp, (int, float)) and not isinstance(exp, bool)
                and isinstance(act, (int, float)) and not isinstance(act, bool)):
            if exp == 0:
                if act != 0:
                    return f"nonzero_against_zero: {key}"
                continue
            delta = abs(act - exp) / abs(exp) * 100
            if delta > tolerance_pct:
                return (f"{key}: |{act} - {exp}| / |{exp}| "
                        f"= {delta:.2f}% > {tolerance_pct}%")
        else:
            if exp != act:
                return f"value_mismatch: {key}"
    return None


def _run_sanity_diff(mpn: str, cache: dict,
                      sanity_dir: Path) -> tuple[bool, list[dict]]:
    """Run sanity-vector diff for an MPN against its cached extraction.

    Loads <sanity_dir>/<mpn_slug>.json and evaluates each field against the
    cache. Returns (all_pass, divergences) where divergences is a list of
    dicts with 'path' and 'reason' keys.

    Returns (False, [reason]) if the sanity vector file is not found.
    """
    slug = mpn_slug(mpn)
    vector_path = sanity_dir / f"{slug}.json"
    if not vector_path.exists():
        return False, [{"reason": f"sanity vector not found: {vector_path}"}]
    vector = json.loads(vector_path.read_text())
    divergences: list[dict] = []
    for fld in vector["fields"]:
        actual = _coerce_specvalue(_walk_path(cache, fld["path"]))
        reason = _compare_sanity_field(fld["expected"], actual,
                                        fld.get("tolerance_pct", 0))
        if reason:
            divergences.append({"path": fld["path"], "reason": reason})
    return (len(divergences) == 0, divergences)


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

    # ─── Gate re-run (belt-and-suspenders; skipped with --no-gate)
    if not args.no_gate:
        gate_pass, gate_summary = _run_a6_gate(args.mpn, cache_dir)
        if not gate_pass:
            print("ERROR: A6 gate did not pass 4/4. Promotion blocked.",
                  file=sys.stderr)
            print(gate_summary, file=sys.stderr)
            return 2
        print("[ok] A6 gate: 4/4 PASS")

    # ─── Sanity-vector diff
    sanity_dir = _resolve_sanity_dir()
    sanity_pass, divergences = _run_sanity_diff(args.mpn, cache, sanity_dir)
    if not sanity_pass:
        print("ERROR: sanity-vector diff has divergences. Promotion blocked.",
              file=sys.stderr)
        for d in divergences:
            print(f"  - {d.get('path', '<no path>')}: {d['reason']}",
                  file=sys.stderr)
        return 2
    print("[ok] sanity-vector diff: all fields within tolerance")

    # ─── Schema validation, write gold + meta — Task 2c
    return 0  # placeholder until Task 2c lands (gate + sanity passed)


if __name__ == "__main__":
    sys.exit(main())
