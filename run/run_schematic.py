#!/usr/bin/env python3
"""Run schematic analysis on all discovered schematic files.

Usage:
    python3 run/run_schematic.py
    python3 run/run_schematic.py --repo OpenMower

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
    parser = argparse.ArgumentParser(description="Run schematic analysis")
    parser.add_argument("--repo", help="Only analyze schematics for this repo")
    args = parser.parse_args()

    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / "analyze_schematic.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    manifest = MANIFESTS_DIR / "all_schematics.txt"

    if not manifest.exists():
        print("Error: all_schematics.txt not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    schematics = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]

    if args.repo:
        schematics = filter_manifest_by_repo(schematics, args.repo)
        if not schematics:
            print(f"No schematics found for repo '{args.repo}'", file=sys.stderr)
            sys.exit(1)

    print(f"=== Running schematic analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Files: {len(schematics)}")
    print()

    passed = failed = 0

    for i, sch_path in enumerate(schematics, 1):
        repo = repo_name_from_path(sch_path)
        sname = safe_name(sch_path)
        relpath = sch_path[len(str(REPOS_DIR)):].lstrip(os.sep) if sch_path.startswith(str(REPOS_DIR)) else sch_path

        repo_out_dir = OUTPUTS_DIR / "schematic" / repo
        repo_out_dir.mkdir(parents=True, exist_ok=True)
        outfile = repo_out_dir / f"{sname}.json"
        errfile = repo_out_dir / f"{sname}.err"

        try:
            result = subprocess.run(
                [sys.executable, str(analyzer), sch_path, "-o", str(outfile)],
                capture_output=True, text=True, timeout=120,
            )
            errfile.write_text(result.stderr)

            if result.returncode == 0:
                passed += 1
                try:
                    with open(outfile) as f:
                        d = json.load(f)
                    s = d.get("statistics", {})
                    comps = s.get("total_components", 0)
                    nets = s.get("total_nets", 0)
                    print(f"PASS [{i}] {relpath} (components={comps} nets={nets})")
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
