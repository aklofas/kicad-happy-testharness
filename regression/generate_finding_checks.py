#!/usr/bin/env python3
"""Auto-generate check fields for finding items using refextract.

For each finding item with an analyzer_section:
- correct item with refs -> contains_match (verify ref IS in section)
- incorrect item with refs -> not_contains_match (verify ref is NOT there)
- missed item with refs -> contains_match (verify ref IS now detected)
- items without extractable refs -> section-level exists/not_exists

Writes check fields directly into findings.json items. Re-renders findings.md.

Usage:
    python3 regression/generate_finding_checks.py                   # all findings (dry-run)
    python3 regression/generate_finding_checks.py --apply           # write changes
    python3 regression/generate_finding_checks.py --repo hackrf     # one repo
    python3 regression/generate_finding_checks.py --dry-run         # preview (default)
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from regression.refextract import extract_refs, extract_refs_ordered, REF_FIELD_MAP
from regression.findings import _iter_findings_files, save_findings


def _detect_ref_field(detector_name):
    """Determine the ref field path for a given detector name.

    E.g., "detect_opamp_circuits" -> "reference"
          "detect_voltage_dividers" -> "r_top.ref"

    Returns the field path for use with contains_match, or None.
    """
    return REF_FIELD_MAP.get(detector_name)


# Map field paths to preferred ref prefixes
_FIELD_PREFIX_HINTS = {
    "resistor.ref": {"R", "RN", "RV", "VR"},
    "r_top.ref": {"R", "RN", "RV", "VR"},
    "r_bottom.ref": {"R", "RN", "RV", "VR"},
    "inductor.ref": {"L", "FB", "FL"},
    "capacitor.ref": {"C"},
    "shunt": {"R", "RN"},
    "shunt.ref": {"R", "RN"},
}

# Crystal circuits use Y or X prefixes
_DETECTOR_PREFIX_HINTS = {
    "detect_crystal_circuits": {"Y", "X"},
    "detect_power_regulators": {"U", "IC"},
    "detect_led_drivers": {"U", "IC", "Q", "D"},
    "detect_transistor_circuits": {"Q", "T"},
    "detect_opamp_circuits": {"U", "IC"},
    "detect_bms_systems": {"U", "IC"},
    "detect_memory_interfaces": {"U", "IC"},
}


def _pick_best_ref(refs, ref_field, detector_name):
    """Pick the most appropriate ref from a list for a given field/detector.

    Prefers refs whose prefix matches the expected component type for the field.
    Falls back to the first ref if no match.
    """
    if not refs:
        return None
    if len(refs) == 1:
        return refs[0]

    # Check field-level hints first
    preferred_prefixes = _FIELD_PREFIX_HINTS.get(ref_field)
    if not preferred_prefixes:
        preferred_prefixes = _DETECTOR_PREFIX_HINTS.get(detector_name)

    if preferred_prefixes:
        for ref in refs:
            prefix = ""
            for c in ref:
                if c.isalpha():
                    prefix += c
                else:
                    break
            if prefix in preferred_prefixes:
                return ref

    return refs[0]


def _check_from_structured(item, item_type):
    """Generate a check dict from structured finding fields."""
    detector = item.get("detector", "")
    refs = item.get("subject_refs", [])
    relation = item.get("expected_relation", "")

    def _base():
        return {"path": "findings", "detector_filter": detector}

    if relation == "in_detector":
        ref_field = REF_FIELD_MAP.get(detector)
        if refs and ref_field:
            ref = _pick_best_ref(refs, ref_field, detector)
            op = "contains_match" if item_type != "incorrect" else "not_contains_match"
            return {**_base(), "op": op, "field": ref_field,
                    "pattern": f"^{re.escape(ref)}$"}
        if refs and not ref_field:
            return None
        return {**_base(), "op": "min_count", "value": 1}

    elif relation == "not_in_detector":
        ref_field = REF_FIELD_MAP.get(detector)
        if refs and ref_field:
            ref = _pick_best_ref(refs, ref_field, detector)
            return {**_base(), "op": "not_contains_match", "field": ref_field,
                    "pattern": f"^{re.escape(ref)}$"}
        return None

    elif relation == "field_value_equals":
        field = item.get("field")
        value = item.get("expected_value")
        if field is not None and value is not None:
            return {**_base(), "op": "field_equals", "field": field, "value": value}
        return None

    elif relation == "count_equals":
        value = item.get("expected_value")
        if value is not None:
            return {**_base(), "op": "equals", "value": value}
        return None

    elif relation == "section_exists":
        if item_type == "incorrect":
            return {**_base(), "op": "max_count", "value": 0}
        return {**_base(), "op": "min_count", "value": 1}

    return None


def _generate_check_for_item(item, item_type):
    """Generate a check dict for a finding item.

    item_type: "correct", "incorrect", or "missed"
    Returns check dict or None.
    """
    # Structured path — deterministic, no heuristics
    if item.get("expected_relation") and item.get("detector"):
        return _check_from_structured(item, item_type)

    section = item.get("analyzer_section", "")
    desc = item.get("description", "")
    if not section:
        return None

    # Extract detector name from section path.
    # Old format: "signal_analysis.voltage_dividers" -> map to full detector name
    # New format: "detect_voltage_dividers" -> use directly
    parts = section.split(".")
    if len(parts) >= 2 and parts[0] == "signal_analysis":
        detector_name = parts[1]
        # Find the full detector name in REF_FIELD_MAP (keyed by full name)
        full_name = None
        for key in REF_FIELD_MAP:
            if key.endswith(detector_name) or key.endswith("_" + detector_name):
                full_name = key
                break
        if not full_name:
            full_name = f"detect_{detector_name}"
        detector_name = full_name
    else:
        detector_name = section

    refs = extract_refs_ordered(desc)
    ref_field = _detect_ref_field(detector_name)

    base = {"path": "findings", "detector_filter": detector_name}

    if refs and ref_field:
        ref = _pick_best_ref(refs, ref_field, detector_name)
        if item_type == "correct":
            return {**base, "op": "contains_match", "field": ref_field,
                    "pattern": f"^{re.escape(ref)}$"}
        elif item_type == "incorrect":
            return {**base, "op": "not_contains_match", "field": ref_field,
                    "pattern": f"^{re.escape(ref)}$"}
        elif item_type == "missed":
            return {**base, "op": "contains_match", "field": ref_field,
                    "pattern": f"^{re.escape(ref)}$"}
    else:
        if item_type == "correct":
            return {**base, "op": "min_count", "value": 1}
        elif item_type == "incorrect":
            return None
        elif item_type == "missed":
            return {**base, "op": "min_count", "value": 1}

    return None


def generate_checks(repo_name=None, dry_run=True):
    """Generate check fields for all finding items.

    Returns (findings_updated, items_with_checks, items_skipped).
    """
    findings_updated = 0
    items_with_checks = 0
    items_skipped = 0

    for repo, proj, ff in _iter_findings_files(repo_name):
        data = json.loads(ff.read_text(encoding="utf-8"))
        modified = False

        for finding in data.get("findings", []):
            for item_type in ("correct", "incorrect", "missed"):
                for item in finding.get(item_type, []):
                    # Skip items that already have a check
                    if "check" in item:
                        continue

                    check = _generate_check_for_item(item, item_type)
                    if check:
                        if not dry_run:
                            item["check"] = check
                        items_with_checks += 1
                        modified = True
                        if dry_run:
                            desc = item.get("description", "")[:60]
                            fid = finding.get("id", "?")
                            print(f"  {fid} {item_type}: {desc}")
                            print(f"    -> {json.dumps(check)}")
                    else:
                        items_skipped += 1

        if modified:
            findings_updated += 1
            if not dry_run:
                save_findings(repo, proj, data)

    return findings_updated, items_with_checks, items_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Generate check fields for finding items")
    parser.add_argument("--repo", help="Filter by repo name")
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing (default)")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("[DRY RUN] Preview of checks to generate:\n")

    findings_updated, items_with_checks, items_skipped = generate_checks(
        args.repo, dry_run)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Findings files modified: {findings_updated}")
    print(f"  Items with checks generated: {items_with_checks}")
    print(f"  Items skipped (no section or no refs): {items_skipped}")

    if dry_run and items_with_checks > 0:
        print("\nRun with --apply to write changes.")


if __name__ == "__main__":
    main()
