#!/usr/bin/env python3
"""Schema validation for analyzer outputs — field inventory and drift detection.

Scans analyzer outputs to build a per-detector field inventory, saves it as a
reference snapshot, and on subsequent runs diffs against the saved inventory to
detect field additions, removals, or renames.

Usage:
    python3 validate/validate_schema.py scan              # Build/update inventory
    python3 validate/validate_schema.py scan --repo X     # Scan one repo only
    python3 validate/validate_schema.py diff              # Diff current vs saved
    python3 validate/validate_schema.py diff --repo X     # Diff one repo only
    python3 validate/validate_schema.py diff --json       # Machine-readable output
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, DATA_DIR, list_repos


INVENTORY_FILE = DATA_DIR / "schema_inventory.json"

# Analyzer types that have signal_analysis detectors
SCHEMATIC_DETECTORS_PATH = "signal_analysis"
PCB_SECTIONS = [
    "connectivity", "dfm", "thermal_analysis", "assembly_analysis",
]


def _collect_fields(items):
    """Collect all field names from a list of dicts, returning {field: count}."""
    fields = defaultdict(int)
    for item in items:
        if isinstance(item, dict):
            for key in item:
                fields[key] += 1
    return dict(fields)


def scan_schematic_outputs(repos):
    """Scan schematic outputs and build field inventory for signal_analysis detectors.

    Returns {detector_name: {field_name: count_of_items_with_field}}.
    """
    inventory = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for repo in repos:
        repo_dir = OUTPUTS_DIR / "schematic" / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            sa = data.get(SCHEMATIC_DETECTORS_PATH, {})
            if not isinstance(sa, dict):
                continue

            for detector, items in sa.items():
                if not isinstance(items, list):
                    # Some detectors (decoupling_analysis) can be a dict
                    if isinstance(items, dict):
                        for key in items:
                            inventory[detector][key] += 1
                    continue
                for item in items:
                    if isinstance(item, dict):
                        for key in item:
                            inventory[detector][key] += 1

    return dict({k: dict(v) for k, v in inventory.items()}), file_count


def scan_pcb_outputs(repos):
    """Scan PCB outputs and build field inventory for key sections.

    Returns {section.subsection: {field_name: count}}.
    """
    inventory = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for repo in repos:
        repo_dir = OUTPUTS_DIR / "pcb" / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            for section in PCB_SECTIONS:
                sec_data = data.get(section, {})
                if isinstance(sec_data, dict):
                    for subsection, items in sec_data.items():
                        key = f"{section}.{subsection}"
                        if isinstance(items, list):
                            for item in items:
                                if isinstance(item, dict):
                                    for field in item:
                                        inventory[key][field] += 1
                        elif isinstance(items, dict):
                            for field in items:
                                inventory[key][field] += 1

    return dict({k: dict(v) for k, v in inventory.items()}), file_count


def build_inventory(repos):
    """Build complete schema inventory from outputs.

    Returns dict with metadata and per-type field inventories.
    """
    sch_inv, sch_count = scan_schematic_outputs(repos)
    pcb_inv, pcb_count = scan_pcb_outputs(repos)

    return {
        "metadata": {
            "schematic_files_scanned": sch_count,
            "pcb_files_scanned": pcb_count,
            "schematic_detectors": len(sch_inv),
            "pcb_sections": len(pcb_inv),
        },
        "schematic": sch_inv,
        "pcb": pcb_inv,
    }


def diff_inventories(saved, current):
    """Diff two inventories, returning changes per detector/section.

    Returns list of {detector, change_type, field, details}.
    change_type is one of: "added", "removed", "count_changed".
    """
    changes = []

    for category in ("schematic", "pcb"):
        saved_cat = saved.get(category, {})
        current_cat = current.get(category, {})

        all_detectors = set(saved_cat) | set(current_cat)
        for detector in sorted(all_detectors):
            saved_fields = set(saved_cat.get(detector, {}))
            current_fields = set(current_cat.get(detector, {}))

            # New detector
            if detector not in saved_cat:
                changes.append({
                    "category": category,
                    "detector": detector,
                    "change_type": "new_detector",
                    "field": None,
                    "details": f"{len(current_fields)} fields",
                })
                continue

            # Removed detector
            if detector not in current_cat:
                changes.append({
                    "category": category,
                    "detector": detector,
                    "change_type": "removed_detector",
                    "field": None,
                    "details": f"had {len(saved_fields)} fields",
                })
                continue

            # Added fields
            for field in sorted(current_fields - saved_fields):
                count = current_cat[detector][field]
                changes.append({
                    "category": category,
                    "detector": detector,
                    "change_type": "added",
                    "field": field,
                    "details": f"appears in {count} items",
                })

            # Removed fields
            for field in sorted(saved_fields - current_fields):
                prev_count = saved_cat[detector][field]
                changes.append({
                    "category": category,
                    "detector": detector,
                    "change_type": "removed",
                    "field": field,
                    "details": f"was in {prev_count} items",
                })

    # Heuristic: detect renames (field removed + field added in same detector)
    for change in list(changes):
        if change["change_type"] == "removed":
            # Look for a matching "added" in same detector
            for other in changes:
                if (other["change_type"] == "added"
                        and other["detector"] == change["detector"]
                        and other["category"] == change["category"]):
                    change["details"] += f" (possible rename → {other['field']}?)"
                    break

    return changes


def cmd_scan(args):
    """Build/update schema inventory from current outputs."""
    repos = [args.repo] if args.repo else list_repos()
    if not repos:
        print("No repos found. Run checkout.py first.", file=sys.stderr)
        sys.exit(1)

    inventory = build_inventory(repos)

    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        meta = inventory["metadata"]
        print(f"Scanned {meta['schematic_files_scanned']} schematic files, "
              f"{meta['pcb_files_scanned']} PCB files")
        print(f"Found {meta['schematic_detectors']} schematic detectors, "
              f"{meta['pcb_sections']} PCB sections")
        print()

        for category in ("schematic", "pcb"):
            cat_data = inventory[category]
            if not cat_data:
                continue
            print(f"=== {category.upper()} ===")
            for det in sorted(cat_data):
                fields = cat_data[det]
                print(f"  {det}: {sorted(fields.keys())}")
            print()

    if not args.repo:
        # Save full inventory (not per-repo scans)
        INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY_FILE.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
        if not args.json:
            print(f"Saved inventory to {INVENTORY_FILE}")


def cmd_diff(args):
    """Diff current outputs against saved inventory."""
    if not INVENTORY_FILE.exists():
        print(f"No saved inventory at {INVENTORY_FILE}. Run 'scan' first.",
              file=sys.stderr)
        sys.exit(1)

    saved = json.loads(INVENTORY_FILE.read_text())
    repos = [args.repo] if args.repo else list_repos()
    current = build_inventory(repos)

    changes = diff_inventories(saved, current)

    if args.json:
        result = {
            "total_changes": len(changes),
            "changes": changes,
            "saved_metadata": saved.get("metadata", {}),
            "current_metadata": current.get("metadata", {}),
        }
        print(json.dumps(result, indent=2))
    else:
        saved_meta = saved.get("metadata", {})
        current_meta = current.get("metadata", {})
        print(f"Saved:   {saved_meta.get('schematic_files_scanned', '?')} schematic, "
              f"{saved_meta.get('pcb_files_scanned', '?')} PCB files")
        print(f"Current: {current_meta.get('schematic_files_scanned', '?')} schematic, "
              f"{current_meta.get('pcb_files_scanned', '?')} PCB files")
        print()

        if not changes:
            print("NO SCHEMA CHANGES DETECTED")
            return

        print(f"SCHEMA CHANGES ({len(changes)}):")
        print()
        for c in changes:
            prefix = f"[{c['category']}] {c['detector']}"
            if c["field"]:
                print(f"  {c['change_type']:18s} {prefix}.{c['field']} — {c['details']}")
            else:
                print(f"  {c['change_type']:18s} {prefix} — {c['details']}")

    sys.exit(1 if changes else 0)


def main():
    parser = argparse.ArgumentParser(
        description="Schema validation — field inventory and drift detection"
    )
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="Build/update field inventory from outputs")
    scan_p.add_argument("--repo", help="Scan one repo only")
    scan_p.add_argument("--json", action="store_true", help="JSON output")

    diff_p = sub.add_parser("diff", help="Diff current outputs vs saved inventory")
    diff_p.add_argument("--repo", help="Diff one repo only")
    diff_p.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "diff":
        cmd_diff(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
