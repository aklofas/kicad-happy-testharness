#!/usr/bin/env python3
"""Run PCB analysis on all discovered PCB files.

Usage:
    python3 run/run_pcb.py
    python3 run/run_pcb.py --repo OpenMower
    python3 run/run_pcb.py --repo OpenMower --jobs 4
    python3 run/run_pcb.py --cross-section smoke --jobs 16
    python3 run/run_pcb.py --repo OpenMower --no-full       # skip geometry sections
    python3 run/run_pcb.py --repo OpenMower --no-proximity  # skip trace_proximity

By default, passes --full and --proximity to analyze_pcb.py.
- --full enables return_path_continuity, via-in-pad tenting, board-edge via
  clearance, and related geometry detectors that EMC GP-001 depends on.
- --proximity produces trace_proximity data consumed by EMC XT-001 crosstalk
  detection and SPICE parasitics extraction. Near-zero runtime cost.

Use --no-full or --no-proximity to opt out of either.

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


def normalize_pcb_argv(argv):
    """Return (remaining_argv, extra_args): --full/--proximity default on, opt out with
    --no-full / --no-proximity; explicit --full / --proximity are redundant and dropped."""
    argv = list(argv)
    extra = ["--full", "--proximity"]
    for opt_out, flag in (("--no-full", "--full"), ("--no-proximity", "--proximity")):
        if opt_out in argv:
            argv.remove(opt_out)
            extra.remove(flag)
    argv = [a for a in argv if a not in ("--full", "--proximity")]
    return argv, extra


if __name__ == "__main__":
    remaining, extra = normalize_pcb_argv(sys.argv[1:])
    run_analyzer({
        "type_name": "pcb",
        "analyzer_script": "analyze_pcb.py",
        "manifest_file": "all_pcbs.txt",
        "output_subdir": "pcb",
        "summarize": _summarize,
        "extra_args": extra,
    }, argv=remaining)
