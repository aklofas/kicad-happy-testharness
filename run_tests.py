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
import re
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
    "tests/test_ab_test.py",          # 14 tests — A/B blast-radius framework (P11)
    "tests/test_generate_analytics.py",  # 9 tests — analytics chart data collection
    "tests/test_reclassify_repos.py",  # 9 tests — repo classification scoring
    "tests/test_generate_catalog.py",  # 18 tests — catalog query + matching
    "tests/test_detect_changes.py",  # 14 tests — upstream change detection mapping
    "tests/test_add_repos.py",       # 6 tests — category insert point logic
    "tests/test_build_sch.py",       # 12 tests — KiCad schematic builder (P4)
    "tests/test_synthetic.py",       # 11 tests — synthetic detector fixtures (P4)
    "tests/test_spice_coverage.py",  # 14 tests — SPICE coverage metrics (P10)
    "tests/test_bug_cemetery.py",    # 11 tests — historical bug reproducers (P8)
    "tests/test_metamorphic.py",     # 10 tests — invariance/covariance (P5)
    "tests/test_structured_findings.py",  # 11 tests — structured finding checks (P3.A)
    "tests/test_manufacturer_match.py",  # 11 tests — manufacturer prefix matching (DS-2)
    "tests/test_finding_schema.py",  # 26 tests — finding_schema.py contract (P13)
    "tests/test_downstream_tools.py",  # 12 tests — downstream tool smoke tests (P13)
    "tests/datasheets/test_a3_lookup_path.py",       # 18 tests — A3.1 raw lookup() + best/trusted (v1.4)
    "tests/datasheets/test_a3_trust_gates_deny.py",  # 16 tests — A3.3 synthetic-liar trust-gate denial
    "tests/datasheets/test_a4_v13_on_v14_cache.py",  # 18 tests — A4 divergence + convergence
    "tests/test_check_acceptance_gate.py",           # 22 tests — 4-check acceptance gate runner (A6)
    "tests/test_extraction_differ.py",                # 36 tests — extraction differ framework (A5)
    "tests/datasheets/test_a7_meta_schema.py",        # 12 tests — A7 meta schema + mpn_slug helper
    "tests/datasheets/test_a7_promote_gold.py",       # 8 tests — promote_gold.py CLI (A7)
    "tests/datasheets/test_a7_re_curate_mode.py",     # 6 tests — re-curation mode (A7)
    "tests/datasheets/test_a7_check_gold_currency.py",  # 13 tests — gold currency check (A7)
    "tests/datasheets/test_a7_known_divergences.py",  # 4 tests — known divergences seed (A7)
    "tests/datasheets/test_a7_run_extraction_checks.py",  # 10 tests — extraction diff checks (A7)
    "tests/test_b1_b2_finding_id_invariants.py",      # 10 tests — capability_mode_ref + finding_id (B1+B2)
    "tests/test_b4_b7_layer2_schemas.py",             # 12 tests — design_context precedence + novel-findings schema (B4+B7)
    "tests/test_b3_b8_layer2_behavior.py",            # 11 tests — renderer contract + annotation merge lifecycle (B3+B8)
    "tests/test_b5_4b_4c_detector_invariants.py",     # 10 tests — schema_era + enum + XT-001 emission gate (B5 a/b/c)
    "tests/test_b5d_detector_fire_shapes.py",         # 16 tests — per-rule fire-shape AM/OV/TJ/FT/PM/EX (B5 d)
    "tests/test_b6_reviewer_output_invariants.py",    # 16 tests — reviewer-output replay + invariants (B6)
    "tests/test_top_level_sheets.py",                 # 3 tests — top_level_sheets merge + power_symbols refresh (PR #19)
    "tests/test_b9_review_metrics.py",                # 12 tests — review metrics runner + demo packet (B9)
]


def discover_tests(dirs, tier_filter=None):
    """Find all test_*.py files in given directories, optionally filtered by TIER.

    Each test file can declare TIER = "unit"|"online" at module level.
    If tier_filter is set, only files matching that tier are returned.
    Files without a TIER declaration default to "unit" for tests/ and "online"
    for integration/.

    tests/contract/ is excluded — it is a pytest-driven suite invoked separately
    with KICAD_HAPPY_DIR set, not the custom-runner subprocess pattern.
    """
    tests = []
    for d in dirs:
        test_dir = HARNESS_DIR / d
        if not test_dir.exists():
            continue
        default_tier = "online" if d == "integration" else "unit"
        # rglob so subdirectories like tests/datasheets/ are discovered too.
        for f in sorted(test_dir.rglob("test_*.py")):
            # Skip pytest-driven sub-suites that don't fit the custom runner.
            if "contract" in f.relative_to(HARNESS_DIR).parts:
                continue
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


_MAIN_RE = re.compile(r"^if __name__\s*==\s*['\"]__main__['\"]", re.MULTILINE)
_SUMMARY_RE = re.compile(r"(\d+)\s+passed,\s+(\d+)\s+failed")
_SKIPPED_RE = re.compile(r"(\d+)\s+skipped")


def has_main_block(path):
    """True iff the file contains an ``if __name__ == "__main__"`` runner."""
    try:
        return bool(_MAIN_RE.search(Path(path).read_text(encoding="utf-8")))
    except OSError:
        return False


def run_test_file(path, timeout):
    """Run one stdlib test file as a subprocess and return a result dict.

    status: pass | fail | timeout | no_runner | unparsed. Only ``pass`` with
    ``failed == 0`` counts toward a green run (TH-052: no phantom passes).
    """
    path = Path(path)
    try:
        rel = str(path.relative_to(HARNESS_DIR))
    except ValueError:
        rel = str(path)
    base = {"file": rel, "passed": 0, "failed": 0, "skipped": 0, "detail": ""}
    if not has_main_block(path):
        return {**base, "status": "no_runner",
                "detail": "no __main__ runner block (TH-052)"}
    try:
        result = subprocess.run([sys.executable, str(path)],
                                capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {**base, "status": "timeout", "detail": f"timed out after {timeout}s"}
    lines = result.stdout.strip().split("\n")
    summary = lines[-1] if lines else ""
    m = _SUMMARY_RE.search(summary)
    if m is None:
        tail = "\n".join(l for l in lines[-3:] if l.strip())
        if result.returncode != 0:
            return {**base, "status": "fail", "failed": 1,
                    "detail": f"exit {result.returncode}\n{tail}"}
        return {**base, "status": "unparsed",
                "detail": f"unparsed summary: {summary!r}"}
    p, f = int(m.group(1)), int(m.group(2))
    ms = _SKIPPED_RE.search(summary)
    s = int(ms.group(1)) if ms else 0
    status = "pass" if (result.returncode == 0 and f == 0) else "fail"
    return {**base, "status": status, "passed": p, "failed": f, "skipped": s,
            "detail": "" if status == "pass" else f"exit {result.returncode}"}


def exit_code(results):
    """0 iff every file passed with zero failures; 2 for an empty selection."""
    if not results:
        return 2
    bad = [r for r in results if r["status"] != "pass" or r["failed"]]
    return 1 if bad else 0


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
        if tier_filter is None and not args.integration and not args.unit:
            tier_filter = "unit"

        # Determine which directories to scan
        dirs = ["tests", "integration"]
        if tier_filter == "unit":
            dirs = ["tests"]
        elif tier_filter == "online":
            dirs = ["integration"]

        tests = discover_tests(dirs, tier_filter=tier_filter)

    if not tests:
        print("No test files found.")
        return 2

    results = []
    for test_file in tests:
        timeout = INTEGRATION_TEST_TIMEOUT if "integration" in str(test_file) else TEST_TIMEOUT
        r = run_test_file(test_file, timeout)
        results.append(r)
        if not args.json:
            tag = "PASS" if r["status"] == "pass" else "FAIL"
            counts = f"{r['passed']}p {r['failed']}f" + (f" {r['skipped']}s" if r["skipped"] else "")
            detail = f"; {r['detail']}" if r["detail"] else ""
            print(f"  {tag}  {r['file']} ({counts}{detail})")

    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    failures = [r["file"] for r in results if r["status"] != "pass" or r["failed"]]
    if args.json:
        print(json.dumps({"total_passed": total_passed, "total_failed": total_failed,
                          "total_skipped": total_skipped, "files": results}, indent=2))
    else:
        print()
        print("=" * 50)
        print(f"Results: {total_passed} passed, {total_failed} failed, {total_skipped} skipped")
        print(f"Files:   {len(tests)} test files ({len(tests) - len(failures)} ok, {len(failures)} failed)")
        print("=" * 50)
        if failures:
            print(f"\nFailed: {', '.join(failures)}")
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
