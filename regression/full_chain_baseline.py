#!/usr/bin/env python3
"""Tracked --full pcb -> emc -> thermal chain runner.

Samples N projects with a same-stem .kicad_pro/.kicad_sch/.kicad_pcb triple, runs
analyze_schematic (hierarchy on) + analyze_pcb --full --proximity + analyze_emc +
analyze_thermal per side with the harnesslib offline env (PYTHONHASHSEED=0, credentials stripped).

Usage: python3 regression/full_chain_baseline.py --base <worktree> [--cand <worktree>] --out <ABSOLUTE dir>
       [--n 300] [--seed 23] [--jobs 32] [--timeout 600]
Layout: <out>/<side>/<owner>/<repo>/<unit>/{schematic,pcb,emc,thermal}.json, <out>/chain_log.jsonl, <out>/sample.json,
<out>/done.json (completion marker, written last)

Operational note (TH-067): pool workers can outlive a SIGKILLed parent. Start a real run
under its own process group (e.g. `setsid python3 regression/full_chain_baseline.py ...`)
and, if the run is aborted, kill the whole group rather than only the parent.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
from harnesslib.execution import build_env  # noqa: E402

MANIFESTS = HARNESS / "results" / "manifests"
REPOS = HARNESS / "repos"


def sample_projects(n: int, seed: int, manifests_dir: Path = MANIFESTS) -> tuple[list[Path], int]:
    triples = set()
    for pcbs in sorted(Path(manifests_dir).rglob("pcbs.txt")):
        for line in pcbs.read_text(encoding="utf-8").splitlines():
            p = Path(line.strip())
            if p.suffix != ".kicad_pcb":
                continue
            if p.with_suffix(".kicad_sch").exists() and p.with_suffix(".kicad_pro").exists():
                triples.add(p)
    ordered = sorted(triples)
    random.Random(seed).shuffle(ordered)
    return ordered[:n], len(ordered)


def chain_steps(pcb_path: Path, product_dir: Path, out_dir: Path) -> list[tuple[str, list[str]]]:
    scripts = Path(product_dir) / "skills"
    sch_out, pcb_out = out_dir / "schematic.json", out_dir / "pcb.json"
    return [
        ("schematic", [sys.executable, str(scripts / "kicad/scripts/analyze_schematic.py"),
                       str(pcb_path.with_suffix(".kicad_sch")), "-o", str(sch_out)]),
        ("pcb", [sys.executable, str(scripts / "kicad/scripts/analyze_pcb.py"),
                 str(pcb_path), "--full", "--proximity", "-o", str(pcb_out)]),
        ("emc", [sys.executable, str(scripts / "emc/scripts/analyze_emc.py"),
                 "--schematic", str(sch_out), "--pcb", str(pcb_out), "-o", str(out_dir / "emc.json")]),
        ("thermal", [sys.executable, str(scripts / "kicad/scripts/analyze_thermal.py"),
                     "--schematic", str(sch_out), "--pcb", str(pcb_out), "-o", str(out_dir / "thermal.json")]),
    ]


def sides_for(*, base: str, cand: str | None) -> list[tuple[str, str]]:
    sides = [("baseline", base)]
    if cand:
        sides.append(("candidate", cand))
    return sides


def run_chain(args):
    pcb_path, side, wt, out_root, timeout = args
    pcb_path = Path(pcb_path)
    rel = pcb_path.relative_to(REPOS)
    unit = str(rel.with_suffix("")).replace("/", "_")
    owner, repo = rel.parts[0], rel.parts[1]
    out_dir = Path(out_root) / side / owner / repo / unit
    out_dir.mkdir(parents=True, exist_ok=True)
    env = build_env(offline=True)
    log = {"unit": unit, "side": side, "pcb_path": str(pcb_path)}  # "pcb" is the pcb step's result
    for name, cmd in chain_steps(pcb_path, Path(wt), out_dir):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=timeout, cwd=str(out_dir))
            log[name] = {"rc": r.returncode, "stderr_tail": r.stderr[-400:] if r.returncode else ""}
        except subprocess.TimeoutExpired:
            log[name] = {"rc": -9, "stderr_tail": "timeout"}
        if log[name]["rc"] != 0 and name in ("schematic", "pcb"):
            break
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--jobs", type=int, default=32)
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)
    out = Path(args.out)
    if not out.is_absolute():
        print("--out must be ABSOLUTE (analyzers run with cwd=unit dir)", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    base = str(Path(args.base).resolve())  # analyzers run with cwd=unit dir
    cand = str(Path(args.cand).resolve()) if args.cand else None
    sample, population = sample_projects(args.n, args.seed)
    (out / "sample.json").write_text(json.dumps({"seed": args.seed, "n": args.n, "population": population,
                                                 "pcbs": [str(p) for p in sample]}, indent=2) + "\n")
    jobs = [(str(p), side, wt, str(out), args.timeout) for p in sample for side, wt in
            sides_for(base=base, cand=cand)]
    with (out / "chain_log.jsonl").open("w", encoding="utf-8") as log, \
            ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for i, rec in enumerate(ex.map(run_chain, jobs), 1):
            log.write(json.dumps(rec) + "\n")
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)}")
    n_sides = len(sides_for(base=base, cand=cand))
    # Completion marker for waiters (tools/wait_for_run.py): written only after every chain_log record.
    (out / "done.json").write_text(json.dumps({"projects": len(sample), "sides": n_sides,
                                               "records": len(jobs)}, indent=2) + "\n")
    print(f"done: {len(sample)} projects x {n_sides} side(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
