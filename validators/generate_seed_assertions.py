#!/usr/bin/env python3
"""Generate seed assertions from existing analyzer outputs.

Reads schematic/pcb/gerber outputs and creates conservative assertions
that should remain stable across analyzer changes. Useful for
bootstrapping the assertion set for newly tested repos.

Usage:
    python3 validators/generate_seed_assertions.py
    python3 validators/generate_seed_assertions.py --type schematic
    python3 validators/generate_seed_assertions.py --filter "OpenMower*"
    python3 validators/generate_seed_assertions.py --tolerance 0.15
"""

import argparse
import fnmatch
import json
import math
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
ASSERTIONS_DIR = HARNESS_DIR / "data" / "assertions"


def _range_bounds(value, tolerance):
    """Compute [lo, hi] range with tolerance around a value."""
    lo = max(0, math.floor(value * (1 - tolerance)))
    hi = math.ceil(value * (1 + tolerance))
    # Ensure minimum spread of 2 for small values
    if hi - lo < 2 and value > 0:
        lo = max(0, value - 1)
        hi = value + 1
    return lo, hi


def generate_schematic_assertions(output_file, tolerance=0.10):
    """Generate assertions from a schematic analyzer output."""
    data = json.loads(output_file.read_text())
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
            "id": f"SEED-{ast_num:03d}",
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
            "id": f"SEED-{ast_num:03d}",
            "description": f"Net count ~{total_nets} (tolerance {tolerance:.0%})",
            "check": {"path": "statistics.total_nets", "op": "range",
                      "min": lo, "max": hi},
        })
        ast_num += 1

    # BOM exists
    if bom:
        assertions.append({
            "id": f"SEED-{ast_num:03d}",
            "description": "BOM is non-empty",
            "check": {"path": "bom", "op": "min_count", "value": 1},
        })
        ast_num += 1

    # Signal analysis exists
    if sa:
        assertions.append({
            "id": f"SEED-{ast_num:03d}",
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
            "id": f"SEED-{ast_num:03d}",
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
                "id": f"SEED-{ast_num:03d}",
                "description": f"Has {count} {ctype}(s)",
                "check": {"path": f"statistics.component_types.{ctype}",
                          "op": "min_count", "value": max(1, count // 2)},
            })
            ast_num += 1

    return assertions


def main():
    parser = argparse.ArgumentParser(description="Generate seed assertions from outputs")
    parser.add_argument("--type", choices=["schematic", "pcb", "gerber"],
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

    type_dir = OUTPUTS_DIR / args.type
    if not type_dir.exists():
        print(f"No outputs found at {type_dir}")
        sys.exit(1)

    output_files = sorted(type_dir.glob("*.json"))
    if args.filter:
        patterns = [p.strip() for p in args.filter.split(",")]
        output_files = [f for f in output_files
                        if any(fnmatch.fnmatch(f.name, p) for p in patterns)]

    # Filter out .err files
    output_files = [f for f in output_files if not f.name.endswith(".err")]

    if not output_files:
        print("No matching output files found.")
        sys.exit(1)

    out_dir = ASSERTIONS_DIR / args.type
    out_dir.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_assertions = 0
    skipped = 0

    for output_file in output_files:
        try:
            data = json.loads(output_file.read_text())
        except Exception:
            continue

        # Skip small files
        comps = data.get("statistics", {}).get("total_components", 0)
        if comps < args.min_components:
            skipped += 1
            continue

        if args.type == "schematic":
            assertions = generate_schematic_assertions(output_file, args.tolerance)
        else:
            # TODO: pcb and gerber generators
            continue

        if not assertions:
            continue

        file_pattern = output_file.stem  # e.g. "OpenMower_..._dcdc.kicad_sch"

        assertion_data = {
            "file_pattern": file_pattern,
            "analyzer_type": args.type,
            "generated_by": "generate_seed_assertions.py",
            "assertions": assertions,
        }

        if args.dry_run:
            print(f"\n{file_pattern}:")
            for a in assertions:
                print(f"  {a['id']}: {a['description']}")
            total_files += 1
            total_assertions += len(assertions)
            continue

        # Write assertion file (don't overwrite manually curated ones)
        out_file = out_dir / f"{file_pattern}.json"
        if out_file.exists():
            existing = json.loads(out_file.read_text())
            if existing.get("generated_by") != "generate_seed_assertions.py":
                print(f"  SKIP {file_pattern} (manually curated)")
                continue

        out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")
        total_files += 1
        total_assertions += len(assertions)

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Generated {total_assertions} assertions "
          f"across {total_files} files (skipped {skipped} small files)")
    if not args.dry_run:
        print(f"Written to {out_dir}/")


if __name__ == "__main__":
    main()
