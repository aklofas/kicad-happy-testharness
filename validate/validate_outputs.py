#!/usr/bin/env python3
"""Validate analyzer JSON outputs across all schematics in the test corpus.

Checks structural invariants, cross-references, and flags anomalies.

Usage:
    python3 validate/validate_outputs.py
    python3 validate/validate_outputs.py --repo OpenMower
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import OUTPUTS_DIR, REPOS_DIR, MANIFESTS_DIR, list_repos


def load_result(json_path):
    with open(json_path) as f:
        return json.load(f)


# Validation categories
anomalies = defaultdict(list)  # category -> [(file, detail)]
stats = defaultdict(int)


def validate_structural(name, data, is_modern):
    """Check structural invariants that should always hold."""
    stats["total"] += 1

    required = ["file", "components", "nets", "labels", "power_symbols", "no_connects", "bom"]
    for key in required:
        if key not in data:
            anomalies["missing_key"].append((name, f"missing '{key}'"))

    stat_section = data.get("statistics", data.get("summary", {}))
    total_comps = stat_section.get("total_components", len(data.get("components", [])))
    total_nets = stat_section.get("total_nets", len(data.get("nets", [])))

    stats["total_components"] += total_comps
    stats["total_nets"] += total_nets

    if total_comps == 0:
        stats["zero_comp"] += 1
    if total_nets == 0:
        stats["zero_net"] += 1

    if is_modern and total_comps > 0:
        stats["modern_with_comps"] += 1
        if "signal_analysis" not in data:
            anomalies["missing_signal_analysis"].append((name, f"{total_comps} comps but no signal_analysis"))
        if "design_analysis" not in data:
            anomalies["missing_design_analysis"].append((name, f"{total_comps} comps but no design_analysis"))

        new_sections = [
            "annotation_issues", "label_shape_warnings", "pwr_flag_warnings",
            "footprint_filter_warnings", "sourcing_audit", "ground_domains",
            "bus_topology", "wire_geometry", "property_issues",
            "hierarchical_labels", "title_block"
        ]
        for section in new_sections:
            if section not in data:
                anomalies["missing_new_section"].append((name, f"missing '{section}'"))

    if not is_modern:
        stats["legacy"] += 1
    else:
        stats["modern"] += 1


def validate_components(name, data):
    """Check component data integrity."""
    components = data.get("components", [])
    refs = [c.get("reference", "") for c in components]

    real_refs = [r for r in refs if r and r != "?" and not r.startswith("#")]
    ref_counts = defaultdict(int)
    for r in real_refs:
        ref_counts[r] += 1
    dupes = {r: c for r, c in ref_counts.items() if c > 1}
    if dupes and len(dupes) > 5:
        anomalies["many_duplicate_refs"].append((name, f"{len(dupes)} duplicate refs"))

    unknown = [c for c in components if c.get("type") == "unknown" and not c.get("reference", "").startswith("#")]
    if len(unknown) > len(components) * 0.3 and len(unknown) > 5:
        anomalies["high_unknown_type"].append((name, f"{len(unknown)}/{len(components)} unknown type"))

    bom = data.get("bom", [])
    bom_total = sum(b.get("quantity", 0) for b in bom)
    non_power_comps = [c for c in components if not c.get("reference", "").startswith("#")]
    if bom and abs(bom_total - len(non_power_comps)) > 5:
        anomalies["bom_mismatch"].append((name, f"BOM qty={bom_total} vs components={len(non_power_comps)}"))


def validate_nets(name, data, total_comps):
    """Check net data integrity."""
    nets = data.get("nets", {})
    if isinstance(nets, list):
        total_nets = len(nets)
        net_items = nets
    elif isinstance(nets, dict):
        total_nets = len(nets)
        net_items = nets.values()
    else:
        total_nets = 0
        net_items = []

    if total_comps > 10 and total_nets > 0 and total_comps / total_nets > 10:
        anomalies["high_comp_net_ratio"].append((name, f"comps={total_comps} nets={total_nets} ratio={total_comps/total_nets:.1f}"))

    if total_comps > 5 and total_nets == 0:
        anomalies["comps_but_no_nets"].append((name, f"{total_comps} components but 0 nets"))

    for net in net_items:
        if isinstance(net, dict):
            pin_count = net.get("pin_count", len(net.get("pins", [])))
            net_name = net.get("name", "?")
        else:
            continue
        if pin_count > 500:
            anomalies["huge_net"].append((name, f"net '{net_name}' has {pin_count} pins"))


def validate_signal_analysis(name, data):
    """Check signal analysis plausibility for modern files."""
    if "signal_analysis" not in data:
        return

    sa = data["signal_analysis"]

    for key, items in sa.items():
        if isinstance(items, list) and len(items) > 200:
            anomalies["signal_explosion"].append((name, f"signal_analysis.{key} has {len(items)} entries"))

    da = sa.get("decoupling_analysis", {})
    if isinstance(da, dict):
        ics = da.get("ics_analyzed", 0)
        if ics > 200:
            anomalies["decoupling_explosion"].append((name, f"decoupling analyzed {ics} ICs"))


def validate_design_analysis(name, data):
    """Check design analysis plausibility."""
    if "design_analysis" not in data:
        return

    da = data["design_analysis"]
    erc = da.get("erc_warnings", [])
    if isinstance(erc, list) and len(erc) > 100:
        anomalies["many_erc_warnings"].append((name, f"{len(erc)} ERC warnings"))


def validate_new_sections(name, data):
    """Validate the new Tier 1/2 analysis sections."""
    aa = data.get("annotation_issues", {})
    if isinstance(aa, dict):
        dupes = aa.get("duplicate_references", [])
        if isinstance(dupes, list) and len(dupes) > 20:
            anomalies["many_annotation_dupes"].append((name, f"{len(dupes)} duplicate refs"))

    wg = data.get("wire_geometry", {})
    if isinstance(wg, dict):
        diag = wg.get("diagonal_wires", 0)
        if isinstance(diag, list):
            diag = len(diag)
        total_wires = wg.get("total_wires", 1)
        if isinstance(total_wires, list):
            total_wires = len(total_wires)
        if isinstance(diag, (int, float)) and isinstance(total_wires, (int, float)) and total_wires > 0 and diag / max(total_wires, 1) > 0.5:
            anomalies["many_diagonal_wires"].append((name, f"{diag}/{total_wires} diagonal"))

    pi = data.get("property_issues", {})
    if isinstance(pi, dict):
        value_eq_ref = pi.get("value_equals_reference", [])
        if isinstance(value_eq_ref, list) and len(value_eq_ref) > 20:
            anomalies["many_value_eq_ref"].append((name, f"{len(value_eq_ref)} value==reference"))

    gd = data.get("ground_domains", {})
    if isinstance(gd, dict):
        domains = gd.get("domains", [])
        if len(domains) > 10:
            anomalies["many_ground_domains"].append((name, f"{len(domains)} ground domains"))


def validate_cross_reference(name, data, sch_path):
    """Cross-reference schematic data with PCB if available."""
    sch_dir = Path(sch_path).parent
    pcb_files = list(sch_dir.glob("*.kicad_pcb"))
    if not pcb_files:
        return
    stats["has_pcb"] += 1


def main():
    parser = argparse.ArgumentParser(description="Validate analyzer JSON outputs")
    parser.add_argument("--repo", help="Only validate outputs for this repo")
    args = parser.parse_args()

    if args.repo:
        repos = [args.repo]
    else:
        repos = list_repos()

    schematics_list = MANIFESTS_DIR / "all_schematics.txt"

    if not schematics_list.exists():
        print(f"Error: {schematics_list} not found. Run discover.py first.")
        sys.exit(1)

    with open(schematics_list) as f:
        schematics = [line.strip() for line in f if line.strip()]

    if args.repo:
        repos_str = str(REPOS_DIR)
        prefix = repos_str + os.sep + args.repo + os.sep
        schematics = [s for s in schematics if s.startswith(prefix)]

    print(f"Validating {len(schematics)} schematics...")
    print()

    repos_dir = str(REPOS_DIR)

    for sch_path in schematics:
        relpath = sch_path
        if sch_path.startswith(repos_dir):
            relpath = sch_path[len(repos_dir):].lstrip("/").lstrip(os.sep)

        # Determine repo and within-repo safe name
        parts = relpath.replace("\\", "/").split("/", 1)
        repo = parts[0]
        within_repo = parts[1] if len(parts) > 1 else relpath
        safe_name = within_repo.replace(os.sep, "_").replace("/", "_")

        # Look for output in per-repo dir
        json_path = OUTPUTS_DIR / "schematic" / repo / f"{safe_name}.json"

        if not json_path.exists():
            anomalies["missing_result"].append((sch_path, "no JSON output"))
            continue

        try:
            data = load_result(json_path)
        except Exception as e:
            anomalies["invalid_json"].append((str(json_path), str(e)))
            continue

        name = os.path.basename(sch_path)
        is_modern = sch_path.endswith(".kicad_sch")

        stat_section = data.get("statistics", data.get("summary", {}))
        total_comps = stat_section.get("total_components", len(data.get("components", [])))

        validate_structural(name, data, is_modern)
        validate_components(name, data)
        validate_nets(name, data, total_comps)
        validate_signal_analysis(name, data)
        validate_design_analysis(name, data)
        if is_modern and total_comps > 0:
            validate_new_sections(name, data)

    # Report
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total schematics: {stats['total']}")
    print(f"Modern: {stats['modern']}  Legacy: {stats['legacy']}")
    print(f"Modern with components: {stats['modern_with_comps']}")
    print(f"Total components: {stats['total_components']:,}")
    print(f"Total nets: {stats['total_nets']:,}")
    print(f"Zero-component files: {stats['zero_comp']}")
    print(f"Zero-net files: {stats['zero_net']}")
    print(f"Files with paired PCB: {stats['has_pcb']}")
    print()

    if not anomalies:
        print("NO ANOMALIES FOUND")
        return

    print(f"ANOMALIES ({sum(len(v) for v in anomalies.values())} total across {len(anomalies)} categories):")
    print()

    for cat in sorted(anomalies.keys()):
        items = anomalies[cat]
        print(f"--- {cat} ({len(items)}) ---")
        for name, detail in items[:10]:
            print(f"  {name}: {detail}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")
        print()


if __name__ == "__main__":
    main()
