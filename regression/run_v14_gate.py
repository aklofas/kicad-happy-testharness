#!/usr/bin/env python3
"""v1.4 Layer 1 regression gate driver.

Proves v1.4's ``--only-deterministic`` flag produces v1.3.1-equivalent
output across the harness corpus. For each repo x analyzer:

  1. run the v1.3.1 analyzer (plain)             -> v131 snapshot
  2. run the v1.4 analyzer (--only-deterministic) -> v14 snapshot
  3. diff the two envelopes via regression/regression_diff.py

Aggregates a per-analyzer + corpus-wide rollup. Clean (disappeared==0,
downgrades==0) -> tag v1.4.0-rc.1. Any FAIL repo -> drives rc.2.

Worktree setup (see RUNBOOK Checklist 25):
    git -C ~/Projects/kicad-happy worktree add /tmp/kh-v131 v1.3.1
    git -C ~/Projects/kicad-happy worktree add /tmp/kh-v14  v1.4-dev   # 0df3b7f

Analyzer invocation is identical on both sides except the v1.4 run adds
``--only-deterministic``. Schematic gets ``--no-hierarchy`` on BOTH sides
(matches the harness batch convention and avoids parallel-worker OOM; the
flag treats input identically for both versions so the comparison stays
fair). No other extra flags are passed -- a plain run, per the handoff.

Phases:
  A  schematic / pcb / gerber   -- independent, fully parallel
  B  thermal / emc / cross_analysis -- consume the Phase A sch/pcb snapshots

Usage:
    python3 regression/run_v14_gate.py --cross-section smoke --jobs 16
    python3 regression/run_v14_gate.py --cross-section quick_200 --jobs 32
    python3 regression/run_v14_gate.py --jobs 32                 # full corpus
    python3 regression/run_v14_gate.py --repo owner/repo
    python3 regression/run_v14_gate.py --cross-section smoke --resume

Environment / args:
    --v131-dir   v1.3.1 worktree (default /tmp/kh-v131)
    --v14-dir    v1.4-dev worktree (default /tmp/kh-v14)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "regression"))

import regression_diff as rdiff  # noqa: E402
from utils import (  # noqa: E402
    MANIFESTS_DIR, DEFAULT_JOBS, ANALYZER_TIMEOUT,
    add_repo_filter_args, resolve_repos, list_repos,
    filter_manifest_by_repo, repo_name_from_path, safe_name,
)

GATE_DIR = HARNESS_DIR / "results" / "v14_gate"

# analyzer -> path of the analyzer script relative to a kicad-happy worktree
ANALYZER_REL = {
    "schematic": "skills/kicad/scripts/analyze_schematic.py",
    "pcb": "skills/kicad/scripts/analyze_pcb.py",
    "gerber": "skills/kicad/scripts/analyze_gerbers.py",
    "thermal": "skills/kicad/scripts/analyze_thermal.py",
    "emc": "skills/emc/scripts/analyze_emc.py",
    "cross_analysis": "skills/kicad/scripts/cross_analysis.py",
}
PHASE_A = ["schematic", "pcb", "gerber"]
PHASE_B = ["thermal", "emc", "cross_analysis"]
ALL_ANALYZERS = PHASE_A + PHASE_B

# manifest file for the file-input (Phase A) analyzers
MANIFEST_FILE = {
    "schematic": "all_schematics.txt",
    "pcb": "all_pcbs.txt",
    "gerber": "all_gerbers.txt",
}


# ---------------------------------------------------------------------------
# subprocess helpers (module-level so ProcessPoolExecutor can pickle them)
# ---------------------------------------------------------------------------

# Pin the hash seed for every analyzer subprocess. Several detectors
# (RC-DET, DO-DET, ...) iterate sets whose order is hash-seed dependent --
# --only-deterministic does NOT suppress this. Without a fixed seed the
# diff would flag the same finding as disappeared+new on different runs.
# Pinning the seed identically on BOTH sides keeps the comparison fair and
# reproducible. (Flagged to the main-repo agent as a v1.5 carry-over: the
# --only-deterministic flag should arguably pin this itself.)
_ANALYZER_ENV = {**os.environ, "PYTHONHASHSEED": "0"}


def _run(cmd, timeout):
    """Run an analyzer subprocess. Returns (ok, detail) where ok means the
    output file exists and parses as JSON (exit code is ignored -- emc and
    thermal exit 1 on critical findings but still write valid output)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, env=_ANALYZER_ENV)
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return False, f"exec error: {e}"
    out_path = Path(cmd[cmd.index("-o") + 1]) if "-o" in cmd \
        else Path(cmd[cmd.index("--output") + 1])
    if not out_path.exists() or out_path.stat().st_size < 3:
        err = (proc.stderr or "").strip().splitlines()
        return False, (err[-1] if err else f"no output (exit {proc.returncode})")
    try:
        json.loads(out_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return False, f"invalid output JSON: {e}"
    return True, "ok"


def _file_cmd(analyzer, kh_dir, input_path, out_path, deterministic):
    """Build the command for a Phase A (file-input) analyzer."""
    script = str(Path(kh_dir) / ANALYZER_REL[analyzer])
    cmd = [sys.executable, script, str(input_path), "-o", str(out_path)]
    if analyzer == "schematic":
        cmd.append("--no-hierarchy")
    if deterministic:
        cmd.append("--only-deterministic")
    return cmd


def _chained_cmd(analyzer, kh_dir, sch_json, pcb_json, out_path, deterministic):
    """Build the command for a Phase B (chained) analyzer."""
    script = str(Path(kh_dir) / ANALYZER_REL[analyzer])
    cmd = [sys.executable, script,
           "--schematic", str(sch_json), "--output", str(out_path)]
    if pcb_json is not None:
        cmd += ["--pcb", str(pcb_json)]
    if deterministic:
        cmd.append("--only-deterministic")
    return cmd


def _diff_envelopes(v131_path, v14_path, v131_ok, v14_ok):
    """Diff two snapshot envelopes. Returns a result dict (subset of the
    fields regression_diff emits) plus a verdict.

    Failure handling:
      both fail              -> verdict SKIP  (excluded from PASS/WARN/FAIL)
      v131 ok, v14 failed    -> verdict FAIL  (the deterministic path broke)
      v131 failed, v14 ok    -> verdict WARN  (baseline broke; can't compare)
    """
    if not v131_ok and not v14_ok:
        return {"verdict": "SKIP", "reason": "both analyzers failed"}
    if v131_ok and not v14_ok:
        return {"verdict": "FAIL", "reason": "v1.4 analyzer failed/produced no output",
                "disappeared_count": 0, "severity_downgrades": 0,
                "severity_upgrades": 0, "new_known_count": 0,
                "new_upgraded_count": 0, "new_unknown_count": 0}
    if not v131_ok and v14_ok:
        return {"verdict": "WARN", "reason": "v1.3.1 baseline failed; not comparable",
                "disappeared_count": 0, "severity_downgrades": 0,
                "severity_upgrades": 0, "new_known_count": 0,
                "new_upgraded_count": 0, "new_unknown_count": 0}
    try:
        before = json.loads(Path(v131_path).read_text(encoding="utf-8"))
        after = json.loads(Path(v14_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"verdict": "SKIP", "reason": f"snapshot read error: {e}"}
    d = rdiff.diff(rdiff._collect_observations(before),
                   rdiff._collect_observations(after))
    verdict, reason = rdiff.verdict(d)
    downgrades = [c for c in d["severity_changes"] if c["kind"] == "downgrade"]
    upgrades = [c for c in d["severity_changes"] if c["kind"] == "upgrade"]
    return {
        "verdict": verdict,
        "reason": reason,
        "disappeared_count": len(d["disappeared"]),
        "severity_downgrades": len(downgrades),
        "severity_upgrades": len(upgrades),
        "new_known_count": len(d["new_known"]),
        "new_upgraded_count": len(d["new_upgraded"]),
        "new_unknown_count": len(d["new_unknown"]),
        "disappeared": [
            {"rule_id": f.get("rule_id"), "components": f.get("components"),
             "summary": (f.get("summary") or "")[:120]}
            for f in d["disappeared"][:5]
        ],
        "downgrades": downgrades[:5],
        "new_known_rule_ids": [f.get("rule_id") for f in d["new_known"]],
        "new_upgraded_rule_ids": [f.get("rule_id") for f in d["new_upgraded"]],
        "new_unknown_rule_ids": [f.get("rule_id") for f in d["new_unknown"]],
    }


def _snap_paths(analyzer, repo, key):
    """Return (v131, v14, diff) snapshot paths for a unit of work.

    Each unit gets a PRIVATE <key>/ directory for its snapshot. The v1.4
    analyzers write a ``capability_mode.json`` sidecar into the -o directory
    via a non-concurrency-safe writer (TOCTOU exists-check + non-atomic
    write). If two same-analyzer+repo jobs shared a directory, one could
    read that sidecar mid-write and crash. A per-unit directory isolates
    the sidecar so sibling jobs never collide.
    """
    v131 = GATE_DIR / "v131" / analyzer / repo / key / "snap.json"
    v14 = GATE_DIR / "v14" / analyzer / repo / key / "snap.json"
    df = GATE_DIR / "diff" / analyzer / repo / f"{key}.json"
    for p in (v131, v14, df):
        p.parent.mkdir(parents=True, exist_ok=True)
    return v131, v14, df


def _result_record(analyzer, repo, identity, diff_res, v131_detail, v14_detail):
    rec = {"analyzer": analyzer, "repo": repo, "identity": identity,
           "v131_detail": v131_detail, "v14_detail": v14_detail}
    rec.update(diff_res)
    return rec


# ---------------------------------------------------------------------------
# Phase A worker -- file-input analyzers
# ---------------------------------------------------------------------------

def _phase_a_job(args):
    analyzer, input_path, repo, v131_dir, v14_dir, timeout, resume = args
    key = safe_name(input_path)
    identity = f"{repo}/{key}"
    v131_out, v14_out, diff_out = _snap_paths(analyzer, repo, key)

    if resume and diff_out.exists() and diff_out.stat().st_size > 3:
        try:
            return json.loads(diff_out.read_text(encoding="utf-8"))["_record"]
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    v131_ok, v131_detail = _run(
        _file_cmd(analyzer, v131_dir, input_path, v131_out, False), timeout)
    v14_ok, v14_detail = _run(
        _file_cmd(analyzer, v14_dir, input_path, v14_out, True), timeout)

    diff_res = _diff_envelopes(v131_out, v14_out, v131_ok, v14_ok)
    rec = _result_record(analyzer, repo, identity, diff_res,
                         v131_detail, v14_detail)
    diff_out.write_text(json.dumps({"_record": rec}, indent=2), encoding="utf-8")
    return rec


# ---------------------------------------------------------------------------
# Phase B worker -- chained analyzers (consume Phase A snapshots)
# ---------------------------------------------------------------------------

def _phase_b_job(args):
    (analyzer, repo, sch_key, v131_sch, v14_sch, v131_pcb, v14_pcb,
     timeout, resume) = args
    identity = f"{repo}/{sch_key}"
    v131_out, v14_out, diff_out = _snap_paths(analyzer, repo, sch_key)

    if resume and diff_out.exists() and diff_out.stat().st_size > 3:
        try:
            return json.loads(diff_out.read_text(encoding="utf-8"))["_record"]
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    # thermal requires a PCB pair; emc/cross_analysis treat it as optional.
    if analyzer == "thermal" and (v131_pcb is None or v14_pcb is None):
        rec = _result_record(analyzer, repo, identity,
                             {"verdict": "SKIP", "reason": "no PCB pair"},
                             "skipped", "skipped")
        diff_out.write_text(json.dumps({"_record": rec}, indent=2),
                            encoding="utf-8")
        return rec

    v131_ok, v131_detail = _run(
        _chained_cmd(analyzer, _phase_b_job.v131_dir, v131_sch, v131_pcb,
                     v131_out, False), timeout)
    v14_ok, v14_detail = _run(
        _chained_cmd(analyzer, _phase_b_job.v14_dir, v14_sch, v14_pcb,
                     v14_out, True), timeout)

    diff_res = _diff_envelopes(v131_out, v14_out, v131_ok, v14_ok)
    rec = _result_record(analyzer, repo, identity, diff_res,
                         v131_detail, v14_detail)
    diff_out.write_text(json.dumps({"_record": rec}, indent=2), encoding="utf-8")
    return rec


def _pcb_snapshot_for(sch_snapshot):
    """Given a Phase A schematic snapshot path, return the matching PCB
    snapshot path (or None). Mirrors utils.find_pcb_output naming.

    Layout: <gate>/<ver>/schematic/<owner>/<repo>/<key>/snap.json
    where <key> is e.g. ``Hardware_Connectors.kicad_sch``.
    """
    key_dir = sch_snapshot.parent                        # <key>
    repo_dir = key_dir.parent                            # <repo>
    owner_dir = repo_dir.parent                          # <owner>
    ver_root = owner_dir.parent.parent                   # <ver>
    sch_key = key_dir.name
    for old in (".kicad_sch", ".sch"):
        if sch_key.endswith(old):
            pcb_key = sch_key[:-len(old)] + ".kicad_pcb"
            cand = (ver_root / "pcb" / owner_dir.name / repo_dir.name
                    / pcb_key / "snap.json")
            if cand.exists() and cand.stat().st_size > 3:
                return cand
    return None


# ---------------------------------------------------------------------------
# job-list builders
# ---------------------------------------------------------------------------

def _load_manifest(analyzer, repos):
    path = MANIFESTS_DIR / MANIFEST_FILE[analyzer]
    if not path.exists():
        print(f"  WARN: manifest {path} missing", file=sys.stderr)
        return []
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip()]
    if repos is None:
        return lines
    out = []
    for rn in repos:
        out.extend(filter_manifest_by_repo(lines, rn))
    return out


def _build_phase_a_jobs(repos, v131_dir, v14_dir, timeout, resume):
    jobs = []
    for analyzer in PHASE_A:
        for input_path in _load_manifest(analyzer, repos):
            repo = repo_name_from_path(input_path)
            if repo is None:
                continue
            jobs.append((analyzer, input_path, repo, v131_dir, v14_dir,
                         timeout, resume))
    return jobs


def _build_phase_b_jobs(repos, timeout, resume):
    """After Phase A has run, scan the v131/v14 schematic snapshot trees and
    pair them with PCB snapshots to build chained-analyzer jobs."""
    jobs = []
    v131_sch_root = GATE_DIR / "v131" / "schematic"
    v14_sch_root = GATE_DIR / "v14" / "schematic"
    if not v131_sch_root.exists():
        return jobs
    repo_set = set(repos) if repos else None
    for owner_dir in sorted(v131_sch_root.iterdir()):
        if not owner_dir.is_dir():
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            repo = f"{owner_dir.name}/{repo_dir.name}"
            if repo_set is not None and repo not in repo_set:
                continue
            for sch_key_dir in sorted(repo_dir.iterdir()):
                if not sch_key_dir.is_dir():
                    continue
                v131_sch = sch_key_dir / "snap.json"
                if not (v131_sch.exists() and v131_sch.stat().st_size > 3):
                    continue
                sch_key = sch_key_dir.name
                v14_sch = v14_sch_root / repo / sch_key / "snap.json"
                if not (v14_sch.exists() and v14_sch.stat().st_size > 3):
                    continue
                v131_pcb = _pcb_snapshot_for(v131_sch)
                v14_pcb = _pcb_snapshot_for(v14_sch)
                for analyzer in PHASE_B:
                    jobs.append((analyzer, repo, sch_key,
                                 str(v131_sch), str(v14_sch),
                                 str(v131_pcb) if v131_pcb else None,
                                 str(v14_pcb) if v14_pcb else None,
                                 timeout, resume))
    return jobs


# Phase B worker needs the worktree dirs; pass them via function attributes
# (simpler than threading them through every job tuple, and picklable since
# they are plain strings set before the pool forks).
def _init_phase_b(v131_dir, v14_dir):
    _phase_b_job.v131_dir = v131_dir
    _phase_b_job.v14_dir = v14_dir


# ---------------------------------------------------------------------------
# execution + aggregation
# ---------------------------------------------------------------------------

def _run_jobs(jobs, worker, jobs_n, label, initializer=None, initargs=()):
    if not jobs:
        return []
    print(f"  {label}: {len(jobs)} units, {jobs_n} workers")
    results = []
    t0 = time.time()
    done = 0
    if jobs_n <= 1:
        if initializer:
            initializer(*initargs)
        for job in jobs:
            results.append(worker(job))
            done += 1
            if done % 200 == 0:
                print(f"    {done}/{len(jobs)} ({time.time()-t0:.0f}s)")
    else:
        with ProcessPoolExecutor(max_workers=jobs_n, initializer=initializer,
                                 initargs=initargs) as pool:
            futs = [pool.submit(worker, job) for job in jobs]
            for fut in as_completed(futs):
                results.append(fut.result())
                done += 1
                if done % 200 == 0:
                    print(f"    {done}/{len(jobs)} ({time.time()-t0:.0f}s)")
    print(f"  {label} done: {len(results)} units in {time.time()-t0:.0f}s")
    return results


def _aggregate(records):
    """Build the corpus-wide rollup from the flat record list."""
    by_analyzer = {a: Counter() for a in ALL_ANALYZERS}
    fail_repos = defaultdict(list)       # repo -> [records]
    new_known_rules = Counter()
    new_upgraded_rules = Counter()
    new_unknown_rules = Counter()

    for r in records:
        a = r["analyzer"]
        v = r["verdict"]
        c = by_analyzer[a]
        c[v] += 1
        c["disappeared"] += r.get("disappeared_count", 0)
        c["downgrades"] += r.get("severity_downgrades", 0)
        c["upgrades"] += r.get("severity_upgrades", 0)
        c["new_known"] += r.get("new_known_count", 0)
        c["new_upgraded"] += r.get("new_upgraded_count", 0)
        c["new_unknown"] += r.get("new_unknown_count", 0)
        for rid in r.get("new_known_rule_ids", []):
            new_known_rules[rid] += 1
        for rid in r.get("new_upgraded_rule_ids", []):
            new_upgraded_rules[rid] += 1
        for rid in r.get("new_unknown_rule_ids", []):
            new_unknown_rules[rid] += 1
        if v == "FAIL":
            fail_repos[r["repo"]].append(r)

    return {
        "by_analyzer": by_analyzer,
        "fail_repos": fail_repos,
        "new_known_rules": new_known_rules,
        "new_upgraded_rules": new_upgraded_rules,
        "new_unknown_rules": new_unknown_rules,
    }


def _compute_pass_criteria(totals: dict) -> dict:
    """Derive the pass_criteria block from rollup totals.

    Two clean verdicts (LOG 5, audit Highest-Risk #14):

      * ``clean`` — rc.1-compatible. ZERO disappeared findings, ZERO
        severity downgrades, ZERO FAIL verdicts, ZERO NewUnknown findings.
        NewUnknown is the safety-critical addition (an unrecognized new
        rule_id at the producer side must be triaged, not silently
        approved). WARN rows are tolerated.

      * ``strict_clean`` — release-blocking interpretation. All of the
        above PLUS ZERO WARN rows. A WARN row means the v1.3.1 baseline
        could not be produced for that repo, so the v1.4 output isn't
        comparable — that's incomplete coverage, not clean. Use this for
        the actual tag decision; the rc.1-compatible ``clean`` is kept
        for historical comparability.

    Extracted from ``_write_rollup`` for direct unit testability — the
    LOG 5 test suite asserts these verdicts on synthetic totals dicts.
    """
    return {
        "disappeared_count": totals["Disappeared"],
        "severity_downgrades": totals["Downgrades"],
        "fail_verdicts": totals["FAIL"],
        "new_unknown_count": totals["NewUnknown"],
        "new_upgraded_count": totals["NewUpgraded"],
        "warn_count": totals["WARN"],
        "clean": (totals["Disappeared"] == 0
                  and totals["Downgrades"] == 0
                  and totals["FAIL"] == 0
                  and totals["NewUnknown"] == 0),
        "strict_clean": (totals["Disappeared"] == 0
                         and totals["Downgrades"] == 0
                         and totals["FAIL"] == 0
                         and totals["NewUnknown"] == 0
                         and totals["WARN"] == 0),
    }


def _write_rollup(records, agg, section, out_json, out_csv):
    rows = []
    for a in ALL_ANALYZERS:
        c = agg["by_analyzer"][a]
        rows.append({
            "analyzer": a,
            "PASS": c.get("PASS", 0), "WARN": c.get("WARN", 0),
            "FAIL": c.get("FAIL", 0), "SKIP": c.get("SKIP", 0),
            "Disappeared": c.get("disappeared", 0),
            "Downgrades": c.get("downgrades", 0),
            "Upgrades": c.get("upgrades", 0),
            "NewKnown": c.get("new_known", 0),
            "NewUpgraded": c.get("new_upgraded", 0),
            "NewUnknown": c.get("new_unknown", 0),
        })

    totals = {k: sum(row[k] for row in rows)
              for k in ("PASS", "WARN", "FAIL", "SKIP", "Disappeared",
                        "Downgrades", "Upgrades", "NewKnown", "NewUpgraded",
                        "NewUnknown")}

    fail_list = []
    for repo, recs in sorted(agg["fail_repos"].items()):
        fail_list.append({
            "repo": repo,
            "analyzers": sorted({r["analyzer"] for r in recs}),
            "units": [
                {"analyzer": r["analyzer"], "identity": r["identity"],
                 "reason": r.get("reason"),
                 "disappeared": r.get("disappeared", [])[:5],
                 "downgrades": r.get("downgrades", [])[:5]}
                for r in recs
            ],
        })

    report = {
        "section": section,
        "total_units": len(records),
        "rollup": rows,
        "totals": totals,
        "fail_repo_count": len(agg["fail_repos"]),
        "fail_repos": fail_list,
        "new_known_rule_distribution": dict(agg["new_known_rules"].most_common()),
        "new_upgraded_rule_distribution": dict(agg["new_upgraded_rules"].most_common()),
        "new_unknown_rule_distribution": dict(agg["new_unknown_rules"].most_common()),
        "pass_criteria": _compute_pass_criteria(totals),
    }
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True),
                        encoding="utf-8")

    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Analyzer", "PASS", "WARN", "FAIL", "SKIP", "Disappeared",
                    "Downgrades", "Upgrades", "NewKnown", "NewUpgraded",
                    "NewUnknown"])
        for row in rows:
            w.writerow([row["analyzer"], row["PASS"], row["WARN"], row["FAIL"],
                        row["SKIP"], row["Disappeared"], row["Downgrades"],
                        row["Upgrades"], row["NewKnown"], row["NewUpgraded"],
                        row["NewUnknown"]])
        w.writerow(["TOTAL", totals["PASS"], totals["WARN"], totals["FAIL"],
                    totals["SKIP"], totals["Disappeared"], totals["Downgrades"],
                    totals["Upgrades"], totals["NewKnown"],
                    totals["NewUpgraded"], totals["NewUnknown"]])
    return report


def _print_summary(report):
    print()
    print("=" * 78)
    print(f"v1.4 Layer 1 regression gate -- section: {report['section']}  "
          f"({report['total_units']} units)")
    print("=" * 78)
    hdr = (f"{'Analyzer':<16}{'PASS':>7}{'WARN':>7}{'FAIL':>7}{'SKIP':>7}"
           f"{'Disapp':>8}{'Downgr':>8}{'NewKnown':>10}{'NewUnkn':>9}")
    print(hdr)
    print("-" * len(hdr))
    for row in report["rollup"]:
        print(f"{row['analyzer']:<16}{row['PASS']:>7}{row['WARN']:>7}"
              f"{row['FAIL']:>7}{row['SKIP']:>7}{row['Disappeared']:>8}"
              f"{row['Downgrades']:>8}{row['NewKnown']:>10}"
              f"{row['NewUnknown']:>9}")
    t = report["totals"]
    print("-" * len(hdr))
    print(f"{'TOTAL':<16}{t['PASS']:>7}{t['WARN']:>7}{t['FAIL']:>7}"
          f"{t['SKIP']:>7}{t['Disappeared']:>8}{t['Downgrades']:>8}"
          f"{t['NewKnown']:>10}{t['NewUnknown']:>9}")
    print()
    crit = report["pass_criteria"]
    warn_count = crit.get('warn_count', 0)
    print(f"Pass criteria: disappeared={crit['disappeared_count']}  "
          f"downgrades={crit['severity_downgrades']}  "
          f"fail_verdicts={crit['fail_verdicts']}  "
          f"new_unknown={crit['new_unknown_count']}  "
          f"new_upgraded={crit['new_upgraded_count']}  "
          f"warn={warn_count}")
    # LOG 5: distinguish CLEAN (rc.1-compatible, NewUnknown-gated) from
    # STRICT-CLEAN (also gates on WARN). Surface both verdicts so main-repo
    # picks the right one for the release decision.
    if crit.get('strict_clean'):
        print(f"  => STRICT-CLEAN -- 0 WARN baselines, eligible for tag")
    elif crit['clean']:
        print(f"  => CLEAN -- but {warn_count} WARN baseline(s) -- "
              f"comparison incomplete on those repos")
    else:
        if crit['new_unknown_count']:
            print(f"  => NOT CLEAN -- {crit['new_unknown_count']} NewUnknown "
                  f"finding(s) require triage before tag")
        else:
            print(f"  => NOT CLEAN -- FAIL repos drive rc.2")
    if report["fail_repo_count"]:
        print(f"\nFAIL repos ({report['fail_repo_count']}):")
        for fr in report["fail_repos"][:30]:
            print(f"  {fr['repo']}  [{', '.join(fr['analyzers'])}]")
        if report["fail_repo_count"] > 30:
            print(f"  ... +{report['fail_repo_count'] - 30} more (see JSON)")
    if report["new_known_rule_distribution"]:
        print(f"\nNewKnown rule_ids: {report['new_known_rule_distribution']}")
    if report["new_upgraded_rule_distribution"]:
        print(f"NewUpgraded rule_ids: {report['new_upgraded_rule_distribution']}")
    if report["new_unknown_rule_distribution"]:
        print(f"NewUnknown rule_ids: {report['new_unknown_rule_distribution']}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_repo_filter_args(ap)
    ap.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS,
                    help=f"parallel workers (default {DEFAULT_JOBS})")
    ap.add_argument("--v131-dir", default="/tmp/kh-v131",
                    help="v1.3.1 kicad-happy worktree")
    ap.add_argument("--v14-dir", default="/tmp/kh-v14",
                    help="v1.4-dev kicad-happy worktree")
    ap.add_argument("--timeout", type=int, default=ANALYZER_TIMEOUT,
                    help=f"per-analyzer timeout (default {ANALYZER_TIMEOUT}s)")
    ap.add_argument("--resume", action="store_true",
                    help="skip units that already have a diff record")
    ap.add_argument("--label", default=None,
                    help="rollup filename label (default: section name)")
    args = ap.parse_args(argv)

    for d in (args.v131_dir, args.v14_dir):
        if not Path(d).exists():
            print(f"Error: worktree {d} does not exist. Create it:\n"
                  f"  git -C ~/Projects/kicad-happy worktree add {d} <ref>",
                  file=sys.stderr)
            sys.exit(2)

    repos = resolve_repos(args)
    section = (args.label or getattr(args, "cross_section", None)
               or getattr(args, "repo", None) or "full")
    section = section.replace("/", "_")
    n_repos = len(repos) if repos is not None else len(list_repos())
    print(f"=== v1.4 Layer 1 regression gate ===")
    print(f"  v1.3.1 worktree: {args.v131_dir}")
    print(f"  v1.4   worktree: {args.v14_dir}")
    print(f"  repos: {n_repos}   jobs: {args.jobs}   section: {section}")
    GATE_DIR.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    # Phase A -- file-input analyzers
    print("\n[Phase A] schematic / pcb / gerber")
    a_jobs = _build_phase_a_jobs(repos, args.v131_dir, args.v14_dir,
                                 args.timeout, args.resume)
    a_results = _run_jobs(a_jobs, _phase_a_job, args.jobs, "Phase A")

    # Phase B -- chained analyzers (consume Phase A snapshots)
    print("\n[Phase B] thermal / emc / cross_analysis")
    b_jobs = _build_phase_b_jobs(repos, args.timeout, args.resume)
    b_results = _run_jobs(b_jobs, _phase_b_job, args.jobs, "Phase B",
                          initializer=_init_phase_b,
                          initargs=(args.v131_dir, args.v14_dir))

    records = a_results + b_results
    agg = _aggregate(records)

    out_json = GATE_DIR / f"rollup_{section}.json"
    out_csv = GATE_DIR / f"rollup_{section}.csv"
    report = _write_rollup(records, agg, section, out_json, out_csv)
    _print_summary(report)
    print(f"\nElapsed: {time.time()-t_start:.0f}s")
    print(f"Rollup JSON: {out_json}")
    print(f"Rollup CSV:  {out_csv}")

    # exit 1 if not clean (any disappeared finding or severity downgrade)
    sys.exit(0 if report["pass_criteria"]["clean"] else 1)


if __name__ == "__main__":
    main()
