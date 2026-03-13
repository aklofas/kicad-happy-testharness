#!/usr/bin/env python3
"""Run all assertions against current analyzer outputs.

Validates that analyzer outputs match expected facts encoded in
data/assertions/. This is the automated regression checker.

Usage:
    python3 review/check_assertions.py
    python3 review/check_assertions.py --type schematic
    python3 review/check_assertions.py --file "hackrf*"
    python3 review/check_assertions.py --json
"""

import argparse
import fnmatch
import json
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR / "review"))
from assertions import evaluate_assertion, load_assertions

OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
ASSERTIONS_DIR = HARNESS_DIR / "data" / "assertions"


def find_output_file(file_pattern, outputs_dir):
    """Find the output JSON file matching an assertion's file_pattern."""
    for json_file in outputs_dir.glob("*.json"):
        if fnmatch.fnmatch(json_file.name, file_pattern + ".json"):
            return json_file
        # Also try without .json suffix in pattern
        if fnmatch.fnmatch(json_file.stem, file_pattern):
            return json_file
    return None


def main():
    parser = argparse.ArgumentParser(description="Check assertions against analyzer outputs")
    parser.add_argument("--type", choices=["schematic", "pcb", "gerber"],
                        help="Only check assertions for this analyzer type")
    parser.add_argument("--file", help="Only check assertions matching this file pattern")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    assertion_sets = load_assertions(ASSERTIONS_DIR, analyzer_type=args.type, file_pattern=args.file)

    if not assertion_sets:
        print("No assertions found in data/assertions/")
        print("Create assertion files to enable regression testing.")
        sys.exit(0)

    total = passed = failed = errors = 0
    failures = []
    all_results = []

    for aset in assertion_sets:
        atype = aset.get("analyzer_type", "schematic")
        file_pattern = aset.get("file_pattern", "")
        type_dir = OUTPUTS_DIR / atype

        output_file = find_output_file(file_pattern, type_dir) if type_dir.exists() else None

        if not output_file:
            for assertion in aset.get("assertions", []):
                total += 1
                errors += 1
                all_results.append({
                    "file": file_pattern,
                    "id": assertion.get("id", "?"),
                    "description": assertion.get("description", ""),
                    "passed": False,
                    "error": "output file not found",
                })
            continue

        try:
            data = json.loads(output_file.read_text())
        except Exception as e:
            for assertion in aset.get("assertions", []):
                total += 1
                errors += 1
                all_results.append({
                    "file": file_pattern,
                    "id": assertion.get("id", "?"),
                    "passed": False,
                    "error": f"JSON parse error: {e}",
                })
            continue

        for assertion in aset.get("assertions", []):
            total += 1
            result = evaluate_assertion(assertion, data)
            result["file"] = file_pattern

            if result["passed"]:
                passed += 1
            else:
                failed += 1
                failures.append(result)

            all_results.append(result)

    if args.json:
        print(json.dumps({
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "N/A",
            "results": all_results,
        }, indent=2))
        return

    # Human-readable report
    print("=" * 70)
    print("ASSERTION CHECK RESULTS")
    print("=" * 70)
    print(f"\nTotal:  {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    if total > 0:
        print(f"Rate:   {passed/total*100:.1f}%")

    if failures:
        print(f"\n--- Failures ---")
        for f in failures:
            print(f"  FAIL {f.get('file', '?')}: {f['description']}")
            print(f"       Expected: {f.get('expected', '?')}, Actual: {f.get('actual', '?')}")
            if f.get("error"):
                print(f"       Error: {f['error']}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
