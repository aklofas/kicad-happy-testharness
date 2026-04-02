#!/usr/bin/env python3
"""Unified corpus run orchestrator — generate outputs and validate in one command.

Unlike validate_all.py (which validates existing outputs), this script generates
fresh analyzer outputs and then runs the full validation pipeline.

Usage:
    python3 run_corpus.py --full      # All analyzers, all repos, full validation
    python3 run_corpus.py --quick     # Unit tests + assertions only (no re-run)
    python3 run_corpus.py --smoke     # 10 repos, all analyzers, full validation
    python3 run_corpus.py --repo X    # One repo, all analyzers
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
HEALTH_LOG = HARNESS_DIR / "reference" / "health_log.jsonl"
CORPUS_LOG = HARNESS_DIR / "results" / "corpus_run.json"


def _run_step(name, cmd, timeout=600, abort_on_fail=False):
    """Run a step, return {name, status, elapsed_s, detail}."""
    print(f"\n{'='*60}")
    print(f"Step: {name}")
    print(f"{'='*60}")
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(HARNESS_DIR),
        )
        elapsed = time.time() - t0
        status = "pass" if result.returncode == 0 else "fail"
        detail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        # Print last few lines of output
        lines = result.stdout.strip().splitlines()
        for line in lines[-5:]:
            print(f"  {line}")
        if result.returncode != 0 and result.stderr:
            for line in result.stderr.strip().splitlines()[-3:]:
                print(f"  ERR: {line}")
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        status = "timeout"
        detail = f"Timed out after {timeout}s"
        print(f"  TIMEOUT after {timeout}s")
    except Exception as e:
        elapsed = time.time() - t0
        status = "error"
        detail = str(e)
        print(f"  ERROR: {e}")

    icon = {"pass": "OK", "fail": "FAIL", "timeout": "TIME", "error": "ERR"}
    print(f"  [{icon.get(status, '?')}] {name} ({elapsed:.1f}s)")

    if abort_on_fail and status != "pass":
        print(f"\nABORT: {name} failed — stopping pipeline.")
        sys.exit(1)

    return {"name": name, "status": status, "elapsed_s": round(elapsed, 2),
            "detail": detail[:200]}


def _last_health():
    """Load last health log entry for comparison."""
    if not HEALTH_LOG.exists():
        return None
    lines = HEALTH_LOG.read_text().strip().splitlines()
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Unified corpus run — generate outputs and validate")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--full", action="store_true",
                      help="All analyzers, all repos, full validation")
    mode.add_argument("--quick", action="store_true",
                      help="Unit tests + assertions only (no re-run)")
    mode.add_argument("--smoke", action="store_true",
                      help="10 repos, all analyzers, full validation")
    parser.add_argument("--repo", help="Run on a specific repo (overrides --smoke)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    py = sys.executable
    steps = []
    t_total = time.time()

    # Determine repo filter
    repo_args = []
    if args.repo:
        repo_args = ["--repo", args.repo]
    elif args.smoke:
        # Pick first 10 repos from outputs/schematic
        sch_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
        if sch_dir.exists():
            repos = sorted(d.name for d in sch_dir.iterdir() if d.is_dir())[:10]
            if repos:
                repo_args = ["--repo", repos[0]]  # Will loop below
            else:
                print("No schematic outputs found for smoke test", file=sys.stderr)
                sys.exit(1)

    # Step 1: Unit tests (always, abort on failure)
    steps.append(_run_step(
        "Unit tests",
        [py, "run_tests.py", "--unit"],
        timeout=60, abort_on_fail=True,
    ))

    if args.quick:
        # Quick mode: just unit tests + assertions
        steps.append(_run_step(
            "Assertions",
            [py, "regression/run_checks.py"] + repo_args,
            timeout=600,
        ))
    else:
        # Step 2: Upstream change detection (informational)
        steps.append(_run_step(
            "Upstream changes",
            [py, "detect_changes.py"],
            timeout=30,
        ))

        if args.smoke and not args.repo:
            # Smoke: run all analyzers on 10 repos sequentially
            sch_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
            repos = sorted(d.name for d in sch_dir.iterdir() if d.is_dir())[:10]
            for repo in repos:
                ra = ["--repo", repo]
                steps.append(_run_step(
                    f"Schematic ({repo})",
                    [py, "run/run_schematic.py", "--jobs", "4"] + ra,
                    timeout=120,
                ))
                steps.append(_run_step(
                    f"PCB ({repo})",
                    [py, "run/run_pcb.py", "--jobs", "4"] + ra,
                    timeout=120,
                ))
                steps.append(_run_step(
                    f"SPICE ({repo})",
                    [py, "run/run_spice.py", "--jobs", "16"] + ra,
                    timeout=120,
                ))
                steps.append(_run_step(
                    f"EMC ({repo})",
                    [py, "run/run_emc.py", "--jobs", "8"] + ra,
                    timeout=120,
                ))
        else:
            # Full or single-repo: run all analyzers
            steps.append(_run_step(
                "Schematic analysis",
                [py, "run/run_schematic.py", "--jobs", "16"] + repo_args,
                timeout=3600,
            ))
            steps.append(_run_step(
                "PCB analysis",
                [py, "run/run_pcb.py", "--jobs", "16"] + repo_args,
                timeout=3600,
            ))
            steps.append(_run_step(
                "Gerber analysis",
                [py, "run/run_gerbers.py", "--jobs", "16"] + repo_args,
                timeout=3600,
            ))
            steps.append(_run_step(
                "SPICE simulations",
                [py, "run/run_spice.py", "--jobs", "16"] + repo_args,
                timeout=3600,
            ))
            steps.append(_run_step(
                "EMC analysis",
                [py, "run/run_emc.py", "--jobs", "8"] + repo_args,
                timeout=3600,
            ))

        # Validation steps
        steps.append(_run_step(
            "Assertions",
            [py, "regression/run_checks.py"] + repo_args,
            timeout=600,
        ))
        steps.append(_run_step(
            "Cross-analyzer consistency",
            [py, "validate/cross_analyzer.py", "--summary"] + repo_args,
            timeout=300,
        ))
        steps.append(_run_step(
            "SPICE cross-validation",
            [py, "validate/validate_spice.py", "--summary"] + repo_args,
            timeout=300,
        ))
        steps.append(_run_step(
            "EMC cross-validation",
            [py, "validate/validate_emc.py", "--summary"] + repo_args,
            timeout=300,
        ))
        steps.append(_run_step(
            "Constants audit",
            [py, "validate/audit_constants.py", "list", "--risk", "critical"],
            timeout=60,
        ))
        steps.append(_run_step(
            "Schema drift",
            [py, "validate/validate_schema.py", "diff"] + repo_args,
            timeout=120,
        ))
        steps.append(_run_step(
            "Assertion staleness",
            [py, "regression/check_staleness.py"] + repo_args,
            timeout=120,
        ))
        steps.append(_run_step(
            "Health report",
            [py, "generate_health_report.py", "--log"],
            timeout=120,
        ))

    total_elapsed = time.time() - t_total
    passed = sum(1 for s in steps if s["status"] == "pass")
    failed = sum(1 for s in steps if s["status"] == "fail")
    mode_name = "full" if args.full else ("smoke" if args.smoke else "quick")

    # Compare with last health log
    prev = _last_health()
    comparison = None
    if prev:
        prev_assertions = prev.get("assertions", {}).get("total", 0)
        comparison = {"prev_assertions": prev_assertions,
                      "prev_timestamp": prev.get("timestamp", "?")}

    result = {
        "mode": mode_name,
        "repo": args.repo,
        "total_elapsed_s": round(total_elapsed, 2),
        "steps": len(steps),
        "passed": passed,
        "failed": failed,
        "comparison": comparison,
        "step_results": steps,
    }

    # Write corpus run log
    CORPUS_LOG.parent.mkdir(parents=True, exist_ok=True)
    CORPUS_LOG.write_text(json.dumps(result, indent=2))

    if args.json:
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        print(f"\n{'='*60}")
        print(f"CORPUS RUN COMPLETE ({mode_name})")
        print(f"{'='*60}")
        print(f"Steps: {passed}/{len(steps)} passed, {failed} failed")
        print(f"Total time: {total_elapsed:.1f}s")
        if comparison:
            print(f"Previous assertion count: {comparison['prev_assertions']:,}")
        print(f"Results saved to: {CORPUS_LOG}")
        if failed > 0:
            print(f"\nFailed steps:")
            for s in steps:
                if s["status"] != "pass":
                    print(f"  [{s['status'].upper()}] {s['name']}: {s['detail']}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
