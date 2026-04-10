#!/usr/bin/env python3
"""One-shot migration: rename reference/ project dirs using the new TH-013 project_key().

For each reference/{owner}/{repo}/{old_key}/ directory:
  1. Reconstruct (pdir, stem) from baselines/metadata.json. New-format snapshots
     have a `stem` field directly; older snapshots are missing it, in which case
     we look up the .kicad_pro stem by checking repos/{owner}/{repo}/{pdir}/.
  2. Compute new_key = project_key(pdir, stem)
  3. If new_key != old_key, `git mv old_key new_key`

Usage:
    python3 tools/migrate_th013_rename.py --dry-run           # preview only (default)
    python3 tools/migrate_th013_rename.py --apply             # execute renames
    python3 tools/migrate_th013_rename.py --apply --repo owner/repo  # one repo only
"""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))

from utils import DATA_DIR, REPOS_DIR, project_key, _truncate_with_hash, _NAME_HASH_LEN, NAME_MAX_BYTES

# Reserved names at repo level that are not project directories.
# Some old-layout reference snapshots put assertions/ and baselines/ directly
# under reference/{owner}/{repo}/ instead of under a {project_key}/ subdirectory.
# These should be skipped by the walker — they're not project directories.
RESERVED_REPO_LEVEL_NAMES = frozenset({"assertions", "baselines"})


def _is_empty_shell(proj_dir: Path) -> bool:
    """True if `proj_dir` contains no files anywhere (may have empty subdirs)."""
    return not any(p.is_file() for p in proj_dir.rglob("*"))


def _find_stem_in_repos(owner_repo: str, pdir: str) -> str | None:
    """Look up the .kicad_pro/.kicad_pcb/.pro stem by checking repos/{owner}/{repo}/{pdir}/."""
    repo_dir = REPOS_DIR / owner_repo
    if not repo_dir.exists():
        return None
    project_dir = repo_dir / pdir if pdir and pdir != "." else repo_dir
    if not project_dir.exists():
        return None
    # Prefer .kicad_pro, fall back to .kicad_pcb, then .pro
    for pattern in ("*.kicad_pro", "*.kicad_pcb", "*.pro"):
        for pro in sorted(project_dir.glob(pattern)):
            return pro.stem
    return None


def _reconstruct_pdir_stem(proj_dir: Path, owner_repo: str) -> tuple[str, str] | None:
    """Read metadata.json to get (pdir, stem); fall back to repos/ lookup, then
    to directory-name reverse-engineering for old snapshots whose repo state has
    drifted from the snapshot time."""
    meta_path = proj_dir / "baselines" / "metadata.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    pdir = meta.get("project_path") or meta.get("pdir") or "."
    stem = meta.get("stem")  # new format (Task 4) — may be absent on old snapshots
    if not stem:
        stem = _find_stem_in_repos(owner_repo, pdir)
    if not stem:
        # Final fallback: reverse-engineer stem from the old directory name.
        # Old format was `pdir_flat + "_" + stem` where pdir_flat = pdir.replace("/","_").
        # For root projects (pdir == "."), old_name was just the stem.
        old_name = proj_dir.name
        if pdir and pdir != ".":
            pdir_flat = pdir.replace("/", "_").replace("\\", "_")
            if old_name == pdir_flat:
                # No stem was ever appended — old code would only produce this if
                # pdir == stem, i.e., the stem-dedup case.
                from pathlib import PurePosixPath
                stem = PurePosixPath(pdir).name
            elif old_name.startswith(pdir_flat + "_"):
                stem = old_name[len(pdir_flat) + 1:]
        else:
            stem = old_name
    if not stem:
        # Truly unresolvable — skip
        return None
    return (pdir, stem)


def _orphan_new_name(old_name: str) -> str | None:
    """Best-effort new name for an orphan directory (no metadata.json).

    Applies two transformations:
    1. Stem deduplication: if the directory name ends with a repeated token
       sequence (e.g., `foo_bar_bar` or `a_b_c_b_c`), drop the trailing duplicate.
       This mirrors the `project_key` stem dedup for orphans whose pdir/stem
       cannot be reconstructed from metadata.
    2. Length cap: if the result still exceeds NAME_MAX_BYTES, apply
       `_truncate_with_hash` to produce a deterministic short name.

    Returns the new name if it differs from old_name, else None.
    """
    new_name = old_name

    # Step 1: stem deduplication via trailing-duplicate pattern detection
    tokens = new_name.split("_")
    for k in range(1, len(tokens) // 2 + 1):
        if tokens[-k:] == tokens[-2 * k:-k]:
            new_name = "_".join(tokens[:-k])
            break

    # Step 2: length cap
    if len(new_name.encode("utf-8")) > NAME_MAX_BYTES:
        new_name = _truncate_with_hash(new_name)

    return new_name if new_name != old_name else None


def _compute_renames_for_repo(repo_dir: Path, owner_repo: str, skipped: list) -> list:
    """Compute renames for a single repo, applying conflict disambiguation.

    If two or more projects in the same repo produce the same new_key, ALL of
    them get a path-derived hash suffix (mirroring discover_projects() in utils.py).
    """
    # Gather proper candidates (reconstructible from metadata) and orphans separately
    candidates = []
    orphans = []
    for proj_dir in sorted(repo_dir.iterdir()):
        if not proj_dir.is_dir() or proj_dir.name.startswith("."):
            continue
        # Skip reserved names (old-layout data dirs misplaced at repo level)
        if proj_dir.name in RESERVED_REPO_LEVEL_NAMES:
            continue
        reconstructed = _reconstruct_pdir_stem(proj_dir, owner_repo)
        if reconstructed is None:
            orphans.append(proj_dir)
            continue
        pdir, stem = reconstructed
        base_new_key = project_key(pdir, stem)
        candidates.append({"proj_dir": proj_dir, "pdir": pdir, "stem": stem, "new_key": base_new_key})

    # Detect collisions and disambiguate symmetrically. Unlike discover_projects
    # which hashes on pdir, migration hashes on the OLD directory name to handle
    # stale data: two projects with the same reconstructed (pdir, stem) can exist
    # when the repo has been restructured since an old snapshot. Old directory
    # names are guaranteed unique by filesystem constraint.
    name_counts = Counter(c["new_key"] for c in candidates)
    if any(count > 1 for count in name_counts.values()):
        for c in candidates:
            if name_counts[c["new_key"]] > 1:
                old_name_hash = hashlib.sha1(c["proj_dir"].name.encode("utf-8")).hexdigest()[:_NAME_HASH_LEN]
                c["new_key"] = _truncate_with_hash(f"{c['new_key']}_{old_name_hash}")

    # Emit renames for changed keys only
    renames = []
    for c in candidates:
        old_key = c["proj_dir"].name
        if c["new_key"] != old_key:
            renames.append((c["proj_dir"], c["proj_dir"].parent / c["new_key"], c["pdir"], c["stem"]))

    # Orphan pass: apply best-effort name fix-up without colliding with proper projects
    # or other orphans. Build the set of names that will exist in this repo AFTER the
    # proper-project renames are applied.
    final_names = set()
    for c in candidates:
        final_names.add(c["new_key"])
    for proj_dir in orphans:
        # If orphan's old name doesn't collide with anything, it stays as-is
        final_names.add(proj_dir.name)

    for proj_dir in orphans:
        old_name = proj_dir.name
        # Skip empty-shell orphans — those are handled by the delete pass
        if _is_empty_shell(proj_dir):
            continue
        new_name = _orphan_new_name(old_name)
        if new_name is None:
            skipped.append(str(proj_dir.relative_to(DATA_DIR)))
            continue
        # Avoid creating a collision with a proper-project new name or another orphan's
        # (post-rename) name
        if new_name in final_names and new_name != old_name:
            # Collision — append an old-name hash to disambiguate deterministically
            old_hash = hashlib.sha1(old_name.encode("utf-8")).hexdigest()[:_NAME_HASH_LEN]
            new_name = _truncate_with_hash(f"{new_name}_{old_hash}")
        final_names.discard(old_name)
        final_names.add(new_name)
        renames.append((proj_dir, proj_dir.parent / new_name, ".", f"orphan:{old_name[:40]}"))

    return renames


def _find_empty_orphans(repo_filter: str | None) -> list[Path]:
    """Find orphan directories that are truly empty (0 files anywhere inside).

    These are leftover dir shells from prior incomplete operations. Safe to
    remove via rmdir/rm -r — they have no data and aren't tracked by git.
    """
    empties = []
    if not DATA_DIR.exists():
        return empties
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            owner_repo = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and owner_repo != repo_filter:
                continue
            for proj_dir in sorted(repo_dir.iterdir()):
                if not proj_dir.is_dir() or proj_dir.name.startswith("."):
                    continue
                if proj_dir.name in RESERVED_REPO_LEVEL_NAMES:
                    continue
                # Orphan = no metadata.json or empty metadata.json
                meta = proj_dir / "baselines" / "metadata.json"
                if meta.exists() and meta.stat().st_size > 0:
                    continue
                # Empty shell (no files anywhere) → delete
                if _is_empty_shell(proj_dir):
                    empties.append(proj_dir)
    return empties


def _find_long_basename_files(repo_filter: str | None) -> list[tuple[Path, Path]]:
    """Walk DATA_DIR and find tracked files whose basename exceeds NAME_MAX_BYTES.

    Returns a list of (old_path, new_path) tuples. Does NOT apply any rename.
    The new basename is computed via `_truncate_with_hash(old_basename)`.
    """
    renames = []
    if not DATA_DIR.exists():
        return renames
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            owner_repo = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and owner_repo != repo_filter:
                continue
            for f in repo_dir.rglob("*"):
                if not f.is_file():
                    continue
                basename = f.name
                if len(basename.encode("utf-8")) > NAME_MAX_BYTES:
                    new_basename = _truncate_with_hash(basename)
                    renames.append((f, f.parent / new_basename))
    return renames


def _delete_empties(empties: list[Path]) -> bool:
    print(f"\nDeleting {len(empties)} empty orphan directories...")
    for i, p in enumerate(empties, 1):
        try:
            # Walk bottom-up and rmdir each empty dir
            for sub in sorted(p.rglob("*"), reverse=True):
                if sub.is_dir():
                    try:
                        sub.rmdir()
                    except OSError:
                        pass
            p.rmdir()
        except OSError as e:
            print(f"  [{i}/{len(empties)}] FAILED to delete {p.relative_to(DATA_DIR)}: {e}",
                  file=sys.stderr)
            return False
        if i % 50 == 0:
            print(f"  [{i}/{len(empties)}]")
    print(f"Deleted {len(empties)} empty orphan directories.")
    return True


def _apply_file_renames(file_renames: list[tuple[Path, Path]]) -> bool:
    print(f"\nApplying {len(file_renames)} file basename renames via git mv...")
    applied = 0
    skipped = 0
    for i, (old_path, new_path) in enumerate(file_renames, 1):
        if not old_path.exists():
            # Old path no longer exists (parent dir may have been renamed in a prior pass).
            # Try to locate the file under the current tree by searching for the basename.
            # This is a safety net for the dir-rename-then-file-rename interaction.
            print(f"  [{i}/{len(file_renames)}] SKIP — old path no longer exists: "
                  f"{old_path.relative_to(DATA_DIR)}", file=sys.stderr)
            skipped += 1
            continue
        if new_path.exists():
            print(f"  [{i}/{len(file_renames)}] SKIP — target exists: "
                  f"{new_path.relative_to(DATA_DIR)}", file=sys.stderr)
            skipped += 1
            continue
        result = subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            cwd=HARNESS_DIR, capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  [{i}/{len(file_renames)}] FAILED: {result.stderr.strip()}", file=sys.stderr)
            return False
        applied += 1
    if skipped:
        print(f"Applied {applied}/{len(file_renames)} file renames ({skipped} skipped).")
    else:
        print(f"All {applied} file renames applied.")
    return True


def _compute_renames(repo_filter: str | None):
    """Return a list of (old_path, new_path, pdir, stem) tuples for dirs that need renaming."""
    renames = []
    skipped_no_meta = []
    if not DATA_DIR.exists():
        print(f"ERROR: {DATA_DIR} does not exist", file=sys.stderr)
        return [], []
    for owner_dir in sorted(DATA_DIR.iterdir()):
        if not owner_dir.is_dir() or owner_dir.name.startswith("."):
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            owner_repo = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and owner_repo != repo_filter:
                continue
            renames.extend(_compute_renames_for_repo(repo_dir, owner_repo, skipped_no_meta))
    return renames, skipped_no_meta


def _print_report(renames, skipped_no_meta):
    print(f"Found {len(renames)} directories needing rename")
    print(f"Skipped (no metadata or stem unresolvable): {len(skipped_no_meta)}")
    if skipped_no_meta:
        print("  first 5 skipped:")
        for s in skipped_no_meta[:5]:
            print(f"    {s}")
    print()
    for old_path, new_path, pdir, stem in renames[:20]:
        rel = old_path.relative_to(DATA_DIR)
        print(f"  {rel}")
        print(f"    → {new_path.name}")
        print(f"      (pdir={pdir}, stem={stem})")
    if len(renames) > 20:
        print(f"  ... and {len(renames) - 20} more")


def _apply_renames(renames):
    print(f"\nApplying {len(renames)} renames via git mv...")
    applied = 0
    skipped = 0
    for i, (old_path, new_path, _, _) in enumerate(renames, 1):
        if new_path.exists():
            print(f"  [{i}/{len(renames)}] SKIP — target exists: {new_path.relative_to(DATA_DIR)}",
                  file=sys.stderr)
            skipped += 1
            continue
        result = subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            cwd=HARNESS_DIR, capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  [{i}/{len(renames)}] FAILED: {result.stderr.strip()}", file=sys.stderr)
            print(f"  Failed after {applied} successful renames. Run 'git status' to inspect state.",
                  file=sys.stderr)
            return False
        applied += 1
        if i % 100 == 0:
            print(f"  [{i}/{len(renames)}]")
    if skipped:
        print(f"Applied {applied}/{len(renames)} renames ({skipped} skipped — target existed).")
    else:
        print(f"All {applied} renames applied.")
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Rename reference/ project dirs using the new TH-013 project_key().",
    )
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="Preview renames without executing (default)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually execute changes (overrides --dry-run)")
    ap.add_argument("--repo", help="Only migrate this owner/repo")
    args = ap.parse_args()

    # Compute all three passes from current state
    dir_renames, skipped_no_meta = _compute_renames(repo_filter=args.repo)
    empties = _find_empty_orphans(repo_filter=args.repo)
    file_renames = _find_long_basename_files(repo_filter=args.repo)

    # Report
    _print_report(dir_renames, skipped_no_meta)
    print(f"\nEmpty orphan directories to delete: {len(empties)}")
    for p in empties[:5]:
        print(f"  {p.relative_to(DATA_DIR)}")
    if len(empties) > 5:
        print(f"  ... and {len(empties) - 5} more")
    print(f"\nLong-basename files to rename: {len(file_renames)}")
    for old_path, new_path in file_renames[:5]:
        print(f"  {old_path.relative_to(DATA_DIR)}")
        print(f"    → {new_path.name[:80]}")
    if len(file_renames) > 5:
        print(f"  ... and {len(file_renames) - 5} more")

    if args.apply:
        # Order: delete empties → rename dirs → rename files (recomputed from new state)
        if not _delete_empties(empties):
            sys.exit(1)
        if not _apply_renames(dir_renames):
            sys.exit(1)
        # Recompute file renames after dir moves so paths are current
        file_renames_after = _find_long_basename_files(repo_filter=args.repo)
        if not _apply_file_renames(file_renames_after):
            sys.exit(1)
        print("\nMigration complete.")


if __name__ == "__main__":
    main()
