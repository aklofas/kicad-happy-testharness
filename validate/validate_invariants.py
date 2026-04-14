#!/usr/bin/env python3
"""Property-based invariant checker for schematic analyzer outputs.

Checks mathematical and structural invariants that must always hold:
- Voltage divider ratio: 0 < ratio < 1
- RC filter cutoff: cutoff_hz > 0 (when R > 0 and C > 0)
- LC filter resonance: resonant_hz > 0 (when L > 0 and C > 0)
- Crystal: effective_load_pF > 0
- Component count: total_components >= sum of component_types counts
- No unexpected duplicate component refs

Usage:
    python3 validate/validate_invariants.py
    python3 validate/validate_invariants.py --repo owner/repo
    python3 validate/validate_invariants.py --summary
    python3 validate/validate_invariants.py --cross-section smoke --jobs 16
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, MANIFESTS_DIR, REPOS_DIR, list_repos,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
                   _truncate_with_hash)


def check_invariants(data, filepath=""):
    """Check invariants on a schematic analyzer output dict.

    Returns a list of (filepath, violation_description) tuples.
    Null values are skipped (not flagged).
    """
    violations = []

    def _add(desc):
        violations.append((filepath, desc))

    # Group findings by detector
    grouped = {}
    for f in data.get("findings", []):
        det = f.get("detector", "")
        if det:
            grouped.setdefault(det, []).append(f)

    # --- Voltage divider ratio: 0 < ratio < 1 ---
    for i, vd in enumerate(grouped.get("detect_voltage_dividers", [])):
        ratio = vd.get("ratio")
        if ratio is None:
            continue
        if ratio <= 0:
            _add(f"voltage_dividers[{i}].ratio={ratio} <= 0")
        if ratio >= 1:
            _add(f"voltage_dividers[{i}].ratio={ratio} >= 1")

    # --- RC filter cutoff_hz > 0 ---
    for i, rc in enumerate(grouped.get("detect_rc_filters", [])):
        cutoff = rc.get("cutoff_hz")
        if cutoff is None:
            continue
        if cutoff <= 0:
            _add(f"rc_filters[{i}].cutoff_hz={cutoff} <= 0")

    # --- LC filter resonant_hz > 0 ---
    for i, lc in enumerate(grouped.get("detect_lc_filters", [])):
        resonant = lc.get("resonant_hz")
        if resonant is None:
            continue
        if resonant <= 0:
            _add(f"lc_filters[{i}].resonant_hz={resonant} <= 0")

    # --- Crystal effective_load_pF > 0 ---
    for i, xtal in enumerate(grouped.get("detect_crystal_circuits", [])):
        load = xtal.get("effective_load_pF")
        if load is None:
            continue
        if load <= 0:
            _add(f"crystal_circuits[{i}].effective_load_pF={load} <= 0")

    # --- Every net referenced in findings exists in extracted nets ---
    nets = data.get("nets", {})
    if isinstance(nets, dict):
        net_names = set(nets.keys())
    elif isinstance(nets, list):
        net_names = {n.get("name", "") for n in nets if isinstance(n, dict)}
    else:
        net_names = set()

    if net_names and grouped:
        for det_name, items in grouped.items():
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                for field, val in item.items():
                    if field.endswith("_net") and isinstance(val, str) and val:
                        if val not in net_names:
                            _add(f"{det_name}[{i}].{field}='{val}' not in nets")

    # --- total_components >= len(components) ---
    components = data.get("components", [])
    stats = data.get("statistics", {})
    total = stats.get("total_components")
    if total is not None and len(components) > total:
        _add(f"len(components)={len(components)} > total_components={total}")

    # --- Component count: total_components >= sum(component_types) ---
    stats = data.get("statistics", {})
    total = stats.get("total_components")
    comp_types = stats.get("component_types")
    if total is not None and isinstance(comp_types, dict):
        type_sum = sum(v for v in comp_types.values() if isinstance(v, (int, float)))
        if type_sum > total:
            _add(f"component_types sum ({type_sum}) > total_components ({total})")

    # --- Duplicate component refs (excluding known annotation issues) ---
    components = data.get("components", [])
    if components:
        # Gather known duplicate refs from annotation_issues
        aa = data.get("annotation_issues", {})
        known_dupes = set()
        if isinstance(aa, dict):
            for ref in aa.get("duplicate_references", []):
                if isinstance(ref, str):
                    known_dupes.add(ref)
                elif isinstance(ref, dict):
                    r = ref.get("reference", "")
                    if r:
                        known_dupes.add(r)

        # Count refs (skip power symbols and unassigned)
        ref_counts = defaultdict(int)
        for comp in components:
            ref = comp.get("reference", "")
            if ref and ref != "?" and not ref.startswith("#"):
                ref_counts[ref] += 1

        for ref, count in sorted(ref_counts.items()):
            if count > 1 and ref not in known_dupes:
                _add(f"duplicate ref '{ref}' appears {count} times "
                     f"(not in annotation_issues)")

    return violations


def _check_file(json_path):
    """Load a JSON output and check invariants. Returns list of violations."""
    try:
        with open(json_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    return check_invariants(data, filepath=str(json_path))


def _check_repo(repo_pair):
    """Check all schematic outputs for a repo. Picklable worker."""
    repo, schematics = repo_pair
    repos_dir = str(REPOS_DIR)
    all_violations = []

    for sch_path in schematics:
        relpath = sch_path
        if sch_path.startswith(repos_dir):
            relpath = sch_path[len(repos_dir):].lstrip("/").lstrip(os.sep)

        parts = relpath.replace("\\", "/").split("/", 2)
        if len(parts) < 3:
            continue
        owner = parts[0]
        repo_name = parts[1]
        within_repo = parts[2]
        safe_name = _truncate_with_hash(within_repo.replace(os.sep, "_").replace("/", "_"))

        json_path = OUTPUTS_DIR / "schematic" / owner / repo_name / f"{safe_name}.json"
        if json_path.exists():
            all_violations.extend(_check_file(json_path))

    return repo, all_violations


def main():
    parser = argparse.ArgumentParser(
        description="Check mathematical/structural invariants in schematic outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--summary", action="store_true",
                        help="Show only summary counts, not individual violations")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        repos = list_repos()

    schematics_list = MANIFESTS_DIR / "all_schematics.txt"
    if not schematics_list.exists():
        print(f"Error: {schematics_list} not found. Run discover.py first.")
        sys.exit(1)

    with open(schematics_list) as f:
        all_schematics = [line.strip() for line in f if line.strip()]

    # Group schematics by repo
    repos_dir = str(REPOS_DIR)
    repo_set = set(repos)
    by_repo = defaultdict(list)
    for s in all_schematics:
        relpath = s
        if s.startswith(repos_dir):
            relpath = s[len(repos_dir):].lstrip("/").lstrip(os.sep)
        parts = relpath.replace("\\", "/").split("/")
        if len(parts) >= 2:
            repo_name = f"{parts[0]}/{parts[1]}"
        else:
            repo_name = parts[0]
        if repo_name in repo_set:
            by_repo[repo_name].append(s)

    total_schematics = sum(len(v) for v in by_repo.values())
    work_items = list(by_repo.items())

    all_violations = []
    violations_by_repo = {}
    jobs = args.jobs

    if jobs > 1 and len(work_items) > 1:
        with ProcessPoolExecutor(max_workers=min(jobs, len(work_items))) as pool:
            futures = {pool.submit(_check_repo, item): item[0]
                       for item in work_items}
            for future in as_completed(futures):
                repo, viols = future.result()
                if viols:
                    violations_by_repo[repo] = viols
                    all_violations.extend(viols)
    else:
        for item in work_items:
            repo, viols = _check_repo(item)
            if viols:
                violations_by_repo[repo] = viols
                all_violations.extend(viols)

    # Categorize violations
    categories = defaultdict(int)
    for _fp, desc in all_violations:
        if "voltage_dividers" in desc:
            categories["voltage_divider_ratio"] += 1
        elif "rc_filters" in desc:
            categories["rc_filter_cutoff"] += 1
        elif "lc_filters" in desc:
            categories["lc_filter_resonance"] += 1
        elif "crystal_circuits" in desc:
            categories["crystal_load"] += 1
        elif "component_types sum" in desc:
            categories["component_count"] += 1
        elif "duplicate ref" in desc:
            categories["duplicate_ref"] += 1
        else:
            categories["other"] += 1

    if args.json:
        output = {
            "schematics_checked": total_schematics,
            "repos_checked": len(by_repo),
            "total_violations": len(all_violations),
            "repos_with_violations": len(violations_by_repo),
            "categories": dict(categories),
            "violations": [{"file": fp, "description": desc}
                           for fp, desc in all_violations],
        }
        print(json.dumps(output, indent=2))
        return

    print(f"Checked {total_schematics} schematics across {len(by_repo)} repos")
    print(f"Violations: {len(all_violations)} across "
          f"{len(violations_by_repo)} repos")
    print()

    if categories:
        print("By category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        print()

    if all_violations and not args.summary:
        for repo in sorted(violations_by_repo.keys()):
            viols = violations_by_repo[repo]
            print(f"--- {repo} ({len(viols)}) ---")
            for fp, desc in viols[:20]:
                short = os.path.basename(fp) if fp else "(unknown)"
                print(f"  {short}: {desc}")
            if len(viols) > 20:
                print(f"  ... and {len(viols) - 20} more")
            print()

    if not all_violations:
        print("NO INVARIANT VIOLATIONS")


if __name__ == "__main__":
    main()
