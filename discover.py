#!/usr/bin/env python3
"""Discover all KiCad files in repos/ and write manifests.

Scans repos/ for schematic, PCB, project, and Gerber files.
Writes file lists to results/manifests/ (flat) and per-repo manifests
to results/manifests/{repo}/.

The flat all_*.txt manifests are always rebuilt from every per-repo manifest
(a --repo run refreshes one repo, then rebuilds the globals), replaced atomically,
and described by census.json: per-file line counts and sha256, plus the census
floor of the last full discover. The corpus gate checks a full run against it.

Usage:
    python3 discover.py
    python3 discover.py --repo OpenMower
"""

import argparse
import contextlib
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils import REPOS_DIR, MANIFESTS_DIR, list_repos, atomic_write_text

# Gerber file extensions to look for
GERBER_EXTENSIONS = {
    ".gbr", ".gtl", ".gbl", ".gts", ".gbs", ".gto", ".gbo",
    ".drl", ".g1", ".g2", ".g3", ".g4",
    ".gtp", ".gbp",  # paste layers
}


def _is_kicad_legacy_sch(path):
    """Check if a .sch file is KiCad legacy format (not Eagle or other EDA).

    KiCad legacy .sch files start with 'EESchema Schematic File'.
    Eagle .sch files are XML (start with '<?xml') or binary.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            header = f.read(64)
        return header.startswith("EESchema")
    except Exception:
        return False


def _admissible(p, scan_dir):
    """A discovered path must stay inside the clone (a symlink may point within it, never
    out of it) and its name must survive one-path-per-line manifests: str.splitlines()
    splits on more than \n, and a split row names a file that does not exist."""
    if p.name.splitlines() != [p.name]:
        print(f"  skip {p!r}: name contains a line delimiter", file=sys.stderr)
        return False
    try:
        real, base = p.resolve(), scan_dir.resolve()
    except OSError:
        return False
    if real != base and base not in real.parents:
        print(f"  skip {p}: resolves outside the clone", file=sys.stderr)
        return False
    return True


def discover_in(scan_dir):
    """Discover KiCad files under a directory. Returns dict of file lists."""
    def found(pattern):
        return [p for p in scan_dir.rglob(pattern) if p.is_file() and _admissible(p, scan_dir)]

    # Schematics: .kicad_sch and .sch (filtered to KiCad format only)
    kicad_sch_files = sorted(str(p) for p in found("*.kicad_sch"))
    legacy_sch_candidates = sorted(str(p) for p in found("*.sch"))
    legacy_sch_files = [s for s in legacy_sch_candidates if _is_kicad_legacy_sch(s)]
    skipped = len(legacy_sch_candidates) - len(legacy_sch_files)
    schematics = sorted(kicad_sch_files + legacy_sch_files)

    # PCBs: .kicad_pcb
    pcbs = sorted(str(p) for p in found("*.kicad_pcb"))  # TH-069

    # Gerber directories — single traversal, case-insensitive
    gerber_exts_lower = {e.lower() for e in GERBER_EXTENSIONS}
    gerber_dirs = set()
    for p in scan_dir.rglob("*"):
        if p.suffix.lower() in gerber_exts_lower and p.is_file() and _admissible(p, scan_dir) \
                and _admissible(p.parent, scan_dir):
            gerber_dirs.add(str(p.parent))
    gerber_dirs = sorted(gerber_dirs)

    # Project files: .kicad_pro
    projects = sorted(str(p) for p in found("*.kicad_pro"))

    return {
        "schematics": schematics,
        "kicad_sch_count": len(kicad_sch_files),
        "legacy_sch_count": len(legacy_sch_files),
        "skipped_sch": skipped,
        "pcbs": pcbs,
        "gerbers": gerber_dirs,
        "projects": projects,
    }


GLOBAL_KINDS = ("schematics", "pcbs", "gerbers", "projects")
CENSUS_FILE = "census.json"


@contextlib.contextmanager
def manifests_lock(manifests_dir):
    """Serialise discover runs (add_repos runs one per repo in a pool). Linux-only: where
    fcntl is unavailable the lock is skipped."""
    try:
        import fcntl
    except ImportError:
        yield
        return
    manifests_dir.mkdir(parents=True, exist_ok=True)
    with open(manifests_dir / ".discover.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def rebuild_global_manifests(manifests_dir, repos, full):
    """Rebuild all_<kind>.txt from the per-repo manifests of `repos`, replace each atomically,
    and write census.json. A full discover resets the census floor to the new counts; a
    --repo rebuild keeps the previous floor. Returns the census dict."""
    lists = {k: [] for k in GLOBAL_KINDS}
    for repo in repos:
        for k in GLOBAL_KINDS:
            f = manifests_dir / repo / f"{k}.txt"
            if f.exists():
                lists[k].extend(ln for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip())
    counts, digests = {}, {}
    for k in GLOBAL_KINDS:
        text = "\n".join(sorted(lists[k])) + "\n" if lists[k] else ""
        atomic_write_text(manifests_dir / f"all_{k}.txt", text)
        counts[k] = len(lists[k])
        digests[k] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    prev = read_census(manifests_dir)
    floor = counts if full or not prev else prev.get("floor", counts)
    census = {"counts": counts, "sha256": digests, "floor": floor, "mode": "full" if full else "repo",
              "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    atomic_write_text(manifests_dir / CENSUS_FILE, json.dumps(census, indent=2, sort_keys=True) + "\n")
    return census


def read_census(manifests_dir):
    try:
        return json.loads((Path(manifests_dir) / CENSUS_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_manifest(out_dir, result):
    """Write manifest files to a directory."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "schematics.txt").write_text(
        "\n".join(result["schematics"]) + "\n" if result["schematics"] else "", encoding="utf-8")
    (out_dir / "pcbs.txt").write_text(
        "\n".join(result["pcbs"]) + "\n" if result["pcbs"] else "", encoding="utf-8")
    (out_dir / "gerbers.txt").write_text(
        "\n".join(result["gerbers"]) + "\n" if result["gerbers"] else "", encoding="utf-8")
    (out_dir / "projects.txt").write_text(
        "\n".join(result["projects"]) + "\n" if result["projects"] else "", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Discover KiCad files in repos/")
    parser.add_argument("--repo", help="Only discover files for this repo")
    args = parser.parse_args()

    if not REPOS_DIR.exists():
        print(f"Error: {REPOS_DIR} not found. Run checkout.py first.")
        sys.exit(1)

    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.repo:
        repo_dir = REPOS_DIR / args.repo
        if not repo_dir.exists():
            print(f"Error: Repo '{args.repo}' not found in {REPOS_DIR}")
            sys.exit(1)
        repos = [args.repo]
    else:
        repos = list_repos()

    print("=== Discovering KiCad files in repos/ ===")

    total_skipped = 0
    with manifests_lock(MANIFESTS_DIR):
        for repo in repos:
            repo_dir = REPOS_DIR / repo
            result = discover_in(repo_dir)

            # Write per-repo manifest
            repo_manifest_dir = MANIFESTS_DIR / repo
            write_manifest(repo_manifest_dir, result)
            total_skipped += result["skipped_sch"]

            total = len(result["schematics"]) + len(result["pcbs"]) + len(result["gerbers"])
            if total > 0:
                print(f"  {repo}: {len(result['schematics'])} sch, {len(result['pcbs'])} pcb, {len(result['gerbers'])} gerber")

        # the flat manifests always cover every repo, never only this run's
        census = rebuild_global_manifests(MANIFESTS_DIR, list_repos(), full=not args.repo)
    all_schematics = (MANIFESTS_DIR / "all_schematics.txt").read_text(encoding="utf-8").splitlines()
    counts = census["counts"]
    if any(counts[k] < census["floor"].get(k, 0) for k in GLOBAL_KINDS):
        print(f"WARNING: census {counts} is below the last full discover's floor {census['floor']}",
              file=sys.stderr)

    kicad_sch_count = sum(1 for s in all_schematics if s.endswith(".kicad_sch"))
    legacy_sch_count = len(all_schematics) - kicad_sch_count

    print(f"\nSchematics: {len(all_schematics)}")
    print(f"  .kicad_sch: {kicad_sch_count}")
    print(f"  .sch:       {legacy_sch_count}")
    if total_skipped:
        print(f"  (skipped {total_skipped} non-KiCad .sch files)")
    print(f"PCBs:       {counts['pcbs']}")
    print(f"Gerber dirs: {counts['gerbers']}")
    print(f"Projects:   {counts['projects']}")
    print(f"\nManifests written to {MANIFESTS_DIR}/")
    print(f"Per-repo manifests written for {len(repos)} repos")


if __name__ == "__main__":
    main()
