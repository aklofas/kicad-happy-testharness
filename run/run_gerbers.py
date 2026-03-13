#!/usr/bin/env python3
"""Run Gerber analysis on all discovered Gerber directories.

Usage:
    python3 run/run_gerbers.py
    python3 run/run_gerbers.py --repo OpenMower

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    HARNESS_DIR, REPOS_DIR, MANIFESTS_DIR, OUTPUTS_DIR,
    resolve_kicad_happy_dir, repo_name_from_path, safe_name,
    filter_manifest_by_repo,
)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Gerber analysis")
    parser.add_argument("--repo", help="Only analyze Gerbers for this repo")
    args = parser.parse_args()

    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / "analyze_gerbers.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    manifest = MANIFESTS_DIR / "all_gerbers.txt"

    if not manifest.exists():
        print("Error: all_gerbers.txt not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    gerber_dirs = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]

    if args.repo:
        gerber_dirs = filter_manifest_by_repo(gerber_dirs, args.repo)
        if not gerber_dirs:
            print(f"No Gerber dirs found for repo '{args.repo}'", file=sys.stderr)
            sys.exit(1)

    print(f"=== Running Gerber analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Directories: {len(gerber_dirs)}")
    print()

    passed = failed = 0

    for i, gerber_dir in enumerate(gerber_dirs, 1):
        repo = repo_name_from_path(gerber_dir)
        sname = safe_name(gerber_dir)
        relpath = gerber_dir[len(str(REPOS_DIR)):].lstrip(os.sep) if gerber_dir.startswith(str(REPOS_DIR)) else gerber_dir

        repo_out_dir = OUTPUTS_DIR / "gerber" / repo
        repo_out_dir.mkdir(parents=True, exist_ok=True)
        outfile = repo_out_dir / f"{sname}.json"
        errfile = repo_out_dir / f"{sname}.err"

        try:
            result = subprocess.run(
                [sys.executable, str(analyzer), gerber_dir, "-o", str(outfile)],
                capture_output=True, text=True, timeout=120,
            )
            errfile.write_text(result.stderr)

            if result.returncode == 0:
                passed += 1
                try:
                    with open(outfile) as f:
                        d = json.load(f)
                    layers = len(d.get("layers", []))
                    drills = len(d.get("drill_files", []))
                    print(f"PASS [{i}] {relpath} (layers={layers} drills={drills})")
                except Exception:
                    print(f"PASS [{i}] {relpath} (parse_error)")
            else:
                failed += 1
                err_lines = result.stderr.strip().splitlines()
                err_msg = err_lines[-1] if err_lines else f"exit {result.returncode}"
                print(f"FAIL [{i}] {relpath}")
                print(f"     {err_msg}")

        except subprocess.TimeoutExpired:
            failed += 1
            errfile.write_text("Timed out after 120s")
            print(f"FAIL [{i}] {relpath}")
            print(f"     Timed out")

    total = passed + failed
    print(f"\n=== Results ===")
    print(f"Total: {total}")
    print(f"Pass:  {passed}")
    print(f"Fail:  {failed}")
    if total > 0:
        print(f"Rate:  {passed * 100 / total:.1f}%")


if __name__ == "__main__":
    main()
