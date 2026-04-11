#!/usr/bin/env python3
"""Audit BUGFIX assertion coverage against closed issues.

Parses FIXED.md for all KH-* entries, cross-references against
bugfix_registry.json, and reports gaps — issues without regression
assertions.

Usage:
    python3 regression/audit_bugfix_coverage.py
    python3 regression/audit_bugfix_coverage.py --json
    python3 regression/audit_bugfix_coverage.py --feasible-only
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import HARNESS_DIR

FIXED_MD = HARNESS_DIR / "FIXED.md"
REGISTRY = Path(__file__).resolve().parent / "bugfix_registry.json"

# Patterns that indicate a fix has observable output changes (feasible)
_OBSERVABLE_KEYWORDS = [
    "count", "detect", "false positive", "false negative", "missing",
    "added", "removed", "classification", "misclassif", "wrong",
    "zero", "ratio", "value", "threshold",
]

# Patterns that indicate internal-only changes (not feasible)
_INTERNAL_KEYWORDS = [
    "documentation", "canonical", "refactor", "comment", "readme",
    "report", "format", "prompt", "template", "style",
]


def parse_fixed_md():
    """Parse FIXED.md for all KH-* issue entries.

    Returns list of {issue, severity, title, has_repo_mention, has_ref_mention}.
    """
    if not FIXED_MD.exists():
        return []

    entries = []
    text = FIXED_MD.read_text(encoding="utf-8")

    # Match "### KH-NNN (SEVERITY): Title"
    pattern = re.compile(r'^### (KH-\d+)\s*\((\w+)\):\s*(.+)', re.MULTILINE)

    for match in pattern.finditer(text):
        issue = match.group(1)
        severity = match.group(2)
        title = match.group(3).strip()

        # Get the section text until next "###" or "---"
        start = match.end()
        next_header = re.search(r'^(###|---)', text[start:], re.MULTILINE)
        section = text[start:start + next_header.start()] if next_header else text[start:]

        # Heuristic: does the fix mention specific repos or component refs?
        has_repo = bool(re.search(r'repos?[/\\](\w+)', section, re.IGNORECASE) or
                        re.search(r'\b(bitaxe|modular-psu|OpenMower|hackrf|ubertooth)\b', section))
        has_ref = bool(re.search(r'\b[RCULQDJFYH]\d+\b', section))

        entries.append({
            "issue": issue,
            "severity": severity,
            "title": title,
            "has_repo_mention": has_repo,
            "has_ref_mention": has_ref,
        })

    return entries


def load_registry():
    """Load bugfix_registry.json. Returns dict of issue → entry."""
    if not REGISTRY.exists():
        return {}
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {entry["issue"]: entry for entry in data}


def assess_feasibility(entry):
    """Heuristic: is a bugfix assertion feasible for this issue?

    Returns "feasible", "maybe", or "not_feasible".
    """
    title_lower = entry["title"].lower()

    # Internal-only changes are not feasible
    if any(kw in title_lower for kw in _INTERNAL_KEYWORDS):
        return "not_feasible"

    # Observable changes with repo/ref mentions are feasible
    if entry["has_repo_mention"] and entry["has_ref_mention"]:
        return "feasible"

    if any(kw in title_lower for kw in _OBSERVABLE_KEYWORDS):
        if entry["has_repo_mention"] or entry["has_ref_mention"]:
            return "feasible"
        return "maybe"

    if entry["has_repo_mention"]:
        return "maybe"

    return "not_feasible"


def main():
    parser = argparse.ArgumentParser(
        description="Audit BUGFIX assertion coverage against closed issues"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--feasible-only", action="store_true",
                        help="Only show gaps assessed as feasible/maybe")
    args = parser.parse_args()

    fixed_entries = parse_fixed_md()
    registry = load_registry()

    covered = []
    gaps = []

    for entry in fixed_entries:
        issue = entry["issue"]
        if issue in registry:
            reg_entry = registry[issue]
            assertion_count = len(reg_entry.get("assertions", []))
            covered.append({
                **entry,
                "assertion_count": assertion_count,
                "type": reg_entry.get("type", "unknown"),
            })
        else:
            feasibility = assess_feasibility(entry)
            gaps.append({
                **entry,
                "feasibility": feasibility,
            })

    if args.feasible_only:
        gaps = [g for g in gaps if g["feasibility"] in ("feasible", "maybe")]

    if args.json:
        output = {
            "summary": {
                "total_closed_issues": len(fixed_entries),
                "covered_by_registry": len(covered),
                "gaps": len(gaps),
                "feasible_gaps": sum(1 for g in gaps if g["feasibility"] == "feasible"),
                "maybe_gaps": sum(1 for g in gaps if g["feasibility"] == "maybe"),
                "not_feasible_gaps": sum(1 for g in gaps if g["feasibility"] == "not_feasible"),
                "coverage_pct": f"{len(covered)/len(fixed_entries)*100:.1f}%"
                    if fixed_entries else "N/A",
            },
            "covered": covered,
            "gaps": gaps,
        }
        print(json.dumps(output, indent=2))
        return

    # Human-readable output
    print("=" * 70)
    print("BUGFIX ASSERTION COVERAGE AUDIT")
    print("=" * 70)
    print(f"Closed KH-* issues in FIXED.md: {len(fixed_entries)}")
    print(f"Covered by bugfix_registry.json: {len(covered)}")
    print(f"Gaps (no registry entry):        {len(gaps)}")
    if fixed_entries:
        print(f"Coverage: {len(covered)/len(fixed_entries)*100:.1f}%")
    print()

    feasible = [g for g in gaps if g["feasibility"] == "feasible"]
    maybe = [g for g in gaps if g["feasibility"] == "maybe"]
    not_feasible = [g for g in gaps if g["feasibility"] == "not_feasible"]

    print(f"Gap breakdown:")
    print(f"  Feasible (repo+ref mentioned):  {len(feasible)}")
    print(f"  Maybe (partial indicators):     {len(maybe)}")
    print(f"  Not feasible (internal/docs):   {len(not_feasible)}")
    print()

    if feasible:
        print("--- FEASIBLE GAPS (prioritize these) ---")
        for g in feasible:
            print(f"  {g['issue']} ({g['severity']}): {g['title']}")
        print()

    if maybe:
        print("--- MAYBE GAPS ---")
        for g in maybe:
            print(f"  {g['issue']} ({g['severity']}): {g['title']}")
        print()

    if not_feasible and not args.feasible_only:
        print(f"--- NOT FEASIBLE ({len(not_feasible)} issues, internal/doc changes) ---")
        for g in not_feasible[:10]:
            print(f"  {g['issue']} ({g['severity']}): {g['title']}")
        if len(not_feasible) > 10:
            print(f"  ... and {len(not_feasible) - 10} more")


if __name__ == "__main__":
    main()
