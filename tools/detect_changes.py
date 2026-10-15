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
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
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
    "skills/kicad/scripts/analyze_thermal.py": {"thermal"},
}

# Glob patterns for broader matching
GLOB_PATTERNS = {
    "skills/emc/": {"emc"},
    "skills/spice/": {"spice"},
    "skills/kicad/scripts/": {"schematic", "pcb"},
}


def get_changed_files(kicad_happy_dir, since="HEAD~1"):
    """Changed files in kicad-happy since `since`. Returns None when git fails
    (not a repo, unknown ref, shallow clone) - callers must treat None as a
    diagnostic failure, never as 'no changes' (report B12)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", since],
            capture_output=True, text=True, cwd=str(kicad_happy_dir), timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"error: git diff failed in {kicad_happy_dir}: {e}", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"error: git diff --name-only {since} failed in {kicad_happy_dir}: "
              f"{result.stderr.strip()}", file=sys.stderr)
        return None
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


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

    new_source = full_path.read_text(encoding="utf-8")

    old_funcs = _extract_functions(old_source)
    new_funcs = _extract_functions(new_source)
    if new_funcs is None:
        return None
    if old_funcs is None:
        old_funcs = {}

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
    """{function_name: body_hash}; {} for empty source; None on SyntaxError."""
    if not source.strip():
        return {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    funcs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs[node.name] = hashlib.sha256(ast.dump(node).encode()).hexdigest()[:16]
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


# Entry points the harness invokes directly, and the analyzer types each one
# evidences. cross_analysis consumes schematic+pcb outputs; thermal was an
# empty exact entry before (report A2); datasheets had none.
ENTRY_POINTS = {
    "skills/kicad/scripts/analyze_schematic.py": {"schematic"},
    "skills/kicad/scripts/analyze_pcb.py": {"pcb"},
    "skills/kicad/scripts/analyze_gerbers.py": {"gerber"},
    "skills/kicad/scripts/analyze_thermal.py": {"thermal"},
    "skills/kicad/scripts/cross_analysis.py": {"schematic", "pcb"},
    "skills/emc/scripts/analyze_emc.py": {"emc"},
    "skills/spice/scripts/simulate_subcircuits.py": {"spice"},
    "skills/datasheets/scripts/datasheet_lookup.py": {"datasheets"},
    "skills/digikey/scripts/sync_datasheets_digikey.py": {"datasheets"},
}


def build_module_index(kicad_happy_dir):
    """Dotted module name -> root-relative path, package-qualified (report A2).

    A file skills/<skill>/scripts/a/b.py is importable as 'a.b' from any script
    in that skill (scripts/ is on sys.path), and 'a' maps to a/__init__.py.
    Sibling packages beside scripts/ (skills/datasheets/datasheet_types) are
    indexed by their package name too.
    """
    root = Path(kicad_happy_dir)
    index = {}
    for skill_dir in sorted((root / "skills").glob("*")):
        if not skill_dir.is_dir():
            continue
        roots = [skill_dir / "scripts", skill_dir]
        for base in roots:
            if not base.is_dir():
                continue
            for py in sorted(base.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                relp = py.relative_to(root).as_posix()
                parts = py.relative_to(base).with_suffix("").parts
                if parts[-1] == "__init__":
                    parts = parts[:-1]
                if not parts:
                    continue
                if base == skill_dir and parts[0] == "scripts":
                    continue   # scripts/ files were indexed under the scripts base
                index.setdefault(".".join(parts), relp)
    return index


def resolve_import(importer_rel, node, index):
    """Root-relative paths an Import/ImportFrom node resolves to inside the tree."""
    out = set()
    if isinstance(node, ast.Import):
        for alias in node.names:
            name = alias.name
            while name:
                if name in index:
                    out.add(index[name])
                    break
                name = name.rpartition(".")[0]
        return out
    if not isinstance(node, ast.ImportFrom):
        return out
    if node.level == 0:
        base = node.module or ""
    else:
        pkg_parts = Path(importer_rel).with_suffix("").parts
        # drop the file name, then (level-1) more packages
        pkg_parts = pkg_parts[:-1]
        if pkg_parts and pkg_parts[-1] == "__init__":
            pkg_parts = pkg_parts[:-1]
        cut = node.level - 1
        pkg_parts = pkg_parts[:len(pkg_parts) - cut] if cut else pkg_parts
        # strip the skills/<skill>/scripts prefix to get the dotted package
        dotted = []
        for p in reversed(pkg_parts):
            if p == "scripts":
                break
            dotted.append(p)
        dotted.reverse()
        base = ".".join(dotted + ([node.module] if node.module else []))
    candidates = [base] + [f"{base}.{a.name}" if base else a.name for a in node.names]
    for cand in candidates:
        if cand in index:
            out.add(index[cand])
    return out


def _build_dependency_graph(kicad_happy_dir):
    """{file_relpath: set(imported_relpaths)} over the package-qualified index."""
    root = Path(kicad_happy_dir)
    index = build_module_index(root)
    graph = {}
    for relp in sorted(set(index.values())):
        try:
            tree = ast.parse((root / relp).read_bytes())
        except (OSError, SyntaxError):
            graph[relp] = set()
            continue
        deps = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                deps |= resolve_import(relp, node, index)
        deps.discard(relp)
        graph[relp] = deps
    return graph


def _compute_impact_map(graph, entry_points):
    """Compute transitive closure: for each entry point, find all reachable files.

    Returns {relpath: set(analyzer_types)}.
    """
    impact = {}  # relpath -> set of types

    for ep_path, atype in entry_points.items():
        if ep_path not in graph:
            continue
        # BFS from entry point
        visited = set()
        queue = [ep_path]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for dep in graph.get(current, set()):
                if dep not in visited:
                    queue.append(dep)
        # All visited files are affected by this analyzer type
        for f in visited:
            impact.setdefault(f, set()).update(atype if isinstance(atype, set) else {atype})

    return impact


def cmd_generate_map(args):
    """Generate the file-to-types impact map from import analysis."""
    kicad_happy = resolve_kicad_happy_dir()
    graph = _build_dependency_graph(kicad_happy)

    if not graph:
        print(f"No Python files found under {kicad_happy}/skills/", file=sys.stderr)
        sys.exit(1)

    impact = _compute_impact_map(graph, ENTRY_POINTS)

    # Compare with hand-maintained map
    divergences = []
    for filepath, hand_types in FILE_TO_TYPES.items():
        auto_types = impact.get(filepath, set())
        if hand_types and not auto_types:
            divergences.append(("missing_from_auto", filepath, hand_types))
        elif auto_types != hand_types and hand_types:
            divergences.append(("differs", filepath, hand_types, auto_types))

    # Files not reachable from any entry point
    all_files = set(graph.keys())
    reachable = set(impact.keys())
    unreachable = sorted(all_files - reachable)

    if args.json:
        json.dump({
            "entry_points": {k: sorted(v) for k, v in ENTRY_POINTS.items()},
            "total_files": len(all_files),
            "reachable_files": len(reachable),
            "unreachable_files": len(unreachable),
            "impact_map": {k: sorted(v) for k, v in sorted(impact.items())},
            "divergences": [
                {"type": d[0], "file": d[1],
                 "hand": sorted(d[2]) if len(d) > 2 else [],
                 "auto": sorted(d[3]) if len(d) > 3 else []}
                for d in divergences
            ],
            "unreachable": unreachable,
        }, sys.stdout, indent=2)
        print()
        return

    print(f"Impact map generated from import analysis")
    print(f"{'='*60}")
    print(f"Entry points: {len(ENTRY_POINTS)}")
    print(f"Python files found: {len(all_files)}")
    print(f"Reachable from entry points: {len(reachable)}")
    print(f"Unreachable: {len(unreachable)}")
    print()

    # Print map grouped by type
    by_type = {}
    for filepath, types in sorted(impact.items()):
        key = ",".join(sorted(types))
        by_type.setdefault(key, []).append(filepath)

    for types_str, files in sorted(by_type.items()):
        print(f"  [{types_str}]")
        for f in sorted(files):
            marker = " *" if f in FILE_TO_TYPES else ""
            print(f"    {f}{marker}")
        print()

    if divergences:
        print(f"Divergences from hand-maintained map ({len(divergences)}):")
        for d in divergences:
            if d[0] == "missing_from_auto":
                print(f"  MISS: {d[1]} (hand={sorted(d[2])}, not reachable via imports)")
            elif d[0] == "differs":
                print(f"  DIFF: {d[1]} (hand={sorted(d[2])}, auto={sorted(d[3])})")
        print()

    if unreachable:
        print(f"Unreachable files (not imported by any entry point):")
        for f in unreachable:
            print(f"  {f}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect upstream kicad-happy changes and recommend test actions")
    sub = parser.add_subparsers(dest="command")

    # Default behavior (no subcommand) = detect changes
    parser.add_argument("--since", default="HEAD~1",
                        help="Git ref to diff against (default: HEAD~1)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    gen_p = sub.add_parser("generate-map",
                           help="Generate impact map from import analysis")
    gen_p.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if args.command == "generate-map":
        cmd_generate_map(args)
        return 0

    kicad_happy = resolve_kicad_happy_dir()

    files = get_changed_files(kicad_happy, args.since)
    if files is None:
        return 2
    if not files:
        if args.json:
            json.dump({"changed_files": 0, "affected_types": [],
                       "actions": []}, sys.stdout, indent=2)
        else:
            print(f"No changes detected in {kicad_happy} since {args.since}")
        return 0

    graph = _build_dependency_graph(kicad_happy)
    impact = _compute_impact_map(graph, ENTRY_POINTS)

    # Analyze changes
    affected_types = set()
    file_details = []
    for filepath in files:
        types = set(impact.get(filepath, set())) or set(map_file_to_types(filepath))
        funcs = get_changed_functions(kicad_happy, filepath, args.since)
        parse_incomplete = funcs is None
        if parse_incomplete:
            parts = filepath.split("/")
            same_skill = {t for ep, ts in ENTRY_POINTS.items()
                          if ep.split("/")[1:2] == parts[1:2] for t in ts}
            types = same_skill or types
            funcs = []
        affected_types |= types
        detectors = map_functions_to_detectors(filepath, funcs)

        file_details.append({
            "file": filepath,
            "affected_types": sorted(types),
            "functions_changed": funcs[:20],
            "detectors": detectors,
            "parse_incomplete": parse_incomplete,
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
        return 0

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
        if fd["parse_incomplete"]:
            print("    (parse incomplete: SyntaxError; types widened to the whole skill)")

    if actions:
        print(f"\nRecommended actions:")
        for a in actions:
            print(f"  $ {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
