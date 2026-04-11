#!/usr/bin/env python3
"""Run thermal analysis on matching schematic+PCB output pairs.

This script reads existing schematic and PCB analyzer JSON outputs and runs
analyze_thermal.py on each matching pair. It does NOT re-run the schematic or
PCB analyzers — it consumes outputs already in results/outputs/.

A pair is matched by project prefix: schematic ``Foo.kicad_sch.json`` pairs
with PCB ``Foo.kicad_pcb.json`` in the same owner/repo.

Usage:
    python3 run/run_thermal.py
    python3 run/run_thermal.py --repo Dylanfg123/Zebra-X
    python3 run/run_thermal.py --jobs 16
    python3 run/run_thermal.py --cross-section smoke --resume

Prerequisites:
    1. Schematic analysis outputs in results/outputs/schematic/
    2. PCB analysis outputs in results/outputs/pcb/

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import json
import sys
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, ANALYZER_TIMEOUT, resolve_kicad_happy_dir,
                   find_schematic_outputs, find_pcb_output, should_skip_resume,
                   add_repo_filter_args, resolve_repos, DEFAULT_JOBS)


def find_thermal_pairs(repo_filter=None):
    """Find matching schematic+PCB output pairs for thermal analysis.

    Returns list of (schematic_json, pcb_json) tuples where both files exist
    and share the same project prefix.
    """
    pairs = []
    for sch_json in find_schematic_outputs(repo_filter):
        pcb_json = find_pcb_output(sch_json)
        if pcb_json:
            pairs.append((sch_json, pcb_json))
    return pairs


def run_one_thermal(analyzer_script, schematic_json, pcb_json, output_json,
                    timeout=ANALYZER_TIMEOUT):
    """Run analyze_thermal.py on one schematic+PCB pair.

    Returns:
        (returncode, summary_dict_or_None, elapsed_s)
    """
    cmd = [sys.executable, str(analyzer_script),
           "--schematic", str(schematic_json),
           "--pcb", str(pcb_json),
           "--output", str(output_json)]

    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout)
        elapsed = time.time() - t0
        if result.returncode == 0 and output_json.exists():
            with open(output_json) as f:
                data = json.load(f)
            return 0, data.get("summary", {}), elapsed
        else:
            err_file = output_json.with_suffix(".err")
            err_file.write_text(result.stderr or f"exit {result.returncode}", encoding="utf-8")
            return result.returncode, None, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        err_file = output_json.with_suffix(".err")
        err_file.write_text(f"Timed out after {timeout}s", encoding="utf-8")
        return None, None, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        err_file = output_json.with_suffix(".err")
        err_file.write_text(str(e), encoding="utf-8")
        return -1, None, elapsed


def _process_one_thermal(sch_json, pcb_json, thermal_out_dir, timeout,
                         resume, analyzer):
    """Top-level function for ProcessPoolExecutor (must be picklable)."""
    repo_name = f"{sch_json.parent.parent.name}/{sch_json.parent.name}"
    out_dir = thermal_out_dir / repo_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Output filename: replace .kicad_sch.json / .sch.json with _thermal.json
    stem = sch_json.name
    for suffix in (".kicad_sch.json", ".sch.json"):
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
            break
    output_json = out_dir / f"{stem}_thermal.json"

    if should_skip_resume(output_json, resume):
        return sch_json, "SKIPPED", None, output_json, 0.0

    returncode, summary, elapsed = run_one_thermal(
        analyzer, sch_json, pcb_json, output_json, timeout=timeout,
    )
    return sch_json, returncode, summary, output_json, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Run thermal analysis on schematic+PCB output pairs"
    )
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel jobs (default: {DEFAULT_JOBS})")
    parser.add_argument("--timeout", "-t", type=int, default=ANALYZER_TIMEOUT,
                        help=f"Timeout per file in seconds (default: {ANALYZER_TIMEOUT})")
    parser.add_argument("--resume", action="store_true",
                        help="Skip files that already have valid output JSON")
    args = parser.parse_args()

    # Resolve paths
    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "kicad" / "scripts" / "analyze_thermal.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    # Find matching pairs
    repo_list = resolve_repos(args)
    if repo_list:
        pairs = []
        for rn in repo_list:
            pairs.extend(find_thermal_pairs(rn))
    else:
        pairs = find_thermal_pairs(None)

    if not pairs:
        if repo_list:
            print("No matching schematic+PCB output pairs found for specified repos",
                  file=sys.stderr)
        else:
            print("No matching schematic+PCB output pairs found.\n"
                  "Run run/run_schematic.py and run/run_pcb.py first.",
                  file=sys.stderr)
        sys.exit(1)

    # Output directory
    thermal_out_dir = OUTPUTS_DIR / "thermal"

    print(f"=== Running Thermal Analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Inputs: {len(pairs)} schematic+PCB pairs")
    print(f"Jobs: {args.jobs}")
    print()

    # Aggregate stats
    total_files = 0
    errors = 0
    skipped = 0
    total_findings = 0
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    files_with_findings = 0
    timings = []
    t_start = time.time()

    process_fn = partial(_process_one_thermal,
                         thermal_out_dir=thermal_out_dir,
                         timeout=args.timeout,
                         resume=args.resume,
                         analyzer=analyzer)

    results_list = []
    if args.jobs <= 1:
        for i, (sch_json, pcb_json) in enumerate(pairs, 1):
            result = process_fn(sch_json, pcb_json)
            results_list.append((i, result))
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(process_fn, sch, pcb): i
                       for i, (sch, pcb) in enumerate(pairs, 1)}
            for future in as_completed(futures):
                i = futures[future]
                results_list.append((i, future.result()))

    results_list.sort(key=lambda x: x[0])

    for i, (input_json, returncode, summary, output_json, elapsed) in results_list:
        rel = f"{input_json.parent.name}/{input_json.name}"

        if returncode == "SKIPPED":
            skipped += 1
            continue

        timings.append((rel, elapsed))
        total_files += 1

        if returncode != 0 and returncode is not None:
            errors += 1
            err_file = output_json.with_suffix(".err")
            err_msg = (err_file.read_text(encoding="utf-8").strip().splitlines()[-1]
                       if err_file.exists() else "unknown error")
            print(f"FAIL [{i:4d}] {rel}")
            print(f"           {err_msg}")
            continue
        if summary is None:
            errors += 1
            print(f"FAIL [{i:4d}] {rel} (timeout)")
            continue

        tc = summary.get("total_checks", 0)
        total_findings += tc
        if tc > 0:
            files_with_findings += 1

        for sev in severity_counts:
            severity_counts[sev] += summary.get(sev.lower(), 0)

        score = summary.get("thermal_score", 0)
        if tc == 0:
            print(f"  -- [{i:4d}] {rel} (no findings)")
        else:
            crit = summary.get("critical", 0)
            high = summary.get("high", 0)
            print(f"PASS [{i:4d}] {rel} "
                  f"(findings={tc} score={score} C={crit} H={high})")

    # Summary
    print()
    print(f"{'='*60}")
    print(f"Thermal Analysis Summary")
    print(f"{'='*60}")
    print(f"Files processed:            {total_files}")
    if skipped:
        print(f"Skipped (--resume):         {skipped}")
    print(f"Files with findings:        {files_with_findings}")
    print(f"Script errors:              {errors}")
    print(f"{'='*60}")
    print(f"Total findings:             {total_findings}")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        print(f"  {sev:10s}:               {severity_counts[sev]}")
    print(f"{'='*60}")

    total_elapsed = time.time() - t_start
    avg_elapsed = sum(t for _, t in timings) / len(timings) if timings else 0
    slowest = sorted(timings, key=lambda x: -x[1])[:5]
    print(f"Time:  {total_elapsed:.1f}s total, {avg_elapsed:.2f}s avg per file")
    if slowest:
        print(f"Slowest:")
        for path, t in slowest:
            print(f"  {t:6.1f}s  {path}")

    # Write aggregate report
    agg_file = thermal_out_dir / "_aggregate.json"
    agg = {
        "total_files": total_files,
        "files_with_findings": files_with_findings,
        "errors": errors,
        "total_findings": total_findings,
        "severity": severity_counts,
    }
    agg_file.parent.mkdir(parents=True, exist_ok=True)
    agg_file.write_text(json.dumps(agg, indent=2), encoding="utf-8")
    print(f"\nAggregate report: {agg_file}")

    # Write timing data
    timing_file = thermal_out_dir / "_timing.json"
    timing_data = {
        "total_files": total_files,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_per_file_s": round(avg_elapsed, 3),
        "slowest": [{"file": p, "elapsed_s": round(t, 3)} for p, t in slowest],
    }
    timing_file.write_text(json.dumps(timing_data, indent=2), encoding="utf-8")

    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
