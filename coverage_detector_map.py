#!/usr/bin/env python3
"""Per-detector coverage map.

For each signal detector, shows corpus hits, assertion counts by type,
equation tags, and constants status. Identifies weakly-tested detectors.

Usage:
    python3 coverage_detector_map.py
    python3 coverage_detector_map.py --json
    python3 coverage_detector_map.py --uncovered-only
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import OUTPUTS_DIR, DATA_DIR, safe_load_json

# Canonical detector list from seed.py
DETECTORS = [
    "addressable_led_chains", "bms_systems", "bridge_circuits",
    "buzzer_speaker_circuits", "crystal_circuits", "current_sense",
    "ethernet_interfaces", "feedback_networks", "hdmi_dvi_interfaces",
    "isolation_barriers", "key_matrices", "lc_filters", "memory_interfaces",
    "opamp_circuits", "power_regulators", "protection_devices", "rc_filters",
    "rf_chains", "rf_matching", "snubbers", "transistor_circuits",
    "voltage_dividers",
]

EQUATION_REGISTRY = DATA_DIR / "equation_registry.json"
CONSTANTS_REGISTRY = DATA_DIR / "constants_registry.json"


def count_corpus_hits():
    """Count how many schematic outputs have non-empty detections per detector.

    Returns dict of {detector: hit_count}.
    """
    hits = {d: 0 for d in DETECTORS}
    sch_dir = OUTPUTS_DIR / "schematic"
    if not sch_dir.exists():
        return hits

    for owner_dir in sch_dir.iterdir():
        if not owner_dir.is_dir():
            continue
        for repo_dir in owner_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            for f in repo_dir.glob("*.json"):
                if f.name.startswith("_"):
                    continue
                try:
                    data = json.loads(f.read_text())
                    sa = data.get("signal_analysis", {})
                    for det in DETECTORS:
                        items = sa.get(det, [])
                        if isinstance(items, list) and len(items) > 0:
                            hits[det] += 1
                except Exception:
                    continue

    return hits


def count_assertions():
    """Count assertions per detector, grouped by type prefix.

    Returns dict of {detector: {SEED: n, STRUCT: n, FND: n, BUGFIX: n}}.
    """
    counts = {d: {"SEED": 0, "STRUCT": 0, "FND": 0, "BUGFIX": 0}
              for d in DETECTORS}

    if not DATA_DIR.exists():
        return counts

    for f in DATA_DIR.rglob("assertions/schematic/*.json"):
        data = safe_load_json(f, {})
        for a in data.get("assertions", []):
            path = a.get("check", {}).get("path", "")
            aid = a.get("id", "")
            prefix = aid.split("-")[0] if "-" in aid else ""
            # Match detector from path like "signal_analysis.voltage_dividers"
            for det in DETECTORS:
                if f"signal_analysis.{det}" in path:
                    if prefix in counts[det]:
                        counts[det][prefix] += 1
                    break

    return counts


def count_equations():
    """Count equation tags per detector from equation registry.

    Returns dict of {detector: count}.
    """
    eqs = {d: 0 for d in DETECTORS}
    data = safe_load_json(EQUATION_REGISTRY, {})
    for eq in data.get("equations", []):
        context = eq.get("context", "").lower()
        for det in DETECTORS:
            short = det.replace("_", " ").replace("circuits", "").strip()
            if short in context or det in context:
                eqs[det] += 1
                break
    return eqs


def constants_status():
    """Check which detectors have verified constants.

    Returns dict of {detector: {total: n, verified: n}}.
    """
    status = {d: {"total": 0, "verified": 0} for d in DETECTORS}
    data = safe_load_json(CONSTANTS_REGISTRY, {})
    for c in data.get("constants", []):
        scope = (c.get("scope", "") + " " + c.get("name", "")).lower()
        for det in DETECTORS:
            short = det.replace("_", " ").replace("circuits", "").strip()
            if short in scope or det in scope:
                status[det]["total"] += 1
                if c.get("source") or c.get("verified_date"):
                    status[det]["verified"] += 1
                break
    return status


def build_matrix():
    """Build full coverage matrix."""
    hits = count_corpus_hits()
    assertions = count_assertions()
    equations = count_equations()
    constants = constants_status()

    rows = []
    for det in DETECTORS:
        a = assertions[det]
        c = constants[det]
        total_assertions = sum(a.values())
        rows.append({
            "detector": det,
            "corpus_hits": hits[det],
            "assertions_total": total_assertions,
            "seed": a["SEED"],
            "struct": a["STRUCT"],
            "fnd": a["FND"],
            "bugfix": a["BUGFIX"],
            "equations": equations[det],
            "constants_total": c["total"],
            "constants_verified": c["verified"],
        })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Per-detector coverage map")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--uncovered-only", action="store_true",
                        help="Only show detectors with weak coverage")
    args = parser.parse_args()

    rows = build_matrix()

    if args.json:
        json.dump(rows, sys.stdout, indent=2)
        print()
        return

    # Table output
    print(f"{'Detector':<28s} {'Hits':>5s} {'SEED':>5s} {'STRCT':>5s} "
          f"{'FND':>5s} {'BFIX':>4s} {'EQ':>3s} {'Const':>6s}")
    print("-" * 75)

    for r in sorted(rows, key=lambda x: -x["corpus_hits"]):
        if args.uncovered_only:
            if r["assertions_total"] > 0 and r["corpus_hits"] > 0:
                continue

        const_str = (f"{r['constants_verified']}/{r['constants_total']}"
                     if r["constants_total"] else "-")
        print(f"{r['detector']:<28s} {r['corpus_hits']:>5d} {r['seed']:>5d} "
              f"{r['struct']:>5d} {r['fnd']:>5d} {r['bugfix']:>4d} "
              f"{r['equations']:>3d} {const_str:>6s}")

    total_hits = sum(r["corpus_hits"] for r in rows)
    total_assertions = sum(r["assertions_total"] for r in rows)
    zero_coverage = sum(1 for r in rows if r["assertions_total"] == 0 and r["corpus_hits"] > 0)
    print("-" * 75)
    print(f"{'TOTAL':<28s} {total_hits:>5d} "
          f"{sum(r['seed'] for r in rows):>5d} "
          f"{sum(r['struct'] for r in rows):>5d} "
          f"{sum(r['fnd'] for r in rows):>5d} "
          f"{sum(r['bugfix'] for r in rows):>4d}")
    if zero_coverage:
        print(f"\nWARNING: {zero_coverage} detectors have corpus hits but zero assertions")


if __name__ == "__main__":
    main()
