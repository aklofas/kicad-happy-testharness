#!/usr/bin/env python3
"""Equation tracking and verification for kicad-happy analyzer scripts.

Scans Python source files for `# EQ-NNN:` tagged equations, tracks them in a
registry with verification status and source citations, and detects untagged
functions that likely contain engineering formulas.

Unlike constants (detectable via AST patterns), equations are ordinary Python
expressions. This tool uses two detection methods:
  1. Structured `# EQ-NNN:` comment tags placed by developers
  2. Heuristic detection of math-heavy functions without EQ tags

Commands:
  scan [--diff]                 Scan sources, update registry
  list [--unverified|--file F]  List tracked equations
  show EQ-NNN                   Detail view for one equation
  verify EQ-NNN --source "..."  Mark equation as verified
  render                        Generate equation_registry.md
  untagged                      Find functions with math but no EQ tag

Usage:
    python3 validate/audit_equations.py scan
    python3 validate/audit_equations.py scan --diff
    python3 validate/audit_equations.py list --unverified
    python3 validate/audit_equations.py untagged
    python3 validate/audit_equations.py verify EQ-001 --source "Ott Eq. 6.4"
    python3 validate/audit_equations.py render
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR, resolve_kicad_happy_dir

REGISTRY_PATH = DATA_DIR / "equation_registry.json"
MARKDOWN_PATH = DATA_DIR / "equation_registry.md"

# Source files to scan (relative to skills/ subdirectory)
SCAN_FILES = {
    "kicad/scripts": [
        "analyze_schematic.py",
        "analyze_pcb.py",
        "signal_detectors.py",
        "kicad_utils.py",
    ],
    "spice/scripts": [
        "extract_parasitics.py",
        "spice_templates.py",
        "spice_models.py",
        "spice_model_generator.py",
        "spice_results.py",
        "spice_part_library.py",
    ],
    "emc/scripts": [
        "emc_formulas.py",
        "emc_rules.py",
        "analyze_emc.py",
    ],
}

# Heuristic indicators that a function contains engineering math
MATH_INDICATORS = frozenset({
    "math.sqrt", "math.log", "math.log10", "math.pi", "math.sin",
    "math.cos", "math.atan2", "math.exp", "**2", "**0.5",
    "2*math.pi", "2.0*math.pi", "1e-", "2e-",
})

# EQ tag pattern: # EQ-NNN: <formula description>
EQ_TAG_RE = re.compile(r"#\s*EQ-(\d{3}):\s*(.+)")
# Source citation pattern: # Source: <reference>
SOURCE_RE = re.compile(r"#\s*Source:\s*(.+)")

# Impact classification by category
IMPACT_BY_CATEGORY = {
    "emc_radiation": "critical",
    "impedance": "high",
    "filter_design": "high",
    "parasitic": "high",
    "signal_integrity": "medium",
    "opamp": "medium",
    "spice_model": "medium",
    "thermal": "medium",
    "geometry": "low",
    "unit_conversion": "low",
}


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def _hash_function_body(source, func_node):
    """Hash the AST of a function body for change detection."""
    body = ast.dump(func_node, annotate_fields=False)
    return "sha256:" + hashlib.sha256(body.encode()).hexdigest()[:16]


def _find_enclosing_function(tree, line):
    """Find the function definition enclosing a given line number."""
    best = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end = getattr(node, "end_lineno", node.lineno + 100)
            if node.lineno <= line <= end:
                if best is None or node.lineno > best.lineno:
                    best = node
    return best


def scan_file(filepath, source_text=None):
    """Scan a file for EQ-NNN tags and extract equation metadata.

    Returns list of equation info dicts.
    """
    if source_text is None:
        source_text = filepath.read_text()

    lines = source_text.splitlines()
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return []

    equations = []
    filename = filepath.name

    for i, line in enumerate(lines):
        m = EQ_TAG_RE.search(line)
        if not m:
            continue

        eq_num = int(m.group(1))
        eq_id = f"EQ-{eq_num:03d}"
        formula = m.group(2).strip()
        lineno = i + 1  # 1-indexed

        # Collect source citations from subsequent lines
        sources = []
        for j in range(i + 1, min(i + 10, len(lines))):
            sm = SOURCE_RE.search(lines[j])
            if sm:
                sources.append(sm.group(1).strip())
            elif not lines[j].strip().startswith("#"):
                break  # Stop at first non-comment line

        # Find enclosing function
        func_node = _find_enclosing_function(tree, lineno)
        func_name = func_node.name if func_node else None
        func_hash = _hash_function_body(source_text, func_node) if func_node else None

        equations.append({
            "id": eq_id,
            "formula": formula,
            "file": filename,
            "line": lineno,
            "function": func_name,
            "sources": sources,
            "content_hash": func_hash,
        })

    return equations


def find_untagged(filepath, source_text=None):
    """Find functions with math operations but no EQ-NNN tag.

    Returns list of (function_name, line, math_op_count, indicators_found).
    """
    if source_text is None:
        source_text = filepath.read_text()

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return []

    # Find all EQ-tagged lines
    tagged_functions = set()
    for i, line in enumerate(source_text.splitlines()):
        if EQ_TAG_RE.search(line):
            func = _find_enclosing_function(tree, i + 1)
            if func:
                tagged_functions.add(func.name)

    untagged = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name in tagged_functions:
            continue
        if node.name.startswith("_") and node.name not in (
            "_microstrip_impedance", "_arc_length_3pt", "_shoelace_area",
            "_cap_impedance", "_estimate_dc_bias_derating",
        ):
            # Skip most private helpers unless known formula functions
            pass

        # Get function source
        try:
            func_src = ast.get_source_segment(source_text, node)
        except Exception:
            func_src = None
        if not func_src:
            continue

        indicators = [ind for ind in MATH_INDICATORS if ind in func_src]
        if len(indicators) >= 1:
            untagged.append({
                "function": node.name,
                "file": filepath.name,
                "line": node.lineno,
                "math_ops": len(indicators),
                "indicators": indicators,
            })

    return untagged


def scan_all():
    """Scan all configured source files. Returns (tagged, untagged)."""
    kicad_happy = resolve_kicad_happy_dir()
    skills_dir = kicad_happy / "skills"

    all_tagged = []
    all_untagged = []

    for subdir, filenames in SCAN_FILES.items():
        base = skills_dir / subdir
        if not base.exists():
            continue
        for fname in filenames:
            fpath = base / fname
            if not fpath.exists():
                print(f"  Skipping {subdir}/{fname} (not found)", file=sys.stderr)
                continue
            source = fpath.read_text()
            tagged = scan_file(fpath, source)
            untagged = find_untagged(fpath, source)
            all_tagged.extend(tagged)
            all_untagged.extend(untagged)
            tag_count = len(tagged)
            untag_count = len(untagged)
            label = f"{subdir.split('/')[0]}/{fname}"
            print(f"  {label}: {tag_count} tagged, {untag_count} untagged")

    return all_tagged, all_untagged


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def load_registry():
    """Load equation registry from JSON file."""
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {"version": 1, "last_scan": None, "equations": []}


def save_registry(registry):
    """Save equation registry to JSON file."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def update_registry(registry, scanned):
    """Update registry with scanned equations. Returns (added, updated, removed)."""
    old_by_id = {eq["id"]: eq for eq in registry["equations"]}
    new_by_id = {eq["id"]: eq for eq in scanned}

    added = 0
    updated = 0
    removed = 0

    # Update existing and add new
    merged = []
    for eq in scanned:
        eid = eq["id"]
        if eid in old_by_id:
            old = old_by_id[eid]
            # Check if function body changed
            if eq.get("content_hash") and old.get("content_hash"):
                if eq["content_hash"] != old["content_hash"]:
                    if old.get("status") == "verified":
                        old["status"] = "stale"
                    updated += 1
            # Update location info
            old["file"] = eq["file"]
            old["line"] = eq["line"]
            old["function"] = eq["function"]
            old["formula"] = eq["formula"]
            old["content_hash"] = eq.get("content_hash")
            if eq["sources"]:
                old["sources"] = eq["sources"]
            merged.append(old)
        else:
            # New equation
            new_eq = {
                "id": eid,
                "formula": eq["formula"],
                "file": eq["file"],
                "line": eq["line"],
                "function": eq["function"],
                "sources": eq["sources"],
                "content_hash": eq.get("content_hash"),
                "status": "unverified",
                "category": _classify_category(eq),
                "impact": IMPACT_BY_CATEGORY.get(
                    _classify_category(eq), "medium"),
                "verification_source": None,
                "notes": None,
            }
            merged.append(new_eq)
            added += 1

    # Detect removed equations
    new_ids = set(new_by_id.keys())
    for eid in old_by_id:
        if eid not in new_ids:
            removed += 1

    registry["equations"] = sorted(merged, key=lambda e: e["id"])
    registry["last_scan"] = datetime.now(timezone.utc).isoformat()
    return added, updated, removed


def _classify_category(eq):
    """Auto-classify equation category from file and function name."""
    fname = eq.get("file", "")
    func = eq.get("function", "") or ""
    formula = eq.get("formula", "").lower()

    if "emc_formulas" in fname or "emc_rules" in fname:
        if any(kw in formula for kw in ("radiation", "e =", "e=", "dbuv")):
            return "emc_radiation"
        if any(kw in formula for kw in ("harmonic", "sinc", "trapezoidal")):
            return "emc_radiation"
        if any(kw in formula for kw in ("cavity", "resonan", "slot")):
            return "emc_radiation"
        if any(kw in formula for kw in ("impedance", "z =", "z=", "srf", "esr")):
            return "impedance"
        if any(kw in formula for kw in ("propagation", "skew", "bandwidth", "wavelength", "lambda")):
            return "signal_integrity"
        if any(kw in formula for kw in ("inductance", "capacitance", "resistance", "trace", "via")):
            return "parasitic"
        if any(kw in formula for kw in ("derating", "thermal", "ferrite")):
            return "thermal"
        if any(kw in formula for kw in ("filter", "cutoff", "ratio")):
            return "filter_design"
        if any(kw in formula for kw in ("crosstalk", "3h", "spacing")):
            return "signal_integrity"
    if "extract_parasitics" in fname:
        return "parasitic"
    if "spice_" in fname:
        return "spice_model"
    if "signal_detectors" in fname:
        if "opamp" in func:
            return "opamp"
        if "rc_filter" in func or "lc_filter" in func:
            return "filter_design"
        return "filter_design"
    if "analyze_pcb" in fname:
        if "impedance" in func:
            return "impedance"
        if "thermal" in func:
            return "thermal"
        return "geometry"
    if "analyze_schematic" in fname:
        if "pdn" in func:
            return "impedance"
        return "filter_design"
    return "unknown"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_scan(args):
    """Scan sources for EQ tags, update registry."""
    print("Scanning for equation tags...", file=sys.stderr)
    tagged, untagged = scan_all()

    registry = load_registry()
    old_count = len(registry["equations"])
    added, updated, removed = update_registry(registry, tagged)
    save_registry(registry)

    print(f"\nRegistry updated: {added} added, {updated} updated, {removed} removed",
          file=sys.stderr)
    print(f"Total tagged equations: {len(tagged)}", file=sys.stderr)
    print(f"Untagged math functions: {len(untagged)}", file=sys.stderr)
    print(f"Registry entries: {len(registry['equations'])}", file=sys.stderr)

    if args.diff:
        old_ids = {eq["id"] for eq in registry["equations"]}
        print("\n--- Changes ---", file=sys.stderr)
        for eq in tagged:
            if eq["id"] not in {e["id"] for e in load_registry()["equations"]
                                 if e.get("content_hash") == eq.get("content_hash")}:
                print(f"  + {eq['file']}:{eq['function']} ({eq['id']})", file=sys.stderr)


def cmd_list(args):
    """List tracked equations."""
    registry = load_registry()
    equations = registry.get("equations", [])

    if args.unverified:
        equations = [e for e in equations if e.get("status") != "verified"]
    if args.file:
        equations = [e for e in equations if e.get("file") == args.file]
    if args.category:
        equations = [e for e in equations if e.get("category") == args.category]

    if not equations:
        print("No matching equations.")
        return

    print(f"{'ID':<8s} {'File':<25s} {'Function':<35s} {'Category':<20s} "
          f"{'Impact':<10s} {'Status':<12s}")
    print("-" * 110)
    for eq in equations:
        print(f"{eq['id']:<8s} {eq.get('file',''):<25s} "
              f"{(eq.get('function') or '?'):<35s} "
              f"{eq.get('category','?'):<20s} "
              f"{eq.get('impact','?'):<10s} {eq.get('status','?'):<12s}")
    print(f"\n{len(equations)} equations")


def cmd_show(args):
    """Show details for one equation."""
    registry = load_registry()
    eq = next((e for e in registry["equations"] if e["id"] == args.eq_id), None)
    if not eq:
        print(f"Equation {args.eq_id} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"ID:       {eq['id']}")
    print(f"Formula:  {eq.get('formula', '?')}")
    print(f"File:     {eq.get('file', '?')}:{eq.get('line', '?')}")
    print(f"Function: {eq.get('function', '?')}")
    print(f"Category: {eq.get('category', '?')}")
    print(f"Impact:   {eq.get('impact', '?')}")
    print(f"Status:   {eq.get('status', '?')}")
    print(f"Hash:     {eq.get('content_hash', '?')}")
    if eq.get("sources"):
        print(f"Sources:")
        for s in eq["sources"]:
            print(f"  - {s}")
    if eq.get("verification_source"):
        print(f"Verified: {eq['verification_source']}")
    if eq.get("notes"):
        print(f"Notes:    {eq['notes']}")


def cmd_verify(args):
    """Mark an equation as verified with a source citation."""
    registry = load_registry()
    eq = next((e for e in registry["equations"] if e["id"] == args.eq_id), None)
    if not eq:
        print(f"Equation {args.eq_id} not found.", file=sys.stderr)
        sys.exit(1)

    eq["status"] = "verified"
    eq["verification_source"] = args.source
    save_registry(registry)
    print(f"Verified {args.eq_id}: {eq.get('function', '?')}")


def cmd_render(args):
    """Generate equation_registry.md from JSON registry."""
    registry = load_registry()
    equations = registry.get("equations", [])

    lines = [
        "# Equation Registry",
        "",
        "Auto-generated from `equation_registry.json` — do not edit manually.",
        "",
        f"**Last scan:** {registry.get('last_scan', 'never')}",
        "",
    ]

    # Summary
    total = len(equations)
    verified = sum(1 for e in equations if e.get("status") == "verified")
    unverified = sum(1 for e in equations if e.get("status") == "unverified")
    stale = sum(1 for e in equations if e.get("status") == "stale")

    by_impact = {}
    for e in equations:
        imp = e.get("impact", "unknown")
        by_impact[imp] = by_impact.get(imp, 0) + 1

    lines.extend([
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Total equations | {total} |",
        f"| Verified | {verified} |",
        f"| Unverified | {unverified} |",
        f"| Stale | {stale} |",
    ])
    for imp in ("critical", "high", "medium", "low"):
        if imp in by_impact:
            lines.append(f"| {imp.title()} impact | {by_impact[imp]} |")
    lines.append("")

    # Group by file
    by_file = {}
    for eq in equations:
        f = eq.get("file", "unknown")
        by_file.setdefault(f, []).append(eq)

    for fname, eqs in sorted(by_file.items()):
        lines.extend([
            f"## {fname}",
            "",
            "| ID | Function | Formula | Category | Impact | Status |",
            "|---|---|---|---|---|---|",
        ])
        for eq in eqs:
            formula = eq.get("formula", "?").replace("|", "\\|")
            func = eq.get("function", "?")
            lines.append(
                f"| {eq['id']} | `{func}` | {formula} | "
                f"{eq.get('category', '?')} | {eq.get('impact', '?')} | "
                f"**{eq.get('status', '?')}** |"
            )
        lines.append("")

    MARKDOWN_PATH.write_text("\n".join(lines))
    print(f"Rendered {MARKDOWN_PATH} ({total} equations)")


def cmd_untagged(args):
    """Find functions with math operations but no EQ tag."""
    print("Scanning for untagged math functions...", file=sys.stderr)
    _, untagged = scan_all()

    if not untagged:
        print("\nNo untagged math functions found.")
        return

    print(f"\n{'File':<30s} {'Function':<40s} {'Line':>6s} {'Math ops':>8s}")
    print("-" * 90)
    for u in sorted(untagged, key=lambda x: (x["file"], x["line"])):
        indicators = ", ".join(u["indicators"][:3])
        print(f"{u['file']:<30s} {u['function']:<40s} {u['line']:>6d} "
              f"{u['math_ops']:>8d}  ({indicators})")
    print(f"\n{len(untagged)} untagged functions")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Equation tracking and verification for kicad-happy")
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Scan sources for EQ tags")
    p_scan.add_argument("--diff", action="store_true", help="Show changes")

    p_list = sub.add_parser("list", help="List tracked equations")
    p_list.add_argument("--unverified", action="store_true")
    p_list.add_argument("--file", help="Filter by filename")
    p_list.add_argument("--category", help="Filter by category")

    p_show = sub.add_parser("show", help="Show one equation")
    p_show.add_argument("eq_id", help="Equation ID (e.g., EQ-001)")

    p_verify = sub.add_parser("verify", help="Verify an equation")
    p_verify.add_argument("eq_id", help="Equation ID")
    p_verify.add_argument("--source", required=True, help="Verification source")

    p_render = sub.add_parser("render", help="Generate equation_registry.md")

    p_untag = sub.add_parser("untagged", help="Find untagged math functions")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "scan": cmd_scan,
        "list": cmd_list,
        "show": cmd_show,
        "verify": cmd_verify,
        "render": cmd_render,
        "untagged": cmd_untagged,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
