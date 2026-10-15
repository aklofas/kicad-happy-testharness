#!/usr/bin/env python3
"""Corpus regression gate (H0-1): baseline vs candidate product worktrees.

Successor of run_v14_gate.py (kept as a flag-compatible wrapper). Changes
(report A3/A6/B12):
  * slots are baseline/candidate (not v131/v14)
  * every analyzer run goes through harnesslib.execution.run_once: exit codes
    recorded, accepted-exit table, temp-then-publish, stale quarantine
  * a run manifest (manifest.json) + units.jsonl bind the gate to product and
    harness SHAs, args, env, selection and input digests, expected census
  * Phase B enumerates the Phase A success records, not directories on disk
  * --resume reuses a unit only on identity match (manifest + input sha)
  * exit 0 only when strict_clean AND census complete AND no both_failed /
    dependency_missing SKIPs ("gate_pass"); `clean` is kept for history
  * per-unit diff records keep complete lists (no top-five truncation)

Usage:
    python3 regression/run_corpus_gate.py --baseline-dir /tmp/kh-base --candidate-dir /tmp/kh-cand \\
        --gate-dir results/<label>_gate --label <label> --cross-section quick_200 --jobs 32
    python3 regression/run_corpus_gate.py ... --profile long-tail --repo-list results/timeouts.txt
    python3 regression/run_corpus_gate.py ... --all --jobs 32          # full corpus (explicit)
    python3 regression/run_corpus_gate.py ... --resume                 # identity-matched resume

A non-empty --gate-dir without --resume is an error (exit 2). With --resume the
previous manifest.json/units.jsonl are archived as manifest.<run_id>.json /
units.<run_id>.jsonl (never deleted). argv is part of the run identity, so a
changed --jobs/--label (or any other flag) breaks resume by design.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "regression"))

import regression_diff as rdiff  # noqa: E402
from harnesslib.execution import run_once, build_env, recorded_env  # noqa: E402
from harnesslib.identity import (RunSpec, git_worktree_ref, sha256_path, input_digest,  # noqa: E402
                                 write_manifest, finish_manifest, read_manifest,
                                 manifests_match, identity_key, unit_is_current,
                                 MANIFEST_VERSION, UnitLog)
from harnesslib.profiles import PROFILES  # noqa: E402
from utils import (MANIFESTS_DIR, DEFAULT_JOBS, add_repo_filter_args,  # noqa: E402
                   resolve_repos_with_source, list_repos, filter_manifest_by_repo,
                   repo_name_from_path, safe_name)

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
MANIFEST_FILE = {"schematic": "all_schematics.txt", "pcb": "all_pcbs.txt",
                 "gerber": "all_gerbers.txt"}
SLOTS = ("baseline", "candidate")
SKIP_REASONS = ("not_applicable", "both_failed", "dependency_missing", "snapshot_read_error")
BAD_SKIP_REASONS = ("both_failed", "dependency_missing", "snapshot_read_error")
OK_STATUSES = ("ok", "ok_findings_exit")


class GateLayout:
    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    @property
    def units(self) -> Path:
        return self.root / "units.jsonl"

    def snap(self, slot: str, analyzer: str, repo: str, key: str) -> Path:
        # per-unit private dir: analyzers write a capability_mode.json sidecar
        # with a non-concurrency-safe writer (see run_v14_gate history)
        return self.root / slot / analyzer / repo / key / "snap.json"

    def diff(self, analyzer: str, repo: str, key: str) -> Path:
        return self.root / "diff" / analyzer / repo / f"{key}.json"

    def rollup(self, section: str) -> Path:
        return self.root / f"rollup_{section}.json"


def file_cmd(analyzer, kh_dir, input_path, out_path, profile):
    script = str(Path(kh_dir) / ANALYZER_REL[analyzer])
    cmd = [sys.executable, script, str(input_path), "-o", str(out_path)]
    if analyzer == "schematic" and profile.schematic_no_hierarchy:
        cmd.append("--no-hierarchy")
    if analyzer == "pcb" and profile.pcb_full:
        cmd.append("--full")
    if profile.only_deterministic:
        cmd.append("--only-deterministic")
    return cmd


def chained_cmd(analyzer, kh_dir, sch_json, pcb_json, out_path, profile):
    script = str(Path(kh_dir) / ANALYZER_REL[analyzer])
    cmd = [sys.executable, script, "--schematic", str(sch_json), "--output", str(out_path)]
    if pcb_json is not None:
        cmd += ["--pcb", str(pcb_json)]
    if profile.only_deterministic:
        cmd.append("--only-deterministic")
    return cmd


def _side(res) -> dict:
    return {"status": res.status, "exit_code": res.exit_code,
            "output_sha256": res.output_sha256, "elapsed_s": round(res.elapsed_s, 3),
            "detail": res.detail}


def _ok(res) -> bool:
    return res.status in ("ok", "ok_findings_exit")


def diff_envelopes(a_path, b_path, a_ok, b_ok):
    """Diff two snapshot envelopes with regression_diff; complete lists kept."""
    if not a_ok and not b_ok:
        return {"verdict": "SKIP", "reason": "both_failed"}
    zero = {"disappeared_count": 0, "severity_downgrades": 0, "severity_upgrades": 0,
            "new_known_count": 0, "new_upgraded_count": 0, "new_unknown_count": 0}
    if a_ok and not b_ok:
        return {"verdict": "FAIL", "reason": "candidate failed/produced no output", **zero}
    if not a_ok and b_ok:
        return {"verdict": "WARN", "reason": "baseline failed; not comparable", **zero}
    try:
        before = json.loads(Path(a_path).read_text(encoding="utf-8"))
        after = json.loads(Path(b_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        return {"verdict": "SKIP", "reason": "snapshot_read_error", "detail": str(e)}
    d = rdiff.diff(rdiff._collect_observations(before), rdiff._collect_observations(after))
    verdict, reason = rdiff.verdict(d)
    downgrades = [c for c in d["severity_changes"] if c["kind"] == "downgrade"]
    upgrades = [c for c in d["severity_changes"] if c["kind"] == "upgrade"]
    return {
        "verdict": verdict, "reason": reason,
        "disappeared_count": len(d["disappeared"]),
        "severity_downgrades": len(downgrades), "severity_upgrades": len(upgrades),
        "new_known_count": len(d["new_known"]), "new_upgraded_count": len(d["new_upgraded"]),
        "new_unknown_count": len(d["new_unknown"]),
        "disappeared": [{"rule_id": f.get("rule_id"), "components": f.get("components"),
                         "summary": f.get("summary") or ""} for f in d["disappeared"]],
        "downgrades": downgrades, "upgrades": upgrades,
        "new_known_rule_ids": [f.get("rule_id") for f in d["new_known"]],
        "new_upgraded_rule_ids": [f.get("rule_id") for f in d["new_upgraded"]],
        "new_unknown_rule_ids": [f.get("rule_id") for f in d["new_unknown"]],
    }


def phase_a_job(args):
    (analyzer, input_path, repo, baseline_dir, candidate_dir, gate_root, profile_name) = args
    profile = PROFILES[profile_name]
    lay = GateLayout(gate_root)
    key = safe_name(input_path)
    unit_id = f"{repo}/{key}"
    env = build_env(offline=profile.offline)
    base_out = lay.snap("baseline", analyzer, repo, key)
    cand_out = lay.snap("candidate", analyzer, repo, key)
    base = run_once(lambda o: file_cmd(analyzer, baseline_dir, input_path, o, profile),
                    base_out, analyzer=analyzer, timeout=profile.timeout_s, env=env)
    cand = run_once(lambda o: file_cmd(analyzer, candidate_dir, input_path, o, profile),
                    cand_out, analyzer=analyzer, timeout=profile.timeout_s, env=env)
    rec = {"analyzer": analyzer, "repo": repo, "identity": unit_id, "unit_id": unit_id,
           "input_sha256": sha256_path(input_path),
           "baseline": _side(base), "candidate": _side(cand)}
    rec.update(diff_envelopes(base_out, cand_out, _ok(base), _ok(cand)))
    diff_out = lay.diff(analyzer, repo, key)
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    diff_out.write_text(json.dumps({"_record": rec}, indent=2), encoding="utf-8")
    return rec


def _load_manifest(analyzer, repos):
    path = MANIFESTS_DIR / MANIFEST_FILE[analyzer]
    if not path.exists():
        print(f"  WARN: manifest {path} missing", file=sys.stderr)
        return []
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if repos is None:
        return lines
    out = []
    for rn in repos:
        out.extend(filter_manifest_by_repo(lines, rn))
    return out


def build_phase_a_jobs(repos, layout, baseline_dir, candidate_dir, profile):
    jobs = []
    for analyzer in PHASE_A:
        if analyzer not in profile.analyzers:
            continue
        for input_path in _load_manifest(analyzer, repos):
            repo = repo_name_from_path(input_path)
            if repo is None:
                continue
            jobs.append((analyzer, input_path, repo, str(baseline_dir), str(candidate_dir),
                         str(layout.root), profile.name))
    return jobs


def expected_census(a_jobs) -> dict[str, int]:
    return dict(Counter(j[0] for j in a_jobs))


def _compute_pass_criteria(totals: dict) -> dict:
    """Unchanged shape from run_v14_gate (tests/test_v14_gate_criteria.py imports it)."""
    return {
        "disappeared_count": totals["Disappeared"],
        "severity_downgrades": totals["Downgrades"],
        "fail_verdicts": totals["FAIL"],
        "new_unknown_count": totals["NewUnknown"],
        "new_upgraded_count": totals["NewUpgraded"],
        "warn_count": totals["WARN"],
        "clean": (totals["Disappeared"] == 0 and totals["Downgrades"] == 0
                  and totals["FAIL"] == 0 and totals["NewUnknown"] == 0),
        "strict_clean": (totals["Disappeared"] == 0 and totals["Downgrades"] == 0
                         and totals["FAIL"] == 0 and totals["NewUnknown"] == 0
                         and totals["WARN"] == 0),
    }


def _print_summary(report):
    print()
    print("=" * 78)
    print(f"Corpus regression gate -- section: {report['section']}  "
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
    gp = report.get("gate_pass")
    if gp is not None:
        print(f"  => GATE {'PASS' if gp['pass'] else 'FAIL'}: strict_clean={gp['strict_clean']} "
              f"census_ok={gp['census_ok']} skips_ok={gp['skips_ok']}")
    m = report.get("modes", {})
    if "raw" in m:
        print(f"modes: raw={m['raw']['verdict']} strict={m['strict']['verdict']} "
              f"budgeted={m['budgeted']['verdict']} -> strict_field_clean={report['gate_pass']['strict_field_clean']}")
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
# Phase B -- chained analyzers, enumerated from the Phase A success records
# ---------------------------------------------------------------------------

def _skip_record(analyzer, repo, sch_key, reason):
    unit_id = f"{repo}/{sch_key}"
    return {"analyzer": analyzer, "repo": repo, "identity": unit_id, "unit_id": unit_id,
            "input_sha256": None, "baseline": {"status": "skipped"},
            "candidate": {"status": "skipped"}, "verdict": "SKIP", "reason": reason}


def _pcb_key_for(sch_key):
    for old in (".kicad_sch", ".sch"):
        if sch_key.endswith(old):
            return sch_key[:-len(old)] + ".kicad_pcb"
    return None


def _both_ok(rec):
    b, c = rec.get("baseline"), rec.get("candidate")
    return (isinstance(b, dict) and isinstance(c, dict)
            and b["status"] in OK_STATUSES and c["status"] in OK_STATUSES)


def build_phase_b_jobs(a_records, layout, baseline_dir, candidate_dir, profile):
    """Pair Phase A schematic records with PCB records. Returns (jobs, skip_records).

    A schematic unit that did not succeed on BOTH sides yields a
    dependency_missing SKIP for every Phase B analyzer. thermal without a PCB
    pair is not_applicable; emc/cross_analysis treat the PCB as optional."""
    ok_pcb = {r["unit_id"] for r in a_records if r["analyzer"] == "pcb" and _both_ok(r)}
    jobs, skips = [], []
    for r in a_records:
        if r["analyzer"] != "schematic":
            continue
        repo, sch_key = r["repo"], r["unit_id"][len(r["repo"]) + 1:]
        if not _both_ok(r):
            skips.extend(_skip_record(a, repo, sch_key, "dependency_missing")
                         for a in PHASE_B if a in profile.analyzers)
            continue
        pcb_key = _pcb_key_for(sch_key)
        has_pcb = pcb_key is not None and f"{repo}/{pcb_key}" in ok_pcb
        for analyzer in PHASE_B:
            if analyzer not in profile.analyzers:
                continue
            if analyzer == "thermal" and not has_pcb:
                skips.append(_skip_record(analyzer, repo, sch_key, "not_applicable"))
                continue
            jobs.append((analyzer, repo, sch_key, pcb_key if has_pcb else None,
                         str(baseline_dir), str(candidate_dir), str(layout.root),
                         profile.name, r["input_sha256"]))
    return jobs, skips


def phase_b_job(args):
    (analyzer, repo, sch_key, pcb_key, baseline_dir, candidate_dir, gate_root,
     profile_name, sch_input_sha) = args
    profile = PROFILES[profile_name]
    lay = GateLayout(gate_root)
    env = build_env(offline=profile.offline)
    sides = {}
    for slot, kh_dir in (("baseline", baseline_dir), ("candidate", candidate_dir)):
        sch = lay.snap(slot, "schematic", repo, sch_key)
        pcb = lay.snap(slot, "pcb", repo, pcb_key) if pcb_key else None
        out = lay.snap(slot, analyzer, repo, sch_key)
        sides[slot] = run_once(lambda o, k=kh_dir, s=sch, p=pcb: chained_cmd(analyzer, k, s, p, o, profile),
                               out, analyzer=analyzer, timeout=profile.timeout_s, env=env)
    base, cand = sides["baseline"], sides["candidate"]
    unit_id = f"{repo}/{sch_key}"
    rec = {"analyzer": analyzer, "repo": repo, "identity": unit_id, "unit_id": unit_id,
           "input_sha256": sch_input_sha, "baseline": _side(base), "candidate": _side(cand),
           "deps": {"schematic": unit_id, "pcb": f"{repo}/{pcb_key}" if pcb_key else None}}
    rec.update(diff_envelopes(lay.snap("baseline", analyzer, repo, sch_key),
                              lay.snap("candidate", analyzer, repo, sch_key), _ok(base), _ok(cand)))
    diff_out = lay.diff(analyzer, repo, sch_key)
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    diff_out.write_text(json.dumps({"_record": rec}, indent=2), encoding="utf-8")
    return rec


# ---------------------------------------------------------------------------
# resume, execution, aggregation, rollup
# ---------------------------------------------------------------------------

class _OneRecordLog:
    """Adapter so harnesslib.identity.unit_is_current can judge one side of a record."""

    def __init__(self, key, record):
        self._m = {key: record}

    def by_unit(self):
        return self._m


def _side_current(layout, slot, rec, input_sha):
    side = rec.get(slot)
    if not isinstance(side, dict):
        return False
    analyzer, unit_id, repo = rec["analyzer"], rec["unit_id"], rec["repo"]
    view = {**rec, "status": side.get("status"), "output_sha256": side.get("output_sha256")}
    snap = layout.snap(slot, analyzer, repo, unit_id[len(repo) + 1:])
    return unit_is_current(_OneRecordLog(f"{analyzer}/{unit_id}", view), analyzer, unit_id,
                           input_sha, snap)


def resume_plan(layout, spec, input_shas=None):
    """Return (reusable, reasons). reusable maps 'analyzer/unit_id' -> record.

    Nothing is reusable unless the previous manifest's identity matches this
    spec (clean worktrees, same SHAs/argv/selection/env). Per unit, both the
    baseline and candidate snapshots must still hash to the logged output and
    both sides must have succeeded; SKIP/FAIL/WARN records always rerun.
    input_shas maps 'analyzer/unit_id' -> current input sha256 for Phase A
    units (absent => not reusable). Phase B records are returned with their
    logged input_sha256 for the caller to compare against the schematic
    snapshot's input (they have no input file of their own). None skips the
    input check entirely."""
    if not layout.manifest.exists():
        return {}, ["no previous manifest"]
    prev = read_manifest(layout.root)
    probe = {"manifest_version": MANIFEST_VERSION, "identity": identity_key(spec),
             "harness": asdict(spec.harness),
             "product": {"baseline": asdict(spec.baseline) if spec.baseline else None,
                         "candidate": asdict(spec.candidate) if spec.candidate else None}}
    ok, reasons = manifests_match(prev, probe)
    if not ok:
        return {}, reasons
    reusable = {}
    for key, rec in UnitLog(layout.root).by_unit().items():
        if rec.get("verdict") == "SKIP" or not rec.get("repo") or not rec.get("unit_id"):
            continue
        if input_shas is None or rec["analyzer"] not in PHASE_A:
            input_sha = rec.get("input_sha256")
        elif key in input_shas:
            input_sha = input_shas[key]
        else:
            continue
        if all(_side_current(layout, slot, rec, input_sha) for slot in SLOTS):
            reusable[key] = rec
    return reusable, []


def _exception_record(analyzer, repo, unit_id, exc):
    """A worker that raised is a FAIL unit, not a dead run (report I2)."""
    return {"analyzer": analyzer, "repo": repo, "identity": unit_id, "unit_id": unit_id,
            "verdict": "FAIL", "reason": "worker_exception",
            "detail": f"{type(exc).__name__}: {exc}", "baseline": None, "candidate": None}


def _exc_record_a(job, exc):
    analyzer, input_path, repo = job[0], job[1], job[2]
    return _exception_record(analyzer, repo, f"{repo}/{safe_name(input_path)}", exc)


def _exc_record_b(job, exc):
    analyzer, repo, sch_key = job[0], job[1], job[2]
    return _exception_record(analyzer, repo, f"{repo}/{sch_key}", exc)


def _run_jobs(jobs, worker, jobs_n, label, sink, on_error):
    """Run jobs, handing each record to sink(record) as it completes."""
    if not jobs:
        return []
    print(f"  {label}: {len(jobs)} units, {jobs_n} workers")
    results, t0, done = [], time.time(), 0

    def finish(job, get):
        nonlocal done
        try:
            rec = get()
        except Exception as exc:  # noqa: BLE001 - any worker failure is a FAIL unit
            rec = on_error(job, exc)
        sink(rec)
        results.append(rec)
        done += 1
        if done % 200 == 0:
            print(f"    {done}/{len(jobs)} ({time.time()-t0:.0f}s)")

    if jobs_n <= 1:
        for job in jobs:
            finish(job, lambda j=job: worker(j))
    else:
        with ProcessPoolExecutor(max_workers=jobs_n) as pool:
            futs = {pool.submit(worker, job): job for job in jobs}
            for fut in as_completed(futs):
                finish(futs[fut], fut.result)
    print(f"  {label} done: {len(results)} units in {time.time()-t0:.0f}s")
    return results


def aggregate(records):
    by_analyzer = {a: Counter() for a in ALL_ANALYZERS}
    fail_repos = defaultdict(list)
    new_known_rules, new_upgraded_rules, new_unknown_rules = Counter(), Counter(), Counter()
    skip_breakdown = Counter({r: 0 for r in SKIP_REASONS})
    executed = Counter()
    for r in records:
        c = by_analyzer[r["analyzer"]]
        c[r["verdict"]] += 1
        dep_missing = r["verdict"] == "SKIP" and r.get("reason") == "dependency_missing"
        if r["verdict"] == "SKIP":
            skip_breakdown[r.get("reason", "both_failed")] += 1
        # dependency_missing units were never attempted and are not in the
        # Phase B expectation; skips_ok already fails the gate on them
        if not dep_missing:
            executed[r["analyzer"]] += 1
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
        if r["verdict"] == "FAIL":
            fail_repos[r["repo"]].append(r)
    return {"by_analyzer": by_analyzer, "fail_repos": fail_repos,
            "new_known_rules": new_known_rules, "new_upgraded_rules": new_upgraded_rules,
            "new_unknown_rules": new_unknown_rules, "skip_breakdown": dict(skip_breakdown),
            "executed_census": dict(executed)}


def compute_gate_pass(criteria, skip_breakdown, expected_census, executed_census):
    skips_ok = all(skip_breakdown.get(r, 0) == 0 for r in BAD_SKIP_REASONS)
    census_ok = all(executed_census.get(a, 0) == n for a, n in expected_census.items())
    strict = bool(criteria["strict_clean"])
    return {"pass": strict and skips_ok and census_ok, "strict_clean": strict,
            "census_ok": census_ok, "skips_ok": skips_ok,
            "skip_breakdown": dict(skip_breakdown),
            "expected_census": dict(expected_census), "executed_census": dict(executed_census)}


def write_rollup(records, agg, section, layout, manifest):
    rows = []
    for a in ALL_ANALYZERS:
        c = agg["by_analyzer"][a]
        rows.append({"analyzer": a, "PASS": c.get("PASS", 0), "WARN": c.get("WARN", 0),
                     "FAIL": c.get("FAIL", 0), "SKIP": c.get("SKIP", 0),
                     "Disappeared": c.get("disappeared", 0), "Downgrades": c.get("downgrades", 0),
                     "Upgrades": c.get("upgrades", 0), "NewKnown": c.get("new_known", 0),
                     "NewUpgraded": c.get("new_upgraded", 0), "NewUnknown": c.get("new_unknown", 0)})
    totals = {k: sum(row[k] for row in rows) for k in
              ("PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades", "Upgrades",
               "NewKnown", "NewUpgraded", "NewUnknown")}
    fail_list = [{"repo": repo, "analyzers": sorted({r["analyzer"] for r in recs}),
                  "units": [{"analyzer": r["analyzer"], "identity": r["identity"],
                             "reason": r.get("reason"), "disappeared": r.get("disappeared", []),
                             "downgrades": r.get("downgrades", [])} for r in recs]}
                 for repo, recs in sorted(agg["fail_repos"].items())]
    criteria = _compute_pass_criteria(totals)
    gate_pass = compute_gate_pass(criteria, agg["skip_breakdown"],
                                  manifest.get("expected_census", {}), agg["executed_census"])
    summary_mode = "strict_clean" if criteria["strict_clean"] else ("clean" if criteria["clean"] else "not_clean")
    product = manifest.get("product") or {}
    report = {
        "section": section, "total_units": len(records), "rollup": rows, "totals": totals,
        "fail_repo_count": len(agg["fail_repos"]), "fail_repos": fail_list,
        "new_known_rule_distribution": dict(agg["new_known_rules"].most_common()),
        "new_upgraded_rule_distribution": dict(agg["new_upgraded_rules"].most_common()),
        "new_unknown_rule_distribution": dict(agg["new_unknown_rules"].most_common()),
        "pass_criteria": criteria,
        "gate_pass": gate_pass,
        "modes": {"findings_summary": summary_mode},
        "identity": {"run_id": manifest.get("run_id"), "profile": manifest.get("profile"),
                     "harness_sha": (manifest.get("harness") or {}).get("sha"),
                     "baseline_sha": (product.get("baseline") or {}).get("sha"),
                     "candidate_sha": (product.get("candidate") or {}).get("sha"),
                     "selection": manifest.get("selection"), "input_digest": manifest.get("input_digest"),
                     "normalization_policy": manifest.get("normalization_policy")},
    }
    out_json = layout.rollup(section)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    with out_json.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        cols = ["Analyzer", "PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades",
                "Upgrades", "NewKnown", "NewUpgraded", "NewUnknown"]
        w.writerow(cols)
        for row in rows:
            w.writerow([row["analyzer"]] + [row[c] for c in cols[1:]])
        w.writerow(["TOTAL"] + [totals[c] for c in cols[1:]])
    return report


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def build_arg_parser():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    add_repo_filter_args(ap)
    ap.add_argument("--baseline-dir", required=True, help="baseline kicad-happy worktree")
    ap.add_argument("--candidate-dir", required=True, help="candidate kicad-happy worktree")
    ap.add_argument("--gate-dir", required=True, help="evidence tree root (results/<label>_gate)")
    ap.add_argument("--profile", default="standard", choices=sorted(PROFILES))
    ap.add_argument("--kind", default="gate", choices=("gate", "aa", "baseline"))
    ap.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS)
    ap.add_argument("--label", default=None, help="rollup filename label (default: section)")
    ap.add_argument("--resume", action="store_true",
                    help="reuse units from a previous run ONLY if its manifest identity matches")
    ap.add_argument("--budget", default=None, metavar="FILE",
                    help="regression/budgets/<id>.json; enables the budgeted mode verdict")
    return ap


def apply_modes(report, modes):
    """Merge run_modes() output into the rollup and AND strict_field_clean into gate_pass."""
    report["modes"] = {**report.get("modes", {}), **modes}
    gp = report.setdefault("gate_pass", {})
    gp["strict_field_clean"] = bool(modes.get("strict_field_clean"))
    gp["pass"] = bool(gp.get("pass")) and gp["strict_field_clean"]
    return report


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    profile = PROFILES[args.profile]
    for d in (args.baseline_dir, args.candidate_dir):
        if not Path(d).exists():
            print(f"Error: worktree {d} does not exist", file=sys.stderr)
            sys.exit(2)
    if args.budget:
        # validate up front: a malformed budget must not surface after an hour of phase A/B
        from regression.field_compare import BudgetError, load_budget
        try:
            load_budget(Path(args.budget))
        except BudgetError as e:
            print(f"Error: --budget {args.budget}: {e}", file=sys.stderr)
            sys.exit(2)
    base_ref, cand_ref = git_worktree_ref(Path(args.baseline_dir)), git_worktree_ref(Path(args.candidate_dir))
    if args.kind != "aa" and (base_ref.dirty or cand_ref.dirty):
        print("Error: product worktree is dirty; evidence runs need clean worktrees", file=sys.stderr)
        sys.exit(2)
    gd = Path(args.gate_dir)
    layout = GateLayout(gd if gd.is_absolute() else HARNESS_DIR / gd)
    prev_run_id = None
    present = [n for n in ("manifest.json", "baseline", "candidate", "diff", "v131", "v14")
               if (layout.root / n).exists()]
    if layout.manifest.exists():
        try:
            prev_run_id = read_manifest(layout.root).get("run_id") or "unknown"
        except (OSError, ValueError):
            prev_run_id = "unreadable"
    if present and not args.resume:
        print(f"Error: gate dir {layout.root} is not empty ({', '.join(present)}); "
              f"pass --resume or a fresh --gate-dir", file=sys.stderr)
        sys.exit(2)

    repos, selection_source = resolve_repos_with_source(args, require_explicit_all=True)
    section = (args.label or getattr(args, "cross_section", None)
               or getattr(args, "repo", None) or "full").replace("/", "_")

    a_jobs = build_phase_a_jobs(repos, layout, args.baseline_dir, args.candidate_dir, profile)
    a_key = lambda j: f"{j[0]}/{j[2]}/{safe_name(j[1])}"  # noqa: E731
    unit_ids = sorted(f"{j[2]}/{safe_name(j[1])}" for j in a_jobs)
    env = build_env(offline=profile.offline)
    spec = RunSpec(kind=args.kind, profile=profile.name, harness=git_worktree_ref(HARNESS_DIR),
                   baseline=base_ref, candidate=cand_ref,
                   argv=tuple(a for a in (argv if argv is not None else sys.argv[1:]) if a != "--resume"),
                   selection_source=selection_source, unit_ids=tuple(unit_ids),
                   normalization_policy="volatile-leaves-v1", env=recorded_env(env))

    input_shas = {a_key(j): sha256_path(j[1]) for j in a_jobs}
    reusable = {}
    if args.resume:
        reusable, reasons = resume_plan(layout, spec, input_shas=input_shas)
        if reasons and present:
            print(f"Error: identity mismatch ({'; '.join(reasons)}); pass a fresh --gate-dir",
                  file=sys.stderr)
            sys.exit(2)
        print(f"  resume: {len(reusable)} reusable units")

    # archive (never delete) the previous run's identity and log
    layout.root.mkdir(parents=True, exist_ok=True)
    if prev_run_id is not None:
        for src, name in ((layout.manifest, f"manifest.{prev_run_id}.json"),
                          (layout.units, f"units.{prev_run_id}.jsonl")):
            if src.exists():
                os.replace(src, layout.root / name)
                print(f"  archived previous {src.name} -> {name}")
    write_manifest(layout.root, spec, run_id=str(uuid.uuid4()), expected_census=expected_census(a_jobs),
                   input_digest=input_digest(sorted(input_shas_by_unit(a_jobs, input_shas))),
                   runtime={"python": platform.python_version(), "platform": platform.platform()})
    manifest = read_manifest(layout.root)
    log = UnitLog(layout.root)
    n_repos = len(repos) if repos is not None else len(list_repos())
    print(f"=== Corpus regression gate ===\n  profile: {profile.name}   kind: {args.kind}\n"
          f"  baseline:  {args.baseline_dir} @ {base_ref.sha[:12]}\n"
          f"  candidate: {args.candidate_dir} @ {cand_ref.sha[:12]}\n"
          f"  gate dir:  {layout.root}\n  repos: {n_repos}   jobs: {args.jobs}   section: {section}")
    t_start = time.time()

    def reuse(key):
        rec = {**reusable[key], "reused": True}
        log.append(rec)
        return rec

    print("\n[Phase A] " + " / ".join(a for a in PHASE_A if a in profile.analyzers))
    a_keys = [a_key(j) for j in a_jobs]
    a_results = [reuse(k) for k in a_keys if k in reusable]
    a_results += _run_jobs([j for j in a_jobs if a_key(j) not in reusable], phase_a_job,
                           args.jobs, "Phase A", log.append, _exc_record_a)
    rerun_a = {k for k in a_keys if k not in reusable}

    print("\n[Phase B] " + " / ".join(a for a in PHASE_B if a in profile.analyzers))
    b_jobs, b_skips = build_phase_b_jobs(a_results, layout, args.baseline_dir, args.candidate_dir, profile)

    def b_reusable(j):
        # reusable only if the logged schematic input matches AND no Phase A input it consumed reran
        analyzer, repo, sch_key, pcb_key = j[0], j[1], j[2], j[3]
        rec = reusable.get(f"{analyzer}/{repo}/{sch_key}")
        if rec is None or rec.get("input_sha256") != j[8]:
            return False
        deps = {"schematic": f"{repo}/{sch_key}", "pcb": f"{repo}/{pcb_key}" if pcb_key else None}
        if rec.get("deps") != deps:
            return False
        return not any(f"{kind}/{uid}" in rerun_a for kind, uid in deps.items() if uid)

    b_results = []
    for rec in b_skips:
        log.append(rec); b_results.append(rec)
    todo_b = []
    for j in b_jobs:
        if b_reusable(j):
            b_results.append(reuse(f"{j[0]}/{j[1]}/{j[2]}"))
        else:
            todo_b.append(j)
    b_results += _run_jobs(todo_b, phase_b_job, args.jobs, "Phase B", log.append, _exc_record_b)

    # Phase B expectation: one unit per Phase A schematic success pair per analyzer
    # (thermal's not_applicable units included so the census balances)
    n_sch_ok = sum(1 for r in a_results if r["analyzer"] == "schematic" and _both_ok(r))
    b_expected = {a: n_sch_ok for a in PHASE_B if a in profile.analyzers}
    manifest = {**manifest, "expected_census": {**manifest.get("expected_census", {}), **b_expected}}

    records = a_results + b_results
    agg = aggregate(records)
    report = write_rollup(records, agg, section, layout, manifest)
    from regression.field_compare import BudgetError, run_modes  # local import keeps the gate importable standalone
    try:
        modes = run_modes(layout.root, budget_path=Path(args.budget) if args.budget else None)
    except (FileNotFoundError, BudgetError) as e:
        print(f"Error: comparator modes could not run: {e}", file=sys.stderr)
        sys.exit(2)
    report = apply_modes(report, modes)
    layout.rollup(section).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    finish_manifest(layout.root, {**report["totals"], "skip_breakdown": agg["skip_breakdown"],
                                  "expected_census": manifest["expected_census"],
                                  "executed_census": agg["executed_census"],
                                  "modes": {k: v.get("verdict") for k, v in modes.items() if isinstance(v, dict)}})
    _print_summary(report)
    print(f"\nElapsed: {time.time()-t_start:.0f}s\nRollup JSON: {layout.rollup(section)}")
    sys.exit(0 if report["gate_pass"]["pass"] else 1)


def input_shas_by_unit(a_jobs, input_shas):
    return [(f"{j[2]}/{safe_name(j[1])}", input_shas[f"{j[0]}/{j[2]}/{safe_name(j[1])}"]) for j in a_jobs]


if __name__ == "__main__":
    main()
