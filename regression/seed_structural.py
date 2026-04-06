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
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
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
                        "pattern": f"^{re.escape(ref)}$",
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


def generate_spice_structural_assertions(data, strict=True):
    """Generate structural assertions from a SPICE simulation output.

    For each subcircuit type, asserts exact count. For each unique component
    ref, asserts presence with its subcircuit type.

    Returns list of assertion dicts.
    """
    results = data.get("simulation_results", [])
    if not results:
        return []

    assertions = []
    ast_num = 1

    # Count per subcircuit type
    by_type = {}
    for r in results:
        t = r.get("subcircuit_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    for stype, count in sorted(by_type.items()):
        if strict:
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"Exactly {count} {stype} simulation(s)",
                "check": {
                    "path": "simulation_results",
                    "op": "count_matches",
                    "field": "subcircuit_type",
                    "pattern": f"^{stype}$",
                    "value": count,
                },
            })
        else:
            lo = max(0, count - 1)
            hi = count + 1
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"~{count} {stype} simulation(s) (±1)",
                "check": {
                    "path": "simulation_results",
                    "op": "count_matches",
                    "field": "subcircuit_type",
                    "pattern": f"^{stype}$",
                    "value": count,
                },
            })
        ast_num += 1

    # Per-component-ref assertions: "R5 simulated as rc_filter"
    # The components field is a list, so str() produces "['R5', 'C3']".
    # Use word-boundary matching to find the ref within the stringified list.
    # Skip un-annotated refs (ending in ?) — they're not stable.
    seen = set()
    for r in results:
        stype = r.get("subcircuit_type", "unknown")
        for comp_ref in r.get("components", []):
            if comp_ref.endswith("?") or not re.match(r'^[A-Za-z0-9_]+$', comp_ref):
                continue
            key = (comp_ref, stype)
            if key in seen:
                continue
            seen.add(key)
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"{comp_ref} simulated as {stype}",
                "check": {
                    "path": "simulation_results",
                    "op": "contains_match",
                    "field": "components",
                    "pattern": rf"\b{re.escape(comp_ref)}\b",
                },
            })
            ast_num += 1

    return assertions


def generate_emc_structural_assertions(data, strict=True):
    """Generate structural assertions from EMC analysis output.

    For each category, asserts exact count of findings.
    For each unique rule_id, asserts presence.
    For each unique component ref in findings, asserts presence.
    """
    findings = data.get("findings", [])
    if not findings:
        return []

    assertions = []
    ast_num = 1

    # Per-category finding counts
    by_category = {}
    for f in findings:
        cat = f.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1

    for cat, count in sorted(by_category.items()):
        assertions.append({
            "id": f"STRUCT-{ast_num:08d}",
            "description": f"{count} {cat} finding(s)",
            "check": {
                "path": "findings",
                "op": "count_matches",
                "field": "category",
                "pattern": f"^{re.escape(cat)}$",
                "value": count,
            },
        })
        ast_num += 1

    # Per-rule_id presence
    rule_ids = sorted(set(f.get("rule_id", "") for f in findings if f.get("rule_id")))
    for rid in rule_ids:
        assertions.append({
            "id": f"STRUCT-{ast_num:08d}",
            "description": f"Rule {rid} present",
            "check": {
                "path": "findings",
                "op": "contains_match",
                "field": "rule_id",
                "pattern": f"^{re.escape(rid)}$",
            },
        })
        ast_num += 1

    # Per-component ref presence
    seen_refs = set()
    for f in findings:
        for comp_ref in f.get("components", []):
            if comp_ref.endswith("?") or not re.match(r'^[A-Za-z0-9_]+$', comp_ref):
                continue
            if comp_ref in seen_refs:
                continue
            seen_refs.add(comp_ref)
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"{comp_ref} in EMC findings",
                "check": {
                    "path": "findings",
                    "op": "contains_match",
                    "field": "components",
                    "pattern": rf"\b{re.escape(comp_ref)}\b",
                },
            })
            ast_num += 1

    return assertions


def generate_datasheets_structural_assertions(data, strict=True):
    """Generate structural assertions from a datasheets validation report.

    For each extracted MPN, asserts presence with category and minimum score.
    """
    parts = data.get("parts", {})
    if not parts:
        return []

    assertions = []
    ast_num = 1

    for mpn, info in sorted(parts.items()):
        score = info.get("score", 0)
        cat = info.get("category", "unknown")

        if info.get("sufficient"):
            assertions.append({
                "id": f"STRUCT-{ast_num:08d}",
                "description": f"{mpn} extracted as {cat} (score {score})",
                "check": {
                    "path": f"parts.{mpn}.score",
                    "op": "greater_than",
                    "value": 6.0,
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

            if atype == "spice":
                total_sims = data_content.get("summary", {}).get("total", 0)
                if total_sims < 1:
                    skipped += 1
                    continue
                assertions = generate_spice_structural_assertions(data_content, strict)
            elif atype == "emc":
                total_checks = data_content.get("summary", {}).get("total_checks", 0)
                if total_checks < 1:
                    skipped += 1
                    continue
                assertions = generate_emc_structural_assertions(data_content, strict)
            elif atype == "datasheets":
                extracted = data_content.get("extracted", 0)
                if extracted < 1:
                    skipped += 1
                    continue
                assertions = generate_datasheets_structural_assertions(data_content, strict)
            else:
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
            # file_pattern is the filename within the project (prefix stripped)
            prefix = project_prefix(proj_path)
            if prefix:
                file_pattern = output_file.stem[len(prefix):]
            else:
                file_pattern = output_file.stem

            out_dir = data_dir(repo_name, proj_name, "assertions") / atype
            out_file = out_dir / f"{file_pattern}_structural.json"

            if not assertions:
                # Remove stale structural file if it exists and was generated by us
                if out_file.exists():
                    try:
                        existing = json.loads(out_file.read_text())
                        if existing.get("generated_by") == "seed_structural.py":
                            out_file.unlink()
                    except (json.JSONDecodeError, OSError):
                        pass
                continue

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

            out_dir.mkdir(parents=True, exist_ok=True)

            # Only overwrite if generated by us
            if out_file.exists():
                existing = json.loads(out_file.read_text())
                if existing.get("generated_by") != "seed_structural.py":
                    continue

            out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")
            total_files += 1
            total_assertions += len(assertions)

    return total_files, total_assertions, skipped


def _structural_one_repo(repo, atype, strict, min_components, dry_run):
    """Worker function for parallel structural seeding. Must be top-level for pickling."""
    return generate_for_repo(repo, atype, strict, min_components, dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Generate structural assertions from signal analysis")
    group = add_repo_filter_args(parser)
    parser.add_argument("--all", action="store_true",
                        help="Generate for all repos")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Number of parallel workers (default: {DEFAULT_JOBS})")
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

    repos = resolve_repos(args)
    if repos is None:
        if args.all:
            repos = list_repos()
        else:
            parser.print_help()
            sys.exit(1)

    jobs = args.jobs
    grand_files = grand_assertions = grand_skipped = 0

    if jobs > 1 and len(repos) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(repos))) as pool:
            futures = {pool.submit(_structural_one_repo, repo, args.type,
                                   strict, args.min_components,
                                   args.dry_run): repo
                       for repo in repos}
            for future in as_completed(futures):
                files, assertions, skipped = future.result()
                grand_files += files
                grand_assertions += assertions
                grand_skipped += skipped
    else:
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
