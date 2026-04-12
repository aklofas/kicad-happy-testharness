#!/usr/bin/env python3
"""Run all assertions against current analyzer outputs.

Assertions live in reference/{repo}/{project}/assertions/{type}/.
Outputs live in results/outputs/{type}/{repo}/.

Usage:
    python3 regression/run_checks.py
    python3 regression/run_checks.py --repo OpenMower
    python3 regression/run_checks.py --cross-section smoke
    python3 regression/run_checks.py --type schematic
    python3 regression/run_checks.py --jobs 16
    python3 regression/run_checks.py --json
"""

import argparse
import fnmatch
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import evaluate_assertion, load_assertions
from utils import (OUTPUTS_DIR, DATA_DIR, project_prefix, ANALYZER_TYPES,
                   DEFAULT_JOBS, add_repo_filter_args, resolve_repos)


def check_assertions(data_dir, repo_name=None, analyzer_type=None):
    """Run assertions and return {total, passed, failed, errors} counts."""
    assertion_sets = load_assertions(
        data_dir, repo_name=repo_name, analyzer_type=analyzer_type,
    )
    total = passed = failed = errors = 0
    for aset in assertion_sets:
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        repo = aset.get("_repo", "")
        project_path = aset.get("_project_path")
        assertions = aset.get("assertions", [])

        output_file = find_output_file(file_pattern, repo, project_path, atype)

        if not output_file:
            n = len(assertions)
            errors += n
            total += n
            continue

        try:
            data = json.loads(output_file.read_text(encoding="utf-8"))
        except Exception:
            n = len(assertions)
            errors += n
            total += n
            continue

        for assertion in assertions:
            total += 1
            result = evaluate_assertion(assertion, data)
            if result["passed"]:
                passed += 1
            else:
                failed += 1

    return {"total": total, "passed": passed, "failed": failed, "errors": errors}


def find_output_file(file_pattern, repo_name, project_path, analyzer_type):
    """Find the output JSON file for an assertion.

    Reconstructs the output safe_name from project_path + file_pattern.
    For root-level projects (project_path is "." or None), no prefix is added.
    """
    type_dir = OUTPUTS_DIR / analyzer_type / repo_name
    if not type_dir.exists():
        return None

    # Build prefix from project_path (not project_name)
    prefix = project_prefix(project_path)

    safe_name = prefix + file_pattern

    # Try exact match first
    candidate = type_dir / (safe_name + ".json")
    if candidate.exists():
        return candidate

    # Try with .json already in pattern
    candidate = type_dir / safe_name
    if candidate.exists():
        return candidate

    # Fallback: glob match
    for json_file in type_dir.glob("*.json"):
        if fnmatch.fnmatch(json_file.name, safe_name + ".json"):
            return json_file
        if fnmatch.fnmatch(json_file.stem, safe_name):
            return json_file

    return None


def _check_one_set(aset):
    """Process one assertion set. Worker function for parallel execution.

    Returns dict with counts and failure details.
    """
    atype = aset.get("analyzer_type", "schematic")
    file_pattern = aset.get("file_pattern", "")
    repo_name = aset.get("_repo", "")
    project_name = aset.get("_project", "")
    project_path = aset.get("_project_path")

    result = {
        "total": 0, "passed": 0, "failed": 0, "errors": 0,
        "aspirational_total": 0, "aspirational_passed": 0,
        "aspirational_failed": 0,
        "failures": [], "results": [],
    }

    output_file = find_output_file(file_pattern, repo_name, project_path, atype)

    if not output_file:
        for assertion in aset.get("assertions", []):
            if assertion.get("aspirational"):
                result["aspirational_total"] += 1
                result["aspirational_failed"] += 1
            else:
                result["total"] += 1
                result["errors"] += 1
            result["results"].append({
                "file": file_pattern, "repo": repo_name,
                "project": project_name,
                "id": assertion.get("id", "?"),
                "description": assertion.get("description", ""),
                "passed": False, "error": "output file not found",
                "aspirational": assertion.get("aspirational", False),
            })
        return result

    try:
        data = json.loads(output_file.read_text(encoding="utf-8"))
    except Exception as e:
        for assertion in aset.get("assertions", []):
            if assertion.get("aspirational"):
                result["aspirational_total"] += 1
                result["aspirational_failed"] += 1
            else:
                result["total"] += 1
                result["errors"] += 1
            result["results"].append({
                "file": file_pattern,
                "id": assertion.get("id", "?"),
                "passed": False, "error": f"JSON parse error: {e}",
                "aspirational": assertion.get("aspirational", False),
            })
        return result

    for assertion in aset.get("assertions", []):
        is_aspirational = assertion.get("aspirational", False)
        eval_result = evaluate_assertion(assertion, data)
        eval_result["file"] = file_pattern
        eval_result["repo"] = repo_name
        eval_result["project"] = project_name
        eval_result["aspirational"] = is_aspirational

        if is_aspirational:
            result["aspirational_total"] += 1
            if eval_result["passed"]:
                result["aspirational_passed"] += 1
            else:
                result["aspirational_failed"] += 1
        else:
            result["total"] += 1
            if eval_result["passed"]:
                result["passed"] += 1
            else:
                result["failed"] += 1
                result["failures"].append(eval_result)

        result["results"].append(eval_result)

    return result


def main():
    parser = argparse.ArgumentParser(description="Check assertions against outputs")
    add_repo_filter_args(parser)
    parser.add_argument("--type", choices=ANALYZER_TYPES,
                        help="Only check one analyzer type")
    parser.add_argument("--file", help="Only check assertions matching this file pattern")
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel workers (default: {DEFAULT_JOBS})")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--allow-errors", action="store_true",
                        help="Exit 0 when errors > 0 but failures == 0 (shallow-clone mode)")
    args = parser.parse_args()

    # Resolve repo filtering
    repo_list = resolve_repos(args)
    repo_name = repo_list[0] if repo_list and len(repo_list) == 1 else None

    # Load assertion sets — if cross-section, load per-repo and merge
    if repo_list and len(repo_list) > 1:
        assertion_sets = []
        for rn in repo_list:
            assertion_sets.extend(load_assertions(
                DATA_DIR, analyzer_type=args.type,
                file_pattern=args.file, repo_name=rn,
            ))
    else:
        assertion_sets = load_assertions(
            DATA_DIR, analyzer_type=args.type,
            file_pattern=args.file, repo_name=repo_name,
        )

    if not assertion_sets:
        print("No assertions found in data/")
        print("Create assertion files to enable regression testing.")
        sys.exit(0)

    total = passed = failed = errors = 0
    aspirational_total = aspirational_passed = aspirational_failed = 0
    failures = []
    all_results = []

    jobs = args.jobs

    if jobs > 1 and len(assertion_sets) > 500:
        # Parallel execution
        with ProcessPoolExecutor(max_workers=min(jobs, len(assertion_sets))) as pool:
            futures = {pool.submit(_check_one_set, aset): i
                       for i, aset in enumerate(assertion_sets)}
            for future in as_completed(futures):
                r = future.result()
                total += r["total"]
                passed += r["passed"]
                failed += r["failed"]
                errors += r["errors"]
                aspirational_total += r["aspirational_total"]
                aspirational_passed += r["aspirational_passed"]
                aspirational_failed += r["aspirational_failed"]
                failures.extend(r["failures"])
                all_results.extend(r["results"])
    else:
        # Sequential execution
        for aset in assertion_sets:
            r = _check_one_set(aset)
            total += r["total"]
            passed += r["passed"]
            failed += r["failed"]
            errors += r["errors"]
            aspirational_total += r["aspirational_total"]
            aspirational_passed += r["aspirational_passed"]
            aspirational_failed += r["aspirational_failed"]
            failures.extend(r["failures"])
            all_results.extend(r["results"])

    if args.json:
        out = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
            "results": all_results,
        }
        if aspirational_total > 0:
            out["aspirational"] = {
                "total": aspirational_total,
                "passed": aspirational_passed,
                "failed": aspirational_failed,
            }
        print(json.dumps(out, indent=2))
    else:
        print("=" * 70)
        print("ASSERTION CHECK RESULTS")
        print("=" * 70)
        print(f"\nTotal:  {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        if total > 0:
            print(f"Rate:   {passed/total*100:.1f}%")

        if aspirational_total > 0:
            print(f"\nAspirational: {aspirational_total} total, "
                  f"{aspirational_passed} passing, {aspirational_failed} failing")

        if failures:
            print(f"\n--- Failures ---")
            for f in failures:
                proj = f.get("project", "")
                print(f"  FAIL {proj}/{f.get('file', '?')}: {f['description']}")
                print(f"       Expected: {f.get('expected', '?')}, Actual: {f.get('actual', '?')}")
                if f.get("error"):
                    print(f"       Error: {f['error']}")

    if failed > 0:
        sys.exit(1)
    elif errors > 0 and not args.allow_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
