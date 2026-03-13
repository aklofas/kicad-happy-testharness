#!/usr/bin/env python3
"""Run Gerber analysis on all discovered Gerber directories.

Usage:
    python3 analyzers/run_gerbers.py

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent


def resolve_kicad_happy_dir() -> Path:
    if "KICAD_HAPPY_DIR" in os.environ:
        p = Path(os.environ["KICAD_HAPPY_DIR"])
        if p.exists():
            return p
        print(f"Error: KICAD_HAPPY_DIR={p} does not exist", file=sys.stderr)
        sys.exit(1)
    fallback = HARNESS_DIR.parent / "kicad-happy"
    if fallback.exists():
        return fallback
    print("Error: Cannot find kicad-happy repo.", file=sys.stderr)
    print("  Set KICAD_HAPPY_DIR or clone it alongside this repo.", file=sys.stderr)
    sys.exit(1)


def main():
    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / "analyze_gerbers.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    manifests_dir = HARNESS_DIR / "results" / "manifests"
    manifest = manifests_dir / "all_gerbers.txt"

    if not manifest.exists():
        print("Error: all_gerbers.txt not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    outputs_dir = HARNESS_DIR / "results" / "outputs" / "gerber"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    gerber_dirs = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]

    print(f"=== Running Gerber analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Directories: {len(gerber_dirs)}")
    print()

    passed = failed = 0
    repos_dir = str(HARNESS_DIR / "repos")

    for i, gerber_dir in enumerate(gerber_dirs, 1):
        relpath = gerber_dir
        if gerber_dir.startswith(repos_dir):
            relpath = gerber_dir[len(repos_dir):].lstrip(os.sep)

        safe_name = relpath.replace(os.sep, "_").replace("/", "_")
        outfile = outputs_dir / f"{safe_name}.json"
        errfile = outputs_dir / f"{safe_name}.err"

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
