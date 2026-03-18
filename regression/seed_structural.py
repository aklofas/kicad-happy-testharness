#!/usr/bin/env python3
"""Generate per-detection structural assertions from analyzer outputs.

For each signal analysis detection, generates:
- One contains_match assertion per unique component ref
- One equals assertion for the exact count of detections

Output files: reference/{repo}/{project}/assertions/{type}/{file}_structural.json

Usage:
    python3 regression/seed_structural.py --repo hackrf
    python3 regression/seed_structural.py --all
    python3 regression/seed_structural.py --repo hackrf --tolerant
    python3 regression/seed_structural.py --repo hackrf --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    discover_projects, data_dir, list_repos,
    project_prefix, filter_project_outputs,
)
from regression.refextract import REF_FIELD_MAP, PCB_REF_FIELD_MAP, get_ref_from_item


def generate_structural_assertions(data, strict=True):
    """Generate structural assertions from a schematic analyzer output.

    Returns list of assertion dicts.
    """
    sa = data.get("signal_analysis", {})
    if not sa:
        return []

    assertions = []
    ast_num = 1

    for det_name, items in sorted(sa.items()):
        if not isinstance(items, list) or not items:
            continue

        # Count assertion
        count = len(items)
        if strict:
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"Exactly {count} {det_name}",
                "check": {
                    "path": f"signal_analysis.{det_name}",
                    "op": "equals",
                    "value": count,
                },
            })
        else:
            lo = max(0, count - 1)
            hi = count + 1
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"~{count} {det_name} (±1)",
                "check": {
                    "path": f"signal_analysis.{det_name}",
                    "op": "range",
                    "min": lo,
                    "max": hi,
                },
            })
        ast_num += 1

        # Per-ref assertions
        ref_field = REF_FIELD_MAP.get(det_name)
        if not ref_field:
            continue

        seen_refs = set()
        for item in items:
            ref = get_ref_from_item(det_name, item)
            if ref and ref not in seen_refs:
                seen_refs.add(ref)
                assertions.append({
                    "id": f"STRUCT-{ast_num:08d}",
                    "description": f"{ref} in {det_name}",
                    "check": {
                        "path": f"signal_analysis.{det_name}",
                        "op": "contains_match",
                        "field": ref_field,
                        "pattern": f"^{ref}$",
                    },
                })
                ast_num += 1

    return assertions


def generate_pcb_structural_assertions(data, strict=True):
    """Generate structural assertions from a PCB analyzer output.

    Covers: decoupling_placement, thermal_pad_vias,
    thermal_analysis.thermal_pads, tombstoning_risk.

    Returns list of assertion dicts.
    """
    assertions = []
    ast_num = 1

    for section_path, ref_field in sorted(PCB_REF_FIELD_MAP.items()):
        # Navigate dotted path (e.g., "thermal_analysis.thermal_pads")
        parts = section_path.split(".")
        items = data
        for part in parts:
            if isinstance(items, dict):
                items = items.get(part)
            else:
                items = None
                break

        if not isinstance(items, list) or not items:
            continue

        # Count assertion
        count = len(items)
        if strict:
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"Exactly {count} {section_path}",
                "check": {
                    "path": section_path,
                    "op": "equals",
                    "value": count,
                },
            })
        else:
            lo = max(0, count - 1)
            hi = count + 1
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"~{count} {section_path} (±1)",
                "check": {
                    "path": section_path,
                    "op": "range",
                    "min": lo,
                    "max": hi,
                },
            })
        ast_num += 1

        # Per-ref assertions
        seen_refs = set()
        for item in items:
            ref = item.get(ref_field)
            if ref and ref not in seen_refs:
                seen_refs.add(ref)
                assertions.append({
                    "id": f"STRUCT-{ast_num:08d}",
                    "description": f"{ref} in {section_path}",
                    "check": {
                        "path": section_path,
                        "op": "contains_match",
                        "field": ref_field,
                        "pattern": f"^{re.escape(ref)}$",
                    },
                })
                ast_num += 1

    return assertions


def generate_for_repo(repo_name, atype, strict, min_components,
                      dry_run):
    """Generate structural assertions for one repo."""
    type_dir = OUTPUTS_DIR / atype / repo_name
    if not type_dir.exists():
        return 0, 0, 0

    projects = discover_projects(repo_name)
    if not projects:
        return 0, 0, 0

    total_files = 0
    total_assertions = 0
    skipped = 0

    for proj in projects:
        proj_name = proj["name"]
        proj_path = proj["path"]

        proj_outputs = filter_project_outputs(type_dir, proj_path)

        for output_file in proj_outputs:
            try:
                data_content = json.loads(output_file.read_text())
            except Exception:
                continue

            stats = data_content.get("statistics", {})
            comps = (stats.get("total_components", 0)
                     or stats.get("footprint_count", 0))
            if comps < min_components:
                skipped += 1
                continue

            if atype == "schematic":
                assertions = generate_structural_assertions(data_content, strict)
            elif atype == "pcb":
                assertions = generate_pcb_structural_assertions(data_content, strict)
            else:
                continue
            if not assertions:
                continue

            # file_pattern is the filename within the project (prefix stripped)
            prefix = project_prefix(proj_path)
            if prefix:
                file_pattern = output_file.stem[len(prefix):]
            else:
                file_pattern = output_file.stem

            assertion_data = {
                "file_pattern": file_pattern,
                "analyzer_type": atype,
                "generated_by": "seed_structural.py",
                "assertions": assertions,
            }

            if dry_run:
                print(f"  {repo_name}/{proj_name}: {file_pattern} "
                      f"({len(assertions)} assertions)")
                total_files += 1
                total_assertions += len(assertions)
                continue

            out_dir = data_dir(repo_name, proj_name, "assertions") / atype
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{file_pattern}_structural.json"

            # Only overwrite if generated by us
            if out_file.exists():
                existing = json.loads(out_file.read_text())
                if existing.get("generated_by") != "seed_structural.py":
                    continue

            out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")
            total_files += 1
            total_assertions += len(assertions)

    return total_files, total_assertions, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Generate structural assertions from signal analysis")
    parser.add_argument("--repo", help="Generate for one repo")
    parser.add_argument("--all", action="store_true",
                        help="Generate for all repos")
    parser.add_argument("--type", choices=ANALYZER_TYPES,
                        default="schematic",
                        help="Analyzer type (default: schematic)")
    parser.add_argument("--strict", action="store_true", default=True,
                        help="Use exact counts (default)")
    parser.add_argument("--tolerant", action="store_true",
                        help="Use ±1 range for counts")
    parser.add_argument("--min-components", type=int, default=10,
                        help="Skip files with fewer components (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print without writing files")
    args = parser.parse_args()

    strict = not args.tolerant

    if args.repo:
        repos = [args.repo]
    elif args.all:
        repos = list_repos()
    else:
        parser.print_help()
        sys.exit(1)

    grand_files = grand_assertions = grand_skipped = 0
    for repo in repos:
        files, assertions, skipped = generate_for_repo(
            repo, args.type, strict, args.min_components, args.dry_run)
        grand_files += files
        grand_assertions += assertions
        grand_skipped += skipped

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}"
          f"Generated {grand_assertions} structural assertions "
          f"across {grand_files} files (skipped {grand_skipped} small files)")


if __name__ == "__main__":
    main()
