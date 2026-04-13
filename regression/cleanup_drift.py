#!/usr/bin/env python3
"""Clean up findings based on drift detection results.

Removes stale items from findings that have drifted due to analyzer fixes:
- possibly_fixed incorrect items → remove from incorrect array
- now_detected missed items → remove from missed array
- regression correct items → remove from correct array (stale check paths)

Usage:
    python3 regression/cleanup_drift.py --dry-run    # preview changes
    python3 regression/cleanup_drift.py --apply       # apply changes
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift import validate_finding
from findings import load_findings, save_findings, _iter_findings_files
from utils import DATA_DIR


def _find_removal_indices(finding):
    """Run drift validation and return indices to remove per item type.

    Matches drift results to finding items by iterating in the same order
    as validate_finding(), which processes correct/incorrect/missed items
    sequentially. Items with explicit check fields are matched by their
    (category, item_type) — not by description substrings.

    Returns {correct: set(int), incorrect: set(int), missed: set(int)}.
    """
    results = validate_finding(finding)
    removals = {"correct": set(), "incorrect": set(), "missed": set()}

    # Build per-type result lists in the same iteration order as validate_finding
    type_results = {"correct": [], "incorrect": [], "missed": []}
    for category, item_type, desc in results:
        if item_type in type_results:
            type_results[item_type].append(category)

    # Map categories to removal decisions
    removal_categories = {
        "correct": {"regression"},
        "incorrect": {"possibly_fixed"},
        "missed": {"now_detected"},
    }

    for item_type, categories in type_results.items():
        items = finding.get(item_type, [])
        # validate_finding skips items without analyzer_section, so we
        # need to track which items produced results
        result_idx = 0
        for i, item in enumerate(items):
            section = item.get("analyzer_section")
            if not section:
                continue
            if result_idx < len(categories):
                if categories[result_idx] in removal_categories[item_type]:
                    removals[item_type].add(i)
                result_idx += 1

    return removals


def main():
    parser = argparse.ArgumentParser(description="Clean up findings based on drift")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--repo", help="Filter by repo")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.print_help()
        sys.exit(1)

    # Collect removal indices per finding across all files
    drift_removals = {}  # finding_id -> removals dict

    for _repo, _proj, fpath in _iter_findings_files(args.repo):
        fdata = json.loads(fpath.read_text(encoding="utf-8"))
        for finding in fdata.get("findings", []):
            fid = finding.get("id", "?")
            removals = _find_removal_indices(finding)
            if any(removals.values()):
                drift_removals[fid] = removals

    if not drift_removals:
        print("No drift items to clean up.")
        return

    # Report
    total_removed = 0
    for fid, removals in sorted(drift_removals.items()):
        parts = []
        for key, indices in removals.items():
            if indices:
                parts.append(f"{len(indices)} {key}")
                total_removed += len(indices)
        print(f"  {fid}: remove {', '.join(parts)}")

    print(f"\nTotal items to remove: {total_removed} across {len(drift_removals)} findings")

    if args.dry_run:
        print("\n(dry run — no changes made)")
        return

    # Apply changes and save with findings.md regeneration
    modified_files = set()

    for repo, proj, fpath in _iter_findings_files(args.repo):
        fdata = json.loads(fpath.read_text(encoding="utf-8"))
        changed = False

        for finding in fdata.get("findings", []):
            fid = finding.get("id")
            if fid not in drift_removals:
                continue

            removals = drift_removals[fid]
            for key in ["correct", "incorrect", "missed"]:
                indices = removals.get(key, set())
                if indices and key in finding:
                    original = finding[key]
                    finding[key] = [item for i, item in enumerate(original)
                                    if i not in indices]
                    if len(finding[key]) != len(original):
                        changed = True

        if changed:
            save_findings(fdata, repo, proj)
            modified_files.add(fpath)

    print(f"\nModified {len(modified_files)} findings files (JSON + markdown regenerated)")


if __name__ == "__main__":
    main()
