#!/usr/bin/env python3
"""Take a snapshot of current analyzer outputs as a baseline.

Creates per-project baselines in data/{repo}/{project}/baselines/
with compact manifest entries for each analyzer type.

Usage:
    python3 regression/snapshot.py --repo OpenMower
    python3 regression/snapshot.py --all
    python3 regression/snapshot.py --list
    python3 regression/snapshot.py --delete OpenMower
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _differ import extract_manifest_entry
from utils import (
    HARNESS_DIR, OUTPUTS_DIR, DATA_DIR, ANALYZER_TYPES,
    list_repos, discover_projects, data_dir, list_projects_in_data,
    project_prefix,
)


def _get_analyzer_commit():
    kicad_happy = Path(os.environ.get(
        "KICAD_HAPPY_DIR", str(HARNESS_DIR / ".." / "kicad-happy")
    ))
    if (kicad_happy / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(kicad_happy), capture_output=True, text=True,
            )
            return result.stdout.strip()
        except Exception:
            pass
    return None


def create_snapshot(repo_name):
    """Create baseline snapshots for all projects in a repo."""
    projects = discover_projects(repo_name)
    if not projects:
        print(f"  {repo_name}: no projects found")
        return 0

    analyzer_commit = _get_analyzer_commit()
    created = 0

    for proj in projects:
        proj_name = proj["name"]
        proj_path = proj["path"]
        baseline_dir = data_dir(repo_name, proj_name, "baselines")

        metadata = {
            "repo": repo_name,
            "project": proj_name,
            "project_path": proj_path,
            "created": datetime.now(timezone.utc).isoformat(),
            "analyzer_commit": analyzer_commit,
            "file_counts": {},
        }

        total_files = 0
        baseline_dir.mkdir(parents=True, exist_ok=True)
        for atype in ANALYZER_TYPES:
            type_dir = OUTPUTS_DIR / atype / repo_name
            if not type_dir.exists():
                continue

            # Filter output files to this project: files whose safe_name
            # starts with the project path prefix
            prefix = project_prefix(proj_path)

            json_files = sorted(type_dir.glob("*.json"))
            project_files = []
            for jf in json_files:
                if prefix:
                    if jf.name.startswith(prefix):
                        project_files.append(jf)
                else:
                    project_files.append(jf)

            if not project_files:
                continue

            metadata["file_counts"][atype] = len(project_files)
            total_files += len(project_files)

            manifest = {}
            for jf in project_files:
                # Key is the within-project filename
                if prefix:
                    key = jf.name[len(prefix):]
                else:
                    key = jf.name
                try:
                    d = json.loads(jf.read_text())
                    manifest[key] = extract_manifest_entry(d, atype)
                except Exception as e:
                    manifest[key] = {"error": str(e)}

            (baseline_dir / f"{atype}.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        if total_files == 0:
            continue

        (baseline_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n")
        print(f"  {repo_name}/{proj_name}: {total_files} files")
        created += 1

    return created


def list_snapshots():
    if not DATA_DIR.exists():
        print("No baselines found.")
        return

    print(f"{'Repo':<25s} {'Project':<30s} {'Created':<22s} {'Files':<6s} Analyzer")
    print("-" * 100)

    for repo_dir in sorted(DATA_DIR.iterdir()):
        if not repo_dir.is_dir():
            continue
        for proj_dir in sorted(repo_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            meta_file = proj_dir / "baselines" / "metadata.json"
            if not meta_file.exists():
                continue
            meta = json.loads(meta_file.read_text())
            total = sum(meta.get("file_counts", {}).values())
            commit = (meta.get("analyzer_commit") or "unknown")[:12]
            created = meta["created"][:19].replace("T", " ")
            print(f"{repo_dir.name:<25s} {proj_dir.name:<30s} {created:<22s} {total:<6d} {commit}")


def delete_snapshot(repo_name):
    repo_data = DATA_DIR / repo_name
    if not repo_data.exists():
        print(f"No data for '{repo_name}' found.")
        return
    deleted = 0
    for proj_dir in sorted(repo_data.iterdir()):
        if not proj_dir.is_dir():
            continue
        bl_dir = proj_dir / "baselines"
        if bl_dir.exists():
            shutil.rmtree(bl_dir)
            deleted += 1
    print(f"Deleted baselines for {deleted} project(s) in {repo_name}")


def main():
    parser = argparse.ArgumentParser(description="Manage per-project baseline snapshots")
    parser.add_argument("--repo", help="Snapshot a single repo")
    parser.add_argument("--all", action="store_true", help="Snapshot all repos with outputs")
    parser.add_argument("--list", action="store_true", help="List all baselines")
    parser.add_argument("--delete", metavar="REPO", help="Delete a repo's baselines")
    args = parser.parse_args()

    if args.list:
        list_snapshots()
        return

    if args.delete:
        delete_snapshot(args.delete)
        return

    if args.repo:
        repos = [args.repo]
    elif args.all:
        repos = list_repos()
    else:
        parser.print_help()
        sys.exit(1)

    if not OUTPUTS_DIR.exists():
        print("Error: No analyzer outputs found. Run the analyzers first.")
        sys.exit(1)

    print("=== Creating baseline snapshots ===")
    total = 0
    for repo in repos:
        total += create_snapshot(repo)

    print(f"\n{total} project baseline(s) created")


if __name__ == "__main__":
    main()
