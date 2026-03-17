#!/usr/bin/env python3
"""Generate seed assertions from existing analyzer outputs.

Reads schematic/pcb/gerber outputs and creates conservative assertions
that should remain stable across analyzer changes. Useful for
bootstrapping the assertion set for newly tested repos.

Outputs are in results/outputs/{type}/{repo}/.
Assertions are written to data/{repo}/{project}/assertions/{type}/.

Usage:
    python3 regression/seed.py --repo OpenMower
    python3 regression/seed.py --repo OpenMower --type schematic
    python3 regression/seed.py --all
    python3 regression/seed.py --repo OpenMower --filter "dcdc*"
    python3 regression/seed.py --tolerance 0.15
"""

import argparse
import fnmatch
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    discover_projects, data_dir, list_repos,
    project_prefix, filter_project_outputs,
)


def _range_bounds(value, tolerance):
    """Compute [lo, hi] range with tolerance around a value."""
    lo = max(0, math.floor(value * (1 - tolerance)))
    hi = math.ceil(value * (1 + tolerance))
    # Ensure minimum spread of 2 for small values
    if hi - lo < 2 and value > 0:
        lo = max(0, value - 1)
        hi = value + 1
    return lo, hi


def generate_schematic_assertions(data, tolerance=0.10):
    """Generate assertions from a schematic analyzer output dict."""
    stats = data.get("statistics", {})
    sa = data.get("signal_analysis", {})
    bom = data.get("bom", [])

    assertions = []
    ast_num = 1

    # Component count range
    total_comps = stats.get("total_components", 0)
    if total_comps > 0:
        lo, hi = _range_bounds(total_comps, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Component count ~{total_comps} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_components", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Net count range
    total_nets = stats.get("total_nets", 0)
    if total_nets > 0:
        lo, hi = _range_bounds(total_nets, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Net count ~{total_nets} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_nets", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # BOM exists
    if bom:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "BOM is non-empty",
            "check": {"path": "bom", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Signal analysis exists
    if sa:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Signal analysis section exists",
            "check": {"path": "signal_analysis", "op": "exists"},
        })
        ast_num += 1

    # Assertions for each detected signal type with count > 0
    for sig_type, detections in sorted(sa.items()):
        if not isinstance(detections, list) or len(detections) == 0:
            continue
        count = len(detections)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{count} {sig_type} detected",
            "check": {"path": f"signal_analysis.{sig_type}",
                      "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Component types exist
    comp_types = stats.get("component_types", {})
    for ctype, count in sorted(comp_types.items()):
        if count >= 5:  # Only assert types with significant presence
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"Has {count} {ctype}(s)",
                "check": {"path": f"statistics.component_types.{ctype}",
                          "op": "min_count", "value": max(1, count // 2)},
            })
            ast_num += 1

    return assertions


def generate_pcb_assertions(data, tolerance=0.10):
    """Generate assertions from a PCB analyzer output dict."""
    stats = data.get("statistics", {})
    conn = data.get("connectivity", {})
    dfm = data.get("dfm", {})

    assertions = []
    ast_num = 1

    # Footprint count range
    fp_count = stats.get("footprint_count", 0)
    if fp_count > 0:
        lo, hi = _range_bounds(fp_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Footprint count ~{fp_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.footprint_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Net count range
    net_count = stats.get("net_count", 0)
    if net_count > 0:
        lo, hi = _range_bounds(net_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Net count ~{net_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.net_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Copper layers used
    cu_layers = stats.get("copper_layers_used", 0)
    if cu_layers > 0:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{cu_layers} copper layer(s) used",
            "check": {"path": "statistics.copper_layers_used", "op": "equals",
                      "value": cu_layers},
        })
        ast_num += 1

    # Track segment count range
    track_segs = stats.get("track_segments", 0)
    if track_segs > 0:
        lo, hi = _range_bounds(track_segs, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Track segments ~{track_segs} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.track_segments", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Via count range
    via_count = stats.get("via_count", 0)
    if via_count > 0:
        lo, hi = _range_bounds(via_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Via count ~{via_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.via_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Zone count
    zone_count = stats.get("zone_count", 0)
    if zone_count > 0:
        lo, hi = _range_bounds(zone_count, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"Zone count ~{zone_count} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.zone_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # SMD vs THT breakdown
    smd = stats.get("smd_count", 0)
    if smd > 0:
        lo, hi = _range_bounds(smd, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"SMD count ~{smd} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.smd_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    tht = stats.get("tht_count", 0)
    if tht > 0:
        lo, hi = _range_bounds(tht, tolerance)
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"THT count ~{tht} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.tht_count", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # Routing completeness
    routing_complete = stats.get("routing_complete")
    if routing_complete is not None:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Routing completeness status",
            "check": {"path": "statistics.routing_complete", "op": "equals",
                      "value": routing_complete},
        })
        ast_num += 1

    # Connectivity section exists
    if conn:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Connectivity analysis present",
            "check": {"path": "connectivity", "op": "exists"},
        })
        ast_num += 1

    # DFM section exists
    if dfm:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "DFM analysis present",
            "check": {"path": "dfm", "op": "exists"},
        })
        ast_num += 1

        # DFM tier
        tier = dfm.get("dfm_tier", "")
        if tier:
            assertions.append({
                "id": f"SEED-{ast_num:08d}",
                "description": f"DFM tier is '{tier}'",
                "check": {"path": "dfm.dfm_tier", "op": "equals", "value": tier},
            })
            ast_num += 1

    # Decoupling placement (if present)
    decoupling = data.get("decoupling_placement", [])
    if decoupling:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{len(decoupling)} decoupling placement(s) analyzed",
            "check": {"path": "decoupling_placement", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Power net routing (if present)
    power_routing = data.get("power_net_routing", [])
    if power_routing:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": f"{len(power_routing)} power net(s) analyzed",
            "check": {"path": "power_net_routing", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Thermal analysis (if present)
    thermal = data.get("thermal_analysis", {})
    if thermal:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Thermal analysis present",
            "check": {"path": "thermal_analysis", "op": "exists"},
        })
        ast_num += 1

    # Placement analysis (if present)
    placement = data.get("placement_analysis", {})
    if placement:
        assertions.append({
            "id": f"SEED-{ast_num:08d}",
            "description": "Placement analysis present",
            "check": {"path": "placement_analysis", "op": "exists"},
        })
        ast_num += 1

    return assertions


def generate_for_repo(repo_name, atype, tolerance, min_components,
                      file_filter, dry_run):
    """Generate seed assertions for one repo."""
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
        prefix = project_prefix(proj_path)

        # Find output files for this project (filter_project_outputs
        # only matches *.json which excludes .err files)
        proj_outputs = filter_project_outputs(type_dir, proj_path)

        if file_filter:
            patterns = [p.strip() for p in file_filter.split(",")]
            proj_outputs = [f for f in proj_outputs
                            if any(fnmatch.fnmatch(f.name, p) or
                                   fnmatch.fnmatch(f.name[len(prefix):], p)
                                   for p in patterns)]

        for output_file in proj_outputs:
            try:
                data_content = json.loads(output_file.read_text())
            except Exception:
                continue

            if atype == "schematic":
                comps = data_content.get("statistics", {}).get("total_components", 0)
                if comps < min_components:
                    skipped += 1
                    continue
                assertions = generate_schematic_assertions(data_content, tolerance)
            elif atype == "pcb":
                fps = data_content.get("statistics", {}).get("footprint_count", 0)
                if fps < min_components:
                    skipped += 1
                    continue
                assertions = generate_pcb_assertions(data_content, tolerance)
            else:
                continue

            if not assertions:
                continue

            # file_pattern is the filename within the project (prefix stripped)
            if prefix:
                file_pattern = output_file.stem[len(prefix):]
            else:
                file_pattern = output_file.stem

            assertion_data = {
                "file_pattern": file_pattern,
                "analyzer_type": atype,
                "generated_by": "generate_seed_assertions.py",
                "assertions": assertions,
            }

            if dry_run:
                print(f"\n  {repo_name}/{proj_name}: {file_pattern}")
                for a in assertions:
                    print(f"    {a['id']}: {a['description']}")
                total_files += 1
                total_assertions += len(assertions)
                continue

            # Write to data/{repo}/{project}/assertions/{type}/
            out_dir = data_dir(repo_name, proj_name, "assertions") / atype
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{file_pattern}.json"

            if out_file.exists():
                existing = json.loads(out_file.read_text())
                if existing.get("generated_by") != "generate_seed_assertions.py":
                    continue

            out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")
            total_files += 1
            total_assertions += len(assertions)

    return total_files, total_assertions, skipped


def main():
    parser = argparse.ArgumentParser(description="Generate seed assertions from outputs")
    parser.add_argument("--repo", help="Generate for one repo")
    parser.add_argument("--all", action="store_true", help="Generate for all repos")
    parser.add_argument("--type", choices=ANALYZER_TYPES,
                        default="schematic", help="Analyzer type (default: schematic)")
    parser.add_argument("--filter", default="",
                        help="Glob pattern to filter output filenames")
    parser.add_argument("--tolerance", type=float, default=0.10,
                        help="Tolerance for range assertions (default: 0.10 = 10%%)")
    parser.add_argument("--min-components", type=int, default=10,
                        help="Skip files with fewer components (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print assertions without writing files")
    args = parser.parse_args()

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
            repo, args.type, args.tolerance, args.min_components,
            args.filter, args.dry_run)
        grand_files += files
        grand_assertions += assertions
        grand_skipped += skipped

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Generated {grand_assertions} assertions "
          f"across {grand_files} files (skipped {grand_skipped} small files)")


if __name__ == "__main__":
    main()
