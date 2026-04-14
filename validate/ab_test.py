#!/usr/bin/env python3
"""A/B blast-radius reporter: compare current outputs against reference baselines.

Uses existing reference/ baselines and results/outputs/ to report how many files
changed, which fields changed, and which repos were affected.

Usage:
    python3 validate/ab_test.py --cross-section smoke
    python3 validate/ab_test.py --cross-section quick_200 --type schematic
    python3 validate/ab_test.py --repo owner/repo
    python3 validate/ab_test.py --cross-section smoke --json
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "regression"))
from _differ import extract_manifest_entry
from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    DEFAULT_JOBS, add_repo_filter_args, resolve_repos,
    list_repos, list_projects_in_data,
    project_prefix, filter_project_outputs, load_project_metadata,
)


# ---------------------------------------------------------------------------
# Core comparison logic (mirrors regression/compare.py but aggregation-focused)
# ---------------------------------------------------------------------------

def _compare_manifest_entries(baseline_entry, current_entry):
    """Return dict of changed fields between two manifest entries."""
    changes = {}
    for key in set(baseline_entry.keys()) | set(current_entry.keys()):
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
            for sk in set(bsig.keys()) | set(csig.keys()):
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
            for tk in set(bdist.keys()) | set(cdist.keys()):
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
            continue

        # dict/list: fall back to simple equality
        if bval != cval and not (bval is None and cval is None):
            changes[key] = {"baseline": bval, "current": cval}

    return changes


def compare_one_project(repo_name, project_name, project_path, analyzer_types):
    """Compare all requested analyzer types for one project.

    Returns dict keyed by analyzer type, each value a dict with:
        compared, changed, only_baseline, only_current,
        field_hits (Counter field_name -> file count),
        new_sections (list), lost_sections (list)
    """
    results = {}
    for atype in analyzer_types:
        baseline_file = DATA_DIR / repo_name / project_name / "baselines" / f"{atype}.json"
        current_dir = OUTPUTS_DIR / atype / repo_name

        if not baseline_file.exists():
            continue

        try:
            baseline_manifest = json.loads(baseline_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        prefix = project_prefix(project_path)
        current_manifest = {}
        if current_dir.exists():
            for jf in filter_project_outputs(current_dir, project_path):
                key = jf.name[len(prefix):] if prefix else jf.name
                try:
                    data = json.loads(jf.read_text(encoding="utf-8"))
                    current_manifest[key] = extract_manifest_entry(data, atype)
                except Exception:
                    pass

        all_files = sorted(set(baseline_manifest.keys()) | set(current_manifest.keys()))

        type_result = {
            "compared": 0,
            "changed": 0,
            "only_baseline": [],
            "only_current": [],
            "field_hits": {},     # field_name -> count
            "new_sections": [],
            "lost_sections": [],
        }
        field_hits = Counter()
        new_sections = Counter()
        lost_sections = Counter()

        for fname in all_files:
            in_baseline = fname in baseline_manifest
            in_current = fname in current_manifest
            if in_baseline and not in_current:
                type_result["only_baseline"].append(fname)
                continue
            if in_current and not in_baseline:
                type_result["only_current"].append(fname)
                continue

            type_result["compared"] += 1
            base_entry = baseline_manifest[fname]
            curr_entry = current_manifest[fname]

            if "error" in base_entry or "error" in curr_entry:
                continue

            changes = _compare_manifest_entries(base_entry, curr_entry)
            if changes:
                type_result["changed"] += 1
                for field, detail in changes.items():
                    if field == "signal_counts":
                        for sig_field in detail:
                            field_hits[f"findings.{sig_field}"] += 1
                    elif field == "sections":
                        for s in detail.get("new", []):
                            new_sections[s] += 1
                        for s in detail.get("lost", []):
                            lost_sections[s] += 1
                        field_hits["sections"] += 1
                    elif field == "component_types":
                        field_hits["component_types"] += 1
                    else:
                        field_hits[field] += 1

        type_result["field_hits"] = dict(field_hits)
        type_result["new_sections"] = dict(new_sections)
        type_result["lost_sections"] = dict(lost_sections)
        results[atype] = type_result

    return results


def _ab_repo_worker(repo_name, analyzer_types):
    """Worker: compare one repo. Returns (repo_name, per_type summary)."""
    projects = list_projects_in_data(repo_name)
    if not projects:
        return repo_name, {}

    # Aggregate across all projects in this repo
    agg = {}  # atype -> {compared, changed, only_baseline, only_current, field_hits, new_sections, lost_sections}
    for proj_name in projects:
        project_path = load_project_metadata(repo_name, proj_name).get("project_path", ".")
        proj_result = compare_one_project(repo_name, proj_name, project_path, analyzer_types)
        for atype, pr in proj_result.items():
            if atype not in agg:
                agg[atype] = {
                    "compared": 0, "changed": 0,
                    "only_baseline": [], "only_current": [],
                    "field_hits": Counter(),
                    "new_sections": Counter(),
                    "lost_sections": Counter(),
                }
            a = agg[atype]
            a["compared"] += pr["compared"]
            a["changed"] += pr["changed"]
            a["only_baseline"].extend(pr["only_baseline"])
            a["only_current"].extend(pr["only_current"])
            for f, c in pr["field_hits"].items():
                a["field_hits"][f] += c
            for s, c in pr["new_sections"].items():
                a["new_sections"][s] += c
            for s, c in pr["lost_sections"].items():
                a["lost_sections"][s] += c

    # Serialize Counters to plain dicts
    for atype in agg:
        agg[atype]["field_hits"] = dict(agg[atype]["field_hits"])
        agg[atype]["new_sections"] = dict(agg[atype]["new_sections"])
        agg[atype]["lost_sections"] = dict(agg[atype]["lost_sections"])

    return repo_name, agg


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_results(all_repo_results, analyzer_types):
    """Aggregate per-repo results into global totals.

    Returns a dict with keys:
        total_files, changed_files, unchanged_files,
        new_sections_count, lost_sections_count,
        field_hits (Counter), new_sections (Counter), lost_sections (Counter),
        repos_changed (dict repo -> files_changed),
        per_type (dict atype -> {compared, changed, ...})
    """
    total = 0
    changed = 0
    field_hits = Counter()
    new_sections = Counter()
    lost_sections = Counter()
    repos_changed = {}  # repo -> files_changed
    per_type = {}

    for repo_name, repo_agg in all_repo_results.items():
        repo_changed = 0
        for atype, ar in repo_agg.items():
            if atype not in per_type:
                per_type[atype] = {"compared": 0, "changed": 0,
                                   "only_baseline": 0, "only_current": 0}
            per_type[atype]["compared"] += ar["compared"]
            per_type[atype]["changed"] += ar["changed"]
            per_type[atype]["only_baseline"] += len(ar["only_baseline"])
            per_type[atype]["only_current"] += len(ar["only_current"])
            total += ar["compared"]
            changed += ar["changed"]
            repo_changed += ar["changed"]
            for f, c in ar["field_hits"].items():
                field_hits[f] += c
            for s, c in ar["new_sections"].items():
                new_sections[s] += c
            for s, c in ar["lost_sections"].items():
                lost_sections[s] += c

        if repo_changed > 0:
            repos_changed[repo_name] = repo_changed

    return {
        "total_files": total,
        "changed_files": changed,
        "unchanged_files": total - changed,
        "new_sections_total": sum(new_sections.values()),
        "lost_sections_total": sum(lost_sections.values()),
        "field_hits": dict(field_hits),
        "new_sections": dict(new_sections),
        "lost_sections": dict(lost_sections),
        "repos_changed": dict(sorted(repos_changed.items(),
                                     key=lambda x: -x[1])),
        "per_type": per_type,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(summary, repos_in_section, analyzer_types, section_label):
    total = summary["total_files"]
    changed = summary["changed_files"]
    unchanged = summary["unchanged_files"]
    pct = changed * 100 / total if total else 0.0
    repos_changed_count = len(summary["repos_changed"])
    repos_total = len(repos_in_section)

    print("A/B Report: reference/ vs results/outputs/")
    if section_label:
        print(f"Cross-section: {section_label} ({repos_total} repos)")
    print(f"Types: {', '.join(analyzer_types)}")
    print()

    print(f"Files analyzed:    {total:>7,}")
    print(f"Output changed:    {changed:>7,} ({pct:.1f}%)")

    # Section changes
    ns_total = summary["new_sections_total"]
    ls_total = summary["lost_sections_total"]
    if ns_total or ls_total:
        print(f"  New sections:    {ns_total:>7,}")
        print(f"  Removed sections:{ls_total:>7,}")

    # Field hits (excluding sections)
    field_hits = {k: v for k, v in summary["field_hits"].items() if k != "sections"}
    changed_field_count = len(field_hits)
    if changed_field_count:
        print(f"  Changed fields:  {changed_field_count:>7,}")

    print(f"Unchanged:         {unchanged:>7,} ({100 - pct:.1f}%)")

    # Per-type breakdown
    if len(analyzer_types) > 1 and summary["per_type"]:
        print()
        print("Per-type:")
        for atype in analyzer_types:
            pt = summary["per_type"].get(atype)
            if not pt:
                continue
            pt_total = pt["compared"]
            pt_changed = pt["changed"]
            pt_pct = pt_changed * 100 / pt_total if pt_total else 0.0
            ob = pt["only_baseline"]
            oc = pt["only_current"]
            line = f"  {atype:<12s} {pt_total:>5,} files, {pt_changed:>4,} changed ({pt_pct:.1f}%)"
            if ob:
                line += f", {ob} only-in-baseline"
            if oc:
                line += f", {oc} only-in-current"
            print(line)

    # Top changed fields
    if field_hits:
        print()
        print("Top changed fields:")
        for field, count in sorted(field_hits.items(), key=lambda x: -x[1])[:15]:
            print(f"    {field:<50s} ({count} files)")

    # New/lost sections detail
    if summary["new_sections"]:
        print()
        print("New sections detected:")
        for s, c in sorted(summary["new_sections"].items(), key=lambda x: -x[1])[:10]:
            print(f"    {s:<50s} ({c} files)")
    if summary["lost_sections"]:
        print()
        print("Removed sections:")
        for s, c in sorted(summary["lost_sections"].items(), key=lambda x: -x[1])[:10]:
            print(f"    {s:<50s} ({c} files)")

    # Changed repos
    print()
    if repos_changed_count == 0:
        print("No repos changed.")
    else:
        print(f"Changed repos ({repos_changed_count}/{repos_total}):")
        for repo, n in list(summary["repos_changed"].items())[:30]:
            print(f"  {repo}: {n} files changed")
        if repos_changed_count > 30:
            print(f"  ... and {repos_changed_count - 30} more")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="A/B blast-radius report: reference/ vs results/outputs/"
    )
    add_repo_filter_args(parser)
    parser.add_argument(
        "--type", dest="type_filter",
        choices=ANALYZER_TYPES,
        help="Only compare one analyzer type"
    )
    parser.add_argument(
        "--jobs", "-j", type=int, default=DEFAULT_JOBS,
        help=f"Number of parallel workers (default: {DEFAULT_JOBS})"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of human-readable text"
    )
    args = parser.parse_args()

    resolved = resolve_repos(args)
    if resolved is None:
        # No filter → all repos with baselines
        resolved = list_repos()

    repos = [r for r in resolved if (DATA_DIR / r).exists()]
    if not repos:
        print("No repos with baseline data found.", file=sys.stderr)
        sys.exit(1)

    analyzer_types = [args.type_filter] if args.type_filter else ANALYZER_TYPES
    jobs = args.jobs

    # Determine section label for display
    section_label = None
    if getattr(args, "cross_section", None):
        section_label = args.cross_section
    elif getattr(args, "repo", None):
        section_label = None  # single repo, handled differently

    # Run comparisons
    all_repo_results = {}
    if jobs <= 1 or len(repos) <= 1:
        for repo_name in repos:
            _, repo_agg = _ab_repo_worker(repo_name, analyzer_types)
            if repo_agg:
                all_repo_results[repo_name] = repo_agg
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            futures = {
                pool.submit(_ab_repo_worker, repo_name, analyzer_types): repo_name
                for repo_name in repos
            }
            for future in as_completed(futures):
                repo_name, repo_agg = future.result()
                if repo_agg:
                    all_repo_results[repo_name] = repo_agg

    summary = aggregate_results(all_repo_results, analyzer_types)

    if args.json:
        # Add metadata to JSON output
        output = {
            "section": section_label,
            "repos_total": len(repos),
            "repos_with_baselines": len(all_repo_results),
            "analyzer_types": analyzer_types,
            **summary,
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(summary, repos, analyzer_types, section_label)


if __name__ == "__main__":
    main()
