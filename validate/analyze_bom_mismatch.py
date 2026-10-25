#!/usr/bin/env python3
"""Analyze BOM quantity vs component count mismatches — identify root causes.

Usage:
    python3 validate/analyze_bom_mismatch.py
    python3 validate/analyze_bom_mismatch.py --repo owner/repo
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR


def schematic_output_files(outputs_dir, repo=None):
    """Schematic outputs live at <outputs>/<owner>/<repo>/*.json; `repo` is owner/repo."""
    files = []
    if not outputs_dir.exists():
        return files
    for owner_dir in sorted(d for d in outputs_dir.iterdir() if d.is_dir()):
        for repo_dir in sorted(d for d in owner_dir.iterdir() if d.is_dir()):
            if repo and f"{owner_dir.name}/{repo_dir.name}" != repo:
                continue
            files.extend(f for f in sorted(repo_dir.glob("*.json"))
                         if f.name != "capability_mode.json" and not f.name.startswith("_"))
    return files


def main():
    parser = argparse.ArgumentParser(description="Analyze BOM mismatch root causes")
    parser.add_argument("--repo", help="Only analyze outputs for this repo")
    parser.add_argument("--threshold", type=int, default=5,
                        help="Minimum |bom_qty - comp_count| to flag (default: 5)")
    args = parser.parse_args()

    threshold = args.threshold
    json_files = schematic_output_files(OUTPUTS_DIR / "schematic", args.repo)

    total_mismatch = 0
    cause_final = Counter()

    for jf in json_files:
        try:
            with open(jf) as f:
                data = json.load(f)
        except Exception:
            continue

        bom = data.get("bom", [])
        components = data.get("components", [])
        bom_qty = sum(e.get("quantity", 0) for e in bom)
        non_power = [c for c in components if not c.get("reference", "").startswith("#")]
        comp_count = len(non_power)
        gap = bom_qty - comp_count

        if abs(gap) <= threshold:
            continue

        total_mismatch += 1

        # --- Correction factors ---
        power_in_bom = sum(1 for e in bom for r in e.get("references", []) if r.startswith("#"))

        ref_counts = Counter(c.get("reference", "") for c in non_power)
        comp_dup_extras = sum(count - 1 for count in ref_counts.values() if count > 1)

        ibf = sum(1 for c in non_power
                  if c.get("in_bom") is False or
                  (isinstance(c.get("in_bom"), str) and c.get("in_bom").lower() in ("false", "no")))

        bom_refs_set = set()
        for e in bom:
            for r in e.get("references", []):
                bom_refs_set.add(r)
        comp_refs_set = set(c.get("reference", "") for c in non_power)

        extra_bom = len([r for r in (bom_refs_set - comp_refs_set) if not r.startswith("#")])

        ibf_refs = set(c.get("reference", "") for c in non_power
                       if c.get("in_bom") is False or
                       (isinstance(c.get("in_bom"), str) and c.get("in_bom").lower() in ("false", "no")))
        missing_bom_not_ibf = len((comp_refs_set - bom_refs_set) - ibf_refs)

        corrected = gap + ibf + comp_dup_extras + missing_bom_not_ibf - power_in_bom - extra_bom

        if abs(corrected) <= 2:
            factors = []
            if comp_dup_extras > 0:
                factors.append("multi-unit parts")
            if ibf > 0:
                factors.append("in_bom=false")
            if power_in_bom > 0:
                factors.append("power symbols in BOM")
            if extra_bom > 0:
                factors.append("cross-sheet BOM refs")
            if missing_bom_not_ibf > 0:
                factors.append("missing from BOM (other)")
            cause_final[" + ".join(factors) if factors else "small combined"] += 1
        else:
            cause_final["STILL UNEXPLAINED"] += 1

    if total_mismatch == 0:
        print("No BOM mismatches found above threshold.")
        return

    explained = sum(v for k, v in cause_final.items() if k != "STILL UNEXPLAINED")
    unexpl = cause_final.get("STILL UNEXPLAINED", 0)

    print("=" * 70)
    print("BOM MISMATCH ANALYSIS")
    print("=" * 70)
    print()
    print(f"Total JSON output files analyzed: {len(json_files)}")
    print(f"Files with |bom_qty - comp_count| > {threshold}: {total_mismatch}")
    print()
    print(f"Fully explained by known causes: {explained} ({explained/total_mismatch*100:.1f}%)")
    print(f"Still unexplained: {unexpl} ({unexpl/total_mismatch*100:.1f}%)")
    print()
    print("Root cause breakdown:")
    for cause, count in cause_final.most_common():
        pct = count / total_mismatch * 100
        print(f"  {count:4d} ({pct:5.1f}%) -- {cause}")


if __name__ == "__main__":
    main()
