#!/usr/bin/env python3
"""Cross-validate EMC analysis results against schematic and PCB analyzer values.

Compares EMC board_info fields against their source analyzer outputs to catch
stale inputs, pairing errors, or extraction bugs.

Checks:
  - crystal_frequencies: EMC board_info vs schematic crystal_circuits
  - layer_count: EMC board_info vs PCB statistics.copper_layers_used
  - component_count: EMC board_info vs schematic statistics.total_components
  - footprint_count: EMC board_info vs PCB statistics.footprint_count
  - switching_regulator_count: SW-001 findings vs non-LDO regulators in schematic

Usage:
    python3 validate/validate_emc.py
    python3 validate/validate_emc.py --repo OpenMower
    python3 validate/validate_emc.py --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR


def cross_validate_file(schematic_data, pcb_data, emc_data):
    """Cross-validate one file's EMC results against analyzer values.

    Returns list of {check, emc_value, source_value, status, detail}.
    """
    results = []
    board_info = emc_data.get("board_info", {})

    # 1. Component count (schematic)
    if schematic_data:
        sch_comps = schematic_data.get("statistics", {}).get("total_components", 0)
        emc_comps = board_info.get("total_components")
        if emc_comps is not None and sch_comps > 0:
            status = "match" if emc_comps == sch_comps else "mismatch"
            results.append({
                "check": "component_count",
                "emc_value": emc_comps,
                "source_value": sch_comps,
                "status": status,
                "detail": f"EMC={emc_comps} vs schematic={sch_comps}",
            })

    # 2. Crystal frequencies (schematic)
    if schematic_data:
        sch_crystals = schematic_data.get("signal_analysis", {}).get("crystal_circuits", [])
        sch_freqs = sorted(set(x.get("frequency", 0) for x in sch_crystals if x.get("frequency")))
        emc_freqs = sorted(board_info.get("crystal_frequencies_hz", []))
        if sch_freqs or emc_freqs:
            status = "match" if emc_freqs == sch_freqs else "mismatch"
            results.append({
                "check": "crystal_frequencies",
                "emc_value": emc_freqs,
                "source_value": sch_freqs,
                "status": status,
                "detail": f"EMC={emc_freqs} vs schematic={sch_freqs}",
            })

    # 3. Layer count (PCB)
    if pcb_data:
        pcb_layers = pcb_data.get("statistics", {}).get("copper_layers_used", 0)
        emc_layers = board_info.get("layer_count")
        if emc_layers is not None and pcb_layers > 0:
            status = "match" if emc_layers == pcb_layers else "mismatch"
            results.append({
                "check": "layer_count",
                "emc_value": emc_layers,
                "source_value": pcb_layers,
                "status": status,
                "detail": f"EMC={emc_layers} vs PCB={pcb_layers}",
            })

    # 4. Footprint count (PCB)
    if pcb_data:
        pcb_fp = pcb_data.get("statistics", {}).get("footprint_count", 0)
        emc_fp = board_info.get("footprint_count")
        if emc_fp is not None and pcb_fp > 0:
            status = "match" if emc_fp == pcb_fp else "mismatch"
            results.append({
                "check": "footprint_count",
                "emc_value": emc_fp,
                "source_value": pcb_fp,
                "status": status,
                "detail": f"EMC={emc_fp} vs PCB={pcb_fp}",
            })

    # 5. Switching regulator count (schematic vs EMC SW-001 findings)
    if schematic_data:
        regulators = schematic_data.get("signal_analysis", {}).get("power_regulators", [])
        non_ldo = [r for r in regulators
                   if r.get("topology") not in ("ldo", "linear", None, "")]
        sw_findings = [f for f in emc_data.get("findings", [])
                       if f.get("rule_id") == "SW-001"]
        # Count unique component refs in SW findings
        sw_refs = set()
        for f in sw_findings:
            sw_refs.update(f.get("components", []))
        non_ldo_refs = set(r.get("ref", r.get("reference", "")) for r in non_ldo)

        if non_ldo_refs or sw_refs:
            # Check if EMC found switching regulators that schematic also found
            overlap = sw_refs & non_ldo_refs
            status = "match" if sw_refs == non_ldo_refs or overlap else "mismatch"
            results.append({
                "check": "switching_regulator_count",
                "emc_value": len(sw_refs),
                "source_value": len(non_ldo_refs),
                "status": status,
                "detail": (f"EMC found {len(sw_refs)} switching regs, "
                           f"schematic has {len(non_ldo_refs)} non-LDO regs"),
            })

    # 6. Test plan frequency bands vs actual sources
    test_plan = emc_data.get("test_plan", {})
    if test_plan and schematic_data:
        bands = test_plan.get("frequency_bands", [])
        # Bands with sources should only reference crystals/regulators that exist
        sch_crystals = schematic_data.get("signal_analysis", {}).get("crystal_circuits", [])
        sch_regs = schematic_data.get("signal_analysis", {}).get("power_regulators", [])
        sch_refs = set()
        for x in sch_crystals:
            sch_refs.add(x.get("reference", ""))
        for r in sch_regs:
            sch_refs.add(r.get("ref", r.get("reference", "")))
        sch_refs.discard("")

        sourced_bands = [b for b in bands if b.get("source_count", 0) > 0]
        if sourced_bands:
            results.append({
                "check": "test_plan_frequency_bands",
                "emc_value": len(sourced_bands),
                "source_value": len(bands),
                "status": "match",
                "detail": f"{len(sourced_bands)}/{len(bands)} bands have emission sources",
            })

    # 7. Regulatory market consistency with target standard
    reg = emc_data.get("regulatory_coverage", {})
    standard = emc_data.get("target_standard", "")
    if reg and standard:
        market = reg.get("market", "")
        # Check standard-market consistency
        expected_markets = {
            "fcc-class-b": "us", "fcc-class-a": "us",
            "cispr-class-b": "eu", "cispr-class-a": "eu",
            "cispr-25": "automotive", "mil-std-461": "military",
        }
        expected = expected_markets.get(standard)
        if expected and market:
            status = "match" if market == expected else "mismatch"
            results.append({
                "check": "regulatory_market_consistency",
                "emc_value": market,
                "source_value": expected,
                "status": status,
                "detail": f"standard={standard} → expected market={expected}, got={market}",
            })

    return results


def find_source_json(emc_json_path):
    """Find matching schematic and PCB JSONs for an EMC output.

    EMC output is keyed to schematic filename:
      results/outputs/emc/{repo}/{name}.json
      results/outputs/schematic/{repo}/{name}.json
      results/outputs/pcb/{repo}/{name}.kicad_pcb.json  (derived from name)
    """
    repo_name = f"{emc_json_path.parent.parent.name}/{emc_json_path.parent.name}"
    sch_path = OUTPUTS_DIR / "schematic" / repo_name / emc_json_path.name
    schematic_data = None
    if sch_path.exists():
        try:
            schematic_data = json.loads(sch_path.read_text())
        except Exception:
            pass

    # Derive PCB path
    pcb_data = None
    stem = emc_json_path.name
    pcb_name = None
    if stem.endswith(".kicad_sch.json"):
        pcb_name = stem.replace(".kicad_sch.json", ".kicad_pcb.json")
    elif stem.endswith(".sch.json"):
        pcb_name = stem.replace(".sch.json", ".kicad_pcb.json")
    if pcb_name:
        pcb_path = OUTPUTS_DIR / "pcb" / repo_name / pcb_name
        if pcb_path.exists():
            try:
                pcb_data = json.loads(pcb_path.read_text())
            except Exception:
                pass

    return schematic_data, pcb_data


def main():
    parser = argparse.ArgumentParser(
        description="Cross-validate EMC results against analyzer outputs")
    parser.add_argument("--repo", help="Only validate this repo")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true",
                        help="Only print summary line")
    args = parser.parse_args()

    emc_dir = OUTPUTS_DIR / "emc"
    if not emc_dir.exists():
        print("No EMC outputs found. Run run/run_emc.py first.", file=sys.stderr)
        sys.exit(1)

    total_checks = 0
    total_match = 0
    total_mismatch = 0
    all_results = []
    by_check = {}

    for repo_dir in sorted(emc_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        if args.repo and repo_dir.name != args.repo:
            continue

        for emc_file in sorted(repo_dir.glob("*.json")):
            if emc_file.name.startswith("_"):
                continue
            try:
                emc_data = json.loads(emc_file.read_text())
            except Exception:
                continue

            schematic_data, pcb_data = find_source_json(emc_file)
            results = cross_validate_file(schematic_data, pcb_data, emc_data)

            for r in results:
                total_checks += 1
                if r["status"] == "match":
                    total_match += 1
                else:
                    total_mismatch += 1

                check_name = r["check"]
                if check_name not in by_check:
                    by_check[check_name] = {"match": 0, "mismatch": 0}
                by_check[check_name][r["status"]] += 1

                if not args.summary:
                    rel = f"{repo_dir.name}/{emc_file.name}"
                    status_str = "OK" if r["status"] == "match" else "MISMATCH"
                    if args.json:
                        r["file"] = rel
                        all_results.append(r)
                    else:
                        print(f"  {status_str:8s} {rel}: {r['check']} {r['detail']}")

    if args.json:
        json.dump({
            "total_checks": total_checks,
            "match": total_match,
            "mismatch": total_mismatch,
            "agreement_rate": round(total_match / total_checks * 100, 1) if total_checks else 0,
            "by_check": by_check,
            "results": all_results,
        }, sys.stdout, indent=2)
        print()
        return

    # Print summary
    print()
    print("=" * 60)
    print("EMC Cross-Validation Summary")
    print("=" * 60)
    print(f"Total checks:    {total_checks}")
    print(f"Match:           {total_match}")
    print(f"Mismatch:        {total_mismatch}")
    if total_checks:
        print(f"Agreement rate:  {total_match/total_checks*100:.1f}%")
    print()
    if by_check:
        print("Cross-validation by check:")
        for check, counts in sorted(by_check.items()):
            m = counts["match"]
            mm = counts["mismatch"]
            total = m + mm
            print(f"  {check:30s} {m}/{total} match ({m/total*100:.1f}%)")


if __name__ == "__main__":
    main()
