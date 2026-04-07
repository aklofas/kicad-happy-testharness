#!/usr/bin/env python3
"""Promote current results to reference when they improve.

Compares current analyzer outputs (results/) against reference data
(reference/) and promotes improvements. This updates baselines and
regenerates seed assertions for projects where outputs improved.

Usage:
    python3 regression/promote.py --repo OpenMower              # Show what would change
    python3 regression/promote.py --repo OpenMower --apply       # Promote improvements
    python3 regression/promote.py --all                          # Check all repos
    python3 regression/promote.py --all --apply                  # Promote all improvements
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    discover_projects, list_repos,
    load_project_metadata,
    add_repo_filter_args, resolve_repos,
)
from run_checks import check_assertions
from snapshot import create_snapshot
from compare import compare_project
from seed import generate_for_repo


def check_baseline_changes(repo_name):
    """Check baseline diffs for a repo. Returns summary of changes."""
    projects = discover_projects(repo_name)
    if not projects:
        return []

    changes = []
    for proj in projects:
        proj_name = proj["name"]
        proj_path = proj["path"]

        meta = load_project_metadata(repo_name, proj_name)
        if not meta:
            # No baseline yet — this is new
            # Check if outputs exist
            has_outputs = False
            for atype in ANALYZER_TYPES:
                type_dir = OUTPUTS_DIR / atype / repo_name
                if type_dir.exists() and list(type_dir.glob("*.json")):
                    has_outputs = True
                    break
            if has_outputs:
                changes.append({
                    "project": proj_name,
                    "status": "new",
                    "detail": "no baseline yet, outputs exist",
                })
            continue

        stored_path = meta.get("project_path", ".")

        for atype in ANALYZER_TYPES:
            results = compare_project(repo_name, proj_name, stored_path, atype)
            if "error" in results:
                continue
            if results["files_with_changes"] > 0 or results["files_only_in_current"]:
                changes.append({
                    "project": proj_name,
                    "type": atype,
                    "status": "changed",
                    "compared": results["files_compared"],
                    "changed": results["files_with_changes"],
                    "new_files": len(results["files_only_in_current"]),
                })

    return changes


def promote_repo(repo_name, dry_run=True):
    """Check and optionally promote improvements for a repo."""
    print(f"\n{'=' * 60}")
    print(f"  {repo_name}")
    print(f"{'=' * 60}")

    # Check if outputs exist
    has_outputs = False
    for atype in ANALYZER_TYPES:
        type_dir = OUTPUTS_DIR / atype / repo_name
        if type_dir.exists() and list(type_dir.glob("*.json")):
            has_outputs = True
            break

    if not has_outputs:
        print("  No outputs found. Run analyzers first.")
        return False

    # Check assertion results
    assertion_results = check_assertions(DATA_DIR, repo_name=repo_name)
    total = assertion_results["total"]
    passed = assertion_results["passed"]
    if total > 0:
        rate = passed / total * 100
        print(f"\n  Assertions: {passed}/{total} pass ({rate:.0f}%)")
    else:
        print(f"\n  Assertions: none defined")

    # Check baseline changes
    changes = check_baseline_changes(repo_name)
    if not changes:
        print("  Baselines: no changes")
        return False

    has_improvements = False
    for c in changes:
        if c["status"] == "new":
            print(f"  NEW: {c['project']} — {c['detail']}")
            has_improvements = True
        elif c["status"] == "changed":
            print(f"  CHANGED: {c['project']}/{c['type']} — "
                  f"{c['changed']}/{c['compared']} files changed"
                  + (f", {c['new_files']} new" if c.get('new_files') else ""))
            has_improvements = True

    if not has_improvements:
        return False

    if dry_run:
        print(f"\n  Run with --apply to promote these changes to reference/")
        return True

    # Apply: re-snapshot baselines
    print(f"\n  Promoting baselines...")
    create_snapshot(repo_name)

    # Regenerate seed assertions
    print(f"  Regenerating seed assertions...")
    files, assertions, skipped = generate_for_repo(
        repo_name, "schematic", 0.10, 10, "", False)
    if files:
        print(f"    {assertions} assertions across {files} files")

    print(f"  Done.")
    return True


def preview_summary(repos):
    """Show a compact preview of all changes across repos."""
    total_new = 0
    total_changed = 0
    total_new_files = 0
    total_assertions = 0
    repos_with_changes = 0
    type_changes = {}

    for repo in repos:
        changes = check_baseline_changes(repo)
        if not changes:
            continue
        repos_with_changes += 1
        for c in changes:
            if c["status"] == "new":
                total_new += 1
            elif c["status"] == "changed":
                total_changed += c.get("changed", 0)
                total_new_files += c.get("new_files", 0)
                atype = c.get("type", "?")
                type_changes[atype] = type_changes.get(atype, 0) + c["changed"]

        result = check_assertions(DATA_DIR, repo_name=repo)
        total_assertions += result["total"]

    print(f"\n{'=' * 60}")
    print(f"PROMOTION PREVIEW")
    print(f"{'=' * 60}")
    print(f"Repos with changes:     {repos_with_changes} / {len(repos)}")
    print(f"New projects:           {total_new}")
    print(f"Changed baseline files: {total_changed}")
    print(f"New output files:       {total_new_files}")
    print(f"Current assertions:     {total_assertions}")
    if type_changes:
        print(f"\nChanges by type:")
        for atype, count in sorted(type_changes.items(), key=lambda x: -x[1]):
            print(f"  {atype:<20s} {count} files")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description="Promote improved results to reference")
    add_repo_filter_args(parser)
    parser.add_argument("--all", action="store_true", help="Check/promote all repos")
    parser.add_argument("--apply", action="store_true",
                        help="Apply promotions (default: dry run)")
    parser.add_argument("--preview", action="store_true",
                        help="Show compact summary of all changes")
    args = parser.parse_args()

    repos = resolve_repos(args)
    if repos is None:
        if args.all:
            repos = list_repos()
        else:
            parser.print_help()
            sys.exit(1)

    if args.preview:
        preview_summary(repos)
        return

    if not args.apply:
        print("DRY RUN — showing what would change. Use --apply to promote.\n")

    promoted = 0
    for repo in repos:
        if promote_repo(repo, dry_run=not args.apply):
            promoted += 1

    print(f"\n{'=' * 60}")
    if args.apply:
        print(f"{promoted} repo(s) promoted to reference/")
    else:
        print(f"{promoted} repo(s) have changes to promote")


if __name__ == "__main__":
    main()
