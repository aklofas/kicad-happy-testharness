"""4-check acceptance gate runner for Phase 3a datasheet extractions.

Implements the gate defined in
docs/superpowers/specs/2026-04-20-sanity-vector-authoring.md § 4-check
acceptance gate wiring. Runs four checks against a Phase 3a extraction and
reports per-check pass/fail/skipped + structured details.

Usage:
    python3 validate/check_acceptance_gate.py --mpn LM2596-ADJ \\
        --extract-dir <path-to-datasheets/extracted/>

Exit codes:
    0 — all 4 checks passed
    1 — at least one check FAIL
    2 — all non-skipped checks passed but >=1 SKIPPED (Phase 3a tools missing)
    3 — error before checks ran (missing extraction, malformed input)
"""
from __future__ import annotations

import enum
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


def _resolve_python() -> str:
    """Python interpreter for subprocess CLIs (Checks 1 + 2).

    Order: KICAD_HAPPY_PYTHON env var → kicad-happy `.venv/bin/python` if
    present → sys.executable. The kicad-happy venv ships jsonschema +
    referencing per requirements-dev.txt; falling back to it lets the gate
    work out-of-the-box when run from a system python that lacks those deps.
    """
    env = os.environ.get("KICAD_HAPPY_PYTHON")
    if env:
        return env
    venv_python = (_resolve_kicad_happy_dir() / ".venv" / "bin" / "python")
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _resolve_kicad_happy_dir() -> Path:
    env = os.environ.get("KICAD_HAPPY_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent.parent / "kicad-happy"


class Status(enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CheckResult:
    """Structured result for one of the 4 gate checks."""
    name: str
    status: Status
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is Status.PASS


def _sanitize_mpn(mpn: str) -> str:
    """Mirror datasheet_lookup.sanitize_mpn — [A-Za-z0-9_-] kept, else _."""
    return re.sub(r'[^A-Za-z0-9_\-]', '_', mpn)


# ===========================================================================
# Check 3 — Quality score >= 60 (no main-repo dep, fully working today)
# ===========================================================================

def check_quality_score(*, cache_path: Path, threshold: int = 60) -> CheckResult:
    """Read extraction.quality_score from the merged <mpn>.json cache.

    Spec: "Score >= 60 per main-repo's datasheet_score.py (with Phase 3a
    extensions for v2 schema sections)." main-repo's pipeline writes the
    score into the cache file at extract time; harness just reads it.
    """
    name = "Check 3 — Quality score >= 60"
    if not cache_path.exists():
        return CheckResult(
            name=name, status=Status.ERROR,
            summary=f"cache file not found: {cache_path}",
            details={"reason": f"missing file: {cache_path}"},
        )

    try:
        cache = json.loads(cache_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return CheckResult(
            name=name, status=Status.ERROR,
            summary=f"cache file unreadable: {e}",
            details={"reason": str(e)},
        )

    extraction = cache.get("extraction") or {}
    if "quality_score" not in extraction:
        return CheckResult(
            name=name, status=Status.ERROR,
            summary="extraction.quality_score field missing",
            details={"reason": "extraction.quality_score not present in cache"},
        )

    score = extraction["quality_score"]
    if score >= threshold:
        return CheckResult(
            name=name, status=Status.PASS,
            summary=f"score={score} (threshold {threshold})",
            details={"score": score, "threshold": threshold},
        )
    return CheckResult(
        name=name, status=Status.FAIL,
        summary=f"score={score} below threshold {threshold}",
        details={"score": score, "threshold": threshold},
    )


# ===========================================================================
# Check 4 — Sanity-vector diff (self-implemented in pure Python, post-r7)
# ===========================================================================

def _walk_path(obj: Any, path: str) -> Any:
    """Walk a dotted path through a JSON object. Returns None if not found."""
    parts = path.split(".")
    cur = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def _resolve_actual(cache_value: Any) -> Optional[dict]:
    """Coerce a cache value to a comparable dict.

    Cache fields hold one of:
      - list[SpecValue dict] — pick [0] (highest trust per Track 2.4)
      - scalar (e.g. base.package.pin_count = 5) — wrap as {"typ": 5}
      - string (e.g. base.package.code = "TO-263") — wrap as {"name": ...}
      - None (path resolved but value absent)
      - dict (already SpecValue-shaped) — return as-is
    """
    if cache_value is None:
        return None
    if isinstance(cache_value, list):
        return cache_value[0] if cache_value else None
    if isinstance(cache_value, bool):
        # bool before int (bool is int subclass in Python)
        return {"typ": cache_value}
    if isinstance(cache_value, (int, float)):
        return {"typ": cache_value}
    if isinstance(cache_value, str):
        return {"name": cache_value, "code": cache_value}
    if isinstance(cache_value, dict):
        return cache_value
    return None


def _compare_field(expected: dict, actual: Optional[dict],
                   tolerance_pct: float) -> Optional[dict]:
    """Compare expected vs actual; return a divergence dict if outside
    tolerance, else None.

    Tolerance: |actual - expected| / |expected| * 100 <= tolerance_pct.
    Unit must match string-equal (no fuzzy). Missing keys in actual that
    are present in expected (numeric only) → divergence.
    """
    if actual is None:
        return {"reason": "path not found in cache", "actual": None}

    # Unit check first (string-equal, no fuzzy)
    if "unit" in expected:
        if expected["unit"] != actual.get("unit"):
            return {"reason": "unit_mismatch",
                    "expected_unit": expected["unit"],
                    "actual_unit": actual.get("unit")}

    # Numeric keys: min/typ/max
    max_delta_pct = 0.0
    for key in ("min", "typ", "max"):
        if key not in expected:
            continue
        exp_v = expected[key]
        act_v = actual.get(key)
        if act_v is None:
            return {"reason": f"key_missing_in_cache: {key}"}
        if not isinstance(exp_v, (int, float)) or \
           not isinstance(act_v, (int, float)) or \
           isinstance(exp_v, bool) or isinstance(act_v, bool):
            # Non-numeric: require exact equality
            if exp_v != act_v:
                return {"reason": f"value_mismatch: {key}"}
            continue
        if exp_v == 0:
            if act_v != 0:
                return {"reason": f"nonzero_against_zero: {key}"}
            continue
        delta_pct = abs(act_v - exp_v) / abs(exp_v) * 100
        if delta_pct > max_delta_pct:
            max_delta_pct = delta_pct
        if delta_pct > tolerance_pct:
            return {"delta_pct": round(delta_pct, 2)}

    return None  # within tolerance


def _compare_enum(expected_enum: list, actual: Optional[dict]) -> Optional[dict]:
    """For enum fields, compare actual['name'] or actual['code'] against the list."""
    if actual is None:
        return {"reason": "path not found in cache", "actual": None}
    candidates = [actual.get("name"), actual.get("code")]
    for cand in candidates:
        if cand in expected_enum:
            return None
    return {"reason": "enum_mismatch",
            "expected_enum": expected_enum,
            "actual": actual}


def check_sanity_vector_diff(*, cache_path: Path,
                              sanity_vector_path: Path) -> CheckResult:
    """Walk paths through cache, compare against sanity-vector expectations.

    Pure-Python implementation — no main-repo subprocess, no external deps.
    Sanity vectors are JSON post-r7 migration.
    """
    name = "Check 4 — Sanity-vector diff"
    if not cache_path.exists():
        return CheckResult(name=name, status=Status.ERROR,
                           summary=f"cache file not found: {cache_path}",
                           details={"reason": str(cache_path)})
    if not sanity_vector_path.exists():
        return CheckResult(name=name, status=Status.ERROR,
                           summary=f"sanity vector not found: {sanity_vector_path}",
                           details={"reason": str(sanity_vector_path)})

    try:
        cache = json.loads(cache_path.read_text())
        vector = json.loads(sanity_vector_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return CheckResult(name=name, status=Status.ERROR,
                           summary=f"file unreadable: {e}",
                           details={"reason": str(e)})

    fields = vector.get("fields", [])
    divergences = []
    for f in fields:
        path = f["path"]
        page = f.get("page")
        tolerance_pct = f.get("tolerance_pct", 5)

        cache_value = _walk_path(cache, path)
        actual = _resolve_actual(cache_value)

        if "expected_enum" in f:
            div = _compare_enum(f["expected_enum"], actual)
        elif "expected" in f:
            div = _compare_field(f["expected"], actual, tolerance_pct)
        else:
            div = {"reason": "field has neither 'expected' nor 'expected_enum'"}

        if div is not None:
            divergences.append({
                "path": path,
                "expected": f.get("expected") or f.get("expected_enum"),
                "actual": actual,
                "tolerance_pct": tolerance_pct,
                "page": page,
                **div,
            })

    if divergences:
        return CheckResult(
            name=name, status=Status.FAIL,
            summary=f"{len(divergences)}/{len(fields)} fields outside tolerance",
            details={"divergences": divergences,
                     "fields_compared": len(fields)},
        )
    return CheckResult(
        name=name, status=Status.PASS,
        summary=f"{len(fields)}/{len(fields)} fields within tolerance",
        details={"divergences": [], "fields_compared": len(fields)},
    )


# ===========================================================================
# Check 1 — Schema validation per task result (Phase 3a tool subprocess)
# ===========================================================================

_REQUIRED_TASK_IDS = ("scout", "base", "pinout")


def _discover_task_ids(extract_dir: Path, sanitized_mpn: str) -> list[str]:
    """Find all `<mpn>.<task_id>.result.json` files and return task IDs.

    Phase 3b ships 5 new categories (diode, transistor, opamp, mcu, crystal)
    on top of regulator — the actual category emitted depends on the part.
    Discover via filename glob so the gate doesn't need a hardcoded list.
    """
    pattern = f"{sanitized_mpn}.*.result.json"
    return sorted(p.name.split(".")[-3] for p in extract_dir.glob(pattern))


def check_schema_validation(*, mpn: str, extract_dir: Path,
                             kicad_happy_dir: Path,
                             python: Optional[str] = None) -> CheckResult:
    """Validate each <mpn>.<task_id>.result.json against its Track 2.1 schema.

    Subprocesses main-repo's validate_extraction_result.py (Phase 3a deliverable).
    If the tool is not available, returns SKIPPED — gate runs end-to-end
    without main-repo deps and gains this check when Phase 3a ships.
    """
    name = "Check 1 — Schema validation"
    tool = (kicad_happy_dir / "skills" / "datasheets" / "scripts"
            / "validate_extraction_result.py")
    if not tool.exists():
        return CheckResult(
            name=name, status=Status.SKIPPED,
            summary="validate_extraction_result.py not found in main-repo",
            details={"reason": f"tool not found at {tool} — Phase 3a deliverable"},
        )

    py = python or _resolve_python()
    sanitized = _sanitize_mpn(mpn)
    discovered = _discover_task_ids(extract_dir, sanitized)
    missing_required = [t for t in _REQUIRED_TASK_IDS if t not in discovered]
    if missing_required:
        return CheckResult(
            name=name, status=Status.FAIL,
            summary=f"missing required task results: {missing_required}",
            details={"discovered": discovered, "required": list(_REQUIRED_TASK_IDS)},
        )

    task_results = []
    any_fail = False
    for task_id in discovered:
        result_file = extract_dir / f"{sanitized}.{task_id}.result.json"
        if not result_file.exists():
            task_results.append({
                "file": str(result_file), "task_id": task_id, "valid": False,
                "errors": [f"file not found: {result_file}"],
            })
            any_fail = True
            continue
        proc = subprocess.run(
            [py, str(tool), "--result-file", str(result_file),
             "--task-type", task_id],
            capture_output=True, text=True,
        )
        valid = proc.returncode == 0
        task_results.append({
            "file": str(result_file), "task_id": task_id, "valid": valid,
            "errors": [proc.stderr.strip()] if not valid and proc.stderr else [],
        })
        if not valid:
            any_fail = True

    if any_fail:
        n_fail = sum(1 for t in task_results if not t["valid"])
        return CheckResult(
            name=name, status=Status.FAIL,
            summary=f"{n_fail}/{len(discovered)} task results failed validation",
            details={"task_results": task_results, "discovered": discovered},
        )
    return CheckResult(
        name=name, status=Status.PASS,
        summary=f"{len(discovered)}/{len(discovered)} task results valid",
        details={"task_results": task_results},
    )


# ===========================================================================
# Check 2 — datasheet_verify.py self-consistency (Phase 3a extension)
# ===========================================================================

def check_self_consistency(*, mpn: str, extract_dir: Path,
                            kicad_happy_dir: Path,
                            python: Optional[str] = None) -> CheckResult:
    """Run main-repo's datasheet_verify.py on the merged cache.

    CLI shape (per main-repo's #50 handoff):
        python3 datasheet_verify.py <extraction_path>
    Exit 0 = no issues. Exit nonzero = issues found (text reported on stdout).
    """
    name = "Check 2 — datasheet_verify.py self-consistency"
    tool = (kicad_happy_dir / "skills" / "datasheets" / "scripts"
            / "datasheet_verify.py")
    if not tool.exists():
        return CheckResult(
            name=name, status=Status.SKIPPED,
            summary="datasheet_verify.py not found in main-repo",
            details={"reason": f"tool not found at {tool}"},
        )

    sanitized = _sanitize_mpn(mpn)
    cache_path = extract_dir / f"{sanitized}.json"
    if not cache_path.exists():
        return CheckResult(
            name=name, status=Status.ERROR,
            summary=f"cache file not found: {cache_path}",
            details={"reason": str(cache_path)},
        )

    py = python or _resolve_python()
    proc = subprocess.run(
        [py, str(tool), str(cache_path)],
        capture_output=True, text=True,
    )

    if proc.returncode == 0:
        return CheckResult(
            name=name, status=Status.PASS,
            summary="0 issues",
            details={"tool_path": str(tool),
                     "stdout": proc.stdout.strip()[:200]},
        )
    return CheckResult(
        name=name, status=Status.FAIL,
        summary=f"datasheet_verify.py exit {proc.returncode}",
        details={"tool_path": str(tool),
                 "stdout": proc.stdout.strip(),
                 "stderr": proc.stderr.strip()},
    )


# ===========================================================================
# Orchestrator + report + CLI
# ===========================================================================

def run_gate(*, mpn: str, extract_dir: Path, sanity_vector_path: Path,
             kicad_happy_dir: Path,
             quality_threshold: int = 60,
             python: Optional[str] = None) -> list[CheckResult]:
    """Run all 4 checks and return their results in spec order."""
    py = python or _resolve_python()
    sanitized = _sanitize_mpn(mpn)
    cache_path = extract_dir / f"{sanitized}.json"

    return [
        check_schema_validation(
            mpn=mpn, extract_dir=extract_dir,
            kicad_happy_dir=kicad_happy_dir, python=py,
        ),
        check_self_consistency(
            mpn=mpn, extract_dir=extract_dir,
            kicad_happy_dir=kicad_happy_dir, python=py,
        ),
        check_quality_score(cache_path=cache_path, threshold=quality_threshold),
        check_sanity_vector_diff(
            cache_path=cache_path, sanity_vector_path=sanity_vector_path,
        ),
    ]


def render_text_report(results: list[CheckResult]) -> str:
    lines = []
    n_pass = sum(1 for r in results if r.status is Status.PASS)
    n_fail = sum(1 for r in results if r.status is Status.FAIL)
    n_skip = sum(1 for r in results if r.status is Status.SKIPPED)
    n_err = sum(1 for r in results if r.status is Status.ERROR)

    for r in results:
        lines.append(f"{r.name:42s} {r.status.value.upper():8s} {r.summary}")
        if r.status in (Status.FAIL, Status.ERROR):
            for k, v in r.details.items():
                if isinstance(v, list) and v:
                    lines.append(f"    {k}: ({len(v)} items)")
                    for item in v[:5]:
                        lines.append(f"      - {item}")
                    if len(v) > 5:
                        lines.append(f"      ... and {len(v) - 5} more")
                else:
                    lines.append(f"    {k}: {v}")
        elif r.status is Status.SKIPPED:
            reason = r.details.get("reason", "")
            if reason:
                lines.append(f"    reason: {reason}")

    lines.append("")
    if n_fail or n_err:
        verdict = "FAIL"
    elif n_skip:
        verdict = "PARTIAL"
    else:
        verdict = "PASS"
    lines.append(f"Gate result: {verdict} "
                 f"({n_pass} passed, {n_fail} failed, "
                 f"{n_skip} skipped, {n_err} error)")
    return "\n".join(lines)


def compute_exit_code(results: list[CheckResult]) -> int:
    if any(r.status is Status.ERROR for r in results):
        return 3
    if any(r.status is Status.FAIL for r in results):
        return 1
    if any(r.status is Status.SKIPPED for r in results):
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Run the 4-check acceptance gate for a Phase 3a extraction.")
    parser.add_argument("--mpn", required=True,
                        help="MPN to gate (e.g. LM2596-ADJ).")
    parser.add_argument("--extract-dir", required=True, type=Path,
                        help="Path to datasheets/extracted/ containing the merged "
                             "<mpn>.json + per-task .result.json files.")
    parser.add_argument("--sanity-vectors-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent
                                / "reference" / "datasheets" / "sanity_vectors",
                        help="Directory containing harness-owned <mpn>.json files.")
    parser.add_argument("--threshold", type=int, default=60,
                        help="Minimum quality score for Check 3 (default 60).")
    parser.add_argument("--python", default=None,
                        help="Python interpreter for Check 1 + Check 2 "
                             "subprocess calls. Overrides KICAD_HAPPY_PYTHON. "
                             "Default: env var, then kicad-happy/.venv/bin/"
                             "python, then sys.executable.")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON report instead of text.")
    args = parser.parse_args(argv)

    kicad_happy_dir = _resolve_kicad_happy_dir()
    sanity_vector_path = args.sanity_vectors_dir / f"{args.mpn.lower()}.json"

    results = run_gate(
        mpn=args.mpn, extract_dir=args.extract_dir,
        sanity_vector_path=sanity_vector_path,
        kicad_happy_dir=kicad_happy_dir,
        quality_threshold=args.threshold,
        python=args.python,
    )

    if args.json:
        payload = {
            "mpn": args.mpn,
            "checks": [
                {"name": r.name, "status": r.status.value,
                 "summary": r.summary, "details": r.details}
                for r in results
            ],
            "exit_code": compute_exit_code(results),
        }
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(render_text_report(results))

    return compute_exit_code(results)


if __name__ == "__main__":
    import sys
    sys.exit(main())
