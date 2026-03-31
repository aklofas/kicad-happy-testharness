#!/usr/bin/env python3
"""Run all assertions against current analyzer outputs.

Assertions live in reference/{repo}/{project}/assertions/{type}/.
Outputs live in results/outputs/{type}/{repo}/.

Usage:
    python3 regression/run_checks.py
    python3 regression/run_checks.py --repo OpenMower
    python3 regression/run_checks.py --type schematic
    python3 regression/run_checks.py --json
"""

import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import evaluate_assertion, load_assertions
from utils import OUTPUTS_DIR, DATA_DIR, project_prefix


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
            data = json.loads(output_file.read_text())
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


def main():
    parser = argparse.ArgumentParser(description="Check assertions against outputs")
    parser.add_argument("--repo", help="Only check assertions for this repo")
    parser.add_argument("--type", choices=["schematic", "pcb", "gerber", "spice"],
                        help="Only check one analyzer type")
    parser.add_argument("--file", help="Only check assertions matching this file pattern")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    assertion_sets = load_assertions(
        DATA_DIR,
        analyzer_type=args.type,
        file_pattern=args.file,
        repo_name=args.repo,
    )

    if not assertion_sets:
        print("No assertions found in data/")
        print("Create assertion files to enable regression testing.")
        sys.exit(0)

    total = passed = failed = errors = 0
    aspirational_total = aspirational_passed = aspirational_failed = 0
    failures = []
    all_results = []

    for aset in assertion_sets:
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        repo_name = aset.get("_repo", "")
        project_name = aset.get("_project", "")
        project_path = aset.get("_project_path")

        output_file = find_output_file(file_pattern, repo_name, project_path, atype)

        if not output_file:
            for assertion in aset.get("assertions", []):
                if assertion.get("aspirational"):
                    aspirational_total += 1
                    aspirational_failed += 1
                else:
                    total += 1
                    errors += 1
                all_results.append({
                    "file": file_pattern,
                    "repo": repo_name,
                    "project": project_name,
                    "id": assertion.get("id", "?"),
                    "description": assertion.get("description", ""),
                    "passed": False,
                    "error": "output file not found",
                    "aspirational": assertion.get("aspirational", False),
                })
            continue

        try:
            data = json.loads(output_file.read_text())
        except Exception as e:
            for assertion in aset.get("assertions", []):
                if assertion.get("aspirational"):
                    aspirational_total += 1
                    aspirational_failed += 1
                else:
                    total += 1
                    errors += 1
                all_results.append({
                    "file": file_pattern,
                    "id": assertion.get("id", "?"),
                    "passed": False,
                    "error": f"JSON parse error: {e}",
                    "aspirational": assertion.get("aspirational", False),
                })
            continue

        for assertion in aset.get("assertions", []):
            is_aspirational = assertion.get("aspirational", False)
            result = evaluate_assertion(assertion, data)
            result["file"] = file_pattern
            result["repo"] = repo_name
            result["project"] = project_name
            result["aspirational"] = is_aspirational

            if is_aspirational:
                aspirational_total += 1
                if result["passed"]:
                    aspirational_passed += 1
                else:
                    aspirational_failed += 1
            else:
                total += 1
                if result["passed"]:
                    passed += 1
                else:
                    failed += 1
                    failures.append(result)

            all_results.append(result)

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
        return

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

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
