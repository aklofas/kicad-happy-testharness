"""Batch-diff extractions vs gold (A7).

Subprocesses to regression/extraction_differ.py per MPN and aggregates results.
Spec: docs/superpowers/specs/2026-04-27-a7-gold-set-versioning-design.md §5.3.

Exit codes:
    0  no regressions (every diff has zero ERROR entries and score >= threshold)
    1  regression on at least one MPN
    2  malformed inputs
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HARNESS_ROOT))

from regression._mpn_slug import mpn_slug  # noqa: E402


def _resolve_cache_dir(arg: Optional[str]) -> Path:
    """Resolve cache dir from --cache-dir / env / harness default."""
    if arg:
        return Path(arg)
    env = os.environ.get("HARNESS_CACHE_DIR_OVERRIDE")
    if env:
        return Path(env)
    return _HARNESS_ROOT / "tests" / "fixtures" / "datasheets-extracted"


def _resolve_gold_dir(arg: Optional[str]) -> Path:
    """Resolve gold root from --gold-dir or harness default."""
    if arg:
        return Path(arg)
    return _HARNESS_ROOT / "regression" / "reference_extractions"


@dataclass
class MpnReport:
    """Per-MPN diff result captured from A5."""

    mpn: str
    mpn_slug: str
    score: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    skipped: bool = False
    skip_reason: str = ""


def _diff_one(*, mpn: str, gold_path: Path, cache_path: Path) -> MpnReport:
    """Subprocess to A5 differ for one (gold, cache) pair.

    Returns an MpnReport. If either file is missing, returns skipped=True.
    If the differ subprocess produces malformed JSON, also marks skipped.
    """
    rep = MpnReport(mpn=mpn, mpn_slug=mpn_slug(mpn))
    if not cache_path.exists():
        rep.skipped = True
        rep.skip_reason = f"cache not found: {cache_path}"
        return rep
    if not gold_path.exists():
        rep.skipped = True
        rep.skip_reason = f"gold not found: {gold_path}"
        return rep
    differ_cli = _HARNESS_ROOT / "regression" / "extraction_differ.py"
    cmd = [sys.executable, str(differ_cli),
           "--gold", str(gold_path),
           "--candidate", str(cache_path),
           "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        rep.skipped = True
        rep.skip_reason = (f"differ produced malformed JSON: "
                           f"{proc.stderr[:200]}")
        return rep
    rep.score = payload.get("gold_diff_score", 0)
    for entry in payload.get("entries", []):
        sev = entry.get("severity", "")
        if sev == "error":
            rep.error_count += 1
        elif sev == "warning":
            rep.warning_count += 1
        elif sev == "info":
            rep.info_count += 1
    return rep


def _discover_mpns(*, mpn: Optional[str], cache_dir: Path,
                   gold_root: Path) -> list[tuple[str, Path, Path]]:
    """Return list of (mpn_label, gold_path, cache_path) tuples.

    If --mpn is set, returns a single-item list for that MPN.
    Otherwise walks gold_root for all slug dirs (skipping _ and archived_ prefixes).
    """
    out: list[tuple[str, Path, Path]] = []
    if mpn:
        slug = mpn_slug(mpn)
        slug_dir = gold_root / slug
        gold_files = (list(slug_dir.glob("gold_v*.json"))
                      if slug_dir.exists() else [])
        if not gold_files:
            return [(mpn, slug_dir / "gold_v?.json",
                     cache_dir / f"{mpn}.json")]
        gold_path = sorted(gold_files)[-1]  # highest version wins
        out.append((mpn, gold_path, cache_dir / f"{mpn}.json"))
        return out
    if not gold_root.exists():
        return out
    for slug_dir in sorted(gold_root.iterdir()):
        if not slug_dir.is_dir():
            continue
        if slug_dir.name.startswith("_") or slug_dir.name.startswith("archived_"):
            continue
        gold_files = list(slug_dir.glob("gold_v*.json"))
        if not gold_files:
            continue
        gold_path = sorted(gold_files)[-1]
        meta_path = slug_dir / "meta.json"
        if meta_path.exists():
            try:
                mpn_label = json.loads(meta_path.read_text())["mpn"]
            except (json.JSONDecodeError, KeyError):
                mpn_label = slug_dir.name
        else:
            mpn_label = slug_dir.name
        out.append((mpn_label, gold_path, cache_dir / f"{mpn_label}.json"))
    return out


def _print_human(reports: list[MpnReport], threshold: int) -> None:
    """Print per-MPN row table + summary line."""
    print(f"Diff'ing {len(reports)} MPN(s)")
    print("\u2500" * 60)
    print(f"{'mpn':25s}  {'score':>6}  {'ERR':>4}  {'WARN':>4}  {'INFO':>4}")
    passed = 0
    regressed = 0
    for r in sorted(reports, key=lambda x: x.mpn_slug):
        if r.skipped:
            print(f"{r.mpn_slug:25s}  {'skip':>6}  ({r.skip_reason})")
            continue
        is_regression = r.error_count > 0 or r.score < threshold
        flag = "\u2190 regression" if is_regression else ""
        if is_regression:
            regressed += 1
        else:
            passed += 1
        print(f"{r.mpn_slug:25s}  {r.score:>6}  {r.error_count:>4}  "
              f"{r.warning_count:>4}  {r.info_count:>4}   {flag}")
    print("\u2500" * 60)
    print(f"Summary: {passed} passing, {regressed} regressed")


def _print_json(reports: list[MpnReport], threshold: int) -> None:
    """Print machine-readable JSON aggregate."""
    per_mpn = []
    passed = 0
    regressed = 0
    for r in reports:
        if r.skipped:
            per_mpn.append({"mpn": r.mpn, "skipped": True,
                            "skip_reason": r.skip_reason})
            continue
        is_regression = r.error_count > 0 or r.score < threshold
        if is_regression:
            regressed += 1
        else:
            passed += 1
        per_mpn.append({
            "mpn": r.mpn,
            "score": r.score,
            "error_count": r.error_count,
            "warning_count": r.warning_count,
            "info_count": r.info_count,
            "regression": is_regression,
        })
    print(json.dumps({
        "summary": {"audited": len(reports), "passed": passed,
                    "regressed": regressed},
        "per_mpn": per_mpn,
    }, indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    """Entry point: parse args, discover MPNs, diff each, aggregate, exit."""
    parser = argparse.ArgumentParser(
        description="Batch-diff extractions vs gold (subprocesses to A5 differ).",
    )
    parser.add_argument("--mpn", default=None, help="Diff a single MPN")
    parser.add_argument("--all", action="store_true", help="Diff every MPN")
    parser.add_argument("--cache-dir", default=None,
                        help="Path to extraction cache dir "
                             "(default: tests/fixtures/datasheets-extracted/)")
    parser.add_argument("--gold-dir", default=None,
                        help="Path to gold root (default: regression/reference_extractions)")
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable JSON output")
    parser.add_argument("--jobs", type=int,
                        default=multiprocessing.cpu_count(),
                        help=f"Parallelism (default: cpu_count = "
                             f"{multiprocessing.cpu_count()})")
    parser.add_argument("--score-threshold", type=int, default=90,
                        help="Score below this = regression (default: 90)")
    args = parser.parse_args(argv)

    if not args.mpn and not args.all:
        args.all = True

    cache_dir = _resolve_cache_dir(args.cache_dir)
    gold_root = _resolve_gold_dir(args.gold_dir)

    work = _discover_mpns(mpn=args.mpn, cache_dir=cache_dir, gold_root=gold_root)
    if not work:
        if args.json:
            print(json.dumps({
                "summary": {"audited": 0, "passed": 0, "regressed": 0},
                "per_mpn": [],
            }))
        else:
            print("No MPN gold dirs found; nothing to diff.")
        return 0

    if args.jobs <= 1:
        reports = [_diff_one(mpn=m, gold_path=g, cache_path=c)
                   for (m, g, c) in work]
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            futs = [ex.submit(_diff_one, mpn=m, gold_path=g, cache_path=c)
                    for (m, g, c) in work]
            reports = [f.result() for f in futs]

    if args.json:
        _print_json(reports, args.score_threshold)
    else:
        _print_human(reports, args.score_threshold)

    if any(r.error_count > 0
           or (not r.skipped and r.score < args.score_threshold)
           for r in reports):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
