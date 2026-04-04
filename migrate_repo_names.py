#!/usr/bin/env python3
"""One-time migration: rename repo directories from {repo} to {owner}/{repo}.

Renames directories under repos/, results/outputs/*, results/manifests/,
and reference/. Updates JSON data files with embedded repo name fields.

Usage:
    python3 migrate_repo_names.py --dry-run     # Preview all changes
    python3 migrate_repo_names.py --apply       # Execute migration
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import HARNESS_DIR

REPOS_MD = HARNESS_DIR / "repos.md"
REPOS_DIR = HARNESS_DIR / "repos"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"
REFERENCE_DIR = HARNESS_DIR / "reference"
SMOKE_PACK = REFERENCE_DIR / "smoke_pack.md"
BUGFIX_REGISTRY = HARNESS_DIR / "regression" / "bugfix_registry.json"
CATALOG_JSON = REFERENCE_DIR / "repo_catalog.json"


def _parse_repos_md():
    """Parse repos.md to build {old_name: owner/repo} mapping."""
    mapping = {}
    for line in REPOS_MD.read_text().splitlines():
        line = line.strip()
        if not line.startswith("- http"):
            continue
        # Extract URL (everything between "- " and " @" or end of line)
        url = line[2:].split(" @")[0].split(" (")[0].strip()
        parts = url.rstrip("/").removesuffix(".git").split("/")
        if len(parts) < 2:
            continue
        owner = parts[-2]
        repo = parts[-1]
        old_name = repo
        new_name = f"{owner}/{repo}"
        mapping[old_name] = new_name
    return mapping


def _rename_dirs(base_dir, mapping, dry_run):
    """Rename flat {repo} dirs to {owner}/{repo} under base_dir."""
    if not base_dir.exists():
        return 0, 0
    renamed = skipped = 0
    for old_name, new_name in sorted(mapping.items()):
        old_path = base_dir / old_name
        new_path = base_dir / new_name
        if not old_path.exists() or not old_path.is_dir():
            continue
        if new_path.exists():
            skipped += 1
            continue
        if dry_run:
            print(f"  RENAME {old_path.relative_to(HARNESS_DIR)} -> {new_path.relative_to(HARNESS_DIR)}")
        else:
            # Handle case where owner == repo (e.g., dc-power-supply/dc-power-supply)
            # Can't rename dir into itself, so use a temp name first
            owner_dir = new_path.parent
            if old_path == owner_dir:
                tmp = old_path.with_name(old_path.name + "__migrating")
                old_path.rename(tmp)
                owner_dir.mkdir(parents=True, exist_ok=True)
                tmp.rename(new_path)
            else:
                owner_dir.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
        renamed += 1
    return renamed, skipped


def _update_json_field(filepath, field_path, mapping, dry_run):
    """Update a 'repo' field in a JSON file using the mapping."""
    try:
        data = json.loads(filepath.read_text())
    except (json.JSONDecodeError, OSError):
        return False

    changed = False

    if isinstance(data, list):
        # bugfix_registry.json is a list of entries
        for entry in data:
            for ast_def in entry.get("assertions", []):
                old = ast_def.get("repo", "")
                if old in mapping:
                    ast_def["repo"] = mapping[old]
                    changed = True
    elif isinstance(data, dict):
        # metadata.json, catalog entries
        old = data.get("repo", "")
        if old in mapping:
            data["repo"] = mapping[old]
            changed = True
        # findings.json
        for item in data.get("findings", []):
            old = item.get("repo", "")
            if old in mapping:
                item["repo"] = mapping[old]
                changed = True

    if changed:
        if dry_run:
            print(f"  UPDATE {filepath.relative_to(HARNESS_DIR)}")
        else:
            filepath.write_text(json.dumps(data, indent=2) + "\n")
    return changed


def _update_smoke_pack(mapping, dry_run):
    """Update smoke_pack.md with owner/repo names."""
    if not SMOKE_PACK.exists():
        return 0
    lines = SMOKE_PACK.read_text().splitlines()
    new_lines = []
    updated = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped in mapping:
            new_lines.append(mapping[stripped])
            updated += 1
        else:
            new_lines.append(line)
    if updated > 0:
        if dry_run:
            print(f"  UPDATE smoke_pack.md ({updated} entries)")
        else:
            SMOKE_PACK.write_text("\n".join(new_lines) + "\n")
    return updated


def _update_catalog(mapping, dry_run):
    """Update repo_catalog.json with owner/repo names."""
    if not CATALOG_JSON.exists():
        return 0
    try:
        catalog = json.loads(CATALOG_JSON.read_text())
    except (json.JSONDecodeError, OSError):
        return 0
    updated = 0
    for entry in catalog:
        old = entry.get("repo", "")
        if old in mapping:
            entry["repo"] = mapping[old]
            updated += 1
    if updated > 0:
        if dry_run:
            print(f"  UPDATE repo_catalog.json ({updated} entries)")
        else:
            CATALOG_JSON.write_text(json.dumps(catalog, indent=2, sort_keys=False) + "\n")
    return updated


def migrate(dry_run=True):
    """Run the full migration."""
    mapping = _parse_repos_md()
    print(f"Migration mapping: {len(mapping)} repos")

    # Handle duplicate old names (8 collisions)
    # For collisions, we need to figure out which dir belongs to which owner
    # by checking the git remote URL in the cloned repo
    dupes = {}
    seen = {}
    for old_name, new_name in list(mapping.items()):
        if old_name in seen:
            dupes.setdefault(old_name, [seen[old_name]]).append(new_name)
        seen[old_name] = new_name

    if dupes:
        print(f"\n  {len(dupes)} duplicate repo names (will resolve via git remote):")
        for old_name, new_names in dupes.items():
            print(f"    {old_name} -> {new_names}")

    # For duplicates, we can't use the simple mapping. We need to check which
    # owner the existing repo belongs to by reading git config.
    # Build a refined mapping that handles duplicates correctly.
    refined = {}
    all_entries = []
    for line in REPOS_MD.read_text().splitlines():
        line = line.strip()
        if not line.startswith("- http"):
            continue
        url = line[2:].split(" @")[0].split(" (")[0].strip()
        parts = url.rstrip("/").removesuffix(".git").split("/")
        if len(parts) < 2:
            continue
        owner = parts[-2]
        repo = parts[-1]
        all_entries.append((repo, owner, f"{owner}/{repo}"))

    # Count occurrences of each repo name
    name_counts = {}
    for repo, owner, new_name in all_entries:
        name_counts[repo] = name_counts.get(repo, 0) + 1

    # For non-duplicate names, simple mapping works
    for repo, owner, new_name in all_entries:
        if name_counts[repo] == 1:
            refined[repo] = new_name

    total_renamed = 0
    total_skipped = 0

    # 1. Rename repos/ directories (non-duplicates first)
    print(f"\n=== Renaming repos/ ===")
    r, s = _rename_dirs(REPOS_DIR, refined, dry_run)
    total_renamed += r
    total_skipped += s
    print(f"  {r} renamed, {s} skipped")

    # Handle duplicates: check git remote to identify correct owner
    if dupes:
        print(f"\n=== Resolving {len(dupes)} duplicate repos/ via git remote ===")
        for old_name, new_names in dupes.items():
            old_path = REPOS_DIR / old_name
            if not old_path.exists():
                print(f"  SKIP {old_name} (not cloned)")
                continue
            # Read git remote URL
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True, text=True, cwd=str(old_path), timeout=5)
                remote_url = result.stdout.strip()
            except Exception:
                remote_url = ""
            # Match URL to find correct owner
            matched = None
            for repo, owner, new_name in all_entries:
                if repo == old_name and remote_url and owner in remote_url:
                    matched = new_name
                    break
            if matched:
                new_path = REPOS_DIR / matched
                if not new_path.exists():
                    if dry_run:
                        print(f"  RENAME {old_name} -> {matched} (via git remote)")
                    else:
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        old_path.rename(new_path)
                    total_renamed += 1
            else:
                print(f"  WARN: {old_name} could not resolve owner from remote URL: {remote_url}")

    # 2. Rename results/outputs/{type}/ directories
    output_types = ["schematic", "pcb", "gerber", "emc", "spice", "spice-parasitics", "datasheets"]
    for otype in output_types:
        type_dir = OUTPUTS_DIR / otype
        if type_dir.exists():
            print(f"\n=== Renaming outputs/{otype}/ ===")
            r, s = _rename_dirs(type_dir, refined, dry_run)
            total_renamed += r
            print(f"  {r} renamed, {s} skipped")

    # 3. Rename results/manifests/ directories
    print(f"\n=== Renaming manifests/ ===")
    r, s = _rename_dirs(MANIFESTS_DIR, refined, dry_run)
    total_renamed += r
    print(f"  {r} renamed, {s} skipped")

    # 4. Rename reference/ directories
    print(f"\n=== Renaming reference/ ===")
    # Skip non-repo dirs/files in reference/
    skip_names = {
        "health_log.jsonl", "health_baseline.json", "schema_inventory.json",
        "constants_registry.json", "constants_registry.md", "equation_registry.json",
        "equation_registry.md", "test_mpns.json", "repo_catalog.json", "repo_catalog.md",
        "smoke_pack.md",
    }
    ref_mapping = {k: v for k, v in refined.items()
                   if (REFERENCE_DIR / k).exists() and k not in skip_names}
    r, s = _rename_dirs(REFERENCE_DIR, ref_mapping, dry_run)
    total_renamed += r
    print(f"  {r} renamed, {s} skipped")

    # 5. Update JSON data files
    print(f"\n=== Updating data files ===")

    # bugfix_registry.json
    if BUGFIX_REGISTRY.exists():
        _update_json_field(BUGFIX_REGISTRY, "repo", refined, dry_run)

    # metadata.json files (now under owner/repo structure)
    search_dir = REFERENCE_DIR
    for meta_file in search_dir.rglob("baselines/metadata.json"):
        _update_json_field(meta_file, "repo", refined, dry_run)

    # findings.json files
    for findings_file in search_dir.rglob("findings.json"):
        _update_json_field(findings_file, "repo", refined, dry_run)

    # repo_catalog.json
    _update_catalog(refined, dry_run)

    # smoke_pack.md
    _update_smoke_pack(refined, dry_run)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"{'[DRY RUN] ' if dry_run else ''}Migration summary:")
    print(f"  Directories renamed: {total_renamed}")
    if not dry_run:
        print(f"\nNext steps:")
        print(f"  python3 discover.py              # Regenerate manifests")
        print(f"  python3 generate_catalog.py      # Regenerate catalog")
        print(f"  python3 run_tests.py --unit      # Verify tests pass")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate repo directories from {repo} to {owner}/{repo}")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without applying")
    parser.add_argument("--apply", action="store_true",
                        help="Execute the migration")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        sys.exit(1)

    migrate(dry_run=not args.apply)


if __name__ == "__main__":
    main()
