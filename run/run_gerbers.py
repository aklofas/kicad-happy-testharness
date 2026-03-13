#!/usr/bin/env python3
"""Run Gerber analysis on all discovered Gerber directories.

Usage:
    python3 run/run_gerbers.py
    python3 run/run_gerbers.py --repo OpenMower
    python3 run/run_gerbers.py --repo OpenMower --jobs 4

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import run_analyzer


def _summarize(data):
    return f"layers={len(data.get('layers', []))} drills={len(data.get('drill_files', []))}"


if __name__ == "__main__":
    run_analyzer({
        "type_name": "gerber",
        "analyzer_script": "analyze_gerbers.py",
        "manifest_file": "all_gerbers.txt",
        "output_subdir": "gerber",
        "summarize": _summarize,
    })
