#!/usr/bin/env python3
"""Orchestrate batch Layer 3 (LLM review) of analyzer outputs.

Automates file selection, prompt generation, and findings storage for
batch Layer 3 reviews across the test corpus.

Usage:
    python3 regression/review.py --repo X                 # select files for review
    python3 regression/review.py --batch 50               # first 50 repos
    python3 regression/review.py --repo X --dry-run       # list files only
    python3 regression/review.py --repo X --count 3       # override file count
    python3 regression/review.py --repo X --prompts       # print review prompts
    python3 regression/review.py --status                 # show review coverage
    python3 regression/review.py --save REPO PROJECT FILE # import findings JSON
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (
    HARNESS_DIR, REPOS_DIR, OUTPUTS_DIR, MANIFESTS_DIR, DATA_DIR,
    repo_name_from_path, safe_name, within_repo_path,
    filter_manifest_by_repo, discover_projects,
)

MIN_COMPONENTS = 3  # Skip trivial files


def _load_manifest():
    """Load the schematic manifest."""
    mf = MANIFESTS_DIR / "all_schematics.txt"
    if not mf.exists():
        return []
    return [l.strip() for l in mf.read_text(encoding="utf-8").splitlines() if l.strip()]


def _score_file(source_path):
    """Score a file by complexity for review prioritization.

    Returns (score, total_components, signal_count, is_top_level).
    """
    repo = repo_name_from_path(source_path)
    sname = safe_name(source_path)
    output_file = OUTPUTS_DIR / "schematic" / repo / f"{sname}.json"

    if not output_file.exists():
        return 0, 0, 0, False

    try:
        data = json.loads(output_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0, 0, 0, False

    stats = data.get("statistics", {})
    total = stats.get("total_components", 0)

    # Count signal detections
    sa = data.get("signal_analysis", {})
    signal_count = sum(len(v) for v in sa.values() if isinstance(v, list))

    # Check if top-level (has hierarchical sheet references)
    is_top = bool(data.get("hierarchical_sheets"))

    score = total + signal_count * 2 + (100 if is_top else 0)
    return score, total, signal_count, is_top


def _file_to_project(source_path, repo_name):
    """Map a source file to its project name."""
    projects = discover_projects(repo_name)
    within = within_repo_path(source_path)

    # Find the project whose path is the best prefix match.
    # Compare via PurePosixPath segments rather than string startswith so
    # the same code works on Windows where Path returns backslash separators.
    from pathlib import PurePosixPath
    within_parts = PurePosixPath(within.replace("\\", "/")).parts
    best_match = None
    best_len = -1
    for proj in projects:
        ppath = proj["path"]
        if ppath == ".":
            if best_len < 0:
                best_match = proj
                best_len = 0
            continue
        proj_parts = PurePosixPath(ppath.replace("\\", "/")).parts
        if (len(within_parts) > len(proj_parts)
                and within_parts[:len(proj_parts)] == proj_parts):
            if len(ppath) > best_len:
                best_match = proj
                best_len = len(ppath)

    return best_match["name"] if best_match else repo_name


def select_files(repo_name, count_override=None):
    """Select files for review from a repo.

    Returns list of (source_path, score, total_components, signal_count, is_top).
    """
    manifest = _load_manifest()
    repo_files = filter_manifest_by_repo(manifest, repo_name)

    if not repo_files:
        return []

    # Score all files
    scored = []
    for f in repo_files:
        score, total, sigs, is_top = _score_file(f)
        if total >= MIN_COMPONENTS:
            scored.append((f, score, total, sigs, is_top))

    if not scored:
        return []

    # Determine count based on repo size
    n_files = len(repo_files)
    if count_override:
        count = count_override
    elif n_files == 1:
        count = 1
    elif n_files <= 5:
        count = 1
    elif n_files <= 20:
        count = 2
    else:
        count = 3

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # For count >= 2, try to get top-level + most complex non-top
    if count >= 2:
        tops = [s for s in scored if s[4]]  # is_top_level
        non_tops = [s for s in scored if not s[4]]

        selected = []
        if tops:
            selected.append(tops[0])
            remaining = non_tops
        else:
            selected.append(scored[0])
            remaining = scored[1:]

        for item in remaining:
            if len(selected) >= count:
                break
            selected.append(item)

        return selected[:count]

    return scored[:count]


def generate_review_prompt(source_path, analyzer_type="schematic"):
    """Generate a structured review prompt for an LLM agent."""
    repo = repo_name_from_path(source_path)
    sname = safe_name(source_path)
    output_rel = f"{sname}.json"
    output_path = OUTPUTS_DIR / analyzer_type / repo / output_rel

    prompt = f"""Review this KiCad schematic analyzer output for correctness.

SOURCE: {source_path}
OUTPUT: {output_path}

Read both files. Compare component classifications, signal detections, and net
building against what's actually in the schematic. Produce a JSON finding:

{{
  "analyzer_type": "{analyzer_type}",
  "source_file": "{output_rel}",
  "status": "confirmed",
  "summary": "<1-2 sentences: board purpose, overall assessment>",
  "correct": [{{
    "description": "<specific correct detection with refs>",
    "analyzer_section": "<dotted.path>",
    "detector": "<section_name>",
    "subject_refs": ["<R1>", "<R2>"],
    "expected_relation": "in_detector",
    "confidence": 0.95
  }}],
  "incorrect": [{{
    "description": "<error>",
    "analyzer_section": "<dotted.path>",
    "detector": "<section_name>",
    "subject_refs": ["<R1>"],
    "expected_relation": "not_in_detector",
    "confidence": 0.95
  }}],
  "missed": [{{
    "description": "<what was missed>",
    "analyzer_section": "<dotted.path>",
    "detector": "<section_name>",
    "subject_refs": ["<U1>"],
    "expected_relation": "in_detector",
    "confidence": 0.9
  }}],
  "suggestions": ["<actionable fix>"],
  "related_issues": [],
  "should_become_assertion": true
}}

expected_relation values: in_detector, not_in_detector, field_value_equals, count_equals, section_exists.
For field_value_equals, add "field" and "expected_value" keys.
For count_equals, add "expected_value" key.

Rules: Name specific components (U1, R3). Every incorrect/missed needs
analyzer_section (dotted path like signal_analysis.voltage_dividers).
Include subject_refs with component designators. Don't fabricate issues --
if the analyzer did well, say so."""

    return prompt


def show_status():
    """Show review coverage across repos."""
    repos_with_findings = set()
    total_findings = 0

    if DATA_DIR.exists():
        for owner_dir in sorted(DATA_DIR.iterdir()):
            if not owner_dir.is_dir() or owner_dir.name.startswith("."):
                continue
            for repo_dir in sorted(owner_dir.iterdir()):
                if not repo_dir.is_dir():
                    continue
                repo_key = f"{owner_dir.name}/{repo_dir.name}"
                for proj_dir in repo_dir.iterdir():
                    if not proj_dir.is_dir():
                        continue
                    ff = proj_dir / "findings.json"
                    if ff.exists():
                        try:
                            data = json.loads(ff.read_text(encoding="utf-8"))
                            n = len(data.get("findings", []))
                            if n > 0:
                                repos_with_findings.add(repo_key)
                                total_findings += n
                        except Exception:
                            pass

    # Count total repos with outputs
    out_dir = OUTPUTS_DIR / "schematic"
    repos_with_outputs = 0
    if out_dir.exists():
        for owner_dir in out_dir.iterdir():
            if not owner_dir.is_dir():
                continue
            repos_with_outputs += sum(1 for d in owner_dir.iterdir() if d.is_dir())

    print(f"Layer 3 Review Coverage")
    print(f"  Repos reviewed: {len(repos_with_findings)}")
    print(f"  Repos with outputs: {repos_with_outputs}")
    if repos_with_outputs:
        print(f"  Coverage: {len(repos_with_findings)*100//repos_with_outputs}%")
    print(f"  Total findings: {total_findings}")

    if repos_with_findings:
        print(f"\nReviewed repos:")
        for r in sorted(repos_with_findings):
            print(f"  {r}")


def import_findings(repo_name, project_name, findings_file):
    """Import findings from a JSON file."""
    from regression.findings import add_finding

    data = json.loads(Path(findings_file).read_text(encoding="utf-8"))

    if isinstance(data, list):
        for finding in data:
            fid = add_finding(repo_name, project_name, finding)
            print(f"  Added {fid}: {finding.get('summary', '?')[:60]}")
    elif isinstance(data, dict):
        if "findings" in data:
            for finding in data["findings"]:
                fid = add_finding(repo_name, project_name, finding)
                print(f"  Added {fid}: {finding.get('summary', '?')[:60]}")
        else:
            fid = add_finding(repo_name, project_name, data)
            print(f"  Added {fid}: {data.get('summary', '?')[:60]}")


def read_priority_repos(count):
    """Read first N repos from list_repos() for batch review."""
    try:
        repos = list_repos()[:count]
        return repos
    except Exception:
        return []



def main():
    parser = argparse.ArgumentParser(description="Orchestrate Layer 3 reviews")
    parser.add_argument("--repo", help="Select files from this repo")
    parser.add_argument("--batch", type=int, help="Select first N repos for batch review")
    parser.add_argument("--count", type=int, help="Override files per repo")
    parser.add_argument("--dry-run", action="store_true",
                        help="List files without generating prompts")
    parser.add_argument("--prompts", action="store_true",
                        help="Print review prompts")
    parser.add_argument("--status", action="store_true",
                        help="Show review coverage")
    parser.add_argument("--save", nargs=3, metavar=("REPO", "PROJECT", "FILE"),
                        help="Import findings from JSON file")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.save:
        repo, project, ffile = args.save
        import_findings(repo, project, ffile)
        return

    # Determine repos to process
    if args.repo:
        repos = [args.repo]
    elif args.batch:
        repos = read_priority_repos(args.batch)
        if not repos:
            print("Error: no repos found")
            sys.exit(1)
        print(f"Selected {len(repos)} repos for review\n")
    else:
        print("Error: specify --repo, --batch, --status, or --save")
        sys.exit(1)

    total_selected = 0
    for repo in repos:
        files = select_files(repo, args.count)
        if not files:
            continue

        print(f"=== {repo} ({len(files)} file{'s' if len(files) > 1 else ''}) ===")
        for source, score, total, sigs, is_top in files:
            within = within_repo_path(source)
            project = _file_to_project(source, repo)
            top_mark = " [top-level]" if is_top else ""
            print(f"  {within} -- {total} components, {sigs} signals, "
                  f"score={score}{top_mark}")
            print(f"    Project: {project}")

            if args.prompts and not args.dry_run:
                prompt = generate_review_prompt(source)
                print(f"\n--- PROMPT ---\n{prompt}\n--- END ---\n")

        total_selected += len(files)
        print()

    print(f"Total: {total_selected} files from {len(repos)} repos")
    if args.dry_run:
        print("(dry run -- no prompts generated)")


if __name__ == "__main__":
    main()
