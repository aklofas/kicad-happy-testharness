#!/usr/bin/env python3
"""Run PCB analysis on all discovered PCB files.

Usage:
    python3 run/run_pcb.py
    python3 run/run_pcb.py --repo OpenMower
    python3 run/run_pcb.py --repo OpenMower --jobs 4
    python3 run/run_pcb.py --repo OpenMower --full   # include trace segments for parasitics

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import run_analyzer


def _summarize(data):
    s = data.get("statistics", data.get("summary", {}))
    return f"footprints={s.get('footprint_count', 0)} tracks={s.get('track_segments', 0)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PCB analysis")
    parser.add_argument("--repo", help="Only analyze PCBs for this repo")
    parser.add_argument("--jobs", "-j", type=int, default=1,
                        help="Number of parallel analyzer processes (default: 1)")
    parser.add_argument("--full", action="store_true",
                        help="Pass --full to analyze_pcb.py (includes per-trace "
                        "segment data needed for parasitic extraction)")
    args = parser.parse_args()

    config = {
        "type_name": "pcb",
        "analyzer_script": "analyze_pcb.py",
        "manifest_file": "all_pcbs.txt",
        "output_subdir": "pcb",
        "summarize": _summarize,
    }
    if args.full:
        config["extra_args"] = ["--full"]

    run_analyzer(config, args)
