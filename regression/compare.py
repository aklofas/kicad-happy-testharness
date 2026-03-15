#!/usr/bin/env python3
"""Compare current analyzer outputs against baselines.

Uses per-project baselines in data/{repo}/{project}/baselines/ to compare
against current outputs in results/outputs/{type}/{repo}/.

Usage:
    python3 regression/compare.py --repo OpenMower
    python3 regression/compare.py --all
    python3 regression/compare.py --repo OpenMower --type schematic
    python3 regression/compare.py --all --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _differ import extract_manifest_entry
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    list_repos, list_projects_in_data,
    project_prefix, load_project_metadata,
    filter_project_outputs,
)


def _compare_manifest_entries(baseline_entry, current_entry):
    changes = {}
    for key in baseline_entry.keys() | current_entry.keys():
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
            for sk in bsig.keys() | csig.keys():
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
            for tk in bdist.keys() | cdist.keys():
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


def compare_project(repo_name, project_name, project_path, analyzer_type, only_changes=False):
    """Compare a single analyzer type for one project."""
    baseline_file = DATA_DIR / repo_name / project_name / "baselines" / f"{analyzer_type}.json"
    current_dir = OUTPUTS_DIR / analyzer_type / repo_name

    if not baseline_file.exists():
        return {"error": f"No baseline for {project_name}/{analyzer_type}"}

    baseline_manifest = json.loads(baseline_file.read_text())

    # Build current manifest from outputs matching this project
    prefix = project_prefix(project_path)

    current_manifest = {}
    if current_dir.exists():
        for jf in filter_project_outputs(current_dir, project_path):
            key = jf.name[len(prefix):] if prefix else jf.name
            try:
                data = json.loads(jf.read_text())
                current_manifest[key] = extract_manifest_entry(data, analyzer_type)
            except Exception as e:
                current_manifest[key] = {"error": str(e)}

    all_files = sorted(baseline_manifest.keys() | current_manifest.keys())

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


def print_type_report(atype, results):
    if "error" in results:
        print(f"\n  --- {atype}: {results['error']} ---")
        return 0, 0

    print(f"\n  --- {atype} ---")
    print(f"    Compared: {results['files_compared']}")
    print(f"    Changed:  {results['files_with_changes']}")

    if results["files_only_in_baseline"]:
        print(f"    Only in baseline: {len(results['files_only_in_baseline'])}")
    if results["files_only_in_current"]:
        print(f"    Only in current:  {len(results['files_only_in_current'])}")

    scored = sorted(results["change_scores"].items(), key=lambda x: x[1], reverse=True)
    if scored:
        print(f"    Most changed:")
        for fname, score in scored[:10]:
            diff = results["file_diffs"].get(fname, {})
            parts = []
            mc = diff.get("manifest_changes", {})
            for key, val in mc.items():
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
            detail = ", ".join(parts[:5]) if parts else "minor changes"
            short = fname[:50] + "..." if len(fname) > 50 else fname
            print(f"      [{score:3d}] {short}")
            print(f"            {detail}")

    return results["files_compared"], results["files_with_changes"]


def main():
    parser = argparse.ArgumentParser(description="Compare outputs against baselines")
    parser.add_argument("--repo", help="Compare one repo")
    parser.add_argument("--all", action="store_true", help="Compare all repos with baselines")
    parser.add_argument("--type", choices=ANALYZER_TYPES, help="Only compare one analyzer type")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--only-changes", action="store_true", help="Only show changed files")
    args = parser.parse_args()

    if args.repo:
        repos = [args.repo]
    elif args.all:
        if not DATA_DIR.exists():
            print("No data found.")
            sys.exit(1)
        repos = sorted(d.name for d in DATA_DIR.iterdir() if d.is_dir())
    else:
        parser.print_help()
        sys.exit(1)

    types = [args.type] if args.type else ANALYZER_TYPES
    all_output = {}

    for repo in repos:
        projects = list_projects_in_data(repo)
        if not projects:
            continue

        repo_output = {}
        for proj_name in projects:
            # Read project_path from metadata if available
            project_path = load_project_metadata(repo, proj_name).get("project_path", ".")

            proj_results = {}
            for atype in types:
                proj_results[atype] = compare_project(
                    repo, proj_name, project_path, atype,
                    only_changes=args.only_changes)
            repo_output[proj_name] = proj_results

        all_output[repo] = repo_output

    if args.json:
        print(json.dumps(all_output, indent=2))
    else:
        for repo, projects in sorted(all_output.items()):
            print("=" * 70)
            print(f"BASELINE COMPARISON: {repo}")
            print("=" * 70)
            total_compared = total_changed = 0
            for proj_name, type_results in sorted(projects.items()):
                print(f"\n  [{proj_name}]")
                for atype in types:
                    c, ch = print_type_report(atype, type_results.get(atype, {}))
                    total_compared += c
                    total_changed += ch
            print(f"\n  TOTALS: {total_compared} compared, {total_changed} changed")
            print()


if __name__ == "__main__":
    main()
