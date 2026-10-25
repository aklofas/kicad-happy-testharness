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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, resolve_path, add_repo_filter_args, resolve_repos
from regression.findings import load_findings
from regression.checks import evaluate_assertion


def _load_output(analyzer_type, repo, source_file):
    """Load an analyzer output file. Returns parsed JSON or None."""
    output_path = OUTPUTS_DIR / analyzer_type / repo / source_file
    if not output_path.exists():
        return None
    try:
        return json.loads(output_path.read_text(encoding="utf-8"))
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


def _evaluate(check, output):
    """(result, resolvable). A check whose path no longer resolves in the output (a legacy
    `signal_analysis.*` path, a renamed section) says nothing about the bug: it is
    `unresolvable`, never `possibly_fixed` (not_contains_match passes on a non-list)."""
    if check.get("path") and resolve_path(output, check["path"]) is None:
        return None, False
    return evaluate_assertion({"check": check, "id": "drift", "description": ""}, output), True


def checkable_items(finding, item_type):
    """Items drift evaluates, in order: carry an analyzer_section and no disposition (an
    item resolved by cleanup keeps its record and is not re-flagged)."""
    return [(i, item) for i, item in enumerate(finding.get(item_type, []))
            if item.get("analyzer_section") and not item.get("disposition")]


@dataclass(frozen=True)
class ItemResult:
    """Drift verdict for one checkable item; the sentinels (nothing was checked) have
    item_type and index None."""
    item_type: Optional[str]
    index: Optional[int]
    category: str
    description: str
    has_check: bool


def validate_finding_items(finding):
    """Validate a single finding against current output: one ItemResult per checkable item,
    or one sentinel."""
    repo = finding.get("repo", "")
    atype = finding.get("analyzer_type", "")
    source = finding.get("source_file", "")

    if not repo or not atype or not source:
        return [ItemResult(None, None, "no_checkable_items", "missing repo/analyzer_type/source_file", False)]

    output = _load_output(atype, repo, source)
    if output is None:
        return [ItemResult(None, None, "no_output", f"{atype}/{repo}/{source}", False)]

    results = []

    def add(item_type, index, category, description, check):
        results.append(ItemResult(item_type, index, category, description, bool(check)))

    has_checkable = False

    # Check correct items — should still have data
    for index, item in checkable_items(finding, "correct"):
        section = item.get("analyzer_section")
        has_checkable = True
        desc = item.get("description", section)
        check = item.get("check")
        r, resolvable = _evaluate(check, output) if check else (None, True)
        if check and not resolvable:
            add("correct", index, "unresolvable", f"{desc} — check path {check['path']} not in output", check)
        elif check:
            if r["passed"]:
                add("correct", index, "ok", f"{desc} — check passed", check)
            else:
                add("correct", index, "regression", f"{desc} — check FAILED: actual={r.get('actual')}", check)
        else:
            count = _section_count(output, section)
            if count is None or count == 0:
                add("correct", index, "regression", f"{desc} — {section} now empty/missing", check)
            else:
                add("correct", index, "ok", f"{desc} — {section} has {count} items", check)

    # Check incorrect items — count change suggests fix
    for index, item in checkable_items(finding, "incorrect"):
        section = item.get("analyzer_section")
        has_checkable = True
        desc = item.get("description", section)
        check = item.get("check")
        r, resolvable = _evaluate(check, output) if check else (None, True)
        if check and not resolvable:
            add("incorrect", index, "unresolvable", f"{desc} — check path {check['path']} not in output", check)
        elif check:
            if r["passed"]:
                # not_contains_match passed = ref is gone = bug fixed
                add("incorrect", index, "possibly_fixed", f"{desc} — bug appears fixed", check)
            else:
                # not_contains_match failed = ref still there = bug still present
                add("incorrect", index, "ok", f"{desc} — bug still present: {r.get('actual')}", check)
        else:
            count = _section_count(output, section)
            if count is None or count == 0:
                add("incorrect", index, "possibly_fixed", f"{desc} — {section} now empty", check)
            else:
                add("incorrect", index, "ok", f"{desc} — {section} has {count} items", check)

    # Check missed items — data appearing suggests new detection
    for index, item in checkable_items(finding, "missed"):
        section = item.get("analyzer_section")
        has_checkable = True
        desc = item.get("description", section)
        check = item.get("check")
        r, resolvable = _evaluate(check, output) if check else (None, True)
        if check and not resolvable:
            add("missed", index, "unresolvable", f"{desc} — check path {check['path']} not in output", check)
        elif check:
            if r["passed"]:
                add("missed", index, "now_detected", f"{desc} — check passed (now detected)", check)
            else:
                add("missed", index, "ok", f"{desc} — check still failing: actual={r.get('actual')}", check)
        else:
            count = _section_count(output, section)
            if count is not None and count > 0:
                add("missed", index, "now_detected", f"{desc} — {section} now has {count} items", check)
            else:
                add("missed", index, "ok", f"{desc} — {section} still empty/missing", check)

    if not has_checkable:
        return [ItemResult(None, None, "no_checkable_items", "no items with analyzer_section", False)]

    return results


def validate_finding(finding):
    """validate_finding_items as (category, item_type, description) tuples."""
    return [(r.category, r.item_type, r.description) for r in validate_finding_items(finding)]


def main():
    parser = argparse.ArgumentParser(description="Validate findings against current outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--status", help="Filter by finding status")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None or len(repos) != 1:
        # Load all findings then filter by repo list (or load all if repos is None)
        data = load_findings(None)
        findings = data.get("findings", [])
        if repos is not None:
            repos_set = set(repos)
            findings = [f for f in findings if f.get("repo", "") in repos_set]
    else:
        data = load_findings(repos[0])
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
    counts = {"ok": 0, "regression": 0, "possibly_fixed": 0, "now_detected": 0,
              "unresolvable": 0, "no_output": 0, "no_checkable_items": 0}

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
    for cat in ["ok", "regression", "possibly_fixed", "now_detected", "unresolvable",
                "no_output", "no_checkable_items"]:
        if counts[cat]:
            print(f"  {cat}: {counts[cat]}")


if __name__ == "__main__":
    main()
