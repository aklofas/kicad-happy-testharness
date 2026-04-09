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
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            repo_key = f"{owner_dir.name}/{repo_dir.name}"
            for proj_dir in sorted(repo_dir.iterdir()):
                if not proj_dir.is_dir():
                    continue
                ff = proj_dir / "findings.json"
                if ff.exists():
                    yield repo_key, proj_dir.name, ff


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
    """Generate next finding ID, unique across all repos/projects.

    Uses a counter file (reference/.fnd_counter) for atomicity.
    Falls back to scanning all findings if counter file is missing.
    """
    counter_file = DATA_DIR / "fnd_counter"

    # Scan all findings to find the true max
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

    # Also check the counter file (may be ahead of scan if rapid saves)
    if counter_file.exists():
        try:
            max_num = max(max_num, int(counter_file.read_text().strip()))
        except (ValueError, OSError):
            pass

    next_num = max_num + 1
    counter_file.write_text(str(next_num))
    return f"FND-{next_num:08d}"


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


def _strip_project_prefix(safe, repo, proj):
    """Strip the project_path prefix from a safe filename."""
    meta_file = data_dir(repo, proj, "baselines") / "metadata.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text())
            pp = meta.get("project_path", "")
            if pp and pp != ".":
                pp_prefix = pp.replace("/", "_").replace("\\", "_") + "_"
                if safe.startswith(pp_prefix):
                    return safe[len(pp_prefix):]
        except Exception:
            pass
    return safe


def promote_to_assertion(finding_id, dry_run=False):
    """Generate assertion files from a finding's check fields.

    Uses check fields on correct/incorrect/missed items (generated by
    generate_finding_checks.py). Items without checks fall back to
    section-level min_count assertions.

    Returns (assertion_count, aspirational_count) or None if not found.
    """
    repo_name, project_name, data, finding = _find_finding(finding_id)
    if not finding:
        print(f"Finding {finding_id} not found.")
        return None

    atype = finding.get("analyzer_type", "schematic")
    source = finding.get("source_file", "unknown")
    repo = finding.get("repo", repo_name)
    proj = finding.get("project", project_name)

    assertions = []
    aspirational = 0
    ast_num = 1

    # Correct items — positive assertions (this should keep working)
    for item in finding.get("correct", []):
        check = item.get("check")
        section = item.get("analyzer_section", "")
        desc = item.get("description", "")
        if check:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:02d}",
                "description": desc,
                "created_from": finding_id,
                "check": check,
            })
            ast_num += 1
        elif section:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:02d}",
                "description": desc,
                "created_from": finding_id,
                "check": {"path": section, "op": "min_count", "value": 1},
            })
            ast_num += 1

    # Incorrect items — negative assertions (aspirational until bug is fixed)
    for item in finding.get("incorrect", []):
        check = item.get("check")
        desc = item.get("description", "")
        if check:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:02d}",
                "description": f"INCORRECT: {desc}",
                "created_from": finding_id,
                "check": check,
                "aspirational": True,
            })
            ast_num += 1
            aspirational += 1

    # Missed items — aspirational assertions (expected to fail until fixed)
    for item in finding.get("missed", []):
        check = item.get("check")
        section = item.get("analyzer_section", "")
        desc = item.get("description", "")
        if check:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:02d}",
                "description": desc,
                "created_from": finding_id,
                "check": check,
                "aspirational": True,
            })
            ast_num += 1
            aspirational += 1
        elif section:
            assertions.append({
                "id": f"{finding_id}-AST-{ast_num:02d}",
                "description": desc,
                "created_from": finding_id,
                "check": {"path": section, "op": "min_count", "value": 1},
                "aspirational": True,
            })
            ast_num += 1
            aspirational += 1

    if not assertions:
        return 0, 0

    # Build file_pattern from source_file.
    # source_file is like "schematic/repo/projprefix_file.kicad_sch.json"
    # file_pattern should be just "file.kicad_sch" (no type/repo prefix, no project prefix)
    # because find_output_file() prepends project_prefix automatically.
    source_stripped = source
    if source_stripped.endswith(".json"):
        source_stripped = source_stripped[:-5]
    # Strip {type}/{repo}/ prefix if present
    parts = source_stripped.replace("\\", "/").split("/")
    if len(parts) >= 3 and parts[0] == atype and parts[1] == repo:
        safe = "_".join(parts[2:])
    else:
        safe = source_stripped.replace("/", "_").replace("\\", "_")
    # Strip project prefix if present (output files include it but file_pattern shouldn't).
    # First try the current project, then check all projects in case it's cross-project.
    target_proj = proj
    safe = _strip_project_prefix(safe, repo, proj)
    # If safe still doesn't resolve, check if it matches a different project
    from pathlib import Path as _P
    _outputs_dir = _P("results/outputs") / atype / repo
    if _outputs_dir.exists():
        meta_file = data_dir(repo, proj, "baselines") / "metadata.json"
        pp_prefix = ""
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                pp = meta.get("project_path", "")
                if pp and pp != ".":
                    pp_prefix = pp.replace("/", "_").replace("\\", "_") + "_"
            except Exception:
                pass
        expected = _outputs_dir / (pp_prefix + safe + ".json")
        if not expected.exists():
            # Try to find the correct project by matching output files
            repo_dir = DATA_DIR / repo
            if repo_dir.is_dir():
                for pdir in sorted(repo_dir.iterdir()):
                    if not pdir.is_dir() or pdir.name == proj:
                        continue
                    pmeta = pdir / "baselines" / "metadata.json"
                    if not pmeta.exists():
                        continue
                    try:
                        pm = json.loads(pmeta.read_text())
                    except Exception:
                        continue
                    ppp = pm.get("project_path", "")
                    if ppp and ppp != ".":
                        p_prefix = ppp.replace("/", "_").replace("\\", "_") + "_"
                    else:
                        p_prefix = ""
                    candidate_fp = _strip_project_prefix(safe, repo, pdir.name)
                    candidate = _outputs_dir / (p_prefix + candidate_fp + ".json")
                    if candidate.exists():
                        target_proj = pdir.name
                        safe = candidate_fp
                        break

    if dry_run:
        print(f"  {finding_id}: {len(assertions)} assertions "
              f"({aspirational} aspirational) -> {safe}")
        return len(assertions), aspirational

    assertion_data = {
        "file_pattern": safe,
        "analyzer_type": atype,
        "created_from": finding_id,
        "generated_by": "findings.py promote",
        "assertions": assertions,
    }

    # Write to data/{repo}/{project}/assertions/{type}/
    # Use target_proj which may differ from proj for cross-project assertions
    out_dir = data_dir(repo, target_proj, "assertions") / atype
    out_dir.mkdir(parents=True, exist_ok=True)
    # Use _finding suffix to avoid collision with seed assertions
    out_file = out_dir / f"{safe}_finding.json"

    # Merge with existing if present
    if out_file.exists():
        existing = json.loads(out_file.read_text())
        existing_ids = {a["id"] for a in existing.get("assertions", [])}
        new_assertions = [a for a in assertions if a["id"] not in existing_ids]
        existing["assertions"].extend(new_assertions)
        assertion_data = existing

    out_file.write_text(json.dumps(assertion_data, indent=2) + "\n")

    # Update finding status
    finding["status"] = "promoted"
    save_findings(repo_name, project_name, data)

    return len(assertions), aspirational


def promote_all(repo_name=None, status_filter=None, dry_run=True):
    """Promote all findings with should_become_assertion=true.

    Returns (findings_promoted, total_assertions, total_aspirational).
    """
    all_data = load_findings(repo_name)
    findings = all_data.get("findings", [])

    if status_filter:
        findings = [f for f in findings if f.get("status") == status_filter]

    # Filter to promotable findings
    promotable = [f for f in findings
                  if f.get("should_become_assertion")
                  and f.get("status") not in ("promoted",)]

    if not promotable:
        print("No promotable findings found.")
        return 0, 0, 0

    total_assertions = 0
    total_aspirational = 0
    promoted_count = 0

    for f in promotable:
        fid = f.get("id")
        if not fid:
            continue
        result = promote_to_assertion(fid, dry_run=dry_run)
        if result and result[0] > 0:
            total_assertions += result[0]
            total_aspirational += result[1]
            promoted_count += 1

    return promoted_count, total_assertions, total_aspirational


def main():
    parser = argparse.ArgumentParser(description="Manage review findings")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List findings")
    show_p = sub.add_parser("show", help="Show a finding")
    show_p.add_argument("id", help="Finding ID (e.g., FND-00000001)")
    promote_p = sub.add_parser("promote", help="Promote finding to assertion")
    promote_p.add_argument("id", help="Finding ID")
    promote_all_p = sub.add_parser("promote-all",
                                   help="Promote all promotable findings")
    promote_all_p.add_argument("--repo", help="Filter by repo name")
    promote_all_p.add_argument("--status", help="Filter by finding status")
    promote_all_p.add_argument("--apply", action="store_true",
                               help="Write changes (default is dry-run)")
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
            if "id" not in f:
                continue
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

    elif args.command == "promote-all":
        dry_run = not getattr(args, "apply", False)
        repo = getattr(args, "repo", None)
        status = getattr(args, "status", None)
        if dry_run:
            print("[DRY RUN] Promotable findings:\n")
        promoted, total_ast, aspirational = promote_all(
            repo, status, dry_run=dry_run)
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
        print(f"  Findings promoted: {promoted}")
        print(f"  Assertions generated: {total_ast}")
        print(f"  Aspirational (expected to fail): {aspirational}")
        if dry_run and promoted > 0:
            print("\nRun with --apply to write changes.")

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
