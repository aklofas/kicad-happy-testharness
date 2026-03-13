#!/usr/bin/env python3
"""Take a snapshot of current analyzer outputs as a baseline.

Creates two things:
1. A compact baseline manifest (checked into git in data/baselines/)
   containing essential facts — counts, detection lists, sections.
2. Optionally, a full copy of outputs in results/baselines/ (git-ignored)
   for detailed local diffing.

Usage:
    python3 baselines/snapshot.py <name>
    python3 baselines/snapshot.py <name> --full
    python3 baselines/snapshot.py --list
    python3 baselines/snapshot.py --delete <name>
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR / "baselines"))
from _differ import extract_manifest_entry

OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
MANIFESTS_BASE = HARNESS_DIR / "data" / "baselines"
FULL_BASE = HARNESS_DIR / "results" / "baselines"
ANALYZER_TYPES = ["schematic", "pcb", "gerber"]


def _valid_name(name):
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def _get_analyzer_commit():
    """Get the kicad-happy analyzer commit hash if available."""
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


def _load_corpus_state():
    state_file = HARNESS_DIR / "repos_state.json"
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {}


def create_snapshot(name, full_copy=False):
    """Create a baseline snapshot."""
    manifest_dir = MANIFESTS_BASE / name
    if manifest_dir.exists():
        print(f"Error: Baseline '{name}' already exists. Delete it first.")
        sys.exit(1)

    manifest_dir.mkdir(parents=True)

    metadata = {
        "name": name,
        "created": datetime.now(timezone.utc).isoformat(),
        "analyzer_commit": _get_analyzer_commit(),
        "corpus_state": _load_corpus_state(),
        "file_counts": {},
    }

    total_files = 0
    for atype in ANALYZER_TYPES:
        type_dir = OUTPUTS_DIR / atype
        if not type_dir.exists():
            continue

        json_files = sorted(type_dir.glob("*.json"))
        metadata["file_counts"][atype] = len(json_files)
        total_files += len(json_files)

        # Build manifest: compact entry per file
        manifest = {}
        for jf in json_files:
            try:
                data = json.loads(jf.read_text())
                manifest[jf.name] = extract_manifest_entry(data, atype)
            except Exception as e:
                manifest[jf.name] = {"error": str(e)}

        manifest_file = manifest_dir / f"{atype}.json"
        manifest_file.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(f"  {atype}: {len(json_files)} files")

    # Write metadata
    (manifest_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    # Optional full copy (git-ignored)
    if full_copy:
        full_dir = FULL_BASE / name
        full_dir.mkdir(parents=True, exist_ok=True)
        for atype in ANALYZER_TYPES:
            src = OUTPUTS_DIR / atype
            if src.exists():
                shutil.copytree(src, full_dir / atype, dirs_exist_ok=True)
        print(f"  Full copy: {full_dir}")

    print(f"\nBaseline '{name}' created ({total_files} files)")
    print(f"  Manifest: {manifest_dir} (checked into git)")
    if metadata["analyzer_commit"]:
        print(f"  Analyzer commit: {metadata['analyzer_commit'][:12]}")


def list_snapshots():
    """List all baseline snapshots."""
    if not MANIFESTS_BASE.exists():
        print("No baselines found.")
        return

    baselines = []
    for d in sorted(MANIFESTS_BASE.iterdir()):
        meta_file = d / "metadata.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            baselines.append(meta)

    if not baselines:
        print("No baselines found.")
        return

    print(f"{'Name':<30s} {'Created':<22s} {'Files':<10s} Analyzer")
    print("-" * 80)
    for b in baselines:
        total = sum(b.get("file_counts", {}).values())
        commit = (b.get("analyzer_commit") or "unknown")[:12]
        created = b["created"][:19].replace("T", " ")
        print(f"{b['name']:<30s} {created:<22s} {total:<10d} {commit}")


def delete_snapshot(name):
    """Delete a baseline snapshot."""
    manifest_dir = MANIFESTS_BASE / name
    full_dir = FULL_BASE / name
    deleted = False
    if manifest_dir.exists():
        shutil.rmtree(manifest_dir)
        print(f"Deleted manifest: {manifest_dir}")
        deleted = True
    if full_dir.exists():
        shutil.rmtree(full_dir)
        print(f"Deleted full copy: {full_dir}")
        deleted = True
    if not deleted:
        print(f"Baseline '{name}' not found.")


def main():
    parser = argparse.ArgumentParser(description="Manage baseline snapshots")
    parser.add_argument("name", nargs="?", help="Baseline name")
    parser.add_argument("--list", action="store_true", help="List all baselines")
    parser.add_argument("--delete", metavar="NAME", help="Delete a baseline")
    parser.add_argument("--full", action="store_true",
                        help="Also save full JSON outputs (git-ignored)")
    args = parser.parse_args()

    if args.list:
        list_snapshots()
        return

    if args.delete:
        delete_snapshot(args.delete)
        return

    if not args.name:
        parser.print_help()
        sys.exit(1)

    if not _valid_name(args.name):
        print("Error: Name must be alphanumeric with hyphens/underscores only.")
        sys.exit(1)

    if not OUTPUTS_DIR.exists():
        print("Error: No analyzer outputs found. Run the analyzers first.")
        sys.exit(1)

    create_snapshot(args.name, full_copy=args.full)


if __name__ == "__main__":
    main()
