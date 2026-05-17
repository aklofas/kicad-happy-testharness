#!/usr/bin/env python3
"""Backfill schema_era tags on existing assertion corpus (A8, spec §19.3).

One-shot mechanical migration. Walks reference/**/assertions/*.json and
tags any assertion whose detector_filter is in the era's versioned-detector
set. Skips already-tagged assertions unless --force.

Design: docs/superpowers/specs/2026-05-16-a8-schema-era-tagging-design.md §6

Usage:
    tag_assertions.py --schema-era pre-v1.4 --dry-run           # default
    tag_assertions.py --schema-era pre-v1.4 --apply
    tag_assertions.py --schema-era pre-v1.4 --apply --repo {owner}/{repo}
    tag_assertions.py --schema-era pre-v1.4 --apply --force
    tag_assertions.py --schema-era pre-v1.4 --apply --jobs 8
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT))

from regression.schema_era import (
    is_versioned_detector,
    primary_rule_for_detector,
    gating_summary_for_detector,
)


def _iter_assertion_files(reference_root: Path, repo_filter: str | None):
    """Yield assertion JSON files under reference_root.

    Only yields files whose path contains a directory component named
    exactly 'assertions' (i.e. is under an 'assertions/' directory).
    """
    if repo_filter:
        # Limit walk to the named repo subtree
        parts = repo_filter.split("/", 1)
        if len(parts) == 2:
            scope = reference_root / parts[0] / parts[1]
        else:
            scope = reference_root / parts[0]
        if not scope.exists():
            return
        for p in scope.rglob("*.json"):
            if _is_under_assertions_dir(p):
                yield p
        return
    for p in reference_root.rglob("*.json"):
        if _is_under_assertions_dir(p):
            yield p


def _is_under_assertions_dir(p: Path) -> bool:
    """True iff p has a parent directory named exactly 'assertions'."""
    return any(part == "assertions" for part in p.parts)


def _tag_one_file(args_tuple: tuple) -> dict:
    """Process a single assertion file. Returns counts dict.

    Tuple shape: (path_str, era, tagged_at, force, dry_run, registry_dir_str)

    This function is called from worker processes, so it must be importable
    at the module level (no closures over local variables).
    """
    path_str, era, tagged_at, force, dry_run, registry_dir_str = args_tuple
    path = Path(path_str)
    registry_dir = Path(registry_dir_str)

    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except Exception as e:
        return {
            "path": path_str,
            "error": str(e),
            "by_detector": {},
            "assertion_count": 0,
            "eligible_count": 0,
            "tagged_count": 0,
            "skipped_count": 0,
        }

    assertions = data.get("assertions", [])
    eligible = 0
    tagged = 0
    skipped = 0
    by_detector: Counter = Counter()
    changed = False

    for a in assertions:
        df = a.get("check", {}).get("detector_filter")
        if not df:
            continue
        if not is_versioned_detector(df, era=era, registry_dir=registry_dir):
            continue
        eligible += 1
        if "schema_era" in a and not force:
            skipped += 1
            continue
        primary = primary_rule_for_detector(df, era=era, registry_dir=registry_dir)
        summary = gating_summary_for_detector(df, era=era, registry_dir=registry_dir)
        # Stamp in-place, inserting schema_era after the 'check' key.
        # Rebuild the dict to maintain key order: id, description, check, schema_era, ...
        _insert_schema_era(a, era, primary, tagged_at, summary)
        tagged += 1
        by_detector[df] += 1
        changed = True

    if changed and not dry_run:
        serialized = json.dumps(data, indent=2) + "\n"
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(serialized, encoding="utf-8")
        os.replace(tmp_path, path)

    return {
        "path": path_str,
        "error": None,
        "by_detector": dict(by_detector),
        "assertion_count": len(assertions),
        "eligible_count": eligible,
        "tagged_count": tagged,
        "skipped_count": skipped,
    }


def _insert_schema_era(
    assertion: dict,
    era: str,
    tagged_by_rule: str | None,
    tagged_at: str,
    tagged_reason: str | None,
) -> None:
    """Stamp schema_era into assertion in-place.

    Inserts after 'check' key to maintain a stable key order that keeps
    git diffs clean. If 'check' is not present, schema_era is appended.
    """
    new_era = {
        "era": era,
        "tagged_by_rule": tagged_by_rule,
        "tagged_at": tagged_at,
        "tagged_reason": tagged_reason,
    }
    # Rebuild dict preserving all keys, inserting schema_era after 'check'
    result: dict = {}
    inserted = False
    for k, v in list(assertion.items()):
        if k == "schema_era":
            # Will be re-inserted at the right position; skip old value
            continue
        result[k] = v
        if k == "check" and not inserted:
            result["schema_era"] = new_era
            inserted = True
    if not inserted:
        result["schema_era"] = new_era
    assertion.clear()
    assertion.update(result)


def _accumulate(totals: dict, result: dict) -> None:
    """Merge a per-file result dict into running totals."""
    totals["assertion_count"] += result.get("assertion_count", 0)
    totals["eligible_count"] += result.get("eligible_count", 0)
    totals["tagged_count"] += result.get("tagged_count", 0)
    totals["skipped_count"] += result.get("skipped_count", 0)
    if result.get("tagged_count", 0) > 0:
        totals["files_with_changes"] += 1
    for det, n in result.get("by_detector", {}).items():
        totals["by_detector"][det] = totals["by_detector"].get(det, 0) + n
    if result.get("error"):
        totals["errors"].append(f"{result['path']}: {result['error']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--schema-era", required=True,
        help="Era to stamp (e.g. pre-v1.4 or v1.4).",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Write changes. Without this flag, the tool is a dry-run.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="No-op (default behavior even without this flag).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite already-tagged assertions.",
    )
    parser.add_argument(
        "--repo", default=None,
        help="Limit walk to {owner}/{repo} subtree.",
    )
    parser.add_argument(
        "--jobs", type=int,
        default=max(1, (os.cpu_count() or 4)),
        help="Worker count for parallel walk. Default: cpu_count.",
    )
    parser.add_argument(
        "--reference-dir", type=Path,
        default=REPO_ROOT / "reference",
        help="Override reference root directory (for tests).",
    )
    parser.add_argument(
        "--registry-dir", type=Path,
        default=REPO_ROOT / "regression",
        help="Override versioned-detector registry directory (for tests).",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    tagged_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    files = list(_iter_assertion_files(args.reference_dir, args.repo))
    print(f"Scanning {len(files):,} assertion files "
          f"({'dry-run' if dry_run else 'apply'}, era={args.schema_era}, "
          f"force={args.force}, jobs={args.jobs})")

    job_args = [
        (str(p), args.schema_era, tagged_at, args.force, dry_run,
         str(args.registry_dir))
        for p in files
    ]

    totals: dict = {
        "assertion_count": 0,
        "eligible_count": 0,
        "tagged_count": 0,
        "skipped_count": 0,
        "files_with_changes": 0,
        "by_detector": {},
        "errors": [],
    }

    use_parallel = args.jobs > 1 and len(files) > 50
    if use_parallel:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for result in pool.map(_tag_one_file, job_args, chunksize=64):
                _accumulate(totals, result)
    else:
        for ja in job_args:
            result = _tag_one_file(ja)
            _accumulate(totals, result)

    # Always print summary
    print()
    print(f"Scanned:    {len(files):>10,} files / "
          f"{totals['assertion_count']:>10,} assertions")
    print(f"Eligible:   {totals['files_with_changes']:>10,} files / "
          f"{totals['eligible_count']:>10,} assertions in versioned set")
    tagged_line = (f"Tagged:     {totals['files_with_changes']:>10,} files / "
                   f"{totals['tagged_count']:>10,} assertions")
    if dry_run:
        tagged_line += " [DRY-RUN]"
    print(tagged_line)
    print(f"Skipped:    {0:>10,} files / "
          f"{totals['skipped_count']:>10,} assertions (already-tagged)")

    if totals["by_detector"]:
        print()
        print("By detector:")
        for det, n in sorted(totals["by_detector"].items(),
                             key=lambda kv: -kv[1]):
            print(f"  {det:42s} {n:>10,}")

    if totals["errors"]:
        print(f"\nERRORS ({len(totals['errors'])}):", file=sys.stderr)
        for err in totals["errors"][:20]:
            print(f"  {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
