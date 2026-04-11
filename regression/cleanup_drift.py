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
from findings import load_findings, _iter_findings_files
from utils import DATA_DIR


def main():
    parser = argparse.ArgumentParser(description="Clean up findings based on drift")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--repo", help="Filter by repo")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.print_help()
        sys.exit(1)

    # Load all findings
    data = load_findings(args.repo)
    findings = data.get("findings", [])

    # Group drift results by finding_id and item
    drift_removals = {}  # finding_id -> {correct: set(), incorrect: set(), missed: set()}

    for finding in findings:
        fid = finding.get("id", "?")
        results = validate_finding(finding)

        removals = {"correct": set(), "incorrect": set(), "missed": set()}
        for category, item_type, desc in results:
            if category == "regression" and item_type == "correct":
                # Find the matching correct item by description prefix
                for i, item in enumerate(finding.get("correct", [])):
                    section = item.get("analyzer_section", "")
                    if f"{section} now empty/missing" in desc:
                        removals["correct"].add(i)
            elif category == "possibly_fixed" and item_type == "incorrect":
                for i, item in enumerate(finding.get("incorrect", [])):
                    section = item.get("analyzer_section", "")
                    if f"{section} now empty" in desc:
                        removals["incorrect"].add(i)
            elif category == "now_detected" and item_type == "missed":
                for i, item in enumerate(finding.get("missed", [])):
                    section = item.get("analyzer_section", "")
                    if f"{section} now has" in desc:
                        removals["missed"].add(i)

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

    # Apply changes: update findings.json files
    modified_files = set()

    for _repo, _proj, fpath in _iter_findings_files(args.repo):
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
            fpath.write_text(json.dumps(fdata, indent=2) + "\n", encoding="utf-8")
            modified_files.add(fpath)

    print(f"\nModified {len(modified_files)} findings.json files")

    # Re-render findings.md for modified files
    for fpath in modified_files:
        md_path = fpath.parent / "findings.md"
        # Render will be done by findings.py render
        pass

    print("Run 'python3 regression/findings.py render' to update findings.md files")


if __name__ == "__main__":
    main()
