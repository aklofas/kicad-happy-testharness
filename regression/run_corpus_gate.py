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
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "regression"))

import regression_diff as rdiff  # noqa: E402
from harnesslib.execution import run_once, build_env, recorded_env  # noqa: E402
from harnesslib.identity import (RunSpec, git_worktree_ref, sha256_file, input_digest,  # noqa: E402
                                 write_manifest, finish_manifest, read_manifest,
                                 manifests_match, UnitLog)
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
SKIP_REASONS = ("not_applicable", "both_failed", "dependency_missing")


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
    before = json.loads(Path(a_path).read_text(encoding="utf-8"))
    after = json.loads(Path(b_path).read_text(encoding="utf-8"))
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
           "input_sha256": sha256_file(input_path),
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

