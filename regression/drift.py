#!/usr/bin/env python3
"""Detect drift between findings and current analyzer outputs.

Re-checks all findings to detect drift: regressions where correct items
are no longer detected, bugs that may have been fixed, and missed items
now being detected.

Usage:
    python3 regression/drift.py                    # all findings
    python3 regression/drift.py --repo {repo}      # one repo
    python3 regression/drift.py --status confirmed  # filter by status
    python3 regression/drift.py --json              # machine-readable
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, resolve_path
from regression.findings import load_findings


def _load_output(analyzer_type, repo, source_file):
    """Load an analyzer output file. Returns parsed JSON or None."""
    output_path = OUTPUTS_DIR / analyzer_type / repo / source_file
    if not output_path.exists():
        return None
    try:
        return json.loads(output_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _section_count(data, section_path):
    """Get the count of items at a dotted section path. Returns None if missing."""
    value = resolve_path(data, section_path)
    if value is None:
        return None
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    # Scalar — treat as present (count 1)
    return 1


def validate_finding(finding):
    """Validate a single finding against current output.

    Returns list of (category, item_type, description) tuples.
    """
    repo = finding.get("repo", "")
    atype = finding.get("analyzer_type", "")
    source = finding.get("source_file", "")

    if not repo or not atype or not source:
        return [("no_checkable_items", None, "missing repo/analyzer_type/source_file")]

    output = _load_output(atype, repo, source)
    if output is None:
        return [("no_output", None, f"{atype}/{repo}/{source}")]

    results = []
    has_checkable = False

    # Check correct items — should still have data
    for item in finding.get("correct", []):
        section = item.get("analyzer_section")
        if not section:
            continue
        has_checkable = True
        count = _section_count(output, section)
        desc = item.get("description", section)
        if count is None or count == 0:
            results.append(("regression", "correct", f"{desc} — {section} now empty/missing"))
        else:
            results.append(("ok", "correct", f"{desc} — {section} has {count} items"))

    # Check incorrect items — count change suggests fix
    for item in finding.get("incorrect", []):
        section = item.get("analyzer_section")
        if not section:
            continue
        has_checkable = True
        count = _section_count(output, section)
        desc = item.get("description", section)
        if count is None or count == 0:
            results.append(("possibly_fixed", "incorrect", f"{desc} — {section} now empty"))
        else:
            results.append(("ok", "incorrect", f"{desc} — {section} has {count} items"))

    # Check missed items — data appearing suggests new detection
    for item in finding.get("missed", []):
        section = item.get("analyzer_section")
        if not section:
            continue
        has_checkable = True
        count = _section_count(output, section)
        desc = item.get("description", section)
        if count is not None and count > 0:
            results.append(("now_detected", "missed", f"{desc} — {section} now has {count} items"))
        else:
            results.append(("ok", "missed", f"{desc} — {section} still empty/missing"))

    if not has_checkable:
        return [("no_checkable_items", None, "no items with analyzer_section")]

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate findings against current outputs")
    parser.add_argument("--repo", help="Filter by repo name")
    parser.add_argument("--status", help="Filter by finding status")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    data = load_findings(args.repo)
    findings = data.get("findings", [])

    if args.status:
        findings = [f for f in findings if f.get("status") == args.status]

    if not findings:
        if args.json:
            print(json.dumps({"findings": 0, "results": []}))
        else:
            print("No findings to validate.")
        return

    all_results = []
    counts = {"ok": 0, "regression": 0, "possibly_fixed": 0,
              "now_detected": 0, "no_output": 0, "no_checkable_items": 0}

    for finding in findings:
        fid = finding.get("id", "?")
        results = validate_finding(finding)

        for category, item_type, desc in results:
            counts[category] = counts.get(category, 0) + 1
            all_results.append({
                "finding_id": fid,
                "category": category,
                "item_type": item_type,
                "description": desc,
            })

    if args.json:
        print(json.dumps({"findings": len(findings), "counts": counts,
                           "results": all_results}, indent=2))
        return

    # Human-readable output
    print(f"Validated {len(findings)} findings\n")

    # Show actionable items first
    for category, label in [("regression", "REGRESSION"),
                            ("possibly_fixed", "POSSIBLY FIXED"),
                            ("now_detected", "NOW DETECTED")]:
        items = [r for r in all_results if r["category"] == category]
        if items:
            print(f"=== {label} ({len(items)}) ===")
            for r in items:
                print(f"  {r['finding_id']}: {r['description']}")
            print()

    # Summary
    print("Summary:")
    for cat in ["ok", "regression", "possibly_fixed", "now_detected",
                "no_output", "no_checkable_items"]:
        if counts[cat]:
            print(f"  {cat}: {counts[cat]}")


if __name__ == "__main__":
    main()
