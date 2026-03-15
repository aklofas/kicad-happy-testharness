#!/usr/bin/env python3
"""Store and manage review findings.

Findings are structured observations from LLM review of analyzer outputs.
They capture what the analyzer got right, wrong, or missed, and can be
promoted to permanent assertions.

Findings are stored per-project in reference/{repo}/{project}/findings.json.
A human-readable findings.md is auto-generated alongside each findings.json.

Usage:
    python3 regression/findings.py list
    python3 regression/findings.py list --status confirmed
    python3 regression/findings.py list --repo OpenMower
    python3 regression/findings.py show FND-00000001
    python3 regression/findings.py promote FND-00000001
    python3 regression/findings.py stats
    python3 regression/findings.py render          # regenerate all findings.md
    python3 regression/findings.py render --repo X # regenerate for one repo
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import DATA_DIR, data_dir


def _iter_findings_files(repo_name=None):
    """Iterate findings.json files under data/{repo}/{project}/.

    If repo_name is given, only iterate that repo's projects.
    """
    if not DATA_DIR.exists():
        return
    if repo_name:
        repo_dir = DATA_DIR / repo_name
        if repo_dir.is_dir():
            for proj_dir in sorted(repo_dir.iterdir()):
                if not proj_dir.is_dir():
                    continue
                ff = proj_dir / "findings.json"
                if ff.exists():
                    yield repo_name, proj_dir.name, ff
        return
    for repo_dir in sorted(DATA_DIR.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue
        for proj_dir in sorted(repo_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            ff = proj_dir / "findings.json"
            if ff.exists():
                yield repo_dir.name, proj_dir.name, ff


def load_findings(repo_name=None, project_name=None):
    """Load findings. Filter by repo and/or project, or load all."""
    all_findings = []

    if repo_name and project_name:
        ff = data_dir(repo_name, project_name) / "findings.json"
        if ff.exists():
            return json.loads(ff.read_text())
        return {"findings": []}

    for repo, proj, ff in _iter_findings_files(repo_name):
        try:
            data = json.loads(ff.read_text())
            for f in data.get("findings", []):
                f.setdefault("repo", repo)
                f.setdefault("project", proj)
                all_findings.append(f)
        except Exception:
            continue

    return {"findings": all_findings}


def _normalize_issue_ref(ref):
    """Normalize issue references to KH-XXX or TH-XXX format.

    Handles: "#8" -> "KH-008", "#12" -> "KH-012", "KH-008" -> "KH-008",
    "NEW" or other text -> returned as-is.
    """
    if not ref or not isinstance(ref, str):
        return ref
    ref = ref.strip()
    m = re.match(r'^#(\d+)$', ref)
    if m:
        return f"KH-{int(m.group(1)):03d}"
    return ref


def render_md(repo_name, project_name, data=None):
    """Generate findings.md from findings.json for a repo/project.

    If data is None, loads from disk.
    """
    if data is None:
        data = load_findings(repo_name, project_name)

    findings = data.get("findings", [])
    if not findings:
        # Remove stale findings.md if no findings
        md_path = data_dir(repo_name, project_name) / "findings.md"
        if md_path.exists():
            md_path.unlink()
        return

    lines = [f"# Findings: {repo_name} / {project_name}", ""]

    for f in findings:
        fid = f.get("id", "?")
        summary = f.get("summary", "(no summary)")
        lines.append(f"## {fid}: {summary}")
        lines.append("")

        # Metadata
        status = f.get("status", "?")
        atype = f.get("analyzer_type", "?")
        source = f.get("source_file", "?")
        lines.append(f"- **Status**: {status}")
        lines.append(f"- **Analyzer**: {atype}")
        lines.append(f"- **Source**: {source}")

        # Related issues — normalize refs
        related = f.get("related_issues", [])
        if related:
            normalized = [_normalize_issue_ref(r) for r in related]
            lines.append(f"- **Related**: {', '.join(normalized)}")

        # Created date — show just the date portion
        created = f.get("created", "")
        if created:
            date_part = created[:10]  # YYYY-MM-DD
            lines.append(f"- **Created**: {date_part}")

        # Datasheets used
        ds = f.get("datasheets_used", [])
        if ds:
            lines.append(f"- **Datasheets**: {', '.join(ds)}")

        lines.append("")

        # Correct
        lines.append("### Correct")
        correct = f.get("correct", [])
        if correct:
            for item in correct:
                desc = item.get("description", "?")
                lines.append(f"- {desc}")
        else:
            lines.append("(none)")
        lines.append("")

        # Incorrect
        lines.append("### Incorrect")
        incorrect = f.get("incorrect", [])
        if incorrect:
            for item in incorrect:
                desc = item.get("description", "?")
                section = item.get("analyzer_section", "")
                line = f"- {desc}"
                if section:
                    line += f"\n  ({section})"
                lines.append(line)
        else:
            lines.append("(none)")
        lines.append("")

        # Missed
        lines.append("### Missed")
        missed = f.get("missed", [])
        if missed:
            for item in missed:
                desc = item.get("description", "?")
                section = item.get("analyzer_section", "")
                line = f"- {desc}"
                if section:
                    line += f"\n  ({section})"
                lines.append(line)
        else:
            lines.append("(none)")
        lines.append("")

        # Suggestions
        lines.append("### Suggestions")
        suggestions = f.get("suggestions", [])
        if suggestions:
            for s in suggestions:
                lines.append(f"- {s}")
        else:
            lines.append("(none)")
        lines.append("")

        lines.append("---")
        lines.append("")

    proj_dir = data_dir(repo_name, project_name)
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "findings.md").write_text("\n".join(lines))


def save_findings(repo_name, project_name, data):
    """Save findings.json and auto-regenerate findings.md."""
    proj_dir = data_dir(repo_name, project_name)
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "findings.json").write_text(json.dumps(data, indent=2) + "\n")
    render_md(repo_name, project_name, data)


def next_id():
    """Generate next finding ID, unique across all repos/projects."""
    max_num = 0
    for _, _, ff in _iter_findings_files():
        try:
            data = json.loads(ff.read_text())
            for f in data.get("findings", []):
                try:
                    max_num = max(max_num, int(f["id"].split("-")[1]))
                except (IndexError, ValueError):
                    pass
        except Exception:
            pass
    return f"FND-{max_num + 1:08d}"


def add_finding(repo_name, project_name, finding):
    """Add a new finding. Auto-generates ID and timestamp."""
    data = load_findings(repo_name, project_name)
    fid = next_id()
    finding["id"] = fid
    finding["repo"] = repo_name
    finding["project"] = project_name
    finding["created"] = datetime.now(timezone.utc).isoformat()
    finding.setdefault("status", "new")
    finding.setdefault("correct", [])
    finding.setdefault("incorrect", [])
    finding.setdefault("missed", [])
    finding.setdefault("suggestions", [])
    finding.setdefault("datasheets_used", [])
    finding.setdefault("should_become_assertion", False)
    data["findings"].append(finding)
    save_findings(repo_name, project_name, data)
    return fid


def _find_finding(finding_id):
    """Find a finding by ID across all repos/projects.

    Returns (repo_name, project_name, data, finding).
    """
    for repo, proj, ff in _iter_findings_files():
        try:
            data = json.loads(ff.read_text())
            for f in data.get("findings", []):
                if f.get("id") == finding_id:
                    return repo, proj, data, f
        except Exception:
            continue
    return None, None, None, None


def promote_to_assertion(finding_id):
    """Generate an assertion file from a confirmed finding."""
    repo_name, project_name, data, finding = _find_finding(finding_id)
    if not finding:
        print(f"Finding {finding_id} not found.")
        return None

    atype = finding.get("analyzer_type", "schematic")
    source = finding.get("source_file", "unknown")
    repo = finding.get("repo", repo_name)
    proj = finding.get("project", project_name)

    # Generate assertions from incorrect/missed items
    assertions = []
    ast_num = 1

    for item in finding.get("missed", []):
        section = item.get("analyzer_section", "")
        desc = item.get("description", "")
        if section:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:08d}",
                "description": desc,
                "created_from": finding_id,
                "check": {
                    "path": section,
                    "op": "min_count",
                    "value": 1,
                },
                "needs_review": True,
            })
            ast_num += 1

    for item in finding.get("incorrect", []):
        desc = item.get("description", "")
        assertions.append({
            "id": f"{finding_id}-AST-{ast_num:08d}",
            "description": f"REVIEW: {desc}",
            "created_from": finding_id,
            "check": {"path": "", "op": "exists"},
            "needs_review": True,
        })
        ast_num += 1

    if not assertions:
        print(f"No assertions could be generated from {finding_id}.")
        print("Add 'missed' or 'incorrect' entries with 'analyzer_section' fields.")
        return None

    # Build a safe filename from the source file
    safe = source.replace("/", "_").replace("\\", "_")
    if safe.endswith(".json"):
        safe = safe[:-5]

    assertion_data = {
        "file_pattern": safe,
        "analyzer_type": atype,
        "created_from": finding_id,
        "assertions": assertions,
    }

    # Write to data/{repo}/{project}/assertions/{type}/
    out_dir = data_dir(repo, proj, "assertions") / atype
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{safe}.json"

    # Merge with existing if present
    if out_file.exists():
        existing = json.loads(out_file.read_text())
        existing_ids = {a["id"] for a in existing.get("assertions", [])}
        for a in assertions:
            if a["id"] not in existing_ids:
                existing["assertions"].append(a)
        assertion_data = existing

    out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")

    # Update finding status
    finding["status"] = "promoted"
    save_findings(repo_name, project_name, data)

    print(f"Generated {len(assertions)} assertion(s) in {out_file}")
    print("NOTE: Assertions marked needs_review=true need manual review.")
    return assertion_data


def main():
    parser = argparse.ArgumentParser(description="Manage review findings")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List findings")
    show_p = sub.add_parser("show", help="Show a finding")
    show_p.add_argument("id", help="Finding ID (e.g., FND-00000001)")
    promote_p = sub.add_parser("promote", help="Promote finding to assertion")
    promote_p.add_argument("id", help="Finding ID")
    sub.add_parser("stats", help="Show statistics")
    sub.add_parser("render", help="Regenerate all findings.md files")

    # List subcommand options
    for sp in [sub.choices.get("list")]:
        if sp:
            sp.add_argument("--status", help="Filter by status")
            sp.add_argument("--type", help="Filter by analyzer_type")
            sp.add_argument("--repo", help="Filter by repo name")

    # Render subcommand options
    render_sp = sub.choices.get("render")
    if render_sp:
        render_sp.add_argument("--repo", help="Only render for this repo")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        repo = getattr(args, "repo", None)
        data = load_findings(repo)
        findings = data.get("findings", [])

        if hasattr(args, "status") and args.status:
            findings = [f for f in findings if f.get("status") == args.status]
        if hasattr(args, "type") and args.type:
            findings = [f for f in findings if f.get("analyzer_type") == args.type]

        if not findings:
            print("No findings found.")
            return

        print(f"{'ID':<12s} {'Status':<12s} {'Type':<12s} {'Repo':<20s} File")
        print("-" * 85)
        for f in findings:
            source = f.get("source_file", "?")
            if len(source) > 30:
                source = "..." + source[-27:]
            repo_name = f.get("repo", "?")
            print(f"{f['id']:<12s} {f.get('status', '?'):<12s} "
                  f"{f.get('analyzer_type', '?'):<12s} {repo_name:<20s} {source}")

    elif args.command == "show":
        _, _, _, finding = _find_finding(args.id)
        if not finding:
            print(f"Finding {args.id} not found.")
            sys.exit(1)
        print(json.dumps(finding, indent=2))

    elif args.command == "promote":
        promote_to_assertion(args.id)

    elif args.command == "render":
        repo_filter = getattr(args, "repo", None)
        count = 0
        for repo, proj, ff in _iter_findings_files():
            if repo_filter and repo != repo_filter:
                continue
            data = json.loads(ff.read_text())
            render_md(repo, proj, data)
            n = len(data.get("findings", []))
            print(f"  {repo}/{proj}: {n} findings")
            count += 1
        print(f"Rendered {count} findings.md file(s).")

    elif args.command == "stats":
        data = load_findings()
        findings = data.get("findings", [])

        by_status = {}
        by_type = {}
        by_repo = {}
        for f in findings:
            s = f.get("status", "unknown")
            t = f.get("analyzer_type", "unknown")
            r = f.get("repo", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
            by_type[t] = by_type.get(t, 0) + 1
            by_repo[r] = by_repo.get(r, 0) + 1

        print(f"Total findings: {len(findings)}")
        print(f"\nBy status:")
        for s, c in sorted(by_status.items()):
            print(f"  {s}: {c}")
        print(f"\nBy type:")
        for t, c in sorted(by_type.items()):
            print(f"  {t}: {c}")
        print(f"\nBy repo:")
        for r, c in sorted(by_repo.items()):
            print(f"  {r}: {c}")

        actionable = sum(1 for f in findings if f.get("should_become_assertion") and f.get("status") != "promoted")
        if actionable:
            print(f"\nActionable (ready to promote): {actionable}")


if __name__ == "__main__":
    main()
