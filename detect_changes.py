#!/usr/bin/env python3
"""Upstream change detection for kicad-happy.

Diffs the kicad-happy repo to determine which analyzer scripts changed,
maps changes to affected analyzer types, and recommends test actions.

Usage:
    python3 detect_changes.py                    # Diff HEAD vs HEAD~1
    python3 detect_changes.py --since HEAD~5     # Diff against older commit
    python3 detect_changes.py --json
"""

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import resolve_kicad_happy_dir, ANALYZER_TYPES

# Map kicad-happy file paths to affected analyzer types
FILE_TO_TYPES = {
    "skills/kicad/scripts/analyze_schematic.py": {"schematic"},
    "skills/kicad/scripts/signal_detectors.py": {"schematic"},
    "skills/kicad/scripts/analyze_pcb.py": {"pcb"},
    "skills/kicad/scripts/analyze_gerbers.py": {"gerber"},
    "skills/emc/scripts/analyze_emc.py": {"emc"},
    "skills/emc/scripts/emc_rules.py": {"emc"},
    "skills/spice/scripts/simulate_subcircuits.py": {"spice"},
    "skills/spice/scripts/spice_tolerance.py": {"spice"},
    "skills/spice/scripts/spice_results.py": {"spice"},
    "skills/kicad/scripts/kicad_utils.py": {"schematic", "pcb", "spice"},
    "skills/kicad/scripts/kicad_types.py": {"schematic", "pcb"},
    "skills/kicad/scripts/diff_analysis.py": set(),  # standalone, no test impact
    "skills/kicad/scripts/what_if.py": set(),
    "skills/kicad/scripts/analyze_thermal.py": set(),
}

# Glob patterns for broader matching
GLOB_PATTERNS = {
    "skills/emc/": {"emc"},
    "skills/spice/": {"spice"},
    "skills/kicad/scripts/": {"schematic", "pcb"},
}


def get_changed_files(kicad_happy_dir, since="HEAD~1"):
    """Get list of changed files in kicad-happy repo."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", since],
            capture_output=True, text=True, cwd=str(kicad_happy_dir),
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def map_file_to_types(filepath):
    """Map a changed file path to affected analyzer types."""
    # Exact match first
    if filepath in FILE_TO_TYPES:
        return FILE_TO_TYPES[filepath]

    # Glob pattern match
    for pattern, types in GLOB_PATTERNS.items():
        if filepath.startswith(pattern):
            return types

    return set()


def get_changed_functions(kicad_happy_dir, filepath, since="HEAD~1"):
    """Extract function names that changed between since and HEAD.

    Uses Python AST to compare function signatures/bodies.
    Returns list of function names.
    """
    full_path = Path(kicad_happy_dir) / filepath
    if not full_path.exists() or not filepath.endswith(".py"):
        return []

    # Get old version
    try:
        result = subprocess.run(
            ["git", "show", f"{since}:{filepath}"],
            capture_output=True, text=True, cwd=str(kicad_happy_dir),
            timeout=10,
        )
        old_source = result.stdout if result.returncode == 0 else ""
    except Exception:
        old_source = ""

    new_source = full_path.read_text()

    old_funcs = _extract_functions(old_source)
    new_funcs = _extract_functions(new_source)

    changed = []
    # New or modified functions
    for name, body_hash in new_funcs.items():
        if name not in old_funcs:
            changed.append(name)
        elif old_funcs[name] != body_hash:
            changed.append(name)

    # Removed functions
    for name in old_funcs:
        if name not in new_funcs:
            changed.append(name)

    return changed


def _extract_functions(source):
    """Extract {function_name: body_hash} from Python source."""
    if not source.strip():
        return {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    funcs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_str = ast.dump(node)
            funcs[node.name] = hash(body_str)
    return funcs


def map_functions_to_detectors(filepath, function_names):
    """Map function names to signal detector types (for signal_detectors.py)."""
    detectors = []
    if "signal_detectors" not in filepath:
        return detectors

    for name in function_names:
        # detect_voltage_dividers -> voltage_dividers
        if name.startswith("detect_"):
            det = name[len("detect_"):]
            detectors.append(det)
        elif name.startswith("_"):
            # Helper functions — harder to map, flag as generic
            detectors.append(f"helper:{name}")

    return detectors


def recommend_actions(affected_types):
    """Generate recommended test actions for affected analyzer types."""
    actions = []
    for atype in sorted(affected_types):
        actions.append(f"Re-run {atype} analyzer: python3 run/run_{atype}.py --jobs 16")
        actions.append(f"Re-run {atype} assertions: python3 regression/run_checks.py --type {atype}")
        if atype in ("schematic", "pcb"):
            actions.append(f"Re-seed {atype} assertions: python3 regression/seed.py --all --type {atype}")
    if "schematic" in affected_types or "pcb" in affected_types:
        actions.append("Run cross-analyzer checks: python3 validate/cross_analyzer.py --summary")
    return actions


def main():
    parser = argparse.ArgumentParser(
        description="Detect upstream kicad-happy changes and recommend test actions")
    parser.add_argument("--since", default="HEAD~1",
                        help="Git ref to diff against (default: HEAD~1)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    kicad_happy = resolve_kicad_happy_dir()

    files = get_changed_files(kicad_happy, args.since)
    if not files:
        if args.json:
            json.dump({"changed_files": 0, "affected_types": [],
                       "actions": []}, sys.stdout, indent=2)
        else:
            print(f"No changes detected in {kicad_happy} since {args.since}")
        return

    # Analyze changes
    affected_types = set()
    file_details = []
    for filepath in files:
        types = map_file_to_types(filepath)
        affected_types |= types
        funcs = get_changed_functions(kicad_happy, filepath, args.since)
        detectors = map_functions_to_detectors(filepath, funcs)

        file_details.append({
            "file": filepath,
            "affected_types": sorted(types),
            "functions_changed": funcs[:20],
            "detectors": detectors,
        })

    actions = recommend_actions(affected_types)

    if args.json:
        json.dump({
            "since": args.since,
            "changed_files": len(files),
            "affected_types": sorted(affected_types),
            "files": file_details,
            "actions": actions,
        }, sys.stdout, indent=2)
        print()
        return

    # Text output
    print(f"kicad-happy changes since {args.since}:")
    print(f"{'='*60}")
    print(f"Changed files: {len(files)}")
    print(f"Affected analyzer types: {sorted(affected_types) or '(none)'}")
    print()

    for fd in file_details:
        types_str = ", ".join(fd["affected_types"]) if fd["affected_types"] else "(no test impact)"
        print(f"  {fd['file']} -> {types_str}")
        if fd["functions_changed"]:
            print(f"    Functions: {', '.join(fd['functions_changed'][:5])}")
            if len(fd["functions_changed"]) > 5:
                print(f"    ... and {len(fd['functions_changed']) - 5} more")
        if fd["detectors"]:
            print(f"    Detectors: {', '.join(fd['detectors'])}")

    if actions:
        print(f"\nRecommended actions:")
        for a in actions:
            print(f"  $ {a}")


if __name__ == "__main__":
    main()
