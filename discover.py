#!/usr/bin/env python3
"""Discover all KiCad files in repos/ and write manifests.

Scans repos/ for schematic, PCB, project, and Gerber files.
Writes file lists to results/manifests/ (flat) and per-repo manifests
to results/manifests/{repo}/.

Usage:
    python3 discover.py
    python3 discover.py --repo OpenMower
"""

import argparse
import sys
from pathlib import Path

from utils import HARNESS_DIR, REPOS_DIR, MANIFESTS_DIR, list_repos, repo_name_from_path

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


def discover_in(scan_dir):
    """Discover KiCad files under a directory. Returns dict of file lists."""
    # Schematics: .kicad_sch and .sch (filtered to KiCad format only)
    kicad_sch_files = sorted(str(p) for p in scan_dir.rglob("*.kicad_sch"))
    legacy_sch_candidates = sorted(str(p) for p in scan_dir.rglob("*.sch"))
    legacy_sch_files = [s for s in legacy_sch_candidates if _is_kicad_legacy_sch(s)]
    skipped = len(legacy_sch_candidates) - len(legacy_sch_files)
    schematics = sorted(kicad_sch_files + legacy_sch_files)

    # PCBs: .kicad_pcb
    pcbs = sorted(str(p) for p in scan_dir.rglob("*.kicad_pcb"))

    # Gerber directories — single traversal, case-insensitive
    gerber_exts_lower = {e.lower() for e in GERBER_EXTENSIONS}
    gerber_dirs = set()
    for p in scan_dir.rglob("*"):
        if p.suffix.lower() in gerber_exts_lower and p.is_file():
            gerber_dirs.add(str(p.parent))
    gerber_dirs = sorted(gerber_dirs)

    # Project files: .kicad_pro
    projects = sorted(str(p) for p in scan_dir.rglob("*.kicad_pro"))

    return {
        "schematics": schematics,
        "kicad_sch_count": len(kicad_sch_files),
        "legacy_sch_count": len(legacy_sch_files),
        "skipped_sch": skipped,
        "pcbs": pcbs,
        "gerbers": gerber_dirs,
        "projects": projects,
    }


def write_manifest(out_dir, result):
    """Write manifest files to a directory."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "schematics.txt").write_text(
        "\n".join(result["schematics"]) + "\n" if result["schematics"] else "")
    (out_dir / "pcbs.txt").write_text(
        "\n".join(result["pcbs"]) + "\n" if result["pcbs"] else "")
    (out_dir / "gerbers.txt").write_text(
        "\n".join(result["gerbers"]) + "\n" if result["gerbers"] else "")
    (out_dir / "projects.txt").write_text(
        "\n".join(result["projects"]) + "\n" if result["projects"] else "")


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

    # Aggregate totals for flat manifests
    all_schematics = []
    all_pcbs = []
    all_gerbers = []
    all_projects = []
    total_skipped = 0

    for repo in repos:
        repo_dir = REPOS_DIR / repo
        result = discover_in(repo_dir)

        # Write per-repo manifest
        repo_manifest_dir = MANIFESTS_DIR / repo
        write_manifest(repo_manifest_dir, result)

        all_schematics.extend(result["schematics"])
        all_pcbs.extend(result["pcbs"])
        all_gerbers.extend(result["gerbers"])
        all_projects.extend(result["projects"])
        total_skipped += result["skipped_sch"]

        total = len(result["schematics"]) + len(result["pcbs"]) + len(result["gerbers"])
        if total > 0:
            print(f"  {repo}: {len(result['schematics'])} sch, {len(result['pcbs'])} pcb, {len(result['gerbers'])} gerber")

    # Write flat manifests (backwards compat)
    all_schematics.sort()
    all_pcbs.sort()
    all_gerbers.sort()
    all_projects.sort()
    (MANIFESTS_DIR / "all_schematics.txt").write_text(
        "\n".join(all_schematics) + "\n" if all_schematics else "")
    (MANIFESTS_DIR / "all_pcbs.txt").write_text(
        "\n".join(all_pcbs) + "\n" if all_pcbs else "")
    (MANIFESTS_DIR / "all_gerbers.txt").write_text(
        "\n".join(all_gerbers) + "\n" if all_gerbers else "")
    (MANIFESTS_DIR / "all_projects.txt").write_text(
        "\n".join(all_projects) + "\n" if all_projects else "")

    kicad_sch_count = sum(1 for s in all_schematics if s.endswith(".kicad_sch"))
    legacy_sch_count = len(all_schematics) - kicad_sch_count

    print(f"\nSchematics: {len(all_schematics)}")
    print(f"  .kicad_sch: {kicad_sch_count}")
    print(f"  .sch:       {legacy_sch_count}")
    if total_skipped:
        print(f"  (skipped {total_skipped} non-KiCad .sch files)")
    print(f"PCBs:       {len(all_pcbs)}")
    print(f"Gerber dirs: {len(all_gerbers)}")
    print(f"Projects:   {len(all_projects)}")
    print(f"\nManifests written to {MANIFESTS_DIR}/")
    print(f"Per-repo manifests written for {len(repos)} repos")


if __name__ == "__main__":
    main()
