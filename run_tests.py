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
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent


# Curated smoke subset for CI PR gates. `--smoke` passes these paths to
# `python -m pytest -m unit` (see build_pytest_argv). Selection criteria:
#   1. Zero corpus dependency — runs cleanly in a fresh checkout with no
#      `repos/`, `results/`, or `reference/` data present.
#   2. Its tests carry the `unit` marker (explicit, or derived by
#      conftest.py), since `--smoke` selects with `-m unit`.
#   3. Covers diverse subsystems: core utils, schema, diff engine,
#      assertion engine, validators, naming, parser verifier, datasheets.
#   4. Fast: the whole subset is meant to finish in a few seconds.
#
# When adding new test files, decide whether they meet (1)+(2)+(4) and
# add them here if they do. Don't include tests that read from corpus
# directories — those belong in the full unit suite.
SMOKE_TESTS = [
    "tests/test_invariants.py",      # structural invariants
    "tests/test_utils.py",           # shared utilities
    "tests/test_safe_names.py",      # name flattening (TH-013)
    "tests/test_diff_analysis.py",   # diff engine
    "tests/test_differ.py",          # diff library
    "tests/test_checks.py",          # assertion engine
    "tests/test_run_checks.py",      # run_checks exit code (TH-015)
    "tests/test_schema.py",          # schema validation
    "tests/test_validate_outputs.py",  # output structural checks
    "tests/test_verify_parser.py",   # parser verifier
    "tests/test_datasheet_verify.py",  # datasheet extraction validation
    "tests/test_datasheet_db_storage.py",   # datasheet store primitives
    "tests/test_datasheet_db_manifest.py",  # datasheet manifest layer
    "tests/test_ab_test.py",          # A/B blast-radius framework
    "tests/test_generate_analytics.py",  # analytics chart data collection
    "tests/test_reclassify_repos.py",  # repo classification scoring
    "tests/test_generate_catalog.py",  # catalog query + matching
    "tests/test_detect_changes.py",  # upstream change detection mapping + import graph + CLI exit map
    "tests/test_add_repos.py",       # category insert point logic
    "tests/test_build_sch.py",       # KiCad schematic builder
    "tests/test_synthetic.py",       # synthetic detector fixtures
    "tests/test_spice_coverage.py",  # SPICE coverage metrics
    "tests/test_bug_cemetery.py",    # historical bug reproducers
    "tests/test_metamorphic.py",     # invariance/covariance
    "tests/test_structured_findings.py",  # structured finding checks
    "tests/test_finding_schema.py",  # finding_schema.py contract
    "tests/test_downstream_tools.py",  # downstream tool smoke tests
    "tests/datasheets/test_a3_lookup_path.py",       # raw lookup() + best/trusted
    "tests/datasheets/test_a3_trust_gates_deny.py",  # synthetic-liar trust-gate denial
    "tests/datasheets/test_a4_v13_on_v14_cache.py",  # v1.3 detector logic on v1.4 caches: divergence + convergence
    "tests/test_check_acceptance_gate.py",           # 4-check acceptance gate runner
    "tests/test_extraction_differ.py",                # extraction differ framework
    "tests/datasheets/test_a7_meta_schema.py",        # gold meta schema + mpn_slug helper
    "tests/datasheets/test_a7_promote_gold.py",       # promote_gold.py CLI
    "tests/datasheets/test_a7_re_curate_mode.py",     # re-curation mode
    "tests/datasheets/test_a7_check_gold_currency.py",  # gold currency check
    "tests/datasheets/test_a7_known_divergences.py",  # known divergences seed
    "tests/datasheets/test_a7_run_extraction_checks.py",  # extraction diff checks
    "tests/test_b1_b2_finding_id_invariants.py",      # capability_mode_ref + finding_id
    "tests/test_b4_b7_layer2_schemas.py",             # design_context precedence + novel-findings schema
    "tests/test_b3_b8_layer2_behavior.py",            # renderer contract + annotation merge lifecycle
    "tests/test_b5d_detector_fire_shapes.py",         # per-rule fire-shape AM/OV/TJ/FT/PM/EX
    "tests/test_b6_reviewer_output_invariants.py",    # reviewer-output replay + invariants
    "tests/test_top_level_sheets.py",                 # top_level_sheets merge + power_symbols refresh (PR #19)
    "tests/test_b9_review_metrics.py",                # review metrics runner + demo packet
    "tests/test_field_compare_policy.py",             # normalization policy loader
    "tests/test_field_compare_strict.py",             # strict pointer comparison
    "tests/test_field_compare_masking.py",            # exact-leaf masking + linkage
    "tests/test_field_compare_trees.py",              # raw mode + field_report v1
    "tests/test_field_compare_budget.py",             # budget records + evaluate_budget
    "tests/test_compare_snap_trees_cli.py",           # CLI exit codes
    "tests/test_field_compare_run_modes.py",          # gate hook
    "tests/test_run_corpus_gate_modes.py",            # gate wiring (apply_modes, --budget)
    "tests/test_field_compare_real_pr44.py",          # real PR #44 pairs
    "tests/test_field_compare_real_chained.py",       # real chained pair (source_hashes)
    "tests/test_field_compare_budgeted_report.py",    # shared budgeted_report + identity
]


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



def build_pytest_argv(args) -> list[str]:
    """Translate the legacy flags into a pytest command line."""
    argv = [sys.executable, "-m", "pytest", "-q"]
    paths = list(getattr(args, "paths", None) or [])
    if args.smoke:
        argv += ["-m", "unit"]
        paths = paths or list(SMOKE_TESTS)
    else:
        tier = args.tier
        if args.unit:
            tier = "unit"
        elif args.integration:
            tier = "online"
        if tier is None:
            tier = "unit"
        if tier == "all":
            argv.append("--all-tiers")
            paths = paths or ["tests", "integration"]
        elif tier == "online":
            argv += ["-m", "online"]
            paths = paths or ["tests", "integration"]
        else:
            argv += ["-m", "unit"]
            paths = paths or ["tests"]
    return argv + paths


def pytest_exit_to_rc(rc: int) -> int:
    """pytest 0 -> 0; 5 (no tests collected) -> 2; anything else -> 1."""
    if rc == 0:
        return 0
    if rc == 5:
        return 2
    return 1


def junit_to_legacy(xml_path: Path) -> dict:
    """Render pytest's junit XML in the historical ``--json`` shape."""
    root = ET.parse(xml_path).getroot()
    per_file: dict[str, dict] = {}
    for case in root.iter("testcase"):
        f = case.get("file") or case.get("classname", "").replace(".", "/") + ".py"
        row = per_file.setdefault(f, {"file": f, "passed": 0, "failed": 0, "skipped": 0})
        if case.find("skipped") is not None:
            row["skipped"] += 1
        elif case.find("failure") is not None or case.find("error") is not None:
            row["failed"] += 1
        else:
            row["passed"] += 1
    files = []
    for row in sorted(per_file.values(), key=lambda r: r["file"]):
        row["status"] = "fail" if row["failed"] else "pass"
        files.append(row)
    return {"total_passed": sum(r["passed"] for r in files),
            "total_failed": sum(r["failed"] for r in files),
            "total_skipped": sum(r["skipped"] for r in files),
            "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run harness tests (thin alias over pytest)")
    parser.add_argument("--unit", action="store_true", help="unit tier (default)")
    parser.add_argument("--integration", action="store_true", help="online tier")
    parser.add_argument("--tier", choices=["unit", "online", "all"])
    parser.add_argument("--smoke", action="store_true",
                        help="curated PR-gate subset (SMOKE_TESTS), unit tier")
    parser.add_argument("--list-smoke", action="store_true")
    parser.add_argument("--quick-sanity", action="store_true",
                        help="run assertions on 5 smoke_pack repos")
    parser.add_argument("--json", action="store_true", help="legacy JSON summary on stdout")
    parser.add_argument("--paths", nargs="*", help="override the paths pytest collects")
    args = parser.parse_args()

    if args.list_smoke:
        for path in SMOKE_TESTS:
            print(path)
        return 0
    if args.quick_sanity:
        return run_quick_sanity()

    argv = build_pytest_argv(args)
    if args.json:
        with tempfile.TemporaryDirectory() as td:
            xml = Path(td) / "junit.xml"
            proc = subprocess.run(argv + [f"--junitxml={xml}"], cwd=HARNESS_DIR,
                                  capture_output=True, text=True)
            rc = pytest_exit_to_rc(proc.returncode)
            if xml.exists():
                print(json.dumps(junit_to_legacy(xml), indent=2))
            else:
                sys.stderr.write(proc.stdout + proc.stderr)
            return rc
    proc = subprocess.run(argv, cwd=HARNESS_DIR)
    rc = pytest_exit_to_rc(proc.returncode)
    if rc == 2:
        print("ERROR: no tests collected - empty selection is a failure (B9)", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
