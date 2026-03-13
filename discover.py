#!/usr/bin/env python3
"""Discover all KiCad files in repos/ and write manifests.

Scans repos/ for schematic, PCB, project, and Gerber files.
Writes file lists to results/manifests/.

Usage:
    python3 discover.py
"""

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
CLONE_DIR = HARNESS_DIR / "repos"
MANIFESTS_DIR = HARNESS_DIR / "results" / "manifests"

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


def main():
    if not CLONE_DIR.exists():
        print(f"Error: {CLONE_DIR} not found. Run checkout.py first.")
        sys.exit(1)

    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Discovering KiCad files in repos/ ===")

    # Schematics: .kicad_sch and .sch (filtered to KiCad format only)
    kicad_sch_files = sorted(str(p) for p in CLONE_DIR.rglob("*.kicad_sch"))
    legacy_sch_candidates = sorted(str(p) for p in CLONE_DIR.rglob("*.sch"))
    # Filter legacy .sch to only KiCad files (not Eagle XML/binary)
    legacy_sch_files = [s for s in legacy_sch_candidates if _is_kicad_legacy_sch(s)]
    skipped = len(legacy_sch_candidates) - len(legacy_sch_files)
    schematics = sorted(kicad_sch_files + legacy_sch_files)
    (MANIFESTS_DIR / "all_schematics.txt").write_text("\n".join(schematics) + "\n" if schematics else "")
    print(f"Schematics: {len(schematics)}")
    print(f"  .kicad_sch: {len(kicad_sch_files)}")
    print(f"  .sch:       {len(legacy_sch_files)}")
    if skipped:
        print(f"  (skipped {skipped} non-KiCad .sch files)")

    # PCBs: .kicad_pcb
    pcbs = sorted(str(p) for p in CLONE_DIR.rglob("*.kicad_pcb"))
    (MANIFESTS_DIR / "all_pcbs.txt").write_text("\n".join(pcbs) + "\n" if pcbs else "")
    print(f"PCBs:       {len(pcbs)}")

    # Gerber directories: directories containing gerber files
    gerber_dirs = set()
    for ext in GERBER_EXTENSIONS:
        for p in CLONE_DIR.rglob(f"*{ext}"):
            gerber_dirs.add(str(p.parent))
        # Also try uppercase
        for p in CLONE_DIR.rglob(f"*{ext.upper()}"):
            gerber_dirs.add(str(p.parent))
    gerber_dirs = sorted(gerber_dirs)
    (MANIFESTS_DIR / "all_gerbers.txt").write_text("\n".join(gerber_dirs) + "\n" if gerber_dirs else "")
    print(f"Gerber dirs: {len(gerber_dirs)}")

    # Project files: .kicad_pro
    projects = sorted(str(p) for p in CLONE_DIR.rglob("*.kicad_pro"))
    (MANIFESTS_DIR / "all_projects.txt").write_text("\n".join(projects) + "\n" if projects else "")
    print(f"Projects:   {len(projects)}")

    print(f"\nManifests written to {MANIFESTS_DIR}/")


if __name__ == "__main__":
    main()
