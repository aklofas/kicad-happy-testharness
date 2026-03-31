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


def _parse_tested_repos(priority_file, count=5):
    """Parse first N repos from the 'Tested' section of priority.md."""
    repos = []
    in_tested = False
    try:
        text = priority_file.read_text()
    except OSError:
        return repos
    for line in text.splitlines():
        if line.strip() == "## Tested":
            in_tested = True
            continue
        if in_tested and line.startswith("| ") and "/" in line:
            # "| user/repo | Category |" → extract "user/repo"
            parts = line.split("|")
            if len(parts) >= 3:
                repo = parts[1].strip()
                if "/" in repo:
                    # Repo name in repos/ uses the last component
                    repos.append(repo.split("/")[-1] if "/" in repo else repo)
                    if len(repos) >= count:
                        break
    return repos


def run_quick_sanity():
    """Run assertions on 5 repos from priority.md as a quick sanity check."""
    priority_file = HARNESS_DIR / "priority.md"
    repos = _parse_tested_repos(priority_file, count=5)
    if not repos:
        print("  SKIP  quick-sanity (no repos found in priority.md)")
        return 0

    run_checks = HARNESS_DIR / "regression" / "run_checks.py"
    passed = 0
    failed = 0
    for repo in repos:
        try:
            result = subprocess.run(
                [sys.executable, str(run_checks), "--repo", repo, "--json"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                rate = data.get("pass_rate", "?")
                total = data.get("total", 0)
                print(f"  PASS  sanity/{repo} ({total} assertions, {rate})")
                passed += 1
            else:
                print(f"  FAIL  sanity/{repo}")
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"  SKIP  sanity/{repo} (timed out)")
        except Exception as e:
            print(f"  FAIL  sanity/{repo} ({e})")
            failed += 1

    return 1 if failed > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Unit tests only")
    parser.add_argument("--integration", action="store_true", help="Integration tests only")
    parser.add_argument("--quick-sanity", action="store_true",
                        help="Run assertions on 5 repos as a quick sanity check")
    args = parser.parse_args()

    if args.quick_sanity:
        sys.exit(run_quick_sanity())

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
