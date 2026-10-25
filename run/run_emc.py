#!/usr/bin/env python3
"""Run EMC pre-compliance analysis on all schematic (+PCB) analysis outputs.

This script reads existing schematic and PCB analyzer JSON outputs and runs
analyze_emc.py on each schematic file, pairing it with its matching PCB output
when available. It does NOT re-run the schematic or PCB analyzers.

Usage:
    python3 run/run_emc.py --all
    python3 run/run_emc.py --repo owner/repo
    python3 run/run_emc.py --cross-section smoke --jobs 8
    python3 run/run_emc.py --repo owner/repo --standard cispr-class-b

Prerequisites:
    1. Schematic analysis outputs exist in results/outputs/schematic/
    2. PCB analysis outputs exist in results/outputs/pcb/ (optional but recommended)

Environment:
    KICAD_HAPPY_DIR  Path to kicad-happy repo (required if not at ../kicad-happy)
"""

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import (OUTPUTS_DIR, resolve_kicad_happy_dir,
                   find_schematic_outputs, find_pcb_output,
                   add_repo_filter_args, resolve_repos_with_source, DEFAULT_JOBS,
                   retire_orphaned_outputs)


def _err_first_line(err_file):
    """First line of the .err file: the 'status: detail' summary."""
    try:
        lines = err_file.read_text(encoding="utf-8").strip().splitlines()
        return lines[0] if lines else "unknown error"
    except OSError:
        return "unknown error"


def run_one_emc(analyzer_script, schematic_json, pcb_json, output_json,
                standard="fcc-class-b", timeout=30, spice_enhanced=False,
                compact=False, env=None):
    """Run analyze_emc.py on one schematic (+optional PCB) output.

    Returns (returncode, summary_dict_or_None, elapsed_s). EMC exits 1 for
    critical findings with a valid envelope; that is accepted
    (harnesslib ACCEPTED_EXITS["emc"]) and reported as 0. Output is
    temp-written and published atomically, so a stale previous output never
    stands in for this run's result (TH-054). None means timeout.
    """
    from harnesslib.execution import run_once, build_env

    def make_cmd(out_path):
        cmd = [sys.executable, str(analyzer_script),
               "--schematic", str(schematic_json),
               "--output", str(out_path),
               "--standard", standard]
        if compact:
            cmd.append("--compact")
        if pcb_json:
            cmd.extend(["--pcb", str(pcb_json)])
        if spice_enhanced:
            cmd.append("--spice-enhanced")
        return cmd

    output_json = Path(output_json)
    res = run_once(make_cmd, output_json, analyzer="emc", timeout=timeout,
                   env=env or build_env(offline=True))
    if res.status in ("ok", "ok_findings_exit"):
        output_json.with_suffix(".err").unlink(missing_ok=True)
        with open(output_json) as f:
            data = json.load(f)
        return 0, data.get("summary", {}), res.elapsed_s
    output_json.with_suffix(".err").write_text(
        f"{res.status}: {res.detail}\n{res.stderr_tail}", encoding="utf-8")
    return res.exit_code, None, res.elapsed_s


def _process_one_emc(input_json, emc_out_dir, standard, timeout, spice_enhanced,
                     analyzer, compact):
    """Top-level function for ProcessPoolExecutor (must be picklable)."""
    repo_name = f"{input_json.parent.parent.name}/{input_json.parent.name}"
    out_dir = emc_out_dir / repo_name
    out_dir.mkdir(parents=True, exist_ok=True)
    output_json = out_dir / input_json.name

    pcb_json = find_pcb_output(input_json)
    returncode, summary, elapsed = run_one_emc(
        analyzer, input_json, pcb_json, output_json,
        standard=standard, timeout=timeout,
        spice_enhanced=spice_enhanced, compact=compact,
    )
    return input_json, returncode, summary, output_json, pcb_json is not None, elapsed


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run EMC pre-compliance analysis on schematic+PCB outputs"
    )
    add_repo_filter_args(parser)
    parser.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                        help=f"Parallel jobs (default: {DEFAULT_JOBS})")
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
    parser.add_argument("--resume", action="store_true",
                        help="Skip files that already have valid output JSON")
    parser.add_argument("--compact", action="store_true",
                        help="Pass --compact to analyze_emc.py (strips INFO "
                        "findings; hides GP-001 and other INFO-gated visibility "
                        "signals). Default: off (full output).")
    return parser


def main():
    args = build_parser().parse_args()
    if args.resume:
        print("identity-based resume is not implemented for this runner yet (TH-064); "
              "rerun without --resume", file=sys.stderr)
        sys.exit(2)

    # Resolve paths
    kicad_happy = resolve_kicad_happy_dir()
    analyzer = kicad_happy / "skills" / "emc" / "scripts" / "analyze_emc.py"

    if not analyzer.exists():
        print(f"Error: {analyzer} not found", file=sys.stderr)
        sys.exit(1)

    # Find schematic outputs
    repo_list, selection_source = resolve_repos_with_source(
        args, require_explicit_all=True)
    if repo_list is not None:
        inputs = []
        for rn in repo_list:
            inputs.extend(find_schematic_outputs(rn))
    else:
        inputs = find_schematic_outputs(None)

    # Output directory; an EMC output whose schematic output is gone is retired
    emc_out_dir = OUTPUTS_DIR / "emc"
    expected = {}
    for inp in inputs:
        expected.setdefault(f"{inp.parent.parent.name}/{inp.parent.name}", set()).add(inp.name)
    retired = retire_orphaned_outputs(emc_out_dir, repo_list, expected)
    for f in retired:
        print(f"RETIRED {f.parent.parent.name}/{f.parent.name}/{f.name} (schematic output missing/stale)")

    if not inputs:
        if repo_list is not None:
            print(f"No schematic outputs found for specified repos",
                  file=sys.stderr)
        else:
            print("No schematic outputs found. Run run/run_schematic.py first.",
                  file=sys.stderr)
        sys.exit(1)

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

    process_fn = partial(_process_one_emc,
                         emc_out_dir=emc_out_dir,
                         standard=args.standard,
                         timeout=args.timeout,
                         spice_enhanced=args.spice_enhanced,
                         analyzer=analyzer,
                         compact=args.compact)

    results_list = []
    if args.jobs <= 1:
        for i, inp in enumerate(inputs, 1):
            result = process_fn(inp)
            results_list.append((i, result))
    else:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(process_fn, inp): i
                       for i, inp in enumerate(inputs, 1)}
            for future in as_completed(futures):
                i = futures[future]
                results_list.append((i, future.result()))

    results_list.sort(key=lambda x: x[0])

    for i, (input_json, returncode, summary, output_json, had_pcb, elapsed) in results_list:
        rel = f"{input_json.parent.name}/{input_json.name}"

        timings.append((f"{input_json.parent.name}/{input_json.name}", elapsed))
        total_files += 1

        if returncode != 0 and returncode is not None:
            errors += 1
            err_file = output_json.with_suffix(".err")
            err_msg = _err_first_line(err_file)
            print(f"FAIL [{i:4d}] {rel}")
            print(f"           {err_msg}")
            continue
        if summary is None:
            errors += 1
            print(f"FAIL [{i:4d}] {rel} ({_err_first_line(output_json.with_suffix('.err'))})")
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
    print(f"Retired (upstream gone):    {len(retired)}")
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
        "retired": len(retired),
        "total_findings": total_findings,
        "severity": severity_counts,
        "by_category": category_counts,
    }
    agg_file.parent.mkdir(parents=True, exist_ok=True)
    agg_file.write_text(json.dumps(agg, indent=2), encoding="utf-8")
    print(f"\nAggregate report: {agg_file}")

    # Write timing data
    timing_file = emc_out_dir / "_timing.json"
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
