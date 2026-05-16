#!/usr/bin/env python3
"""Validate the run_id envelope invariant across all analyzer outputs.

Every analyzer envelope produced via --analysis-dir carries two run_id
pointers:

  - inputs.run_id            -- minted by build_inputs() at write time
  - capability_mode_ref.run_id -- the session ID from capability_mode.json

Post-v1.4 polish-pass (audit Highest-Risk #5), all 6 analyzers resolve
capability_mode_ref BEFORE build_inputs and pass run_id=capability_mode_ref.run_id
into build_inputs. The output invariant is:

    output["inputs"]["run_id"] == output["capability_mode_ref"]["run_id"]

Outputs missing either field (legacy --output mode, or older analyzers
that don't write the envelope) are skipped, not flagged.

Exits 0 if all checked outputs satisfy the invariant; 1 if any mismatch.

Usage:
    python3 validate/validate_run_id.py
    python3 validate/validate_run_id.py --repo owner/repo
    python3 validate/validate_run_id.py --cross-section smoke --jobs 16
    python3 validate/validate_run_id.py --json
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, DEFAULT_JOBS, add_repo_filter_args,
                   resolve_repos)


# Analyzer output dirs to check. cross_analysis has no batch runner yet but
# is included so it's covered once outputs start landing.
ANALYZER_DIRS = ["schematic", "pcb", "thermal", "emc", "gerber", "cross_analysis"]


def _check_file(path):
    """Return (status, detail) for a single JSON output.

    status: "match" | "mismatch" | "skip"
    detail: free-form string for mismatch / skip reason; "" on match
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return "skip", f"invalid_json: {e}"

    inputs = data.get("inputs") if isinstance(data.get("inputs"), dict) else None
    capref = data.get("capability_mode_ref") if isinstance(data.get("capability_mode_ref"), dict) else None
    i_run = inputs.get("run_id") if inputs else None
    c_run = capref.get("run_id") if capref else None

    if i_run is None or c_run is None:
        return "skip", "missing_field"
    if i_run != c_run:
        return "mismatch", f"inputs.run_id={i_run!r} capability_mode_ref.run_id={c_run!r}"
    return "match", ""


def _check_repo(repo):
    """Walk all analyzer outputs for one repo. Picklable for ProcessPoolExecutor."""
    checked = 0
    matched = 0
    mismatches = []  # [(rel_path, detail)]

    for analyzer in ANALYZER_DIRS:
        repo_dir = OUTPUTS_DIR / analyzer / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            if f.name.startswith("_"):
                continue
            status, detail = _check_file(f)
            if status == "skip":
                continue
            checked += 1
            if status == "match":
                matched += 1
            else:
                rel = f.relative_to(OUTPUTS_DIR)
                mismatches.append((str(rel), detail))

    return checked, matched, mismatches


def _discover_output_repos():
    """List repos that have any analyzer output (owner/repo format)."""
    seen = set()
    for analyzer in ANALYZER_DIRS:
        adir = OUTPUTS_DIR / analyzer
        if not adir.exists():
            continue
        for owner_dir in adir.iterdir():
            if not owner_dir.is_dir() or owner_dir.name.startswith("_"):
                continue
            for repo_dir in owner_dir.iterdir():
                if repo_dir.is_dir():
                    seen.add(f"{owner_dir.name}/{repo_dir.name}")
    return sorted(seen)


def main():
    parser = argparse.ArgumentParser(
        description="Validate inputs.run_id == capability_mode_ref.run_id invariant")
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = _discover_output_repos()

    if not repos:
        print("No analyzer outputs found", file=sys.stderr)
        sys.exit(1)

    total_checked = 0
    total_matched = 0
    all_mismatches = []
    jobs = args.jobs

    if jobs > 1 and len(repos) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
            futures = {pool.submit(_check_repo, repo): repo for repo in repos}
            for future in as_completed(futures):
                checked, matched, mismatches = future.result()
                total_checked += checked
                total_matched += matched
                all_mismatches.extend(mismatches)
    else:
        for repo in repos:
            checked, matched, mismatches = _check_repo(repo)
            total_checked += checked
            total_matched += matched
            all_mismatches.extend(mismatches)

    if args.json:
        json.dump({
            "checked": total_checked,
            "matched": total_matched,
            "mismatched": len(all_mismatches),
            "mismatches": [{"file": f, "detail": d} for f, d in all_mismatches],
        }, sys.stdout, indent=2)
        print()
        sys.exit(1 if all_mismatches else 0)

    print(f"Checked: {total_checked} outputs across {len(repos)} repos")
    print(f"Matched: {total_matched}")
    print(f"Mismatched: {len(all_mismatches)}")

    if all_mismatches:
        print()
        print("Mismatches (showing first 20):")
        for f, d in all_mismatches[:20]:
            print(f"  {f}")
            print(f"    {d}")
        if len(all_mismatches) > 20:
            print(f"  ... and {len(all_mismatches) - 20} more")
        sys.exit(1)


if __name__ == "__main__":
    main()
