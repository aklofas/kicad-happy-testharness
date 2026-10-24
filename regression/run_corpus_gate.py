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
    dependency_missing SKIPs AND modes.strict_field_clean ("gate_pass"); `clean`
    is kept for history
  * after phase B the comparator modes run (raw + strict, budgeted with
    --budget; spec §3.5) and land under rollup["modes"]. With --budget,
    strict_field_clean is the budgeted verdict == clean.
  * gate_pass per --kind (maintainer ruling I9; overrides spec §2.4 read
    literally for the output-changing kinds):
      kind             --budget    gate_pass.pass
      structural       forbidden   findings strict_clean AND strict_field_clean
                                   AND census_ok AND skips_ok AND candidate_failures == 0
      aa, baseline     forbidden   same as structural
      output-changing  required    census_ok AND skips_ok AND budgeted verdict clean
                                   AND candidate_failures == 0
      relock           required    same as output-changing
    candidate_failures (baseline ok, candidate failed/no output) are never budgetable.
    For the output-changing kinds the findings strict_clean stays in gate_pass
    as information only. `--kind gate` is a deprecated alias for structural.
    gate_pass records the resolved `kind` and its `criterion`; the sha256 of
    the budget file is recorded as budget_sha256 (null without a budget).
  * per-unit diff records keep complete lists (no top-five truncation)
  * skips_ok consults the baseline-debts ledger (--ledger; default
    reference/baseline_debts/<baseline sha7>.json when present): a both_failed /
    dependency_missing SKIP is bad only when tools/baseline_ledger_check does not
    cover its identity (timeout_units, or crash_units for a both-sided crash with the
    ledgered exit_code). gate_pass records ledgered_skips, unledgered_skips and
    ledgered_unaccepted (covering entries with accepted_by null); the ledger's
    product_sha must match the baseline sha (exit 2); the ledger path + sha256 land in
    the rollup identity and the finished manifest.

Usage:
    python3 regression/run_corpus_gate.py --baseline-dir /tmp/kh-base --candidate-dir /tmp/kh-cand \\
        --gate-dir results/<label>_gate --label <label> --cross-section quick_200 --jobs 32
    python3 regression/run_corpus_gate.py ... --profile long-tail --repo-list results/timeouts.txt
    python3 regression/run_corpus_gate.py ... --all --jobs 32          # full corpus (explicit)
    python3 regression/run_corpus_gate.py ... --resume                 # identity-matched resume
    python3 regression/run_corpus_gate.py --recheck GATE_DIR [--ledger FILE]   # re-evaluate gate_pass only

A non-empty --gate-dir without --resume is an error (exit 2). With --resume the
previous manifest.json/units.jsonl are archived as manifest.<run_id>.json /
units.<run_id>.jsonl (never deleted). argv is part of the run identity, so a
changed --jobs/--label (or any other flag) breaks resume by design.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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


CANDIDATE_FAILED_REASON = "candidate failed/produced no output"


def diff_envelopes(a_path, b_path, a_ok, b_ok):
    """Diff two snapshot envelopes with regression_diff; complete lists kept."""
    if not a_ok and not b_ok:
        return {"verdict": "SKIP", "reason": "both_failed"}
    zero = {"disappeared_count": 0, "severity_downgrades": 0, "severity_upgrades": 0,
            "new_known_count": 0, "new_upgraded_count": 0, "new_unknown_count": 0,
            "rewrites_count": 0}
    if a_ok and not b_ok:
        return {"verdict": "FAIL", "reason": CANDIDATE_FAILED_REASON, **zero}
    if not a_ok and b_ok:
        return {"verdict": "WARN", "reason": "baseline failed; not comparable", **zero}
    try:
        before = json.loads(Path(a_path).read_text(encoding="utf-8"))
        after = json.loads(Path(b_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
        return {"verdict": "SKIP", "reason": "snapshot_read_error", "detail": str(e)}
    d = rdiff.diff(rdiff._collect_observations(before), rdiff._collect_observations(after))
    verdict, reason = rdiff.verdict(d)
    downgrades = ([c for c in d["severity_changes"] if c["kind"] == "downgrade"]
                  + [r for r in d["rewrites"] if r["severity_kind"] == "downgrade"])
    upgrades = ([c for c in d["severity_changes"] if c["kind"] == "upgrade"]
                + [r for r in d["rewrites"] if r["severity_kind"] == "upgrade"])
    return {
        "verdict": verdict, "reason": reason,
        "disappeared_count": len(d["disappeared"]),
        "severity_downgrades": len(downgrades), "severity_upgrades": len(upgrades),
        "new_known_count": len(d["new_known"]), "new_upgraded_count": len(d["new_upgraded"]),
        "new_unknown_count": len(d["new_unknown"]),
        "rewrites_count": len(d["rewrites"]), "rewrites": d["rewrites"],
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
        "rewrites_count": totals.get("Rewrites", 0),
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
          f"rewrites={crit.get('rewrites_count', 0)}  "
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
              f"census_ok={gp['census_ok']} skips_ok={gp['skips_ok']} "
              f"candidate_failures={gp.get('candidate_failures', 0)}")
        if "kind" in gp:
            print(f"     kind: {gp['kind']}   criterion: {gp['criterion']}")
        if "ledgered_skips" in gp:
            print(f"     ledger: {report.get('identity', {}).get('ledger')}   ledgered_skips={gp['ledgered_skips']}"
                  f"   unledgered_skips={len(gp['unledgered_skips'])}")
            for u in gp["unledgered_skips"][:30]:
                print(f"       unledgered: {u}")
            for u in (gp.get("ledgered_unaccepted") or {}).get("identities", []):
                print(f"       ledgered but accepted_by null: {u}")
    m = report.get("modes", {})
    if "raw" in m:
        print(f"modes: raw={m['raw']['verdict']} strict={m['strict']['verdict']} "
              f"budgeted={m['budgeted']['verdict']} -> strict_field_clean={report['gate_pass']['strict_field_clean']}")
    b = m.get("budgeted") or {}
    if b.get("budget_id"):
        print(f"budget: {b['budget_id']}  sha256 {(b.get('budget_sha256') or '?')[:12]}")
        if b.get("over_budget"):
            print(f"  over_budget: {', '.join(b['over_budget'])}")
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
        c["rewrites"] += r.get("rewrites_count", 0)
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


def _ledger_check():
    tools = str(HARNESS_DIR / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import baseline_ledger_check  # noqa: E402  (sibling tool owns the identity rules)
    return baseline_ledger_check


def resolve_ledger(arg, baseline_sha):
    """Explicit --ledger (must exist), else reference/baseline_debts/<sha7>.json when present, else None."""
    if arg:
        p = Path(arg)
        p = p if p.is_absolute() or p.exists() else HARNESS_DIR / p
        if not p.is_file():
            raise FileNotFoundError(f"--ledger {arg} not found")
        return p
    default = HARNESS_DIR / "reference" / "baseline_debts" / f"{(baseline_sha or '')[:7]}.json"
    return default if baseline_sha and default.is_file() else None


class LedgerError(ValueError):
    """The ledger cannot be used for this run (e.g. built for another baseline)."""


def check_ledger_sha(ledger_doc, path, baseline_sha):
    """The ledger's product_sha (full or prefix) must name the run's baseline sha."""
    have = ledger_doc.get("product_sha") if isinstance(ledger_doc, dict) else None
    ok = (isinstance(have, str) and isinstance(baseline_sha, str) and have and baseline_sha
          and (baseline_sha.startswith(have) or have.startswith(baseline_sha)))
    if not ok:
        raise LedgerError(f"--ledger {path} product_sha {have} != baseline {baseline_sha}")


def ledger_identity(path):
    if path is None:
        return {"ledger": None, "ledger_sha256": None}
    return {"ledger": str(path), "ledger_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def split_bad_skips(records, ledger):
    """(ledgered count, sorted "reason analyzer identity" list of bad SKIPs the ledger does not
    cover, sorted ledger identities that cover a skip but carry accepted_by null)."""
    bad = [r for r in records if r.get("verdict") == "SKIP" and r.get("reason") in BAD_SKIP_REASONS]
    if ledger is None:
        return 0, sorted(f"{r['reason']} {r['analyzer']} {r['identity']}" for r in bad), []
    blc = _ledger_check()
    known, crashes = blc.ledgered_timeouts(ledger), blc.ledgered_crashes(ledger)
    accepted = {e["identity"]: e.get("accepted_by") for g in ("timeout_units", "crash_units")
                for e in ledger.get(g, [])}
    upstream = {r["unit_id"]: r for r in records if r.get("analyzer") == "schematic"}
    ledgered, unledgered, unaccepted = 0, [], set()
    for r in bad:
        cover = blc.skip_covering(r, known, upstream=upstream.get(r["unit_id"]), crashes=crashes)
        if cover is None:
            unledgered.append(f"{r['reason']} {r['analyzer']} {r['identity']}")
            continue
        ledgered += 1
        if accepted.get(cover) is None:
            unaccepted.add(cover)
    return ledgered, sorted(unledgered), sorted(unaccepted)


def compute_gate_pass(criteria, skip_breakdown, expected_census, executed_census,
                      skip_records=None, ledger=None):
    if skip_records is None:  # counts only: no identities to match against a ledger
        ledgered, unaccepted = 0, []
        unledgered = [f"{r} (count {skip_breakdown[r]})" for r in BAD_SKIP_REASONS if skip_breakdown.get(r, 0)]
    else:
        ledgered, unledgered, unaccepted = split_bad_skips(skip_records, ledger)
    cand_fail = sum(1 for r in skip_records or () if r.get("verdict") == "FAIL"
                    and r.get("reason") == CANDIDATE_FAILED_REASON)
    skips_ok = not unledgered
    census_ok = all(executed_census.get(a, 0) == n for a, n in expected_census.items())
    strict = bool(criteria["strict_clean"])
    return {"pass": strict and skips_ok and census_ok and cand_fail == 0, "strict_clean": strict,
            "census_ok": census_ok, "skips_ok": skips_ok, "candidate_failures": cand_fail,
            "ledgered_skips": ledgered, "unledgered_skips": unledgered,
            "ledgered_unaccepted": {"count": len(unaccepted), "identities": unaccepted},
            "skip_breakdown": dict(skip_breakdown),
            "expected_census": dict(expected_census), "executed_census": dict(executed_census)}


def write_rollup(records, agg, section, layout, manifest, ledger=None, ledger_path=None):
    rows = []
    for a in ALL_ANALYZERS:
        c = agg["by_analyzer"][a]
        rows.append({"analyzer": a, "PASS": c.get("PASS", 0), "WARN": c.get("WARN", 0),
                     "FAIL": c.get("FAIL", 0), "SKIP": c.get("SKIP", 0),
                     "Disappeared": c.get("disappeared", 0), "Downgrades": c.get("downgrades", 0),
                     "Upgrades": c.get("upgrades", 0), "NewKnown": c.get("new_known", 0),
                     "NewUpgraded": c.get("new_upgraded", 0), "NewUnknown": c.get("new_unknown", 0),
                     "Rewrites": c.get("rewrites", 0)})
    totals = {k: sum(row[k] for row in rows) for k in
              ("PASS", "WARN", "FAIL", "SKIP", "Disappeared", "Downgrades", "Upgrades",
               "NewKnown", "NewUpgraded", "NewUnknown", "Rewrites")}
    fail_list = [{"repo": repo, "analyzers": sorted({r["analyzer"] for r in recs}),
                  "units": [{"analyzer": r["analyzer"], "identity": r["identity"],
                             "reason": r.get("reason"), "disappeared": r.get("disappeared", []),
                             "downgrades": r.get("downgrades", [])} for r in recs]}
                 for repo, recs in sorted(agg["fail_repos"].items())]
    criteria = _compute_pass_criteria(totals)
    gate_pass = compute_gate_pass(criteria, agg["skip_breakdown"],
                                  manifest.get("expected_census", {}), agg["executed_census"],
                                  skip_records=records, ledger=ledger)
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
                     "normalization_policy": manifest.get("normalization_policy"),
                     **ledger_identity(ledger_path)},
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
    ap.add_argument("--kind", default="structural", choices=KIND_CHOICES,
                    help="round kind (ruling I9); 'gate' is a deprecated alias for structural")
    ap.add_argument("--jobs", "-j", type=int, default=DEFAULT_JOBS)
    ap.add_argument("--label", default=None, help="rollup filename label (default: section)")
    ap.add_argument("--resume", action="store_true",
                    help="reuse units from a previous run ONLY if its manifest identity matches")
    ap.add_argument("--budget", default=None, metavar="FILE",
                    help="regression/budgets/<id>.json; enables the budgeted mode verdict")
    ap.add_argument("--ledger", default=None, metavar="FILE",
                    help="baseline-debts ledger for skips_ok (default: reference/baseline_debts/"
                         "<baseline sha7>.json when present)")
    return ap


KIND_CHOICES = ("structural", "output-changing", "relock", "aa", "baseline", "gate")
BUDGETED_KINDS = ("output-changing", "relock")
CRITERIA = {
    "structural": ("structural: findings strict_clean AND strict_field_clean AND census_ok AND skips_ok "
                   "AND candidate_failures == 0"),
    **{k: f"{k}: census_ok AND skips_ok AND budgeted verdict clean AND candidate_failures == 0"
       for k in BUDGETED_KINDS},
}


def resolve_kind(kind):
    """Resolve the deprecated `gate` alias; the resolved kind is what manifest and rollup record."""
    if kind == "gate":
        print("note: --kind gate is an alias for structural", file=sys.stderr)
        return "structural"
    return kind


def kind_budget_error(kind, budget):
    """Ruling I9 request check: the error message, or None when kind and --budget agree."""
    if budget and kind not in BUDGETED_KINDS:
        return (f"Error: --budget is not allowed for kind={kind}: a structural round's budget "
                f"MUST be empty (ruling I9, spec §2.4)")
    if not budget and kind in BUDGETED_KINDS:
        return f"Error: kind={kind} requires --budget (ruling I9)"
    return None


def budget_file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None


def apply_modes(report, modes, kind="structural", budget_sha256=None):
    """Merge run_modes() output into the rollup and set gate_pass per kind (ruling I9).

    structural/aa/baseline: findings strict_clean AND strict_field_clean AND census_ok
    AND skips_ok. output-changing/relock: census_ok AND skips_ok AND budgeted verdict
    clean (findings strict_clean kept as information)."""
    report["modes"] = {**report.get("modes", {}), **modes}
    budgeted = report["modes"].get("budgeted")
    if isinstance(budgeted, dict):
        report["modes"]["budgeted"] = {**budgeted, "budget_sha256": budget_sha256}
    report.setdefault("identity", {})["budget_sha256"] = budget_sha256
    gp = report.setdefault("gate_pass", {})
    gp["strict_field_clean"] = bool(modes.get("strict_field_clean"))
    if kind in BUDGETED_KINDS:
        # a candidate-only analyzer failure is never budgetable (review I2)
        gp["pass"] = (bool(gp.get("census_ok")) and bool(gp.get("skips_ok"))
                      and gp.get("candidate_failures", 0) == 0
                      and (modes.get("budgeted") or {}).get("verdict") == "clean")
    else:
        gp["pass"] = bool(gp.get("pass")) and gp["strict_field_clean"]
    gp["kind"] = kind
    gp["criterion"] = CRITERIA.get(kind, CRITERIA["structural"])
    return report


def recheck_gate_pass(gate_dir, ledger=None, use_default_ledger=True):
    """Re-evaluate gate_pass of a finished gate dir from its units.jsonl + rollup (no analyzer
    runs): records re-aggregated (last record per analyzer/unit wins), census expectation,
    findings criteria and comparator modes taken from the rollup, skips judged by the ledger."""
    root = Path(gate_dir)
    rollups = sorted(root.glob("rollup_*.json"))
    if len(rollups) != 1:
        raise ValueError(f"{root}: expected exactly one rollup_*.json, found {len(rollups)}")
    report = json.loads(rollups[0].read_text(encoding="utf-8"))
    last = {}
    for line in (root / "units.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            last[(r["analyzer"], r["unit_id"])] = r
    records = list(last.values())
    agg = aggregate(records)
    baseline_sha = (report.get("identity") or {}).get("baseline_sha")
    ledger_path = resolve_ledger(ledger, baseline_sha) if (ledger or use_default_ledger) else None
    ledger_doc = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path else None
    if ledger_doc is not None:
        check_ledger_sha(ledger_doc, ledger_path, baseline_sha)
    gp = compute_gate_pass(report["pass_criteria"], agg["skip_breakdown"],
                           report["gate_pass"]["expected_census"], agg["executed_census"],
                           skip_records=records, ledger=ledger_doc)
    kind = read_manifest(root).get("kind")
    if not kind:
        print("warning: manifest has no kind; rechecking as structural", file=sys.stderr)
        kind = "structural"
    kind = "structural" if kind == "gate" else kind
    modes = report.get("modes") or {}
    out = apply_modes({"gate_pass": gp, "modes": {}, "identity": {}}, modes, kind=kind,
                      budget_sha256=(modes.get("budgeted") or {}).get("budget_sha256"))
    return {"gate_pass": out["gate_pass"], **ledger_identity(ledger_path)}


def _recheck_main(argv):
    ap = argparse.ArgumentParser(prog="run_corpus_gate.py --recheck")
    ap.add_argument("--recheck", required=True, metavar="GATE_DIR")
    ap.add_argument("--ledger", default=None, metavar="FILE")
    args = ap.parse_args(argv)
    try:
        res = recheck_gate_pass(args.recheck, ledger=args.ledger)
    except LedgerError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except (OSError, ValueError, KeyError) as e:
        print(f"Error: --recheck {args.recheck}: {e}", file=sys.stderr)
        sys.exit(2)
    gp = res["gate_pass"]
    print(f"recheck {args.recheck}: GATE {'PASS' if gp['pass'] else 'FAIL'}  kind={gp['kind']}  "
          f"strict_clean={gp['strict_clean']} strict_field_clean={gp['strict_field_clean']} "
          f"census_ok={gp['census_ok']} skips_ok={gp['skips_ok']} "
          f"candidate_failures={gp['candidate_failures']}")
    print(f"  ledger: {res['ledger']}  sha256 {(res['ledger_sha256'] or '-')[:12]}  "
          f"ledgered_skips={gp['ledgered_skips']}  unledgered_skips={len(gp['unledgered_skips'])}")
    for u in gp["unledgered_skips"]:
        print(f"  unledgered: {u}")
    for u in gp["ledgered_unaccepted"]["identities"]:
        print(f"  ledgered but accepted_by null: {u}")
    sys.exit(0 if gp["pass"] else 1)


def main(argv=None):
    if "--recheck" in (sys.argv[1:] if argv is None else argv):
        _recheck_main(sys.argv[1:] if argv is None else argv)
    args = build_arg_parser().parse_args(argv)
    args.kind = resolve_kind(args.kind)

    profile = PROFILES[args.profile]
    if not any(a in PHASE_A for a in profile.analyzers):
        # spice-offline / distributor-offline are declared here for their caps and flags but
        # run through their own runners; a corpus gate over them would record zero units
        print(f"Error: profile {profile.name} runs no corpus analyzer ({'/'.join(PHASE_A)}); "
              "use its own runner (run/run_spice.py, regression/run_distributor_offline_gate.py)",
              file=sys.stderr)
        sys.exit(2)
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
    kind_err = kind_budget_error(args.kind, args.budget)
    if kind_err:
        print(kind_err, file=sys.stderr)
        sys.exit(2)
    budget_sha256 = budget_file_sha256(args.budget)
    if args.ledger:
        try:
            resolve_ledger(args.ledger, None)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)
    base_ref, cand_ref = git_worktree_ref(Path(args.baseline_dir)), git_worktree_ref(Path(args.candidate_dir))
    if args.kind != "aa" and (base_ref.dirty or cand_ref.dirty):
        print("Error: product worktree is dirty; evidence runs need clean worktrees", file=sys.stderr)
        sys.exit(2)
    ledger_path = resolve_ledger(args.ledger, base_ref.sha)
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path else None
    except (OSError, ValueError) as e:
        print(f"Error: --ledger {ledger_path}: {e}", file=sys.stderr)
        sys.exit(2)
    if ledger is not None:
        try:
            check_ledger_sha(ledger, ledger_path, base_ref.sha)
        except LedgerError as e:
            print(f"Error: {e}", file=sys.stderr)
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
    report = write_rollup(records, agg, section, layout, manifest, ledger=ledger, ledger_path=ledger_path)
    from regression.field_compare import BudgetError, run_modes  # local import keeps the gate importable standalone
    try:
        modes = run_modes(layout.root, budget_path=Path(args.budget) if args.budget else None,
                          jobs=args.jobs)
    except (FileNotFoundError, BudgetError) as e:
        print(f"Error: comparator modes could not run: {e}", file=sys.stderr)
        sys.exit(2)
    report = apply_modes(report, modes, kind=args.kind, budget_sha256=budget_sha256)
    layout.rollup(section).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    finish_manifest(layout.root, {**report["totals"], "skip_breakdown": agg["skip_breakdown"],
                                  "expected_census": manifest["expected_census"],
                                  "executed_census": agg["executed_census"],
                                  "budget_sha256": budget_sha256,
                                  **ledger_identity(ledger_path),
                                  "modes": {k: v.get("verdict") for k, v in modes.items() if isinstance(v, dict)}})
    _print_summary(report)
    print(f"\nElapsed: {time.time()-t_start:.0f}s\nRollup JSON: {layout.rollup(section)}")
    sys.exit(0 if report["gate_pass"]["pass"] else 1)


def input_shas_by_unit(a_jobs, input_shas):
    return [(f"{j[2]}/{safe_name(j[1])}", input_shas[f"{j[0]}/{j[2]}/{safe_name(j[1])}"]) for j in a_jobs]


if __name__ == "__main__":
    main()
