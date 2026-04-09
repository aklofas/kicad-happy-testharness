#!/usr/bin/env python3
"""Batch Layer 3 review via LLM subagents.

Selects unreviewed repos, generates review prompts, and saves findings.
Designed to be called from a Claude Code session where subagents handle
the actual review work.

This script handles the orchestration — file selection, prompt generation,
and findings import. The LLM review itself happens via Claude Code subagents
(not automated API calls).

Usage:
    # List unreviewed repos sorted by complexity
    python3 tools/batch_review.py list --count 20

    # Generate review prompts for N repos (copy-paste to subagent)
    python3 tools/batch_review.py prompts --count 5

    # Import a finding from a JSON file
    python3 tools/batch_review.py save --repo owner/repo --project proj --file /tmp/finding.json

    # Show review coverage stats
    python3 tools/batch_review.py status

Workflow for Claude Code sessions:
    1. Run: python3 tools/batch_review.py prompts --count N
    2. For each prompt, spawn a subagent with the prompt text
    3. Subagent reads source + output, produces JSON finding
    4. Save finding: python3 tools/batch_review.py save --repo R --project P --file F
    5. Optionally: python3 regression/generate_finding_checks.py --repo R
    6. Optionally: python3 regression/findings.py promote-all
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    HARNESS_DIR, OUTPUTS_DIR, DATA_DIR, REPOS_DIR, MANIFESTS_DIR,
    repo_name_from_path, safe_name,
)


def _reviewed_repos():
    """Return set of repos that already have findings."""
    reviewed = set()
    if not DATA_DIR.exists():
        return reviewed
    for owner in DATA_DIR.iterdir():
        if not owner.is_dir() or owner.name.startswith("."):
            continue
        for repo in owner.iterdir():
            if not repo.is_dir():
                continue
            for proj in repo.iterdir():
                if (proj / "findings.json").exists():
                    reviewed.add(f"{owner.name}/{repo.name}")
    return reviewed


def _output_project_prefix(path):
    """Extract a project prefix from an output filename for cross-type matching.

    Output filenames keep original dots: 'ZeBra-X.kicad_sch.json'
    Strip the analyzer-specific extension to get the shared project name.
    """
    stem = Path(path).stem  # 'ZeBra-X.kicad_sch'
    # Strip known source file extensions (longest first)
    for suffix in (".kicad_sch", ".kicad_pcb", ".sch"):
        if stem.endswith(suffix):
            return stem[:len(stem) - len(suffix)]
    # For gerber outputs, strip common gerber directory names
    # These use underscores since the directory name is path-encoded
    lower = stem.lower()
    for suffix in ("_gerber", "_gerbers", "_plot", "_fab",
                   "_output_gerber", "_output", "_production"):
        if lower.endswith(suffix):
            return stem[:len(stem) - len(suffix)]
    return stem


def _collect_outputs(repo):
    """Collect all analyzer outputs for a repo, grouped by type.

    Tries to select outputs from the same project across types by matching
    filename prefixes. Falls back to highest-scoring file per type.

    Returns dict: {analyzer_type: [{path, source, components, signals}, ...]}
    """
    result = {}
    for atype in ("schematic", "pcb", "gerber"):
        out_dir = OUTPUTS_DIR / atype / repo
        if not out_dir.exists():
            continue
        files = []
        for j in sorted(out_dir.glob("*.json")):
            try:
                d = json.loads(j.read_text())
                tc = d.get("statistics", {}).get("total_components", 0)
                sa = d.get("signal_analysis", {})
                sc = sum(len(v) for v in sa.values() if isinstance(v, list))
                source = _find_source_path(repo, atype, str(j))
                files.append({
                    "path": str(j),
                    "source": source,
                    "components": tc,
                    "signals": sc,
                    "score": tc + sc,
                    "prefix": _output_project_prefix(str(j)),
                })
            except Exception:
                continue
        if files:
            files.sort(key=lambda x: x["score"], reverse=True)
            result[atype] = files

    # Try to align PCB and gerber outputs to match the best schematic's project
    if "schematic" in result and len(result["schematic"]) > 0:
        sch_prefix = result["schematic"][0]["prefix"]
        for atype in ("pcb", "gerber"):
            if atype not in result:
                continue
            # Find a file whose prefix matches the schematic's prefix
            matched = [f for f in result[atype]
                       if f["prefix"] == sch_prefix
                       or sch_prefix.startswith(f["prefix"])
                       or f["prefix"].startswith(sch_prefix)]
            if matched:
                # Move the matched file to front
                rest = [f for f in result[atype] if f not in matched]
                result[atype] = matched + rest

    return result


def _unreviewed_repos(max_count=None):
    """Find unreviewed repos sorted by complexity (total components)."""
    reviewed = _reviewed_repos()
    out_dir = OUTPUTS_DIR / "schematic"
    if not out_dir.exists():
        return []

    candidates = []
    for owner in sorted(out_dir.iterdir()):
        if not owner.is_dir():
            continue
        for repo in sorted(owner.iterdir()):
            if not repo.is_dir():
                continue
            key = f"{owner.name}/{repo.name}"
            if key in reviewed:
                continue
            jsons = list(repo.glob("*.json"))
            if not jsons:
                continue
            # Score by total components across files
            total_components = 0
            signal_count = 0
            best_file = None
            best_score = 0
            for j in jsons:
                try:
                    d = json.loads(j.read_text())
                    tc = d.get("statistics", {}).get("total_components", 0)
                    total_components += tc
                    sa = d.get("signal_analysis", {})
                    sc = sum(len(v) for v in sa.values() if isinstance(v, list))
                    signal_count += sc
                    score = tc + sc
                    if score > best_score:
                        best_score = score
                        best_file = j
                except Exception:
                    continue
            if total_components >= 5:
                # Check for PCB/gerber outputs too
                has_pcb = (OUTPUTS_DIR / "pcb" / key).exists()
                has_gerber = (OUTPUTS_DIR / "gerber" / key).exists()
                candidates.append({
                    "repo": key,
                    "total_components": total_components,
                    "signal_count": signal_count,
                    "file_count": len(jsons),
                    "best_file": str(best_file),
                    "has_pcb": has_pcb,
                    "has_gerber": has_gerber,
                })

    candidates.sort(key=lambda x: x["total_components"], reverse=True)
    if max_count:
        candidates = candidates[:max_count]
    return candidates


def _find_source_path(repo, atype, output_json_path):
    """Resolve the source file path from an output JSON filename.

    Works for schematic, PCB, and gerber output types.
    """
    stem = Path(output_json_path).stem

    # Manifest file for this type
    manifest_name = {
        "schematic": "schematics.txt",
        "pcb": "pcbs.txt",
        "gerber": "gerbers.txt",
    }.get(atype)

    if manifest_name:
        manifest = MANIFESTS_DIR / repo / manifest_name
        if manifest.exists():
            for line in manifest.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                sn = safe_name(line)
                if sn == stem:
                    return line

    # Fallback: glob the repo dir
    repo_dir = REPOS_DIR / repo
    if repo_dir.exists():
        ext_map = {
            "schematic": ("*.kicad_sch", "*.sch"),
            "pcb": ("*.kicad_pcb",),
            "gerber": (),  # gerber dirs are handled differently
        }
        for ext in ext_map.get(atype, ()):
            for f in repo_dir.rglob(ext):
                if safe_name(str(f)) == stem:
                    return str(f)
    return None


def _generate_prompt(repo, outputs_by_type):
    """Generate a combined review prompt covering all available output types."""
    # Build file list section
    file_sections = []
    primary_output = None
    primary_source = None

    for atype in ("schematic", "pcb", "gerber"):
        files = outputs_by_type.get(atype, [])
        if not files:
            continue
        best = files[0]  # highest-scoring file for this type
        if atype == "schematic":
            primary_output = best["path"]
            primary_source = best["source"]
        label = atype.upper()
        file_sections.append(
            f"  {label} SOURCE: {best['source'] or 'NOT FOUND'}\n"
            f"  {label} OUTPUT: {best['path']}"
        )

    if not file_sections:
        return None, None

    files_block = "\n".join(file_sections)
    output_name = Path(primary_output).name if primary_output else "unknown"

    # Determine which types are available
    has_types = sorted(outputs_by_type.keys())
    types_str = ", ".join(has_types)

    # Build type-specific instructions
    type_instructions = []
    if "schematic" in outputs_by_type:
        type_instructions.append(
            "- SCHEMATIC: Check component classifications, signal detections "
            "(voltage dividers, regulators, filters, opamps, protection devices), "
            "net building, and bus protocols. Name specific components (U1, R3, etc.)"
        )
    if "pcb" in outputs_by_type:
        type_instructions.append(
            "- PCB: Check footprint assignments, track widths vs current requirements, "
            "thermal relief, via counts, zone fills, board dimensions, layer usage, "
            "and DFM metrics. Cross-reference component placement against schematic "
            "signal flow"
        )
    if "gerber" in outputs_by_type:
        type_instructions.append(
            "- GERBER: Check layer completeness (all expected layers present), "
            "drill file alignment, silkscreen legibility, solder mask clearances, "
            "and board outline consistency. Cross-reference layer count against "
            "PCB stackup"
        )

    type_block = "\n".join(type_instructions)

    # Cross-reference instructions
    cross_ref = ""
    if len(has_types) > 1:
        cross_ref = """
7. CROSS-REFERENCE between analyzer outputs:
   - Schematic↔PCB: Do component counts match? Are all schematic nets routed?
   - PCB↔Gerber: Do layer counts match? Are drill files consistent with vias?
   - Schematic↔Gerber: Does board complexity match schematic complexity?
   Flag any inconsistencies between analyzer outputs."""

    # Build the finding template based on available types
    finding_types = []
    for atype in has_types:
        best = outputs_by_type[atype][0]
        finding_types.append(f"""\
{{
  "analyzer_type": "{atype}",
  "source_file": "{Path(best['path']).name}",
  "status": "confirmed",
  "summary": "<1-2 sentences: assessment of {atype} analysis>",
  "correct": [{{"description": "<specific correct detection>", "analyzer_section": "<dotted.path>"}}],
  "incorrect": [{{"description": "<error>", "analyzer_section": "<dotted.path>"}}],
  "missed": [{{"description": "<what was missed>", "analyzer_section": "<dotted.path>"}}],
  "suggestions": ["<actionable fix>"],
  "related_issues": []
}}""")

    if len(finding_types) == 1:
        template = finding_types[0]
    else:
        template = "[\n" + ",\n".join(f"  {t}" for t in finding_types) + "\n]"

    prompt = f"""You are reviewing KiCad analyzer outputs for correctness. This repo has {types_str} outputs. Read ALL source files and ALL output JSONs, compare them, and produce structured findings.

{files_block}

Instructions:
1. Read each source file to understand the actual design
2. Read each analyzer JSON output to see what was detected
3. Compare detections against reality for each analyzer type:
{type_block}
4. Name specific components (U1, R3, etc.) in your findings
5. Every incorrect/missed item needs an analyzer_section (dotted path)
6. Don't fabricate issues — if the analyzer did well, say so{cross_ref}

Produce {"a JSON array with one finding per analyzer type" if len(has_types) > 1 else "a single JSON finding"}:
```json
{template}
```

Output ONLY the JSON {"array" if len(has_types) > 1 else "block"}, nothing else."""

    return prompt, primary_source


def _project_from_output(output_path, repo):
    """Derive the project name from an output path."""
    stem = Path(output_path).stem  # e.g. "Hardware_Rev2_Rev2.kicad_sch"
    # Remove the file extension part
    for ext in (".kicad_sch", ".sch"):
        if stem.endswith(ext.replace(".", "_")):
            break
    # The project is the directory structure encoded in the filename
    # Look for it in reference/
    ref_dir = HARNESS_DIR / "reference" / repo
    if ref_dir.exists():
        for proj_dir in ref_dir.iterdir():
            if proj_dir.is_dir():
                sch_dir = proj_dir / "assertions" / "schematic"
                if sch_dir.exists():
                    for f in sch_dir.glob("*.json"):
                        if f.stem.startswith(stem.rsplit("_", 1)[0]):
                            return proj_dir.name
    # Fallback: use the stem up to the last schematic file part
    return stem


def cmd_list(args):
    """List unreviewed repos."""
    candidates = _unreviewed_repos(args.count)
    print(f"Unreviewed repos ({len(candidates)} shown):\n")
    print(f"{'Components':>10}  {'Signals':>8}  {'Files':>5}  "
          f"{'PCB':>3}  {'GBR':>3}  Repo")
    print(f"{'─'*10}  {'─'*8}  {'─'*5}  {'─'*3}  {'─'*3}  {'─'*40}")
    for c in candidates:
        pcb = " ✓" if c["has_pcb"] else "  "
        gbr = " ✓" if c["has_gerber"] else "  "
        print(f"{c['total_components']:>10}  {c['signal_count']:>8}  "
              f"{c['file_count']:>5}  {pcb}  {gbr}  {c['repo']}")


def cmd_prompts(args):
    """Generate review prompts."""
    candidates = _unreviewed_repos(args.count)
    for c in candidates:
        outputs = _collect_outputs(c["repo"])
        prompt, source = _generate_prompt(c["repo"], outputs)
        if not prompt:
            continue
        project = _project_from_output(c["best_file"], c["repo"])
        types_avail = ", ".join(sorted(outputs.keys()))
        print(f"=== {c['repo']} (project: {project}) ===")
        print(f"Components: {c['total_components']}, Signals: {c['signal_count']}, "
              f"Types: {types_avail}")
        print()
        print(prompt)
        print()
        print("---")
        print()


def _auto_project(repo, source_file=None):
    """Auto-detect project name from reference/ directory or source_file hint."""
    ref_dir = HARNESS_DIR / "reference" / repo
    if not ref_dir.exists():
        return None

    projects = [p.name for p in ref_dir.iterdir() if p.is_dir()]
    if len(projects) == 1:
        return projects[0]

    # If source_file hint given, match against project names
    if source_file:
        stem = Path(source_file).stem
        for proj in projects:
            if stem.startswith(proj) or proj.startswith(stem.split(".")[0]):
                return proj
    return projects[0] if projects else None


def cmd_save(args):
    """Import a finding from JSON file or stdin."""
    from regression.findings import add_finding

    if args.file == "-":
        data = json.loads(sys.stdin.read())
    else:
        data = json.loads(Path(args.file).read_text())

    # Auto-detect project if not given
    project = args.project
    if not project:
        source_file = None
        if isinstance(data, dict):
            source_file = data.get("source_file")
        elif isinstance(data, list) and data:
            source_file = data[0].get("source_file")
        project = _auto_project(args.repo, source_file)
        if not project:
            print(f"Error: could not auto-detect project for {args.repo}. "
                  f"Use --project.", file=sys.stderr)
            sys.exit(1)
        print(f"Auto-detected project: {project}")

    if isinstance(data, dict):
        fid = add_finding(args.repo, project, data)
        print(f"Added {fid}: {data.get('summary', '?')[:80]}")
    elif isinstance(data, list):
        for finding in data:
            fid = add_finding(args.repo, project, finding)
            atype = finding.get("analyzer_type", "?")
            print(f"Added {fid} ({atype}): {finding.get('summary', '?')[:80]}")


def cmd_status(args):
    """Show review coverage."""
    reviewed = _reviewed_repos()
    out_dir = OUTPUTS_DIR / "schematic"
    total = 0
    if out_dir.exists():
        for owner in out_dir.iterdir():
            if owner.is_dir():
                total += sum(1 for d in owner.iterdir() if d.is_dir())

    # Count findings by analyzer_type
    type_counts = {}
    for owner in DATA_DIR.iterdir():
        if not owner.is_dir() or owner.name.startswith("."):
            continue
        for repo in owner.iterdir():
            if not repo.is_dir():
                continue
            for proj in repo.iterdir():
                ff = proj / "findings.json"
                if ff.exists():
                    try:
                        data = json.loads(ff.read_text())
                        for f in data.get("findings", []):
                            atype = f.get("analyzer_type", "unknown")
                            type_counts[atype] = type_counts.get(atype, 0) + 1
                    except Exception:
                        pass

    print(f"Layer 3 Review Coverage")
    print(f"  Reviewed: {len(reviewed)} / {total} repos "
          f"({100*len(reviewed)//max(total,1)}%)")
    print(f"  Remaining: {total - len(reviewed)}")
    if type_counts:
        print(f"\n  Findings by analyzer type:")
        for atype in sorted(type_counts):
            print(f"    {atype}: {type_counts[atype]}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch Layer 3 review orchestration")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List unreviewed repos")
    p_list.add_argument("--count", "-n", type=int, default=20)

    p_prompts = sub.add_parser("prompts", help="Generate review prompts")
    p_prompts.add_argument("--count", "-n", type=int, default=5)

    p_save = sub.add_parser("save", help="Import finding from JSON (file or stdin with -)")
    p_save.add_argument("--repo", required=True)
    p_save.add_argument("--project", help="Project name (auto-detected if omitted)")
    p_save.add_argument("--file", required=True, help="JSON file path, or - for stdin")

    p_status = sub.add_parser("status", help="Show coverage stats")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "prompts":
        cmd_prompts(args)
    elif args.command == "save":
        cmd_save(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
