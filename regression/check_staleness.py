#!/usr/bin/env python3
"""Detect stale assertions by comparing timestamps against outputs.

An assertion file is "stale" if the output it checks is newer than the
assertion — meaning the output has been regenerated but assertions haven't
been re-seeded. Also detects outputs with no assertions at all.

Usage:
    python3 regression/check_staleness.py
    python3 regression/check_staleness.py --repo OpenMower
    python3 regression/check_staleness.py --type schematic
    python3 regression/check_staleness.py --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import load_assertions
from run_checks import find_output_file
from utils import OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES


def check_staleness(data_dir, repo_name=None, analyzer_type=None):
    """Compare assertion and output timestamps.

    Returns:
        (stale, missing, total_sets) where stale and missing are lists of dicts.
    """
    assertion_sets = load_assertions(
        data_dir, repo_name=repo_name, analyzer_type=analyzer_type,
    )

    stale = []
    missing_output = []
    total_sets = 0

    for aset in assertion_sets:
        total_sets += 1
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        repo = aset.get("_repo", "")
        project_path = aset.get("_project_path")
        assertion_file = Path(aset.get("_source_file", ""))
        n_assertions = len(aset.get("assertions", []))

        output_file = find_output_file(file_pattern, repo, project_path, atype)

        if not output_file:
            missing_output.append({
                "repo": repo,
                "type": atype,
                "file_pattern": file_pattern,
                "assertion_file": str(assertion_file),
                "assertions": n_assertions,
            })
            continue

        if assertion_file.exists():
            assertion_mtime = assertion_file.stat().st_mtime
            output_mtime = output_file.stat().st_mtime
            if output_mtime > assertion_mtime:
                stale.append({
                    "repo": repo,
                    "type": atype,
                    "file_pattern": file_pattern,
                    "assertion_file": str(assertion_file),
                    "output_file": str(output_file),
                    "assertions": n_assertions,
                    "output_age_hours": round(
                        (output_mtime - assertion_mtime) / 3600, 1
                    ),
                })

    return stale, missing_output, total_sets


def find_uncovered_outputs(data_dir, repo_name=None, analyzer_type=None):
    """Find output files that have no assertions at all."""
    # Build set of (repo, type, file_pattern) that have assertions
    assertion_sets = load_assertions(
        data_dir, repo_name=repo_name, analyzer_type=analyzer_type,
    )
    covered = set()
    for aset in assertion_sets:
        repo = aset.get("_repo", "")
        atype = aset.get("analyzer_type", "schematic")
        fp = aset.get("file_pattern", "")
        covered.add((repo, atype, fp))

    # Scan outputs
    uncovered = []
    types = [analyzer_type] if analyzer_type else ANALYZER_TYPES
    for atype in types:
        type_dir = OUTPUTS_DIR / atype
        if not type_dir.exists():
            continue
        for repo_dir in sorted(type_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            if repo_name and repo_dir.name != repo_name:
                continue
            for json_file in sorted(repo_dir.glob("*.json")):
                if json_file.name.startswith("_"):
                    continue
                # Check if any assertion covers this output
                repo = repo_dir.name
                stem = json_file.stem  # e.g. "foo.kicad_sch"
                is_covered = any(
                    stem.endswith(fp) or stem == fp
                    for r, t, fp in covered
                    if r == repo and t == atype
                )
                if not is_covered:
                    uncovered.append({
                        "repo": repo,
                        "type": atype,
                        "output_file": str(json_file),
                    })

    return uncovered


def main():
    parser = argparse.ArgumentParser(
        description="Detect stale or missing assertions"
    )
    parser.add_argument("--repo", help="Only check this repo")
    parser.add_argument("--type", choices=ANALYZER_TYPES,
                        help="Only check one analyzer type")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    stale, missing, total_sets = check_staleness(
        DATA_DIR, repo_name=args.repo, analyzer_type=args.type,
    )
    uncovered = find_uncovered_outputs(
        DATA_DIR, repo_name=args.repo, analyzer_type=args.type,
    )

    if args.json:
        json.dump({
            "total_assertion_sets": total_sets,
            "stale": stale,
            "missing_output": missing,
            "uncovered_outputs": len(uncovered),
        }, sys.stdout, indent=2)
        print()
        return

    # Summary
    print(f"Assertion sets checked: {total_sets}")
    print()

    if stale:
        # Group by type
        by_type = {}
        for s in stale:
            by_type.setdefault(s["type"], []).append(s)
        print(f"STALE: {len(stale)} assertion files older than their outputs")
        for atype, items in sorted(by_type.items()):
            print(f"  {atype}: {len(items)} repos")
            for item in items[:5]:
                print(f"    {item['repo']}/{item['file_pattern']} "
                      f"({item['assertions']} assertions, "
                      f"output {item['output_age_hours']}h newer)")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")
    else:
        print("STALE: 0 (all assertions up to date)")

    print()

    if missing:
        print(f"MISSING OUTPUT: {len(missing)} assertion sets have no matching output")
        for item in missing[:5]:
            print(f"  {item['repo']}/{item['file_pattern']} ({item['type']})")
        if len(missing) > 5:
            print(f"  ... and {len(missing) - 5} more")
    else:
        print("MISSING OUTPUT: 0")

    print()

    if uncovered:
        by_type = {}
        for u in uncovered:
            by_type.setdefault(u["type"], []).append(u)
        print(f"UNCOVERED: {len(uncovered)} output files have no assertions")
        for atype, items in sorted(by_type.items()):
            print(f"  {atype}: {len(items)} files")
    else:
        print("UNCOVERED: 0 (all outputs have assertions)")


if __name__ == "__main__":
    main()
