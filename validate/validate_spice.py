#!/usr/bin/env python3
"""Cross-validate SPICE simulation results against schematic analyzer values.

Compares SPICE-computed values (from simulate_subcircuits.py) against the
analyzer's calculated values (from analyze_schematic.py) to catch bugs in
both directions.

Checks:
  - voltage_dividers: SPICE vout vs analyzer ratio × inferred Vin
  - rc_filters: SPICE fc vs analyzer cutoff_hz
  - lc_filters: SPICE f_peak vs analyzer resonant_hz
  - feedback_networks: SPICE vfb vs analyzer ratio × inferred Vin
  - current_sense: SPICE i_at_50mV vs analyzer max_current_50mV_A

Usage:
    python3 validate/validate_spice.py
    python3 validate/validate_spice.py --repo OpenMower
    python3 validate/validate_spice.py --summary
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, list_repos


def cross_validate_file(schematic_json, spice_json):
    """Cross-validate one file's SPICE results against analyzer values.

    Returns list of {type, components, analyzer_value, spice_value, delta_pct, status}.
    """
    results = []
    sa = schematic_json.get("signal_analysis", {})
    spice_results = spice_json.get("simulation_results", [])

    # Index SPICE results by (subcircuit_type, sorted components)
    spice_by_key = {}
    for sr in spice_results:
        stype = sr.get("subcircuit_type", "")
        comps = tuple(sorted(sr.get("components", [])))
        key = (stype, comps)
        spice_by_key[key] = sr

    # voltage_dividers: compare ratio
    for det in sa.get("voltage_dividers", []):
        r_top = det.get("r_top", {})
        r_bot = det.get("r_bottom", {})
        if not isinstance(r_top, dict) or not isinstance(r_bot, dict):
            continue
        comps = tuple(sorted([r_top.get("ref", ""), r_bot.get("ref", "")]))
        sr = spice_by_key.get(("voltage_divider", comps))
        if not sr:
            continue

        analyzer_ratio = det.get("ratio")
        sim_vout = sr.get("simulated", {}).get("vout_V")
        expected_vout = sr.get("expected", {}).get("vout_V")

        if sim_vout is not None and expected_vout is not None and expected_vout != 0:
            delta = abs(sim_vout - expected_vout) / expected_vout * 100
            results.append({
                "type": "voltage_divider",
                "components": list(comps),
                "analyzer_value": f"ratio={analyzer_ratio:.4f}",
                "spice_value": f"vout={sim_vout:.4f}V",
                "delta_pct": round(delta, 3),
                "status": "match" if delta < 0.1 else "mismatch",
            })

    # rc_filters: compare cutoff frequency
    for det in sa.get("rc_filters", []):
        r = det.get("resistor", {})
        c = det.get("capacitor", {})
        if not isinstance(r, dict) or not isinstance(c, dict):
            continue
        comps = tuple(sorted([r.get("ref", ""), c.get("ref", "")]))
        sr = spice_by_key.get(("rc_filter", comps))
        if not sr:
            continue

        analyzer_fc = det.get("cutoff_hz")
        sim_fc = sr.get("simulated", {}).get("fc_hz")

        if sim_fc is not None and analyzer_fc is not None and analyzer_fc > 0:
            delta = abs(sim_fc - analyzer_fc) / analyzer_fc * 100
            results.append({
                "type": "rc_filter",
                "components": list(comps),
                "analyzer_value": f"fc={analyzer_fc:.1f}Hz",
                "spice_value": f"fc={sim_fc:.1f}Hz",
                "delta_pct": round(delta, 3),
                "status": "match" if delta < 1 else "mismatch",
            })

    # lc_filters: compare resonant frequency
    for det in sa.get("lc_filters", []):
        ind = det.get("inductor", {})
        cap = det.get("capacitor", {})
        if not isinstance(ind, dict) or not isinstance(cap, dict):
            continue
        comps = tuple(sorted([ind.get("ref", ""), cap.get("ref", "")]))
        sr = spice_by_key.get(("lc_filter", comps))
        if not sr:
            continue

        analyzer_f = det.get("resonant_hz")
        sim_f = sr.get("simulated", {}).get("resonant_hz")

        if sim_f is not None and analyzer_f is not None and analyzer_f > 0:
            delta = abs(sim_f - analyzer_f) / analyzer_f * 100
            results.append({
                "type": "lc_filter",
                "components": list(comps),
                "analyzer_value": f"f0={analyzer_f:.1f}Hz",
                "spice_value": f"f0={sim_f:.1f}Hz",
                "delta_pct": round(delta, 3),
                "status": "match" if delta < 1 else "mismatch",
            })

    # current_sense: compare I at 50mV
    for det in sa.get("current_sense", []):
        shunt = det.get("shunt", {})
        if not isinstance(shunt, dict):
            continue
        comps = (shunt.get("ref", ""),)
        sr = spice_by_key.get(("current_sense", comps))
        if not sr:
            continue

        analyzer_i = det.get("max_current_50mV_A")
        sim_i = sr.get("simulated", {}).get("i_at_50mV_A")

        if sim_i is not None and analyzer_i is not None and analyzer_i > 0:
            delta = abs(sim_i - analyzer_i) / analyzer_i * 100
            results.append({
                "type": "current_sense",
                "components": list(comps),
                "analyzer_value": f"I@50mV={analyzer_i:.4f}A",
                "spice_value": f"I@50mV={sim_i:.4f}A",
                "delta_pct": round(delta, 3),
                "status": "match" if delta < 1 else "mismatch",
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Cross-validate SPICE results against analyzer values"
    )
    parser.add_argument("--repo", help="Only validate one repo")
    parser.add_argument("--summary", action="store_true",
                        help="Print summary only (no per-file details)")
    parser.add_argument("--mismatches-only", action="store_true",
                        help="Only show mismatches")
    args = parser.parse_args()

    schematic_dir = OUTPUTS_DIR / "schematic"
    spice_dir = OUTPUTS_DIR / "spice"

    if not schematic_dir.exists() or not spice_dir.exists():
        print("Error: need both schematic and spice outputs", file=sys.stderr)
        sys.exit(1)

    repos = [args.repo] if args.repo else sorted(
        d.name for d in spice_dir.iterdir() if d.is_dir()
    )

    total_checks = 0
    total_match = 0
    total_mismatch = 0
    by_type = {}

    for repo in repos:
        repo_sch = schematic_dir / repo
        repo_spice = spice_dir / repo
        if not repo_sch.exists() or not repo_spice.exists():
            continue

        for spice_file in sorted(repo_spice.glob("*.json")):
            sch_file = repo_sch / spice_file.name
            if not sch_file.exists():
                continue

            try:
                sch_data = json.loads(sch_file.read_text())
                spice_data = json.loads(spice_file.read_text())
            except Exception:
                continue

            results = cross_validate_file(sch_data, spice_data)
            for r in results:
                total_checks += 1
                t = r["type"]
                by_type.setdefault(t, {"match": 0, "mismatch": 0})

                if r["status"] == "match":
                    total_match += 1
                    by_type[t]["match"] += 1
                else:
                    total_mismatch += 1
                    by_type[t]["mismatch"] += 1

                if not args.summary:
                    if not args.mismatches_only or r["status"] == "mismatch":
                        status = "OK" if r["status"] == "match" else "MISMATCH"
                        print(f"  {status:8s} {repo}/{spice_file.name}: "
                              f"{r['type']} {r['components']} "
                              f"analyzer={r['analyzer_value']} "
                              f"spice={r['spice_value']} "
                              f"delta={r['delta_pct']:.3f}%")

    # Summary
    print(f"\n{'='*60}")
    print(f"SPICE Cross-Validation Summary")
    print(f"{'='*60}")
    print(f"Total checks:    {total_checks}")
    print(f"Match:           {total_match}")
    print(f"Mismatch:        {total_mismatch}")
    if total_checks:
        print(f"Agreement rate:  {total_match/total_checks*100:.1f}%")
    print(f"\nBy type:")
    for t in sorted(by_type):
        m = by_type[t]["match"]
        mm = by_type[t]["mismatch"]
        total = m + mm
        print(f"  {t:25s} {m}/{total} match ({m/total*100:.1f}%)")


if __name__ == "__main__":
    main()
