#!/usr/bin/env python3
"""SPICE simulation coverage metrics.

Correlates schematic signal detections with SPICE simulation results
to show per-detector coverage rates, pass/fail breakdowns, and gaps.

Usage:
    python3 tools/spice_coverage.py                     # Full corpus
    python3 tools/spice_coverage.py --repo owner/repo   # Single repo
    python3 tools/spice_coverage.py --cross-section smoke
    python3 tools/spice_coverage.py --json              # Machine-readable
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, add_repo_filter_args, resolve_repos, list_repos

# Schematic findings detector → SPICE subcircuit_type
DETECTOR_SPICE_MAP = {
    "voltage_dividers": "voltage_divider",
    "rc_filters": "rc_filter",
    "lc_filters": "lc_filter",
    "crystal_circuits": "crystal_circuit",
    "protection_devices": "protection_device",
    "power_regulators": "regulator_feedback",
    "opamp_circuits": "opamp_circuit",
    "current_sense_resistors": "current_sense",
    "transistor_circuits": "transistor_circuit",
    "feedback_networks": "feedback_network",
    "decoupling_capacitors": "decoupling",
    "rf_matching_networks": "rf_matching",
    "bridge_circuits": "bridge_circuit",
    "snubber_circuits": "snubber_circuit",
    "inrush_limiters": "inrush",
    "bms_balance_circuits": "bms_balance",
    "rf_chains": "rf_chain",
}

# Reverse map for unmapped type detection
_SPICE_TO_DETECTOR = {v: k for k, v in DETECTOR_SPICE_MAP.items()}


def count_detections(schematic_data):
    """Count detections per detector type from a schematic output."""
    # Group findings by detector
    grouped = {}
    for f in schematic_data.get("findings", []):
        det = f.get("detector", "")
        if det:
            grouped.setdefault(det, []).append(f)
    counts = {}
    for det_key in DETECTOR_SPICE_MAP:
        # Match with detect_ prefix
        full_name = f"detect_{det_key}"
        items = grouped.get(full_name, [])
        counts[det_key] = len(items)
    return counts


def count_simulations(spice_data):
    """Count simulations per subcircuit_type and status from SPICE output."""
    results = spice_data.get("simulation_results", [])
    by_type = defaultdict(lambda: {"total": 0, "pass": 0, "warn": 0, "fail": 0, "skip": 0})
    for sim in results:
        stype = sim.get("subcircuit_type", "unknown")
        status = sim.get("status", "unknown")
        by_type[stype]["total"] += 1
        if status in ("pass", "warn", "fail", "skip"):
            by_type[stype][status] += 1
    return dict(by_type)


def merge_coverage(detections, simulations):
    """Merge schematic detections with SPICE simulations into coverage rows."""
    rows = []
    for det_key, spice_type in sorted(DETECTOR_SPICE_MAP.items()):
        detected = detections.get(det_key, 0)
        sim_stats = simulations.get(spice_type,
                                    {"total": 0, "pass": 0, "warn": 0, "fail": 0, "skip": 0})
        simulated = sim_stats["total"]
        coverage_pct = (simulated / detected * 100) if detected > 0 else 0
        rows.append({
            "detector": det_key,
            "spice_type": spice_type,
            "detected": detected,
            "simulated": simulated,
            "coverage_pct": round(coverage_pct, 1),
            "pass": sim_stats["pass"],
            "warn": sim_stats["warn"],
            "fail": sim_stats["fail"],
            "skip": sim_stats["skip"],
        })
    return rows


def aggregate_rows(all_rows):
    """Sum coverage rows from multiple projects into per-detector totals."""
    agg = defaultdict(lambda: {
        "detected": 0, "simulated": 0,
        "pass": 0, "warn": 0, "fail": 0, "skip": 0,
    })
    for row in all_rows:
        key = row["detector"]
        for field in ("detected", "simulated", "pass", "warn", "fail", "skip"):
            agg[key][field] += row[field]
    result = []
    for det_key, spice_type in sorted(DETECTOR_SPICE_MAP.items()):
        stats = agg[det_key]
        coverage_pct = (stats["simulated"] / stats["detected"] * 100) \
            if stats["detected"] > 0 else 0
        result.append({
            "detector": det_key,
            "spice_type": spice_type,
            "detected": stats["detected"],
            "simulated": stats["simulated"],
            "coverage_pct": round(coverage_pct, 1),
            **{k: stats[k] for k in ("pass", "warn", "fail", "skip")},
        })
    return result


def find_unmapped_types(simulations):
    """Return SPICE subcircuit_types not in DETECTOR_SPICE_MAP."""
    known = set(DETECTOR_SPICE_MAP.values())
    return sorted(set(simulations.keys()) - known)


def _list_output_repos(base_dir):
    """List owner/repo paths under an output directory."""
    repos = []
    if not base_dir.exists():
        return repos
    for owner_dir in sorted(base_dir.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                repos.append(f"{owner_dir.name}/{repo_dir.name}")
    return repos


def main():
    parser = argparse.ArgumentParser(description="SPICE simulation coverage metrics")
    add_repo_filter_args(parser)
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = _list_output_repos(OUTPUTS_DIR / "schematic")

    sch_dir = OUTPUTS_DIR / "schematic"
    spice_dir = OUTPUTS_DIR / "spice"

    all_rows = []
    all_unmapped = defaultdict(int)
    files_with_both = 0
    sch_only = 0

    for repo in repos:
        repo_sch = sch_dir / repo
        repo_spice = spice_dir / repo
        if not repo_sch.exists():
            continue

        sch_files = {f.stem: f for f in repo_sch.glob("*.json")
                     if not f.stem.startswith("_")}
        spice_files = {f.stem: f for f in repo_spice.glob("*.json")
                       if not f.stem.startswith("_")} if repo_spice.exists() else {}

        for stem, sch_file in sch_files.items():
            try:
                sch_data = json.loads(sch_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            detections = count_detections(sch_data)

            spice_file = spice_files.get(stem)
            if spice_file:
                try:
                    spice_data = json.loads(spice_file.read_text(encoding="utf-8"))
                    simulations = count_simulations(spice_data)
                    files_with_both += 1
                except (json.JSONDecodeError, OSError):
                    simulations = {}
            else:
                simulations = {}
                if any(v > 0 for v in detections.values()):
                    sch_only += 1

            for utype in find_unmapped_types(simulations):
                all_unmapped[utype] += simulations[utype]["total"]

            rows = merge_coverage(detections, simulations)
            all_rows.extend(rows)

    summary = aggregate_rows(all_rows)

    total_detected = sum(r["detected"] for r in summary)
    total_simulated = sum(r["simulated"] for r in summary)
    total_pass = sum(r["pass"] for r in summary)
    total_warn = sum(r["warn"] for r in summary)
    total_fail = sum(r["fail"] for r in summary)
    total_skip = sum(r["skip"] for r in summary)
    overall_cov = (total_simulated / total_detected * 100) if total_detected > 0 else 0

    if args.json:
        out = {
            "files_with_both": files_with_both,
            "schematic_only_files": sch_only,
            "total_detected": total_detected,
            "total_simulated": total_simulated,
            "overall_coverage_pct": round(overall_cov, 1),
            "by_detector": summary,
        }
        if all_unmapped:
            out["unmapped_spice_types"] = dict(all_unmapped)
        print(json.dumps(out, indent=2))
    else:
        print(f"Files: {files_with_both:,} with SPICE, {sch_only:,} schematic-only")
        print(f"Overall: {total_detected:,} detections → {total_simulated:,} simulations "
              f"({overall_cov:.1f}% coverage)")
        print(f"Status:  {total_pass:,} pass, {total_warn:,} warn, "
              f"{total_fail:,} fail, {total_skip:,} skip")
        print()

        hdr = (f"{'Detector':<30} {'Det':>7} {'Sim':>7} {'Cov%':>6} "
               f"{'Pass':>7} {'Warn':>6} {'Fail':>6} {'Skip':>6}")
        print(hdr)
        print("-" * len(hdr))
        for row in summary:
            if row["detected"] == 0 and row["simulated"] == 0:
                continue
            print(f"{row['detector']:<30} {row['detected']:>7,} {row['simulated']:>7,} "
                  f"{row['coverage_pct']:>5.1f}% {row['pass']:>7,} {row['warn']:>6,} "
                  f"{row['fail']:>6,} {row['skip']:>6,}")

        if all_unmapped:
            print(f"\nUnmapped SPICE types: {dict(all_unmapped)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
