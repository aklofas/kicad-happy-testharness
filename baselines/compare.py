#!/usr/bin/env python3
"""Compare current analyzer outputs against a baseline.

Uses the compact baseline manifests (in data/baselines/) to compare
against current outputs without needing the full baseline JSONs.
If full baseline copies exist (in results/baselines/), uses those
for deeper semantic diffing.

Usage:
    python3 baselines/compare.py <baseline-name>
    python3 baselines/compare.py <baseline-name> --type schematic
    python3 baselines/compare.py <baseline-name> --json
    python3 baselines/compare.py <baseline-name> --only-changes
"""

import argparse
import json
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR / "baselines"))
from _differ import diff_schematic, diff_pcb, diff_gerber, extract_manifest_entry

OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
MANIFESTS_BASE = HARNESS_DIR / "data" / "baselines"
FULL_BASE = HARNESS_DIR / "results" / "baselines"
ANALYZER_TYPES = ["schematic", "pcb", "gerber"]

DIFFER_BY_TYPE = {
    "schematic": diff_schematic,
    "pcb": diff_pcb,
    "gerber": diff_gerber,
}


def _compare_manifest_entries(baseline_entry, current_entry):
    """Compare two manifest entries (compact format). Returns diff dict."""
    changes = {}

    # Compare all numeric fields
    for key in set(list(baseline_entry.keys()) + list(current_entry.keys())):
        bval = baseline_entry.get(key)
        cval = current_entry.get(key)

        if key == "sections":
            bset = set(bval or [])
            cset = set(cval or [])
            new = sorted(cset - bset)
            lost = sorted(bset - cset)
            if new or lost:
                changes["sections"] = {"new": new, "lost": lost}
            continue

        if key == "signal_counts":
            bsig = bval or {}
            csig = cval or {}
            sig_changes = {}
            for sk in set(list(bsig.keys()) + list(csig.keys())):
                sb = bsig.get(sk, 0)
                sc = csig.get(sk, 0)
                if sb != sc:
                    sig_changes[sk] = {"baseline": sb, "current": sc, "delta": sc - sb}
            if sig_changes:
                changes["signal_counts"] = sig_changes
            continue

        if key == "component_types":
            bdist = bval or {}
            cdist = cval or {}
            type_changes = {}
            for tk in set(list(bdist.keys()) + list(cdist.keys())):
                tb = bdist.get(tk, 0)
                tc = cdist.get(tk, 0)
                if tb != tc:
                    type_changes[tk] = {"baseline": tb, "current": tc, "delta": tc - tb}
            if type_changes:
                changes["component_types"] = type_changes
            continue

        if isinstance(bval, (int, float)) and isinstance(cval, (int, float)):
            if bval != cval:
                changes[key] = {"baseline": bval, "current": cval, "delta": cval - bval}

    return changes


def compare_type(baseline_name, analyzer_type, only_changes=False):
    """Compare a single analyzer type. Returns structured results."""
    manifest_file = MANIFESTS_BASE / baseline_name / f"{analyzer_type}.json"
    current_dir = OUTPUTS_DIR / analyzer_type
    full_baseline_dir = FULL_BASE / baseline_name / analyzer_type

    if not manifest_file.exists():
        return {"error": f"No baseline manifest for {analyzer_type}"}

    baseline_manifest = json.loads(manifest_file.read_text())
    use_full = full_baseline_dir.exists()

    # Build current manifest
    current_manifest = {}
    if current_dir.exists():
        for jf in sorted(current_dir.glob("*.json")):
            try:
                data = json.loads(jf.read_text())
                current_manifest[jf.name] = extract_manifest_entry(data, analyzer_type)
            except Exception as e:
                current_manifest[jf.name] = {"error": str(e)}

    all_files = sorted(set(list(baseline_manifest.keys()) + list(current_manifest.keys())))

    results = {
        "files_compared": 0,
        "files_with_changes": 0,
        "files_only_in_baseline": [],
        "files_only_in_current": [],
        "file_diffs": {},
        "change_scores": {},
    }

    for fname in all_files:
        in_baseline = fname in baseline_manifest
        in_current = fname in current_manifest

        if in_baseline and not in_current:
            results["files_only_in_baseline"].append(fname)
            continue
        if in_current and not in_baseline:
            results["files_only_in_current"].append(fname)
            continue

        results["files_compared"] += 1

        # Try full diff if available
        if use_full:
            base_file = full_baseline_dir / fname
            curr_file = current_dir / fname
            if base_file.exists() and curr_file.exists():
                try:
                    base_data = json.loads(base_file.read_text())
                    curr_data = json.loads(curr_file.read_text())
                    differ = DIFFER_BY_TYPE.get(analyzer_type)
                    if differ:
                        diff = differ(base_data, curr_data)
                        if diff["has_changes"]:
                            results["files_with_changes"] += 1
                            results["file_diffs"][fname] = diff
                            results["change_scores"][fname] = diff["change_score"]
                        elif not only_changes:
                            results["file_diffs"][fname] = diff
                        continue
                except Exception:
                    pass

        # Fall back to manifest comparison
        base_entry = baseline_manifest[fname]
        curr_entry = current_manifest[fname]

        if "error" in base_entry or "error" in curr_entry:
            continue

        changes = _compare_manifest_entries(base_entry, curr_entry)
        if changes:
            results["files_with_changes"] += 1
            results["file_diffs"][fname] = {
                "has_changes": True,
                "manifest_changes": changes,
                "change_score": len(changes) * 2,
            }
            results["change_scores"][fname] = len(changes) * 2
        elif not only_changes:
            results["file_diffs"][fname] = {"has_changes": False, "change_score": 0}

    return results


def print_report(all_results, only_changes=False):
    """Print human-readable comparison report."""
    print("=" * 70)
    print("BASELINE COMPARISON REPORT")
    print("=" * 70)

    total_compared = 0
    total_changed = 0
    total_only_baseline = 0
    total_only_current = 0

    for atype, results in sorted(all_results.items()):
        if "error" in results:
            print(f"\n--- {atype}: {results['error']} ---")
            continue

        total_compared += results["files_compared"]
        total_changed += results["files_with_changes"]
        total_only_baseline += len(results["files_only_in_baseline"])
        total_only_current += len(results["files_only_in_current"])

        print(f"\n--- {atype} ---")
        print(f"  Compared: {results['files_compared']}")
        print(f"  Changed:  {results['files_with_changes']}")

        if results["files_only_in_baseline"]:
            print(f"  Only in baseline: {len(results['files_only_in_baseline'])}")
        if results["files_only_in_current"]:
            print(f"  Only in current:  {len(results['files_only_in_current'])}")

        # Show top changed files
        scored = sorted(
            results["change_scores"].items(), key=lambda x: x[1], reverse=True
        )
        if scored:
            print(f"\n  Most changed files:")
            for fname, score in scored[:10]:
                diff = results["file_diffs"].get(fname, {})
                parts = []

                # Summarize changes
                manifest_changes = diff.get("manifest_changes", {})
                if manifest_changes:
                    for key, val in manifest_changes.items():
                        if key == "signal_counts":
                            for sk, sv in val.items():
                                d = sv["delta"]
                                parts.append(f"{sk}: {'+' if d > 0 else ''}{d}")
                        elif key == "sections":
                            if val.get("new"):
                                parts.append(f"+sections: {','.join(val['new'][:3])}")
                            if val.get("lost"):
                                parts.append(f"-sections: {','.join(val['lost'][:3])}")
                        elif isinstance(val, dict) and "delta" in val:
                            d = val["delta"]
                            parts.append(f"{key}: {'+' if d > 0 else ''}{d}")

                # Full diff details
                for key in ["count_deltas", "signal_deltas", "design_deltas"]:
                    section = diff.get(key, {})
                    for sk, sv in section.items():
                        if isinstance(sv, dict):
                            d = sv.get("delta", sv.get("new_count", 0) - sv.get("lost_count", 0))
                            label = sk.split(".")[-1]
                            parts.append(f"{label}: {'+' if d > 0 else ''}{d}")

                detail = ", ".join(parts[:5]) if parts else "minor changes"
                short_name = fname[:50] + "..." if len(fname) > 50 else fname
                print(f"    [{score:3d}] {short_name}")
                print(f"          {detail}")

    print(f"\n{'=' * 70}")
    print(f"TOTALS: {total_compared} compared, {total_changed} changed, "
          f"{total_only_baseline} removed, {total_only_current} new")


def main():
    parser = argparse.ArgumentParser(description="Compare outputs against a baseline")
    parser.add_argument("baseline", help="Baseline name to compare against")
    parser.add_argument("--type", choices=ANALYZER_TYPES, help="Only compare one analyzer type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--only-changes", action="store_true", help="Only show files with changes")
    args = parser.parse_args()

    baseline_dir = MANIFESTS_BASE / args.baseline
    if not baseline_dir.exists():
        print(f"Error: Baseline '{args.baseline}' not found.")
        print(f"Available baselines:")
        if MANIFESTS_BASE.exists():
            for d in sorted(MANIFESTS_BASE.iterdir()):
                if (d / "metadata.json").exists():
                    print(f"  {d.name}")
        sys.exit(1)

    types = [args.type] if args.type else ANALYZER_TYPES
    all_results = {}
    for atype in types:
        all_results[atype] = compare_type(args.baseline, atype, only_changes=args.only_changes)

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        meta_file = baseline_dir / "metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            print(f"Comparing against baseline: {meta['name']}")
            print(f"  Created: {meta['created'][:19]}")
            commit = meta.get("analyzer_commit")
            if commit:
                print(f"  Analyzer commit: {commit[:12]}")
            print()
        print_report(all_results, only_changes=args.only_changes)


if __name__ == "__main__":
    main()
