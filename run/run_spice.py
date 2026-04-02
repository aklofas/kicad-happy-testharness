#!/usr/bin/env python3
"""Run SPICE simulation on all schematic analysis outputs.

This script reads existing schematic analyzer JSON outputs (from run_schematic.py)
and runs simulate_subcircuits.py on each one. It does NOT re-run the schematic
analyzer — it consumes the outputs already in results/outputs/schematic/.

Usage:
    python3 run/run_spice.py
    python3 run/run_spice.py --repo OpenMower
    python3 run/run_spice.py --jobs 4
    python3 run/run_spice.py --timeout 10

Prerequisites:
    1. ngspice installed (apt install ngspice)
    2. Schematic analysis outputs exist in results/outputs/schematic/
       (run run/run_schematic.py first)

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import json
import os
import subprocess
import sys
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
    for repo_dir in sorted(schematic_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        if repo_filter and repo_dir.name != repo_filter:
            continue
        for json_file in sorted(repo_dir.glob("*.json")):
            # Skip .err files and empty files
            if json_file.stat().st_size == 0:
                continue
            outputs.append(json_file)
    return outputs


def find_pcb_output(schematic_json):
    """Find matching PCB output for a schematic output.

    Given results/outputs/schematic/{repo}/{name}.kicad_sch.json,
    looks for results/outputs/pcb/{repo}/{name}.kicad_pcb.json.
    """
    repo_name = schematic_json.parent.name
    pcb_dir = OUTPUTS_DIR / "pcb" / repo_name
    if not pcb_dir.exists():
        return None

    stem = schematic_json.name
    for old, new in [(".kicad_sch.json", ".kicad_pcb.json"),
                     (".sch.json", ".kicad_pcb.json")]:
        if stem.endswith(old):
            pcb_path = pcb_dir / stem.replace(old, new)
            if pcb_path.exists() and pcb_path.stat().st_size > 0:
                return pcb_path
    return None


def run_extract_parasitics(extractor_script, pcb_json, parasitics_json):
    """Run extract_parasitics.py on a PCB analysis JSON.

    Returns:
        True if extraction succeeded, False otherwise.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(extractor_script),
             str(pcb_json),
             "--output", str(parasitics_json)],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0 and parasitics_json.exists()
    except Exception:
        return False


def run_one_spice(simulator_script, input_json, output_json, timeout=5,
                  parasitics_json=None, extra_args=None):
    """Run simulate_subcircuits.py on one schematic analysis JSON.

    Returns:
        (returncode, summary_dict_or_None, elapsed_s)
    """
    cmd = [sys.executable, str(simulator_script),
           str(input_json),
           "--output", str(output_json),
           "--compact",
           "--timeout", str(timeout)]
    if parasitics_json and parasitics_json.exists():
        cmd.extend(["--parasitics", str(parasitics_json)])
    if extra_args:
        import shlex
        cmd.extend(shlex.split(extra_args))

    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=60)
        elapsed = time.time() - t0
        if result.returncode == 0 and output_json.exists():
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
        err_file.write_text("Timed out after 60s")
        return None, None, elapsed
    except Exception as e:
        elapsed = time.time() - t0
        err_file = output_json.with_suffix(".err")
        err_file.write_text(str(e))
        return -1, None, elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Run SPICE simulations on schematic analysis outputs"
    )
    parser.add_argument("--repo", help="Only simulate for this repo")
    parser.add_argument("--jobs", "-j", type=int, default=4,
                        help="Parallel jobs (default: 4)")
    parser.add_argument("--timeout", "-t", type=int, default=5,
                        help="Timeout per subcircuit simulation in seconds (default: 5)")
    parser.add_argument("--with-parasitics", action="store_true",
                        help="Enable PCB parasitic injection: extract trace R/via L "
                        "from PCB outputs and inject into SPICE testbenches. "
                        "Results go to results/outputs/spice-parasitics/.")
    parser.add_argument("--extra-args", type=str, default="",
                        help="Extra arguments to pass through to simulate_subcircuits.py "
                        "(e.g. '--monte-carlo 100 --mc-seed 42')")
    args = parser.parse_args()

    # Resolve paths
    kicad_happy = resolve_kicad_happy_dir()
    simulator = kicad_happy / "skills" / "spice" / "scripts" / "simulate_subcircuits.py"

    if not simulator.exists():
        print(f"Error: {simulator} not found", file=sys.stderr)
        sys.exit(1)

    extractor = None
    if args.with_parasitics:
        extractor = kicad_happy / "skills" / "spice" / "scripts" / "extract_parasitics.py"
        if not extractor.exists():
            print(f"Error: {extractor} not found", file=sys.stderr)
            sys.exit(1)

    # Check ngspice (the simulator script handles NGSPICE_PATH and Windows paths,
    # but do a basic check here for early feedback)
    import shutil
    ngspice_path = os.environ.get("NGSPICE_PATH") or shutil.which("ngspice")
    if not ngspice_path:
        # Check common Windows location
        for candidate in [r"C:\Spice64\bin\ngspice.exe"]:
            if os.path.isfile(candidate):
                ngspice_path = candidate
                break
    if not ngspice_path:
        print("Error: ngspice not found.", file=sys.stderr)
        print("  Linux:   apt install ngspice", file=sys.stderr)
        print("  macOS:   brew install ngspice", file=sys.stderr)
        print("  Windows: download from ngspice.sourceforge.io", file=sys.stderr)
        print("  Or set NGSPICE_PATH env var.", file=sys.stderr)
        sys.exit(1)

    # Find schematic outputs
    inputs = find_schematic_outputs(args.repo)
    if not inputs:
        if args.repo:
            print(f"No schematic outputs found for repo '{args.repo}'", file=sys.stderr)
        else:
            print("No schematic outputs found. Run run/run_schematic.py first.", file=sys.stderr)
        sys.exit(1)

    # Output directory
    if args.with_parasitics:
        spice_out_dir = OUTPUTS_DIR / "spice-parasitics"
    else:
        spice_out_dir = OUTPUTS_DIR / "spice"

    mode_label = "SPICE + PCB Parasitics" if args.with_parasitics else "SPICE simulation"
    print(f"=== Running {mode_label} ===")
    print(f"Simulator: {simulator}")
    if args.with_parasitics:
        print(f"Extractor: {extractor}")
        pcb_matches = sum(1 for inp in inputs if find_pcb_output(inp))
        print(f"Inputs: {len(inputs)} schematic outputs ({pcb_matches} with PCB)")
    else:
        print(f"Inputs: {len(inputs)} schematic outputs")
    print(f"Jobs: {args.jobs}")
    print(f"Timeout: {args.timeout}s per subcircuit")
    if args.extra_args:
        print(f"Extra args: {args.extra_args}")
    print()

    # Aggregate stats
    total_pass = total_warn = total_fail = total_skip = 0
    total_sims = 0
    total_files = 0
    files_with_sims = 0
    errors = 0
    type_counts = {}
    timings = []
    t_start = time.time()

    parasitics_extracted = 0

    def process_one(input_json):
        nonlocal parasitics_extracted
        # Mirror the repo directory structure
        repo_name = input_json.parent.name
        out_dir = spice_out_dir / repo_name
        out_dir.mkdir(parents=True, exist_ok=True)
        output_json = out_dir / input_json.name

        # Extract parasitics from matching PCB output if --with-parasitics
        parasitics_json = None
        if args.with_parasitics:
            pcb_json = find_pcb_output(input_json)
            if pcb_json:
                parasitics_json = out_dir / (input_json.stem + ".parasitics.json")
                ok = run_extract_parasitics(extractor, pcb_json, parasitics_json)
                if ok:
                    parasitics_extracted += 1
                else:
                    parasitics_json = None  # Extraction failed, run without

        returncode, summary, elapsed = run_one_spice(
            simulator, input_json, output_json, timeout=args.timeout,
            parasitics_json=parasitics_json,
            extra_args=args.extra_args,
        )
        return input_json, returncode, summary, output_json, elapsed

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

    # Sort by index for ordered output
    results_list.sort(key=lambda x: x[0])

    for i, (input_json, returncode, summary, output_json, elapsed) in results_list:
        timings.append((f"{input_json.parent.name}/{input_json.name}", elapsed))
        total_files += 1
        rel = f"{input_json.parent.name}/{input_json.name}"

        if returncode != 0 or summary is None:
            errors += 1
            err_file = output_json.with_suffix(".err")
            err_msg = err_file.read_text().strip().splitlines()[-1] if err_file.exists() else "unknown error"
            print(f"FAIL [{i:4d}] {rel}")
            print(f"           {err_msg}")
            continue

        t = summary.get("total", 0)
        p = summary.get("pass", 0)
        w = summary.get("warn", 0)
        f = summary.get("fail", 0)
        s = summary.get("skip", 0)

        total_sims += t
        total_pass += p
        total_warn += w
        total_fail += f
        total_skip += s

        if t > 0:
            files_with_sims += 1

        # Count by type from the output
        if output_json.exists():
            try:
                with open(output_json) as fh:
                    data = json.load(fh)
                for r in data.get("simulation_results", []):
                    tt = r.get("subcircuit_type", "unknown")
                    type_counts[tt] = type_counts.get(tt, 0) + 1
            except Exception:
                pass

        if t == 0:
            print(f"  -- [{i:4d}] {rel} (no simulatable subcircuits)")
        elif f > 0:
            print(f"WARN [{i:4d}] {rel} ({p}p {w}w {f}f {s}s = {t})")
        else:
            print(f"PASS [{i:4d}] {rel} ({p}p {w}w {f}f {s}s = {t})")

    # Summary
    print()
    print(f"{'='*60}")
    title = "SPICE + Parasitics Summary" if args.with_parasitics else "SPICE Simulation Summary"
    print(title)
    print(f"{'='*60}")
    print(f"Schematic files processed:  {total_files}")
    if args.with_parasitics:
        print(f"Parasitics extracted:       {parasitics_extracted}")
    print(f"Files with simulations:     {files_with_sims}")
    print(f"Script errors:              {errors}")
    print(f"{'='*60}")
    print(f"Total subcircuit sims:      {total_sims}")
    print(f"  Pass:                     {total_pass}")
    print(f"  Warn:                     {total_warn}")
    print(f"  Fail:                     {total_fail}")
    print(f"  Skip:                     {total_skip}")
    if total_sims > 0:
        print(f"  Pass rate:                {total_pass/total_sims*100:.1f}%")
    print(f"{'='*60}")
    if type_counts:
        print(f"By subcircuit type:")
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t:25s}: {c}")

    total_elapsed = time.time() - t_start
    avg_elapsed = sum(t for _, t in timings) / len(timings) if timings else 0
    slowest = sorted(timings, key=lambda x: -x[1])[:5]
    print(f"Time:  {total_elapsed:.1f}s total, {avg_elapsed:.2f}s avg per file")
    if slowest:
        print(f"Slowest:")
        for path, t in slowest:
            print(f"  {t:6.1f}s  {path}")

    # Write timing data
    timing_file = spice_out_dir / "_timing.json"
    timing_data = {
        "total_files": total_files,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_per_file_s": round(avg_elapsed, 3),
        "slowest": [{"file": p, "elapsed_s": round(t, 3)} for p, t in slowest],
    }
    timing_file.parent.mkdir(parents=True, exist_ok=True)
    timing_file.write_text(json.dumps(timing_data, indent=2))

    # Write aggregate report
    agg_file = spice_out_dir / "_aggregate.json"
    agg = {
        "total_files": total_files,
        "files_with_sims": files_with_sims,
        "errors": errors,
        "total_sims": total_sims,
        "pass": total_pass,
        "warn": total_warn,
        "fail": total_fail,
        "skip": total_skip,
        "pass_rate": round(total_pass / total_sims * 100, 1) if total_sims else 0,
        "by_type": type_counts,
    }
    if args.with_parasitics:
        agg["parasitics_extracted"] = parasitics_extracted
    agg_file.parent.mkdir(parents=True, exist_ok=True)
    agg_file.write_text(json.dumps(agg, indent=2))
    print(f"\nAggregate report: {agg_file}")

    # Exit with error if any script failures
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
