#!/usr/bin/env python3
"""Run schematic analysis on all discovered schematic files.

Usage:
    python3 analyzers/run_schematic.py

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
    """Resolve path to kicad-happy repo."""
    if "KICAD_HAPPY_DIR" in os.environ:
        p = Path(os.environ["KICAD_HAPPY_DIR"])
        if p.exists():
            return p
        print(f"Error: KICAD_HAPPY_DIR={p} does not exist", file=sys.stderr)
        sys.exit(1)
    # Fallback: sibling directory
    fallback = HARNESS_DIR.parent / "kicad-happy"
    if fallback.exists():
        return fallback
    print("Error: Cannot find kicad-happy repo.", file=sys.stderr)
    print("  Set KICAD_HAPPY_DIR or clone it alongside this repo.", file=sys.stderr)
    sys.exit(1)


def main():
    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / "analyze_schematic.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    manifests_dir = HARNESS_DIR / "results" / "manifests"
    manifest = manifests_dir / "all_schematics.txt"

    if not manifest.exists():
        print("Error: all_schematics.txt not found. Run discover.py first.", file=sys.stderr)
        sys.exit(1)

    outputs_dir = HARNESS_DIR / "results" / "outputs" / "schematic"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    schematics = [line.strip() for line in manifest.read_text().splitlines() if line.strip()]

    print(f"=== Running schematic analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Files: {len(schematics)}")
    print()

    passed = failed = 0
    repos_dir = str(HARNESS_DIR / "repos")

    for i, sch_path in enumerate(schematics, 1):
        relpath = sch_path
        if sch_path.startswith(repos_dir):
            relpath = sch_path[len(repos_dir):].lstrip(os.sep)

        safe_name = relpath.replace(os.sep, "_").replace("/", "_")
        outfile = outputs_dir / f"{safe_name}.json"
        errfile = outputs_dir / f"{safe_name}.err"

        try:
            result = subprocess.run(
                [sys.executable, str(analyzer), sch_path, "-o", str(outfile)],
                capture_output=True, text=True, timeout=120,
            )
            errfile.write_text(result.stderr)

            if result.returncode == 0:
                passed += 1
                # Quick stats
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
