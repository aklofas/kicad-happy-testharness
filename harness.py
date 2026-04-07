#!/usr/bin/env python3
"""Unified entry point for the kicad-happy test harness.

Consolidates validate_all.py, run_corpus.py, and run_tests.py into a single
CLI with subcommands. The old scripts remain for backwards compatibility.

Usage:
    python3 harness.py test                              # unit tests
    python3 harness.py test --tier online                # integration tests
    python3 harness.py validate                          # assertions on existing outputs
    python3 harness.py validate --cross-section smoke    # subset
    python3 harness.py run --smoke                       # generate + validate smoke pack
    python3 harness.py run --cross-section quick_200     # generate + validate subset
    python3 harness.py run --full                        # everything
    python3 harness.py health                            # health report
    python3 harness.py status                            # quick summary
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS_DIR))
from utils import ANALYZER_TYPES


def _run(cmd, description, timeout=600):
    """Run a subprocess, print output, return success."""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}\n")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(HARNESS_DIR), timeout=timeout)
    elapsed = time.time() - t0
    ok = result.returncode == 0
    status = "PASS" if ok else "FAIL"
    print(f"\n  [{status}] {description} ({elapsed:.1f}s)")
    return ok


def cmd_test(args):
    """Run unit and/or integration tests."""
    cmd = [sys.executable, "run_tests.py"]
    if args.tier:
        cmd.extend(["--tier", args.tier])
    return _run(cmd, f"Tests (tier={args.tier or 'unit'})")


def cmd_validate(args):
    """Run assertions on existing outputs."""
    cmd = [sys.executable, "regression/run_checks.py"]
    if args.cross_section:
        cmd.extend(["--cross-section", args.cross_section])
    elif args.repo:
        cmd.extend(["--repo", args.repo])
    if args.type:
        cmd.extend(["--type", args.type])
    return _run(cmd, "Assertion checks", timeout=300)


def cmd_run(args):
    """Generate outputs and validate."""
    py = sys.executable
    steps = []

    # Determine repo filter
    filter_args = []
    if args.smoke:
        filter_args = ["--cross-section", "smoke"]
    elif args.cross_section:
        filter_args = ["--cross-section", args.cross_section]
    elif args.repo:
        filter_args = ["--repo", args.repo]

    resume_flag = ["--resume"] if args.resume else []

    steps.append(([py, "run_tests.py", "--tier", "unit"], "Unit tests"))

    for analyzer in ("run_schematic", "run_pcb", "run_gerbers"):
        cmd = [py, f"run/{analyzer}.py"] + filter_args + resume_flag
        steps.append((cmd, f"Analyzer: {analyzer}"))

    if not args.skip_spice:
        cmd = [py, "run/run_spice.py"] + filter_args + resume_flag
        steps.append((cmd, "SPICE simulations"))

    if not args.skip_emc:
        cmd = [py, "run/run_emc.py"] + filter_args + resume_flag
        steps.append((cmd, "EMC analysis"))

    check_cmd = [py, "regression/run_checks.py"] + filter_args
    steps.append((check_cmd, "Assertion checks"))

    # Run all steps
    results = []
    for cmd, desc in steps:
        ok = _run(cmd, desc, timeout=3600)
        results.append((desc, ok))
        if not ok and not args.continue_on_error:
            break

    # Summary
    print(f"\n{'=' * 60}")
    print("  PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    for desc, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {desc}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n  {passed}/{total} steps passed")
    return all(ok for _, ok in results)


def cmd_health(args):
    """Generate health report."""
    cmd = [sys.executable, "tools/generate_health_report.py", "--log"]
    if args.json:
        cmd.append("--json")
    return _run(cmd, "Health report")


def cmd_status(args):
    """Print quick status summary from latest health data."""
    # Load latest health log entry
    log_path = HARNESS_DIR / "reference" / "health_log.jsonl"
    if not log_path.exists():
        print("No health log found. Run: python3 harness.py health")
        return False

    # Read last line
    lines = [l.strip() for l in log_path.read_text().splitlines() if l.strip()]
    if not lines:
        print("Health log is empty.")
        return False

    latest = json.loads(lines[-1])
    assertions = latest.get("assertions", {})
    findings = latest.get("findings", {})
    schema = latest.get("schema", {})

    print(f"Repos:       {latest.get('repos_in_reference', '?')}")
    print(f"Assertions:  {assertions.get('total', '?')} "
          f"({assertions.get('files', '?')} files)")
    print(f"Detectors:   {schema.get('schematic_detectors', '?')}")
    print(f"Findings:    {findings.get('total_items', '?')} "
          f"across {findings.get('repos_with_findings', '?')} repos")
    print(f"Timestamp:   {latest.get('timestamp', '?')}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="kicad-happy test harness — unified entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
subcommands:
  test       Run unit/integration tests
  validate   Check assertions on existing outputs
  run        Generate outputs + validate (full pipeline)
  health     Generate health report
  status     Print quick status summary
""")
    sub = parser.add_subparsers(dest="command")

    # test
    p_test = sub.add_parser("test", help="Run tests")
    p_test.add_argument("--tier", choices=["unit", "online", "all"],
                        default="unit", help="Test tier (default: unit)")

    # validate
    p_val = sub.add_parser("validate", help="Check assertions")
    p_val.add_argument("--repo", help="Single repo")
    p_val.add_argument("--cross-section", help="Named cross-section")
    p_val.add_argument("--type", choices=ANALYZER_TYPES,
                       help="Analyzer type")

    # run
    p_run = sub.add_parser("run", help="Generate outputs + validate")
    p_run.add_argument("--smoke", action="store_true", help="Smoke pack (20 repos)")
    p_run.add_argument("--repo", help="Single repo")
    p_run.add_argument("--cross-section", help="Named cross-section")
    p_run.add_argument("--full", action="store_true", help="Full corpus")
    p_run.add_argument("--resume", action="store_true", help="Skip existing outputs")
    p_run.add_argument("--skip-spice", action="store_true", help="Skip SPICE")
    p_run.add_argument("--skip-emc", action="store_true", help="Skip EMC")
    p_run.add_argument("--continue-on-error", action="store_true",
                       help="Continue pipeline on step failure")

    # health
    p_health = sub.add_parser("health", help="Health report")
    p_health.add_argument("--json", action="store_true", help="JSON output")

    # status
    sub.add_parser("status", help="Quick status summary")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "test": cmd_test,
        "validate": cmd_validate,
        "run": cmd_run,
        "health": cmd_health,
        "status": cmd_status,
    }

    ok = handlers[args.command](args)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
