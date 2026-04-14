#!/usr/bin/env python3
"""Run schematic analysis on all discovered schematic files.

Usage:
    python3 run/run_schematic.py
    python3 run/run_schematic.py --repo OpenMower
    python3 run/run_schematic.py --repo OpenMower --jobs 4

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import run_analyzer


def _summarize(data):
    s = data.get("statistics", {})
    detectors = set(f.get("detector", "") for f in data.get("findings", []))
    detectors.discard("")
    base = f"components={s.get('total_components', 0)} nets={s.get('total_nets', 0)}"
    if detectors:
        base += f" detectors={len(detectors)}"
    return base


if __name__ == "__main__":
    run_analyzer({
        "type_name": "schematic",
        "analyzer_script": "analyze_schematic.py",
        "manifest_file": "all_schematics.txt",
        "output_subdir": "schematic",
        "summarize": _summarize,
        # Disable hierarchy auto-discovery in batch mode — the harness processes
        # every file independently, and parse_all_sheets() on sub-sheets causes
        # OOM when many workers analyze sub-sheets from large projects in parallel.
        "extra_args": ["--no-hierarchy"],
    })
