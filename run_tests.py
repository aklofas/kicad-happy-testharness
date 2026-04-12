#!/usr/bin/env python3
"""Run all unit and integration tests.

Usage:
    python3 run_tests.py                  # Unit tests (default)
    python3 run_tests.py --unit           # Unit tests only (tests/)
    python3 run_tests.py --integration    # Online integration tests (integration/)
    python3 run_tests.py --tier unit      # Only tier=unit tests
    python3 run_tests.py --tier online    # Only tier=online tests
    python3 run_tests.py --tier all       # All tiers
    python3 run_tests.py --smoke          # Curated PR-gate subset (<1s, no corpus)
    python3 run_tests.py --list-smoke     # Print smoke subset, one per line
    python3 run_tests.py --json           # JSON output
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import TEST_TIMEOUT, INTEGRATION_TEST_TIMEOUT


# Curated smoke subset for CI PR gates. Selection criteria:
#   1. Zero corpus dependency — runs cleanly in a fresh checkout with no
#      `repos/`, `results/`, or `reference/` data present.
#   2. Has a stdlib `if __name__ == "__main__"` runner block (so the file
#      actually executes its tests when invoked as a script). Files
#      missing this block silently exit 0 — see TH-014.
#   3. Covers diverse subsystems: core utils, schema, diff engine,
#      assertion engine, validators, naming, parser verifier, datasheets.
#   4. Total runtime < 1 second on a developer laptop (measured 0.34s
#      on 2026-04-10 against the 242-test set below).
#
# When adding new test files, decide whether they meet (1)+(2)+(4) and
# add them here if they do. Don't include tests that read from corpus
# directories — those belong in the full unit suite.
SMOKE_TESTS = [
    "tests/test_invariants.py",      # 12 tests — structural invariants
    "tests/test_utils.py",           # 22 tests — shared utilities
    "tests/test_safe_names.py",      # 22 tests — name flattening (TH-013)
    "tests/test_diff_analysis.py",   # 25 tests — diff engine
    "tests/test_differ.py",          # 13 tests — diff library
    "tests/test_checks.py",          # 43 tests — assertion engine
    "tests/test_run_checks.py",      # 5 tests — run_checks exit code (TH-015)
    "tests/test_schema.py",          # 24 tests — schema validation
    "tests/test_validate_outputs.py",  # 27 tests — output structural checks
    "tests/test_verify_parser.py",   # 27 tests — P1 parser verifier
    "tests/test_datasheet_verify.py",  # 27 tests — datasheet extraction validation
    "tests/test_datasheet_db_storage.py",   # 30 tests — datasheet store primitives (sub-project A)
    "tests/test_datasheet_db_manifest.py",  # 34 tests — datasheet manifest layer (sub-project A)
]


def discover_tests(dirs, tier_filter=None):
    """Find all test_*.py files in given directories, optionally filtered by TIER.

    Each test file can declare TIER = "unit"|"online" at module level.
    If tier_filter is set, only files matching that tier are returned.
    Files without a TIER declaration default to "unit" for tests/ and "online"
    for integration/.
    """
    tests = []
    for d in dirs:
        test_dir = HARNESS_DIR / d
        if not test_dir.exists():
            continue
        default_tier = "online" if d == "integration" else "unit"
        for f in sorted(test_dir.glob("test_*.py")):
            if tier_filter and tier_filter != "all":
                # Read TIER from file
                tier = default_tier
                try:
                    for line in f.read_text(encoding="utf-8").splitlines()[:30]:
                        if line.startswith("TIER"):
                            tier = line.split("=")[1].strip().strip("'\"")
                            break
                except OSError:
                    pass
                if tier != tier_filter:
                    continue
            tests.append(f)
    return tests


def _load_smoke_repos(count=5):
    """Load first N repos from smoke_pack.md for quick sanity checks."""
    smoke_file = HARNESS_DIR / "reference" / "smoke_pack.md"
    repos = []
    try:
        for line in smoke_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            repos.append(line)
            if len(repos) >= count:
                break
    except OSError:
        pass
    return repos


def run_quick_sanity():
    """Run assertions on 5 repos from smoke_pack.md as a quick sanity check."""
    repos = _load_smoke_repos(count=5)
    if not repos:
        print("  SKIP  quick-sanity (no repos found in smoke_pack.md)")
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
    parser.add_argument("--unit", action="store_true", help="Unit tests only (alias for --tier unit)")
    parser.add_argument("--integration", action="store_true",
                        help="Integration tests only (alias for --tier online)")
    parser.add_argument("--tier", choices=["unit", "online", "all"],
                        help="Run tests matching this tier (unit, online, all)")
    parser.add_argument("--smoke", action="store_true",
                        help="Curated PR-gate subset — fast, no corpus deps. See SMOKE_TESTS.")
    parser.add_argument("--list-smoke", action="store_true",
                        help="Print smoke subset filenames, one per line, then exit")
    parser.add_argument("--quick-sanity", action="store_true",
                        help="Run assertions on 5 repos as a quick sanity check")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.list_smoke:
        for path in SMOKE_TESTS:
            print(path)
        return 0

    if args.quick_sanity:
        sys.exit(run_quick_sanity())

    if args.smoke:
        # Skip discovery — use the curated list. Verify each file exists
        # so a typo or rename in SMOKE_TESTS surfaces immediately rather
        # than silently shrinking the gate.
        tests = []
        missing = []
        for rel in SMOKE_TESTS:
            path = HARNESS_DIR / rel
            if path.exists():
                tests.append(path)
            else:
                missing.append(rel)
        if missing:
            print(f"ERROR: smoke set references missing files: {missing}")
            return 2
    else:
        # Resolve tier filter from flags
        tier_filter = args.tier
        if args.unit:
            tier_filter = "unit"
        elif args.integration:
            tier_filter = "online"

        # Determine which directories to scan
        dirs = ["tests", "integration"]
        if tier_filter == "unit":
            dirs = ["tests"]
        elif tier_filter == "online":
            dirs = ["integration"]

        tests = discover_tests(dirs, tier_filter=tier_filter)

    if not tests:
        print("No test files found.")
        return 0

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    failures = []
    file_results = []

    for test_file in tests:
        rel = test_file.relative_to(HARNESS_DIR)
        timeout = INTEGRATION_TEST_TIMEOUT if "integration" in str(test_file) else TEST_TIMEOUT
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            total_skipped += 1
            file_results.append({"file": str(rel), "passed": 0, "failed": 0, "status": "skip"})
            if not args.json:
                print(f"  SKIP  {rel} (timed out after {timeout}s)")
            continue

        # Parse last line for counts
        last_lines = result.stdout.strip().split("\n")
        summary_line = last_lines[-1] if last_lines else ""
        p = f = s = 0

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
                        p = 1
                        total_passed += 1
                        status = "ok"
                except (IndexError, ValueError):
                    p = 1
                    total_passed += 1
                    status = "ok"
            file_results.append({"file": str(rel), "passed": p, "failed": f, "status": "pass"})
            if not args.json:
                print(f"  PASS  {rel} ({status})")
        else:
            total_failed += 1
            failures.append(rel)
            file_results.append({"file": str(rel), "passed": 0, "failed": 1, "status": "fail"})
            if not args.json:
                print(f"  FAIL  {rel}")
                for line in last_lines[-3:]:
                    if line.strip():
                        print(f"        {line}")

    if args.json:
        print(json.dumps({
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "files": file_results,
        }, indent=2))
    else:
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
