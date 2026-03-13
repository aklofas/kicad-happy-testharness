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
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (
    OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    discover_projects, data_dir, list_repos,
    project_prefix,
)
from checks import load_assertions, evaluate_assertion
from snapshot import create_snapshot
from compare import compare_project
from seed import generate_for_repo


def check_assertions_for_repo(repo_name):
    """Run assertions and return pass/fail/error counts."""
    assertion_sets = load_assertions(
        DATA_DIR, repo_name=repo_name,
    )
    if not assertion_sets:
        return {"total": 0, "passed": 0, "failed": 0, "errors": 0}

    total = passed = failed = errors = 0
    for aset in assertion_sets:
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        repo = aset.get("_repo", "")
        project_path = aset.get("_project_path")

        # Find output file
        type_dir = OUTPUTS_DIR / atype / repo
        if not type_dir.exists():
            errors += len(aset.get("assertions", []))
            total += len(aset.get("assertions", []))
            continue

        prefix = project_prefix(project_path)

        safe_name = prefix + file_pattern
        output_file = type_dir / (safe_name + ".json")

        if not output_file.exists():
            errors += len(aset.get("assertions", []))
            total += len(aset.get("assertions", []))
            continue

        try:
            data = json.loads(output_file.read_text())
        except Exception:
            errors += len(aset.get("assertions", []))
            total += len(aset.get("assertions", []))
            continue

        for assertion in aset.get("assertions", []):
            total += 1
            result = evaluate_assertion(assertion, data)
            if result["passed"]:
                passed += 1
            else:
                failed += 1

    return {"total": total, "passed": passed, "failed": failed, "errors": errors}


def check_baseline_changes(repo_name):
    """Check baseline diffs for a repo. Returns summary of changes."""
    projects = discover_projects(repo_name)
    if not projects:
        return []

    changes = []
    for proj in projects:
        proj_name = proj["name"]
        proj_path = proj["path"]

        meta_file = data_dir(repo_name, proj_name, "baselines") / "metadata.json"
        if not meta_file.exists():
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

        meta = json.loads(meta_file.read_text())
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
    assertion_results = check_assertions_for_repo(repo_name)
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


def main():
    parser = argparse.ArgumentParser(
        description="Promote improved results to reference")
    parser.add_argument("--repo", help="Check/promote one repo")
    parser.add_argument("--all", action="store_true", help="Check/promote all repos")
    parser.add_argument("--apply", action="store_true",
                        help="Apply promotions (default: dry run)")
    args = parser.parse_args()

    if args.repo:
        repos = [args.repo]
    elif args.all:
        repos = list_repos()
    else:
        parser.print_help()
        sys.exit(1)

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
