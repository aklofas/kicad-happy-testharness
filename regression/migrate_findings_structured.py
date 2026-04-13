#!/usr/bin/env python3
"""Batch-migrate findings to structured item schema (P3.A).

Adds detector, subject_refs, expected_relation, confidence fields
to all finding items that have an analyzer_section. Regenerates
check fields via the structured path.

Usage:
    python3 regression/migrate_findings_structured.py --dry-run
    python3 regression/migrate_findings_structured.py --apply
    python3 regression/migrate_findings_structured.py --repo owner/repo --apply
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from refextract import extract_refs
from findings import _iter_findings_files, save_findings
from generate_finding_checks import _check_from_structured

# Regex for count claims: "should detect 3" or "3 voltage_dividers detected"
_COUNT_RE = re.compile(
    r"(?:should\s+detect\s+(\d+))"
    r"|(?:(\d+)\s+\w+\s+detected)",
    re.IGNORECASE,
)

# Regex for value claims: "ratio should be 0.5", "vout ≈ 3.3"
_VALUE_RE = re.compile(
    r"(ratio|vout|cutoff_hz|frequency|gain|estimated_vout)"
    r"\s*(?:should\s+be|≈|=|equals)\s*"
    r"([0-9.]+)",
    re.IGNORECASE,
)

# Default relation by array membership
_DEFAULT_RELATION = {
    "correct": "in_detector",
    "incorrect": "not_in_detector",
    "missed": "in_detector",
}


def derive_detector(analyzer_section):
    """Extract detector name from analyzer_section path.

    'signal_analysis.voltage_dividers' -> 'voltage_dividers'
    Returns None if section doesn't match the signal_analysis.X pattern.
    """
    if not analyzer_section:
        return None
    parts = analyzer_section.split(".")
    if len(parts) >= 2 and parts[0] == "signal_analysis":
        return parts[1]
    return None


def derive_subject_refs(description):
    """Extract component refs from description text."""
    return extract_refs(description or "")


def derive_expected_relation(item, item_type):
    """Derive expected_relation from item content and array membership.

    Checks for count and value override patterns in description text.
    Falls back to default based on item_type.
    """
    desc = item.get("description", "")

    # Check for value claim: "ratio should be 0.5"
    if _VALUE_RE.search(desc):
        return "field_value_equals"

    # Check for count claim: "should detect 3"
    if _COUNT_RE.search(desc):
        return "count_equals"

    return _DEFAULT_RELATION.get(item_type, "in_detector")


def _extract_value_fields(item):
    """Extract field and expected_value for field_value_equals items."""
    desc = item.get("description", "")
    m = _VALUE_RE.search(desc)
    if m:
        return m.group(1).lower(), float(m.group(2))
    return None, None


def _extract_count_value(item):
    """Extract expected count for count_equals items."""
    desc = item.get("description", "")
    m = _COUNT_RE.search(desc)
    if m:
        val = m.group(1) or m.group(2)
        return int(val)
    return None


def derive_confidence(detector, refs, relation):
    """Compute confidence score based on extraction quality."""
    if relation in ("field_value_equals", "count_equals"):
        return 0.6
    if detector and refs:
        return 0.9
    if detector:
        return 0.7
    return 0.5


def enrich_item(item, item_type):
    """Add structured fields to a single finding item. Returns the item (mutated)."""
    section = item.get("analyzer_section", "")
    detector = derive_detector(section)
    if not detector:
        return item

    refs = derive_subject_refs(item.get("description", ""))
    relation = derive_expected_relation(item, item_type)

    item["detector"] = detector
    item["subject_refs"] = refs
    item["expected_relation"] = relation
    item["confidence"] = derive_confidence(detector, refs, relation)

    if relation == "field_value_equals":
        field, value = _extract_value_fields(item)
        if field is not None:
            item["field"] = field
            item["expected_value"] = value

    elif relation == "count_equals":
        count = _extract_count_value(item)
        if count is not None:
            item["expected_value"] = count

    check = _check_from_structured(item, item_type)
    if check:
        item["check"] = check

    return item


def migrate(repo_name=None, dry_run=True):
    """Migrate all findings to structured schema.

    Returns (files_modified, items_enriched, items_skipped).
    """
    files_modified = 0
    items_enriched = 0
    items_skipped = 0

    for repo, proj, ff in _iter_findings_files(repo_name):
        data = json.loads(ff.read_text(encoding="utf-8"))
        modified = False

        for finding in data.get("findings", []):
            for item_type in ("correct", "incorrect", "missed"):
                for item in finding.get(item_type, []):
                    if item.get("expected_relation"):
                        continue

                    section = item.get("analyzer_section", "")
                    if not section:
                        items_skipped += 1
                        continue

                    if not dry_run:
                        enrich_item(item, item_type)
                    items_enriched += 1
                    modified = True

        if modified:
            files_modified += 1
            if not dry_run:
                save_findings(repo, proj, data)

    return files_modified, items_enriched, items_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Migrate findings to structured schema (P3.A)")
    parser.add_argument("--repo", help="Filter by repo name")
    parser.add_argument("--apply", action="store_true", help="Write changes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes (default)")
    args = parser.parse_args()

    dry_run = not args.apply
    prefix = "[DRY RUN] " if dry_run else ""

    files_modified, items_enriched, items_skipped = migrate(args.repo, dry_run)

    print(f"{prefix}Summary:")
    print(f"  Files modified: {files_modified}")
    print(f"  Items enriched: {items_enriched}")
    print(f"  Items skipped (no analyzer_section): {items_skipped}")

    if dry_run and items_enriched > 0:
        print("\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
