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
    HARNESS_DIR, OUTPUTS_DIR, DATA_DIR,
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
                candidates.append({
                    "repo": key,
                    "total_components": total_components,
                    "signal_count": signal_count,
                    "file_count": len(jsons),
                    "best_file": str(best_file),
                })

    candidates.sort(key=lambda x: x["total_components"], reverse=True)
    if max_count:
        candidates = candidates[:max_count]
    return candidates


def _find_source_path(repo, output_json_path):
    """Resolve the source schematic path from an output JSON filename."""
    from utils import REPOS_DIR, MANIFESTS_DIR
    # The output filename encodes the path with _ separators
    stem = Path(output_json_path).stem  # e.g. "Hardware_Rev2_Rev2.kicad_sch"
    # Try manifest lookup
    manifest = MANIFESTS_DIR / repo / "schematics.txt"
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
        for ext in ("*.kicad_sch", "*.sch"):
            for f in repo_dir.rglob(ext):
                if safe_name(str(f)) == stem:
                    return str(f)
    return None


def _generate_prompt(repo, output_path):
    """Generate a review prompt for a single file."""
    source = _find_source_path(repo, output_path)
    output_name = Path(output_path).name

    prompt = f"""You are reviewing a KiCad schematic analyzer output for correctness. Read BOTH files, compare them, and produce a structured JSON finding.

SOURCE schematic: {source or 'NOT FOUND'}
OUTPUT JSON: {output_path}

Instructions:
1. Read the source schematic file to understand the actual design
2. Read the analyzer JSON output to see what the analyzer detected
3. Compare component classifications, signal detections (in signal_analysis), and net building against what's actually in the schematic
4. Name specific components (U1, R3, etc.) in your findings
5. Every incorrect/missed item needs an analyzer_section (dotted path like signal_analysis.voltage_dividers)
6. Don't fabricate issues — if the analyzer did well, say so

Produce your finding as a single JSON block. The JSON must follow this exact structure:
```json
{{
  "analyzer_type": "schematic",
  "source_file": "{output_name}",
  "status": "confirmed",
  "summary": "<1-2 sentences: board purpose, overall assessment>",
  "correct": [{{"description": "<specific correct detection with refs>", "analyzer_section": "<dotted.path>"}}],
  "incorrect": [{{"description": "<error>", "analyzer_section": "<dotted.path>"}}],
  "missed": [{{"description": "<what was missed>", "analyzer_section": "<dotted.path>"}}],
  "suggestions": ["<actionable fix>"],
  "related_issues": [],
  "should_become_assertion": true
}}
```

Output ONLY the JSON block, nothing else."""
    return prompt, source


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
    print(f"{'Components':>10}  {'Signals':>8}  {'Files':>5}  Repo")
    print(f"{'─'*10}  {'─'*8}  {'─'*5}  {'─'*40}")
    for c in candidates:
        print(f"{c['total_components']:>10}  {c['signal_count']:>8}  "
              f"{c['file_count']:>5}  {c['repo']}")


def cmd_prompts(args):
    """Generate review prompts."""
    candidates = _unreviewed_repos(args.count)
    for c in candidates:
        prompt, source = _generate_prompt(c["repo"], c["best_file"])
        project = _project_from_output(c["best_file"], c["repo"])
        print(f"=== {c['repo']} (project: {project}) ===")
        print(f"Components: {c['total_components']}, Signals: {c['signal_count']}")
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
            print(f"Added {fid}: {finding.get('summary', '?')[:80]}")


def cmd_status(args):
    """Show review coverage."""
    reviewed = _reviewed_repos()
    out_dir = OUTPUTS_DIR / "schematic"
    total = 0
    if out_dir.exists():
        for owner in out_dir.iterdir():
            if owner.is_dir():
                total += sum(1 for d in owner.iterdir() if d.is_dir())

    print(f"Layer 3 Review Coverage")
    print(f"  Reviewed: {len(reviewed)} / {total} repos "
          f"({100*len(reviewed)//max(total,1)}%)")
    print(f"  Remaining: {total - len(reviewed)}")


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
