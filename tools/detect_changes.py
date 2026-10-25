#!/usr/bin/env python3
"""Upstream change detection for kicad-happy.

Diffs the kicad-happy repo to determine which analyzer scripts changed,
maps changes to affected analyzer types, and recommends test actions.

Usage:
    python3 detect_changes.py                    # Diff HEAD vs HEAD~1
    python3 detect_changes.py --since HEAD~5     # Diff against older commit
    python3 detect_changes.py --json

Exit codes (change detection, the default command):
    0  report complete
    1  report emitted but parse incomplete: a changed .py file has a
       SyntaxError, so its affected_types are widened to every ENTRY_POINTS
       type (never narrower than the import-graph result)
    2  usage or git failure (product dir missing, not a repo, bad ref); with
       --json, stdout still carries {"error": ..., "affected_types": <all>}
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
    # kicad_core is imported by every analyzer family (emc/spice/thermal/cross included),
    # so a change there is in scope for all of them; must precede the broader scripts glob.
    "skills/kicad/scripts/kicad_core/": {"schematic", "pcb", "gerber", "spice", "emc", "thermal"},
    "skills/emc/": {"emc"},
    "skills/datasheets/": {"datasheets"},
    "skills/spice/": {"spice"},
    "skills/kicad/scripts/": {"schematic", "pcb"},
}


def _changed_files(kicad_happy_dir, since):
    """(files, None) on success, (None, error message) when git fails."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", since],
            capture_output=True, text=True, cwd=str(kicad_happy_dir), timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"git diff failed in {kicad_happy_dir}: {e}"
    if result.returncode != 0:
        return None, (f"git diff --name-only {since} failed in {kicad_happy_dir}: "
                      f"{result.stderr.strip()}")
    return [f.strip() for f in result.stdout.splitlines() if f.strip()], None


def get_changed_files(kicad_happy_dir, since="HEAD~1"):
    """Changed files in kicad-happy since `since`. Returns None when git fails
    (not a repo, unknown ref, shallow clone) - callers must treat None as a
    diagnostic failure, never as 'no changes' (report B12)."""
    files, err = _changed_files(kicad_happy_dir, since)
    if err:
        print(f"error: {err}", file=sys.stderr)
    return files


def all_entry_point_types():
    """Every analyzer type any entry point evidences: the conservative scope."""
    return {t for ts in ENTRY_POINTS.values() for t in ts}


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


def affected_types_for(filepath, impact):
    """The import graph's impact UNION the explicit path rules: a non-empty graph result must
    not shadow a broader rule (kicad_core/ is in scope for every family even when the graph
    reaches it from only some entry points)."""
    return set(impact.get(filepath, set())) | set(map_file_to_types(filepath))


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
    "skills/datasheets/datasheet_types/cache_reader.py": {"datasheets"},
    "skills/digikey/scripts/sync_datasheets_digikey.py": {"datasheets"},
}


def _index_base(relp):
    """Path parts of the import root for a root-relative file path: the
    skills/<skill>/scripts dir when the file lives under it, else skills/<skill>."""
    parts = Path(relp).parts
    if len(parts) >= 3 and parts[0] == "skills":
        if len(parts) > 3 and parts[2] == "scripts":
            return parts[:3]
        return parts[:2]
    return ()


def _discover_modules(kicad_happy_dir):
    """[(dotted_name, root_relative_path)] for EVERY .py under skills/."""
    root = Path(kicad_happy_dir)
    found = []
    for skill_dir in sorted((root / "skills").glob("*")):
        if not skill_dir.is_dir():
            continue
        for base in (skill_dir / "scripts", skill_dir):
            if not base.is_dir():
                continue
            for py in sorted(base.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                relp = py.relative_to(root).as_posix()
                if Path(*_index_base(relp)) != base.relative_to(root):
                    continue   # scripts/ files are indexed under the scripts base only
                parts = py.relative_to(base).with_suffix("").parts
                if parts[-1] == "__init__":
                    parts = parts[:-1]
                if parts:
                    found.append((".".join(parts), relp))
    return found


def build_module_index(kicad_happy_dir):
    """Dotted module name -> root-relative path, package-qualified (report A2).

    A file skills/<skill>/scripts/a/b.py is importable as 'a.b' from any script
    in that skill (scripts/ is on sys.path), and 'a' maps to a/__init__.py.
    Sibling packages beside scripts/ (skills/datasheets/datasheet_types) are
    indexed by their package name too. Name collisions keep the first path and
    warn on stderr naming both.
    """
    index = {}
    for name, relp in _discover_modules(kicad_happy_dir):
        if name in index and index[name] != relp:
            print(f"warning: module name '{name}' is ambiguous: {index[name]} "
                  f"shadows {relp}", file=sys.stderr)
            continue
        index[name] = relp
    return index


def resolve_import(importer_rel, node, index):
    """Root-relative paths an Import/ImportFrom node resolves to inside the tree.

    Importing `a.b.c` executes `a/__init__.py` and `a/b/__init__.py` first, so
    every indexed ancestor package `__init__.py` of a resolved name is an edge
    too (spec §4.2).
    """
    out = set()

    def walk_up(name):
        while name:
            if name in index:
                return index[name]
            name = name.rpartition(".")[0]
        return None

    def ancestors(name):
        parts = name.split(".")
        for i in range(1, len(parts)):
            hit = index.get(".".join(parts[:i]))
            if hit and hit.endswith("/__init__.py"):
                out.add(hit)

    if isinstance(node, ast.Import):
        for alias in node.names:
            hit = walk_up(alias.name)
            if hit:
                out.add(hit)
                ancestors(alias.name)
        return out
    if not isinstance(node, ast.ImportFrom):
        return out
    if node.level == 0:
        base = node.module or ""
    else:
        base_parts = _index_base(importer_rel)
        # package of the importer, relative to its import root (filename dropped)
        pkg = list(Path(importer_rel).parts[len(base_parts):-1])
        cut = node.level - 1
        if cut > len(pkg):
            return out   # relative import above the import root
        pkg = pkg[:len(pkg) - cut]
        base = ".".join(pkg + ([node.module] if node.module else []))
    for a in node.names:
        cand = f"{base}.{a.name}" if base else a.name
        if cand in index:
            out.add(index[cand])
    hit = walk_up(base)
    if hit:
        out.add(hit)
        ancestors(base)
    return out


def _build_dependency_graph(kicad_happy_dir):
    """{file_relpath: set(imported_relpaths)} over the package-qualified index."""
    root = Path(kicad_happy_dir)
    index = build_module_index(root)
    graph = {}
    for relp in sorted({r for _, r in _discover_modules(root)}):
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

    def fail(msg):
        print(f"error: {msg}", file=sys.stderr)
        if args.json:
            json.dump({"error": msg, "affected_types": sorted(all_entry_point_types())},
                      sys.stdout, indent=2)
            print()
        return 2

    try:
        kicad_happy = resolve_kicad_happy_dir()
    except SystemExit:
        return fail("cannot resolve the product dir (KICAD_HAPPY_DIR)")

    files, err = _changed_files(kicad_happy, args.since)
    if files is None:
        return fail(err)
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
        types = affected_types_for(filepath, impact)
        funcs = get_changed_functions(kicad_happy, filepath, args.since)
        parse_incomplete = funcs is None
        if parse_incomplete:
            types = types | all_entry_point_types()   # conservative: all affected
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
    any_incomplete = any(fd["parse_incomplete"] for fd in file_details)
    rc = 1 if any_incomplete else 0

    actions = recommend_actions(affected_types)

    if args.json:
        json.dump({
            "since": args.since,
            "changed_files": len(files),
            "affected_types": sorted(affected_types),
            "files": file_details,
            "actions": actions,
            "parse_incomplete": any_incomplete,
        }, sys.stdout, indent=2)
        print()
        return rc

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
            print("    (parse incomplete: SyntaxError; types widened to every analyzer type)")

    if actions:
        print(f"\nRecommended actions:")
        for a in actions:
            print(f"  $ {a}")
    if any_incomplete:
        print("\nPARSE INCOMPLETE: exit 1 (scope widened to all affected)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
