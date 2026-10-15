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
    "tests/test_field_compare_policy.py",             # 22 tests — normalization policy loader (H0 plan 3)
    "tests/test_field_compare_strict.py",             # 21 tests — strict pointer comparison
    "tests/test_field_compare_masking.py",            # 28 tests — exact-leaf masking + linkage
    "tests/test_field_compare_trees.py",              # 20 tests — raw mode + field_report v1
    "tests/test_field_compare_budget.py",             # 49 tests — budget records + evaluate_budget
    "tests/test_compare_snap_trees_cli.py",           # 12 tests — CLI exit codes
    "tests/test_field_compare_run_modes.py",          # 4 tests — gate hook
    "tests/test_run_corpus_gate_modes.py",            # 4 tests — gate wiring (apply_modes, --budget)
    "tests/test_field_compare_real_pr44.py",          # 4 tests — real PR #44 pairs
    "tests/test_field_compare_real_chained.py",       # 5 tests — real chained pair (C1 source_hashes)
    "tests/test_field_compare_budgeted_report.py",    # 7 tests — shared budgeted_report + identity
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
    """Translate the legacy flags into a pytest command line (B9 alias)."""
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
