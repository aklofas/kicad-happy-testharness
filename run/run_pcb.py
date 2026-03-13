#!/usr/bin/env python3
"""Run PCB analysis on all discovered PCB files.

Usage:
    python3 run/run_pcb.py
    python3 run/run_pcb.py --repo OpenMower
    python3 run/run_pcb.py --repo OpenMower --jobs 4

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import run_analyzer


def _summarize(data):
    s = data.get("statistics", data.get("summary", {}))
    return f"footprints={s.get('footprint_count', 0)} tracks={s.get('track_segments', 0)}"


if __name__ == "__main__":
    run_analyzer({
        "type_name": "pcb",
        "analyzer_script": "analyze_pcb.py",
        "manifest_file": "all_pcbs.txt",
        "output_subdir": "pcb",
        "summarize": _summarize,
    })
