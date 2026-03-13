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
    return f"components={s.get('total_components', 0)} nets={s.get('total_nets', 0)}"


if __name__ == "__main__":
    run_analyzer({
        "type_name": "schematic",
        "analyzer_script": "analyze_schematic.py",
        "manifest_file": "all_schematics.txt",
        "output_subdir": "schematic",
        "summarize": _summarize,
    })
