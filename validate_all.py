#!/usr/bin/env python3
"""Unified validation orchestrator — single command for the full pipeline.

Runs pre-flight checks, then executes validation steps in order.
Replaces the manual 9-step process with one command.

Usage:
    python3 validate_all.py                    # Full validation
    python3 validate_all.py --quick            # Unit tests + assertions only
    python3 validate_all.py --repo OpenMower   # Validate one repo
    python3 validate_all.py --json             # Machine-readable output
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPOS_DIR = HARNESS_DIR / "repos"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
DATA_DIR = HARNESS_DIR / "reference"


def _resolve_kicad_happy_dir():
    """Check if kicad-happy repo is findable."""
    if "KICAD_HAPPY_DIR" in os.environ:
        p = Path(os.environ["KICAD_HAPPY_DIR"])
        return p if p.exists() else None
    fallback = HARNESS_DIR.parent / "kicad-happy"
    return fallback if fallback.exists() else None


def _manifest_mtime():
    """Get mtime of all_schematics.txt, or None."""
    f = MANIFESTS_DIR / "all_schematics.txt"
    return f.stat().st_mtime if f.exists() else None


def _newest_repo_mtime():
    """Get newest .git/FETCH_HEAD mtime across checked-out repos."""
    newest = 0
    if not REPOS_DIR.exists():
        return 0
    for d in REPOS_DIR.iterdir():
        fh = d / ".git" / "FETCH_HEAD"
        if fh.exists():
            newest = max(newest, fh.stat().st_mtime)
    return newest


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def preflight(json_mode=False):
    """Run pre-flight checks. Returns list of {check, status, detail} dicts."""
    checks = []

    # 1. KICAD_HAPPY_DIR
    khd = _resolve_kicad_happy_dir()
    checks.append({
        "check": "kicad_happy_dir",
        "status": "ok" if khd else "warn",
        "detail": str(khd) if khd else "not found (set KICAD_HAPPY_DIR or clone alongside)",
    })

    # 2. Repos checked out
    repo_count = 0
    if REPOS_DIR.exists():
        repo_count = sum(1 for d in REPOS_DIR.iterdir()
                         if d.is_dir() and not d.name.startswith("."))
    checks.append({
        "check": "repos_checked_out",
        "status": "ok" if repo_count > 0 else "fail",
        "detail": f"{repo_count} repos" if repo_count > 0 else "repos/ empty — run checkout.py",
    })

    # 3. Manifests exist
    manifest = MANIFESTS_DIR / "all_schematics.txt"
    checks.append({
        "check": "manifests_exist",
        "status": "ok" if manifest.exists() else "fail",
        "detail": "present" if manifest.exists() else "missing — run discover.py",
    })

    # 4. Manifest freshness
    m_mtime = _manifest_mtime()
    r_mtime = _newest_repo_mtime()
    if m_mtime and r_mtime and r_mtime > m_mtime:
        checks.append({
            "check": "manifests_fresh",
            "status": "warn",
            "detail": "manifests older than repos — consider re-running discover.py",
        })
    elif m_mtime:
        checks.append({
            "check": "manifests_fresh",
            "status": "ok",
            "detail": "up to date",
        })

    # 5. Reference data exists
    ref_count = 0
    if DATA_DIR.exists():
        ref_count = sum(1 for d in DATA_DIR.iterdir()
                        if d.is_dir() and not d.name.startswith("."))
    checks.append({
        "check": "reference_data",
        "status": "ok" if ref_count > 0 else "warn",
        "detail": f"{ref_count} repos in reference/" if ref_count > 0 else "no reference data",
    })

    return checks


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------

def run_step(name, cmd, timeout=300):
    """Run a subprocess step. Returns {name, status, detail, elapsed_s, output}."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(HARNESS_DIR),
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            return {
                "name": name,
                "status": "pass",
                "detail": _extract_summary(result.stdout),
                "elapsed_s": round(elapsed, 1),
                "output": result.stdout,
            }
        else:
            return {
                "name": name,
                "status": "fail",
                "detail": _extract_summary(result.stdout) or result.stderr.strip()[-200:],
                "elapsed_s": round(elapsed, 1),
                "output": result.stdout + result.stderr,
            }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        return {
            "name": name,
            "status": "timeout",
            "detail": f"timed out after {timeout}s",
            "elapsed_s": round(elapsed, 1),
            "output": "",
        }
    except FileNotFoundError:
        return {
            "name": name,
            "status": "skip",
            "detail": "command not found",
            "elapsed_s": 0,
            "output": "",
        }


def _extract_summary(stdout):
    """Extract the last meaningful line from stdout as a summary."""
    lines = [l.strip() for l in stdout.strip().splitlines() if l.strip()]
    if not lines:
        return ""
    # Look for common summary patterns
    for line in reversed(lines):
        if any(k in line.lower() for k in ["result", "total", "pass", "rate", "generated"]):
            return line[:200]
    return lines[-1][:200]


def run_checks_json(repo=None):
    """Run regression/run_checks.py --json and parse results."""
    cmd = [sys.executable, str(HARNESS_DIR / "regression" / "run_checks.py"), "--json"]
    if repo:
        cmd.extend(["--repo", repo])
    step = run_step("assertions", cmd, timeout=600)
    if step["status"] == "pass":
        try:
            data = json.loads(step["output"])
            total = data.get("total", 0)
            passed = data.get("passed", 0)
            failed = data.get("failed", 0)
            rate = data.get("pass_rate", "N/A")
            asp = data.get("aspirational", {})
            asp_total = asp.get("total", 0)
            asp_pass = asp.get("passed", 0)
            detail = f"{passed}/{total} pass ({rate})"
            if asp_total:
                detail += f", aspirational: {asp_pass}/{asp_total}"
            step["detail"] = detail
            step["parsed"] = data
        except (json.JSONDecodeError, KeyError):
            pass
    return step


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Unified validation orchestrator"
    )
    parser.add_argument("--repo", help="Validate one repo only")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: unit tests + assertions only")
    parser.add_argument("--json", action="store_true",
                        help="Machine-readable JSON output")
    args = parser.parse_args()

    # Phase 1: Pre-flight
    pf_checks = preflight(json_mode=args.json)

    has_critical_fail = any(c["status"] == "fail" for c in pf_checks)

    if not args.json:
        print("=" * 60)
        print("PRE-FLIGHT CHECKS")
        print("=" * 60)
        for c in pf_checks:
            icon = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}.get(c["status"], "?")
            print(f"  [{icon:4s}] {c['check']:25s} {c['detail']}")
        print()

    if has_critical_fail:
        if not args.json:
            print("ABORTING — critical pre-flight check failed")
        else:
            print(json.dumps({
                "status": "aborted",
                "preflight": pf_checks,
                "steps": [],
            }, indent=2))
        sys.exit(1)

    # Phase 2: Pipeline steps
    steps = []

    # Step 1: Unit tests (always run)
    step = run_step("unit_tests",
                    [sys.executable, str(HARNESS_DIR / "run_tests.py"), "--unit"],
                    timeout=300)
    steps.append(step)

    if step["status"] != "pass":
        if not args.json:
            print(f"ABORTING — unit tests failed")
            _print_step(step)
        else:
            print(json.dumps({
                "status": "failed",
                "preflight": pf_checks,
                "steps": steps,
            }, indent=2))
        sys.exit(1)

    # Step 2: Assertions
    step = run_checks_json(repo=args.repo)
    steps.append(step)

    if args.quick:
        # Quick mode: stop here
        _finish(pf_checks, steps, args)
        return

    # Step 3: Validate outputs (if --repo or full run)
    if args.repo:
        step = run_step("validate_outputs",
                        [sys.executable,
                         str(HARNESS_DIR / "validate" / "validate_outputs.py"),
                         "--repo", args.repo],
                        timeout=120)
        steps.append(step)

    # Step 4: Constants audit — check for critical-risk constants
    constants_script = HARNESS_DIR / "validate" / "audit_constants.py"
    if constants_script.exists():
        step = run_step("constants_audit",
                        [sys.executable, str(constants_script),
                         "list", "--risk", "critical"],
                        timeout=60)
        # "No matching constants" means pass (exit 0)
        # Any output listing constants means there are critical-risk items
        if step["status"] == "pass" and "No matching" not in step.get("output", ""):
            step["status"] = "warn"
            step["detail"] = "critical-risk constants found"
        steps.append(step)

    # Step 5: Schema diff (skip if validate_schema.py doesn't exist or no inventory)
    schema_script = HARNESS_DIR / "validate" / "validate_schema.py"
    inventory_file = DATA_DIR / "schema_inventory.json"
    if schema_script.exists() and inventory_file.exists():
        cmd = [sys.executable, str(schema_script), "diff"]
        if args.repo:
            cmd.extend(["--repo", args.repo])
        step = run_step("schema_diff", cmd, timeout=120)
        # Schema diff exits 1 if changes found — that's informational, not a failure
        if step["status"] == "fail" and "SCHEMA CHANGES" in step.get("output", ""):
            step["status"] = "warn"
        steps.append(step)

    # Step 5: SPICE cross-validation (if outputs exist)
    spice_dir = OUTPUTS_DIR / "spice"
    if spice_dir.exists() and any(spice_dir.iterdir()):
        cmd = [sys.executable,
               str(HARNESS_DIR / "validate" / "validate_spice.py"),
               "--summary"]
        if args.repo:
            cmd.extend(["--repo", args.repo])
        step = run_step("spice_crossval", cmd, timeout=300)
        steps.append(step)

    # Step 6: EMC cross-validation (if outputs exist)
    emc_dir = OUTPUTS_DIR / "emc"
    if emc_dir.exists() and any(emc_dir.iterdir()):
        cmd = [sys.executable,
               str(HARNESS_DIR / "validate" / "validate_emc.py"),
               "--summary"]
        if args.repo:
            cmd.extend(["--repo", args.repo])
        step = run_step("emc_crossval", cmd, timeout=300)
        steps.append(step)

    _finish(pf_checks, steps, args)


def _finish(pf_checks, steps, args):
    """Print final summary and exit."""
    any_fail = any(s["status"] == "fail" for s in steps)

    if args.json:
        print(json.dumps({
            "status": "failed" if any_fail else "passed",
            "preflight": pf_checks,
            "steps": [{k: v for k, v in s.items() if k != "output"} for s in steps],
        }, indent=2))
    else:
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        for s in steps:
            _print_step(s)
        print()
        if any_fail:
            print("RESULT: FAILED")
        else:
            print("RESULT: PASSED")

    sys.exit(1 if any_fail else 0)


def _print_step(step):
    icon = {
        "pass": "PASS", "fail": "FAIL", "warn": "WARN",
        "skip": "SKIP", "timeout": "TIME",
    }.get(step["status"], "?")
    elapsed = f"({step['elapsed_s']}s)" if step.get("elapsed_s") else ""
    print(f"  [{icon:4s}] {step['name']:25s} {step['detail'][:80]} {elapsed}")


if __name__ == "__main__":
    main()
