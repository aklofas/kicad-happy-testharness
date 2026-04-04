#!/usr/bin/env python3
"""Run EMC pre-compliance analysis on all schematic (+PCB) analysis outputs.

This script reads existing schematic and PCB analyzer JSON outputs and runs
analyze_emc.py on each schematic file, pairing it with its matching PCB output
when available. It does NOT re-run the schematic or PCB analyzers.

Usage:
    python3 run/run_emc.py
    python3 run/run_emc.py --repo OpenMower
    python3 run/run_emc.py --jobs 8
    python3 run/run_emc.py --standard cispr-class-b

Prerequisites:
    1. Schematic analysis outputs exist in results/outputs/schematic/
    2. PCB analysis outputs exist in results/outputs/pcb/ (optional but recommended)

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import json
import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import OUTPUTS_DIR, resolve_kicad_happy_dir


def find_schematic_outputs(repo_filter=None):
    """Find all schematic JSON outputs in results/outputs/schematic/."""
    schematic_dir = OUTPUTS_DIR / "schematic"
    if not schematic_dir.exists():
        return []

    outputs = []
    for owner_dir in sorted(schematic_dir.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            repo_key = f"{owner_dir.name}/{repo_dir.name}"
            if repo_filter and repo_key != repo_filter:
                continue
            for json_file in sorted(repo_dir.glob("*.json")):
                if json_file.stat().st_size == 0:
                    continue
                outputs.append(json_file)
    return outputs


def find_pcb_output(schematic_json):
    """Find matching PCB output for a schematic output.

    Given results/outputs/schematic/{repo}/{name}.kicad_sch.json,
    looks for results/outputs/pcb/{repo}/{name}.kicad_pcb.json.
    """
    repo_name = f"{schematic_json.parent.parent.name}/{schematic_json.parent.name}"
    pcb_dir = OUTPUTS_DIR / "pcb" / repo_name
    if not pcb_dir.exists():
        return None

    stem = schematic_json.name
    # Try replacing .kicad_sch.json -> .kicad_pcb.json
    if stem.endswith(".kicad_sch.json"):
        pcb_name = stem.replace(".kicad_sch.json", ".kicad_pcb.json")
        pcb_path = pcb_dir / pcb_name
        if pcb_path.exists() and pcb_path.stat().st_size > 0:
            return pcb_path

    # Try replacing .sch.json -> .kicad_pcb.json (legacy KiCad 5)
    if stem.endswith(".sch.json"):
        pcb_name = stem.replace(".sch.json", ".kicad_pcb.json")
        pcb_path = pcb_dir / pcb_name
        if pcb_path.exists() and pcb_path.stat().st_size > 0:
            return pcb_path

    return None


def run_one_emc(analyzer_script, schematic_json, pcb_json, output_json,
                standard="fcc-class-b", timeout=30, spice_enhanced=False):
    """Run analyze_emc.py on one schematic (+optional PCB) output.

    Returns:
        (returncode, summary_dict_or_None, elapsed_s)
    """
    cmd = [sys.executable, str(analyzer_script),
           "--schematic", str(schematic_json),
           "--output", str(output_json),
           "--compact",
           "--standard", standard]
    if pcb_json:
        cmd.extend(["--pcb", str(pcb_json)])
    if spice_enhanced:
        cmd.append("--spice-enhanced")

    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout)
        elapsed = time.time() - t0
        # Exit code 0 = success, 1 = critical findings (still valid output)
        if result.returncode in (0, 1) and output_json.exists():
            with open(output_json) as f:
                data = json.load(f)
            return 0, data.get("summary", {}), elapsed
        else:
            err_file = output_json.with_suffix(".err")
            err_file.write_text(result.stderr or f"exit {result.returncode}")
            return result.returncode, None, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        err_file = output_json.with_suffix(".err")
        err_file.write_text(f"Timed out after {timeout}s")
        return None, None, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        err_file = output_json.with_suffix(".err")
        err_file.write_text(str(e))
        return -1, None, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Run EMC pre-compliance analysis on schematic+PCB outputs"
    )
    parser.add_argument("--repo", help="Only analyze for this repo")
    parser.add_argument("--jobs", "-j", type=int, default=8,
                        help="Parallel jobs (default: 8)")
    parser.add_argument("--standard", default="fcc-class-b",
                        choices=["fcc-class-b", "fcc-class-a",
                                 "cispr-class-b", "cispr-class-a",
                                 "cispr-25", "mil-std-461"],
                        help="Target EMC standard (default: fcc-class-b)")
    parser.add_argument("--timeout", "-t", type=int, default=30,
                        help="Timeout per file in seconds (default: 30)")
    parser.add_argument("--spice-enhanced", action="store_true",
                        help="Enable SPICE-verified PDN impedance and EMI "
                        "filter checks (requires ngspice)")
    args = parser.parse_args()

    # Resolve paths
    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "emc" / "scripts" / "analyze_emc.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    # Find schematic outputs
    inputs = find_schematic_outputs(args.repo)
    if not inputs:
        if args.repo:
            print(f"No schematic outputs found for repo '{args.repo}'",
                  file=sys.stderr)
        else:
            print("No schematic outputs found. Run run/run_schematic.py first.",
                  file=sys.stderr)
        sys.exit(1)

    # Output directory
    emc_out_dir = OUTPUTS_DIR / "emc"

    # Count PCB matches
    pcb_matches = sum(1 for inp in inputs if find_pcb_output(inp))

    print(f"=== Running EMC Analysis ===")
    print(f"Analyzer: {analyzer}")
    print(f"Standard: {args.standard}")
    print(f"Inputs: {len(inputs)} schematic outputs ({pcb_matches} with PCB)")
    print(f"Jobs: {args.jobs}")
    print()

    # Aggregate stats
    total_files = 0
    errors = 0
    total_findings = 0
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    category_counts = {}
    files_with_findings = 0
    paired_count = 0
    timings = []
    t_start = time.time()

    def process_one(input_json):
        repo_name = f"{input_json.parent.parent.name}/{input_json.parent.name}"
        out_dir = emc_out_dir / repo_name
        out_dir.mkdir(parents=True, exist_ok=True)
        output_json = out_dir / input_json.name

        pcb_json = find_pcb_output(input_json)
        returncode, summary, elapsed = run_one_emc(
            analyzer, input_json, pcb_json, output_json,
            standard=args.standard, timeout=args.timeout,
            spice_enhanced=args.spice_enhanced,
        )
        return input_json, returncode, summary, output_json, pcb_json is not None, elapsed

    results_list = []
    if args.jobs <= 1:
        for i, inp in enumerate(inputs, 1):
            result = process_one(inp)
            results_list.append((i, result))
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(process_one, inp): i
                       for i, inp in enumerate(inputs, 1)}
            for future in as_completed(futures):
                i = futures[future]
                results_list.append((i, future.result()))

    results_list.sort(key=lambda x: x[0])

    for i, (input_json, returncode, summary, output_json, had_pcb, elapsed) in results_list:
        timings.append((f"{input_json.parent.name}/{input_json.name}", elapsed))
        total_files += 1
        rel = f"{input_json.parent.name}/{input_json.name}"

        if returncode != 0 and returncode is not None:
            errors += 1
            err_file = output_json.with_suffix(".err")
            err_msg = (err_file.read_text().strip().splitlines()[-1]
                       if err_file.exists() else "unknown error")
            print(f"FAIL [{i:4d}] {rel}")
            print(f"           {err_msg}")
            continue
        if summary is None:
            errors += 1
            print(f"FAIL [{i:4d}] {rel} (timeout)")
            continue

        if had_pcb:
            paired_count += 1

        tc = summary.get("total_checks", 0)
        total_findings += tc
        if tc > 0:
            files_with_findings += 1

        for sev in severity_counts:
            severity_counts[sev] += summary.get(sev.lower(), 0)

        # Count categories from output
        if output_json.exists():
            try:
                with open(output_json) as fh:
                    data = json.load(fh)
                for f in data.get("findings", []):
                    cat = f.get("category", "other")
                    category_counts[cat] = category_counts.get(cat, 0) + 1
            except Exception:
                pass

        score = summary.get("emc_risk_score", 0)
        pcb_flag = "+" if had_pcb else " "
        if tc == 0:
            print(f"  -- [{i:4d}] {rel}{pcb_flag} (no findings)")
        else:
            crit = summary.get("critical", 0)
            high = summary.get("high", 0)
            print(f"PASS [{i:4d}] {rel}{pcb_flag} "
                  f"(findings={tc} score={score} C={crit} H={high})")

    # Summary
    print()
    print(f"{'='*60}")
    print(f"EMC Analysis Summary")
    print(f"{'='*60}")
    print(f"Files processed:            {total_files}")
    print(f"Files with PCB paired:      {paired_count}")
    print(f"Files with findings:        {files_with_findings}")
    print(f"Script errors:              {errors}")
    print(f"{'='*60}")
    print(f"Total findings:             {total_findings}")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        print(f"  {sev:10s}:               {severity_counts[sev]}")
    print(f"{'='*60}")
    if category_counts:
        print(f"By category:")
        for cat, cnt in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"  {cat:25s}: {cnt}")

    total_elapsed = time.time() - t_start
    avg_elapsed = sum(t for _, t in timings) / len(timings) if timings else 0
    slowest = sorted(timings, key=lambda x: -x[1])[:5]
    print(f"Time:  {total_elapsed:.1f}s total, {avg_elapsed:.2f}s avg per file")
    if slowest:
        print(f"Slowest:")
        for path, t in slowest:
            print(f"  {t:6.1f}s  {path}")

    # Write aggregate report
    agg_file = emc_out_dir / "_aggregate.json"
    agg = {
        "total_files": total_files,
        "files_with_findings": files_with_findings,
        "paired_with_pcb": paired_count,
        "errors": errors,
        "total_findings": total_findings,
        "severity": severity_counts,
        "by_category": category_counts,
    }
    agg_file.parent.mkdir(parents=True, exist_ok=True)
    agg_file.write_text(json.dumps(agg, indent=2))
    print(f"\nAggregate report: {agg_file}")

    # Write timing data
    timing_file = emc_out_dir / "_timing.json"
    timing_data = {
        "total_files": total_files,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_per_file_s": round(avg_elapsed, 3),
        "slowest": [{"file": p, "elapsed_s": round(t, 3)} for p, t in slowest],
    }
    timing_file.write_text(json.dumps(timing_data, indent=2))

    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
