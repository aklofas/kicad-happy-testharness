#!/usr/bin/env python3
"""Audit bugfix_registry.json paths against actual outputs.

For each registry entry, simulates the find_output_file() logic and reports
whether the assertion would match an output file at runtime.

Usage:
    python3 regression/audit_bugfix_paths.py           # Report mismatches
    python3 regression/audit_bugfix_paths.py --fix     # Fix registry (writes backup)
    python3 regression/audit_bugfix_paths.py --json    # JSON report
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checks import load_assertions, load_project_metadata
from run_checks import find_output_file
from utils import OUTPUTS_DIR, DATA_DIR, project_prefix, discover_projects

REGISTRY_FILE = Path(__file__).resolve().parent / "bugfix_registry.json"


def _resolve_project_path(repo, project_name):
    """Resolve project_path the same way load_assertions does."""
    pp = load_project_metadata(repo, project_name).get("project_path")
    if pp is not None:
        return pp
    try:
        for p in discover_projects(repo):
            if p["name"] == project_name:
                return p["path"]
    except (ImportError, OSError):
        pass
    return None


def _list_outputs(repo, atype):
    """List all output JSON files for a repo/type."""
    type_dir = OUTPUTS_DIR / atype / repo
    if not type_dir.exists():
        return []
    return sorted(f.name for f in type_dir.glob("*.json"))


def _suggest_correction(repo, project_name, source_file, atype):
    """Suggest corrected project + source_file based on actual outputs."""
    outputs = _list_outputs(repo, atype)
    if not outputs:
        return None

    # Try each discovered project to see if any yields a match
    try:
        projects = discover_projects(repo)
    except (ImportError, OSError):
        projects = []

    # Also try projects from reference/ directory
    repo_dir = DATA_DIR / repo
    if repo_dir.exists():
        ref_projects = [d.name for d in repo_dir.iterdir() if d.is_dir()]
    else:
        ref_projects = []

    # For each project, check if prepending its prefix to source_file matches an output
    candidates = []
    for proj in projects:
        prefix = project_prefix(proj["path"])
        safe_sf = source_file.replace("/", "_").replace("\\", "_")
        target = prefix + safe_sf + ".json"
        if target in outputs:
            candidates.append({
                "project": proj["name"],
                "source_file": source_file,
                "match": target,
            })

    if candidates:
        return candidates[0]

    # Try: for each output, see if it ends with source_file
    safe_sf = source_file.replace("/", "_").replace("\\", "_")
    for out in outputs:
        stem = out.removesuffix(".json")
        if stem.endswith(safe_sf):
            # Find which project has this prefix
            prefix = stem.removesuffix(safe_sf)
            for proj in projects:
                if project_prefix(proj["path"]) == prefix:
                    candidates.append({
                        "project": proj["name"],
                        "source_file": source_file,
                        "match": out,
                    })
                    break
            if not candidates and prefix == "":
                # Root project
                for proj in projects:
                    if proj["path"] == ".":
                        candidates.append({
                            "project": proj["name"],
                            "source_file": source_file,
                            "match": out,
                        })
                        break

    if candidates:
        return candidates[0]

    # Try extension variants (.kicad_sch <-> .sch)
    ext_variants = []
    if safe_sf.endswith(".kicad_sch"):
        ext_variants.append(safe_sf.removesuffix(".kicad_sch") + ".sch")
    elif safe_sf.endswith(".sch"):
        ext_variants.append(safe_sf.removesuffix(".sch") + ".kicad_sch")
    for variant in ext_variants:
        for proj in projects:
            prefix = project_prefix(proj["path"])
            target = prefix + variant + ".json"
            if target in outputs:
                return {
                    "project": proj["name"],
                    "source_file": variant,
                    "match": target,
                }
        # Root project case
        if (variant + ".json") in outputs:
            for proj in projects:
                if proj["path"] == ".":
                    return {
                        "project": proj["name"],
                        "source_file": variant,
                        "match": variant + ".json",
                    }

    # Try: source_file is actually a stem that should include the project prefix
    for out in outputs:
        stem = out.removesuffix(".json")
        # Check if any project prefix + some adjusted source_file matches
        for proj in projects:
            prefix = project_prefix(proj["path"])
            if prefix and stem.startswith(prefix):
                remainder = stem[len(prefix):]
                # The remainder is the actual source filename
                return {
                    "project": proj["name"],
                    "source_file": remainder,
                    "match": out,
                    "note": "prefix_adjusted",
                }

    # Last resort: fuzzy — find outputs containing source_file substring
    for out in outputs:
        if safe_sf.lower() in out.lower():
            return {"match": out, "note": "fuzzy"}

    return None


def audit(fix=False):
    """Audit all registry entries. Returns list of result dicts."""
    registry = json.loads(REGISTRY_FILE.read_text())
    results = []

    for entry in registry:
        issue = entry["issue"]
        for i, ast_def in enumerate(entry.get("assertions", []), 1):
            repo = ast_def.get("repo", "")
            project = ast_def.get("project", "")
            source_file = ast_def.get("source_file", "")

            atype = ast_def.get("analyzer_type", "")
            if not atype:
                if source_file.endswith((".kicad_sch", ".sch")):
                    atype = "schematic"
                elif source_file.endswith(".kicad_pcb"):
                    atype = "pcb"
                else:
                    atype = "schematic"

            # Resolve project_path the same way assertions do at runtime
            pp = _resolve_project_path(repo, project)
            safe_sf = source_file.replace("/", "_").replace("\\", "_")
            out = find_output_file(safe_sf, repo, pp, atype)

            result = {
                "issue": issue,
                "index": i,
                "repo": repo,
                "project": project,
                "source_file": source_file,
                "analyzer_type": atype,
                "project_path": pp,
                "matched": out is not None,
                "matched_file": out.name if out else None,
            }

            if not out:
                suggestion = _suggest_correction(repo, project, source_file, atype)
                result["suggestion"] = suggestion

            results.append(result)

    return results


def apply_fixes(results):
    """Apply suggested fixes to the registry."""
    registry = json.loads(REGISTRY_FILE.read_text())

    # Build a lookup: (issue, assertion_index) -> suggestion
    fix_map = {}
    for r in results:
        if not r["matched"] and r.get("suggestion"):
            fix_map[(r["issue"], r["index"])] = r["suggestion"]

    if not fix_map:
        print("No fixes to apply.")
        return 0

    # Write backup
    backup = REGISTRY_FILE.with_suffix(".json.bak")
    shutil.copy2(REGISTRY_FILE, backup)
    print(f"Backup written to {backup}")

    fixed = 0
    for entry in registry:
        issue = entry["issue"]
        for i, ast_def in enumerate(entry.get("assertions", []), 1):
            key = (issue, i)
            if key in fix_map:
                fix = fix_map[key]
                if "project" in fix:
                    old_proj = ast_def["project"]
                    ast_def["project"] = fix["project"]
                    print(f"  {issue}[{i}]: project {old_proj!r} -> {fix['project']!r}")
                if "source_file" in fix and fix["source_file"] != ast_def["source_file"]:
                    old_sf = ast_def["source_file"]
                    ast_def["source_file"] = fix["source_file"]
                    print(f"  {issue}[{i}]: source_file {old_sf!r} -> {fix['source_file']!r}")
                fixed += 1

    REGISTRY_FILE.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"\nFixed {fixed} entries in {REGISTRY_FILE.name}")
    return fixed


def main():
    parser = argparse.ArgumentParser(
        description="Audit bugfix registry paths against actual outputs")
    parser.add_argument("--fix", action="store_true",
                        help="Apply suggested fixes (writes backup first)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = audit()
    matched = sum(1 for r in results if r["matched"])
    unmatched = [r for r in results if not r["matched"]]

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"Bugfix assertions: {matched} matched, {len(unmatched)} unmatched "
          f"(of {len(results)} total)")

    if unmatched:
        print(f"\nUnmatched assertions:")
        for r in unmatched:
            print(f"  {r['issue']}[{r['index']}]: repo={r['repo']} "
                  f"project={r['project']!r} source_file={r['source_file']!r} "
                  f"type={r['analyzer_type']}")
            if r.get("suggestion"):
                s = r["suggestion"]
                parts = []
                if "project" in s:
                    parts.append(f"project={s['project']!r}")
                if "match" in s:
                    parts.append(f"match={s['match']!r}")
                if "note" in s:
                    parts.append(f"({s['note']})")
                print(f"    -> suggest: {', '.join(parts)}")
            else:
                outputs = _list_outputs(r["repo"], r["analyzer_type"])
                if outputs:
                    print(f"    -> available outputs: {outputs[:5]}")
                else:
                    print(f"    -> no outputs found for {r['repo']}/{r['analyzer_type']}")

    if args.fix and unmatched:
        print()
        apply_fixes(results)
    elif unmatched and not args.fix:
        print(f"\nRun with --fix to apply suggested corrections.")


if __name__ == "__main__":
    main()
