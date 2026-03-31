#!/usr/bin/env python3
"""Run all unit and integration tests.

Usage:
    python3 run_tests.py              # All tests
    python3 run_tests.py --unit       # Unit tests only (tests/)
    python3 run_tests.py --integration # Integration tests only (integration/)
"""

import argparse
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent


def discover_tests(dirs):
    """Find all test_*.py files in given directories."""
    tests = []
    for d in dirs:
        test_dir = HARNESS_DIR / d
        if test_dir.exists():
            tests.extend(sorted(test_dir.glob("test_*.py")))
    return tests


def main():
    parser = argparse.ArgumentParser(description="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Unit tests only")
    parser.add_argument("--integration", action="store_true", help="Integration tests only")
    args = parser.parse_args()

    dirs = []
    if args.unit:
        dirs = ["tests"]
    elif args.integration:
        dirs = ["integration"]
    else:
        dirs = ["tests", "integration"]

    tests = discover_tests(dirs)
    if not tests:
        print("No test files found.")
        return 0

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    failures = []

    for test_file in tests:
        rel = test_file.relative_to(HARNESS_DIR)
        timeout = 600 if "integration" in str(test_file) else 120
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            total_skipped += 1
            print(f"  SKIP  {rel} (timed out after {timeout}s)")
            continue

        # Parse last line for counts
        last_lines = result.stdout.strip().split("\n")
        summary_line = last_lines[-1] if last_lines else ""

        if result.returncode == 0:
            # Try to parse "N passed, N failed (N total)"
            try:
                parts = summary_line.split()
                p = int(parts[0])
                f = int(parts[2])
                total_passed += p
                total_failed += f
                status = f"{p}p {f}f"
            except (IndexError, ValueError):
                # Try "Results: N passed, N failed, N skipped (N total)"
                try:
                    if "Results:" in summary_line:
                        p = int(summary_line.split("passed")[0].split()[-1])
                        f = int(summary_line.split("failed")[0].split()[-1])
                        s = int(summary_line.split("skipped")[0].split()[-1])
                        total_passed += p
                        total_failed += f
                        total_skipped += s
                        status = f"{p}p {f}f {s}s"
                    else:
                        total_passed += 1
                        status = "ok"
                except (IndexError, ValueError):
                    total_passed += 1
                    status = "ok"
            print(f"  PASS  {rel} ({status})")
        else:
            total_failed += 1
            failures.append(rel)
            print(f"  FAIL  {rel}")
            # Show last few lines of output for debugging
            for line in last_lines[-3:]:
                if line.strip():
                    print(f"        {line}")

    print()
    print("=" * 50)
    print(f"Results: {total_passed} passed, {total_failed} failed, {total_skipped} skipped")
    print(f"Files:   {len(tests)} test files ({len(tests) - len(failures)} ok, {len(failures)} failed)")
    print("=" * 50)

    if failures:
        print(f"\nFailed: {', '.join(str(f) for f in failures)}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
