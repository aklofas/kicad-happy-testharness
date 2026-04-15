#!/usr/bin/env python3
"""Schema validation for analyzer outputs — field inventory and drift detection.

Scans analyzer outputs to build a per-detector field inventory, saves it as a
reference snapshot, and on subsequent runs diffs against the saved inventory to
detect field additions, removals, or renames.

Usage:
    python3 validate/validate_schema.py scan                              # Build/update inventory
    python3 validate/validate_schema.py scan --repo owner/repo            # Scan one repo only
    python3 validate/validate_schema.py scan --cross-section smoke -j 16  # Parallel scan
    python3 validate/validate_schema.py diff                              # Diff current vs saved
    python3 validate/validate_schema.py diff --repo owner/repo            # Diff one repo only
    python3 validate/validate_schema.py diff --json                       # Machine-readable output
"""

import argparse
import json
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, DATA_DIR, list_repos,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos)


INVENTORY_FILE = DATA_DIR / "schema_inventory.json"

# Analyzer types that have findings detectors
SCHEMATIC_DETECTORS_PATH = "findings"
PCB_SECTIONS = [
    "connectivity", "dfm_summary", "placement_density",
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
    """Scan schematic outputs and build field inventory for findings detectors.

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
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            findings = data.get(SCHEMATIC_DETECTORS_PATH, [])
            if not isinstance(findings, list):
                continue

            for item in findings:
                if not isinstance(item, dict):
                    continue
                detector = item.get("detector", "")
                if not detector:
                    continue
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
                data = json.loads(f.read_text(encoding="utf-8"))
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


def scan_spice_outputs(repos):
    """Scan SPICE outputs and build field inventory for simulation_results items.

    Returns {section: {field_name: count}}.
    """
    inventory = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for repo in repos:
        repo_dir = OUTPUTS_DIR / "spice" / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            for item in data.get("simulation_results", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["simulation_results"][key] += 1

    return dict({k: dict(v) for k, v in inventory.items()}), file_count


def scan_emc_outputs(repos):
    """Scan EMC outputs and build field inventory for findings and other sections.

    Returns {section: {field_name: count}}.
    """
    inventory = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for repo in repos:
        repo_dir = OUTPUTS_DIR / "emc" / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            for item in data.get("findings", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["findings"][key] += 1
            for item in data.get("per_net_scores", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["per_net_scores"][key] += 1
            for item in data.get("component_suggestions", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["component_suggestions"][key] += 1

    return dict({k: dict(v) for k, v in inventory.items()}), file_count


# Gerber top-level dict sections to inventory field-by-field
GERBER_DICT_SECTIONS = [
    "statistics", "completeness", "alignment", "drill_classification",
    "pad_summary", "component_analysis",
]

def scan_gerber_outputs(repos):
    """Scan gerber outputs and build field inventory.

    Returns {section: {field_name: count}}.
    """
    inventory = defaultdict(lambda: defaultdict(int))
    file_count = 0

    for repo in repos:
        repo_dir = OUTPUTS_DIR / "gerber" / repo
        if not repo_dir.exists():
            continue
        for f in repo_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            file_count += 1
            # Dict sections: count which fields are present
            for section in GERBER_DICT_SECTIONS:
                sec_data = data.get(section, {})
                if isinstance(sec_data, dict):
                    for key in sec_data:
                        inventory[section][key] += 1
            # List sections: count fields in items
            for item in data.get("gerbers", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["gerbers"][key] += 1
            for item in data.get("drills", []):
                if isinstance(item, dict):
                    for key in item:
                        inventory["drills"][key] += 1

    return dict({k: dict(v) for k, v in inventory.items()}), file_count


def _scan_one_repo(repo):
    """Scan all output types for a single repo. Picklable top-level worker.

    Returns dict with per-type inventories and file counts.
    """
    sch_inv, sch_count = scan_schematic_outputs([repo])
    pcb_inv, pcb_count = scan_pcb_outputs([repo])
    spice_inv, spice_count = scan_spice_outputs([repo])
    emc_inv, emc_count = scan_emc_outputs([repo])
    gerber_inv, gerber_count = scan_gerber_outputs([repo])
    return {
        "schematic": (sch_inv, sch_count),
        "pcb": (pcb_inv, pcb_count),
        "spice": (spice_inv, spice_count),
        "emc": (emc_inv, emc_count),
        "gerber": (gerber_inv, gerber_count),
    }


def _merge_inventories(target, source):
    """Merge source inventory dict into target (both are {detector: {field: count}})."""
    for det, fields in source.items():
        if det not in target:
            target[det] = {}
        for field, count in fields.items():
            target[det][field] = target[det].get(field, 0) + count


def build_inventory(repos, jobs=1):
    """Build complete schema inventory from outputs.

    Returns dict with metadata and per-type field inventories.
    """
    type_names = ["schematic", "pcb", "spice", "emc", "gerber"]
    merged = {t: ({}, 0) for t in type_names}

    if jobs > 1 and len(repos) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
            futures = {pool.submit(_scan_one_repo, repo): repo for repo in repos}
            for future in as_completed(futures):
                result = future.result()
                for t in type_names:
                    inv, count = result[t]
                    cur_inv, cur_count = merged[t]
                    _merge_inventories(cur_inv, inv)
                    merged[t] = (cur_inv, cur_count + count)
    else:
        for repo in repos:
            result = _scan_one_repo(repo)
            for t in type_names:
                inv, count = result[t]
                cur_inv, cur_count = merged[t]
                _merge_inventories(cur_inv, inv)
                merged[t] = (cur_inv, cur_count + count)

    sch_inv, sch_count = merged["schematic"]
    pcb_inv, pcb_count = merged["pcb"]
    spice_inv, spice_count = merged["spice"]
    emc_inv, emc_count = merged["emc"]
    gerber_inv, gerber_count = merged["gerber"]

    return {
        "metadata": {
            "schematic_files_scanned": sch_count,
            "pcb_files_scanned": pcb_count,
            "spice_files_scanned": spice_count,
            "emc_files_scanned": emc_count,
            "gerber_files_scanned": gerber_count,
            "schematic_detectors": len(sch_inv),
            "pcb_sections": len(pcb_inv),
            "spice_sections": len(spice_inv),
            "emc_sections": len(emc_inv),
            "gerber_sections": len(gerber_inv),
        },
        "schematic": sch_inv,
        "pcb": pcb_inv,
        "spice": spice_inv,
        "emc": emc_inv,
        "gerber": gerber_inv,
    }


def diff_inventories(saved, current):
    """Diff two inventories, returning changes per detector/section.

    Returns list of {detector, change_type, field, details}.
    change_type is one of: "added", "removed", "count_changed".
    """
    changes = []

    for category in ("schematic", "pcb", "spice", "emc", "gerber"):
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

            # Added fields (skip internal _-prefixed metadata fields)
            for field in sorted(current_fields - saved_fields):
                if field.startswith("_"):
                    continue
                count = current_cat[detector][field]
                changes.append({
                    "category": category,
                    "detector": detector,
                    "change_type": "added",
                    "field": field,
                    "details": f"appears in {count} items",
                })

            # Removed fields (skip internal _-prefixed metadata fields)
            for field in sorted(saved_fields - current_fields):
                if field.startswith("_"):
                    continue
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
    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()
    if not repos:
        print("No repos found. Run checkout.py first.", file=sys.stderr)
        sys.exit(1)

    jobs = getattr(args, "jobs", 1)
    inventory = build_inventory(repos, jobs=jobs)

    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        meta = inventory["metadata"]
        print(f"Scanned: {meta['schematic_files_scanned']} schematic, "
              f"{meta['pcb_files_scanned']} PCB, "
              f"{meta.get('spice_files_scanned', 0)} SPICE, "
              f"{meta.get('emc_files_scanned', 0)} EMC, "
              f"{meta.get('gerber_files_scanned', 0)} gerber files")
        print(f"Found: {meta['schematic_detectors']} schematic detectors, "
              f"{meta['pcb_sections']} PCB, "
              f"{meta.get('spice_sections', 0)} SPICE, "
              f"{meta.get('emc_sections', 0)} EMC, "
              f"{meta.get('gerber_sections', 0)} gerber sections")
        print()

        for category in ("schematic", "pcb", "spice", "emc", "gerber"):
            cat_data = inventory.get(category, {})
            if not cat_data:
                continue
            print(f"=== {category.upper()} ===")
            for det in sorted(cat_data):
                fields = cat_data[det]
                print(f"  {det}: {sorted(fields.keys())}")
            print()

    if not (getattr(args, "repo", None) or getattr(args, "cross_section", None)
            or getattr(args, "repo_list", None)):
        # Save full inventory (not per-repo or cross-section scans)
        INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY_FILE.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not args.json:
            print(f"Saved inventory to {INVENTORY_FILE}")


def cmd_diff(args):
    """Diff current outputs against saved inventory."""
    if not INVENTORY_FILE.exists():
        print(f"No saved inventory at {INVENTORY_FILE}. Run 'scan' first.",
              file=sys.stderr)
        sys.exit(1)

    saved = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()
    jobs = getattr(args, "jobs", 1)
    current = build_inventory(repos, jobs=jobs)

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
        for label, meta in [("Saved", saved_meta), ("Current", current_meta)]:
            parts = []
            for key, name in [("schematic_files_scanned", "sch"),
                              ("pcb_files_scanned", "pcb"),
                              ("spice_files_scanned", "spice"),
                              ("emc_files_scanned", "emc"),
                              ("gerber_files_scanned", "gerber")]:
                val = meta.get(key, 0)
                if val:
                    parts.append(f"{val} {name}")
            print(f"{label:8s} {', '.join(parts)} files")
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


def find_stale_assertions(changes):
    """Find assertion files that reference removed fields.

    Returns list of {assertion_file, assertion_id, removed_field, detector}.
    """
    removed_fields = {}
    for c in changes:
        if c["change_type"] == "removed" and c["field"]:
            key = (c["category"], c["detector"], c["field"])
            removed_fields[key] = c

    if not removed_fields:
        return []

    stale = []
    for f in DATA_DIR.rglob("assertions/*/*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        atype = data.get("analyzer_type", "schematic")
        for a in data.get("assertions", []):
            path = a.get("check", {}).get("path", "")
            # Check if path references a removed field
            for (cat, det, field), change in removed_fields.items():
                if cat == atype and f"{det}" in path and field in path:
                    stale.append({
                        "assertion_file": str(f),
                        "assertion_id": a.get("id", "?"),
                        "removed_field": f"{det}.{field}",
                        "detector": det,
                    })
    return stale


def generate_seed_for_new_fields(changes):
    """Generate exists-assertions for newly added fields.

    Returns list of assertion dicts ready to write.
    """
    assertions = []
    for c in changes:
        if c["change_type"] != "added" or not c["field"]:
            continue
        det = c["detector"]
        field = c["field"]
        cat = c["category"]
        if cat == "schematic":
            path = f"findings.{det}"
        else:
            path = det
        assertions.append({
            "id": f"DRIFT-{len(assertions)+1:04d}",
            "description": f"New field {field} in {cat}/{det} (detected by schema drift)",
            "check": {"path": path, "op": "exists"},
            "aspirational": True,
        })
    return assertions


def cmd_auto_seed(args):
    """Auto-generate assertions for schema drift."""
    if not INVENTORY_FILE.exists():
        print(f"No saved inventory. Run 'scan' first.", file=sys.stderr)
        sys.exit(1)

    saved = json.loads(INVENTORY_FILE.read_text(encoding="utf-8"))
    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()
    jobs = getattr(args, "jobs", 1)
    current = build_inventory(repos, jobs=jobs)
    changes = diff_inventories(saved, current)

    if not changes:
        print("No schema drift detected.")
        return

    # New field assertions
    new_assertions = generate_seed_for_new_fields(changes)
    # Stale assertion scan
    stale = find_stale_assertions(changes)

    added = [c for c in changes if c["change_type"] == "added"]
    removed = [c for c in changes if c["change_type"] == "removed"]

    print(f"Schema drift: {len(added)} new fields, {len(removed)} removed fields")
    if new_assertions:
        print(f"\nNew assertions to generate ({len(new_assertions)}):")
        for a in new_assertions[:10]:
            print(f"  {a['id']}: {a['description']}")
        if len(new_assertions) > 10:
            print(f"  ... and {len(new_assertions) - 10} more")

    if stale:
        print(f"\nStale assertions referencing removed fields ({len(stale)}):")
        for s in stale[:10]:
            print(f"  {s['assertion_id']} in {Path(s['assertion_file']).name}: "
                  f"references removed {s['removed_field']}")
        if len(stale) > 10:
            print(f"  ... and {len(stale) - 10} more")

    if not new_assertions and not stale:
        print("No actionable drift detected.")


def main():
    parser = argparse.ArgumentParser(
        description="Schema validation — field inventory and drift detection"
    )
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="Build/update field inventory from outputs")
    add_repo_filter_args(scan_p)
    scan_p.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    scan_p.add_argument("--json", action="store_true", help="JSON output")

    diff_p = sub.add_parser("diff", help="Diff current outputs vs saved inventory")
    add_repo_filter_args(diff_p)
    diff_p.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    diff_p.add_argument("--json", action="store_true", help="JSON output")

    auto_p = sub.add_parser("auto-seed",
                            help="Generate assertions for new fields, flag stale refs")
    add_repo_filter_args(auto_p)
    auto_p.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "diff":
        cmd_diff(args)
    elif args.command == "auto-seed":
        cmd_auto_seed(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
