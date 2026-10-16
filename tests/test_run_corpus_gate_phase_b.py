# tests/test_run_corpus_gate_phase_b.py
"""run_corpus_gate Phase B census, gate_pass, identity-matched resume, end-to-end main()."""
TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from regression import run_corpus_gate as gate  # noqa: E402
from harnesslib import identity as ident  # noqa: E402
from harnesslib.profiles import PROFILES  # noqa: E402

FAKE = ROOT / "tests" / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"
OK = ("ok", "ok_findings_exit")


def _rec(analyzer, repo, key, b_status, c_status, verdict="PASS"):
    return {"analyzer": analyzer, "repo": repo, "unit_id": f"{repo}/{key}", "identity": f"{repo}/{key}",
            "input_sha256": "0" * 64, "verdict": verdict, "reason": "",
            "baseline": {"status": b_status}, "candidate": {"status": c_status}}


def test_phase_b_jobs_come_from_phase_a_success_records(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    a = [_rec("schematic", "o/r", "a.kicad_sch", "ok", "ok"),
         _rec("pcb", "o/r", "a.kicad_pcb", "ok", "ok"),
         _rec("schematic", "o/r", "nopcb.kicad_sch", "ok", "ok")]
    jobs, skips = gate.build_phase_b_jobs(a, lay, "/b", "/c", PROFILES["standard"])
    kinds = sorted((j[0], j[2]) for j in jobs)
    assert ("thermal", "a.kicad_sch") in kinds and ("emc", "nopcb.kicad_sch") in kinds
    assert ("thermal", "nopcb.kicad_sch") not in kinds
    assert [s["reason"] for s in skips] == ["not_applicable"]
    assert skips[0]["analyzer"] == "thermal" and skips[0]["verdict"] == "SKIP"


def test_phase_b_jobs_record_dependency_missing(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    a = [_rec("schematic", "o/r", "a.kicad_sch", "ok", "crash", verdict="FAIL")]
    jobs, skips = gate.build_phase_b_jobs(a, lay, "/b", "/c", PROFILES["standard"])
    assert jobs == []
    assert sorted(s["analyzer"] for s in skips) == ["cross_analysis", "emc", "thermal"]
    assert all(s["reason"] == "dependency_missing" for s in skips)


def test_phase_b_pcb_pair_requires_both_sides(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    a = [_rec("schematic", "o/r", "a.kicad_sch", "ok", "ok"),
         _rec("pcb", "o/r", "a.kicad_pcb", "ok", "crash", verdict="FAIL")]
    jobs, skips = gate.build_phase_b_jobs(a, lay, "/b", "/c", PROFILES["standard"])
    assert [(s["analyzer"], s["reason"]) for s in skips] == [("thermal", "not_applicable")]
    assert all(j[3] is None for j in jobs)


ZERO = {"not_applicable": 0, "both_failed": 0, "dependency_missing": 0, "snapshot_read_error": 0}


def test_phase_b_full_chain_profile_produces_chained_jobs(tmp_path):
    # TH-072: the full-chain profile omitted schematic, so Phase A never ran it and
    # build_phase_b_jobs (which pairs off schematic records) produced no chained unit.
    prof = PROFILES["full-chain"]
    assert "schematic" in prof.analyzers
    lay = gate.GateLayout(tmp_path / "g")
    a = [_rec("schematic", "o/r", "a.kicad_sch", "ok", "ok"),
         _rec("pcb", "o/r", "a.kicad_pcb", "ok", "ok")]
    jobs, skips = gate.build_phase_b_jobs(a, lay, "/b", "/c", prof)
    assert sorted(j[0] for j in jobs) == ["cross_analysis", "emc", "thermal"]
    assert all(j[3] == "a.kicad_pcb" for j in jobs) and skips == []


def test_gate_pass_requires_strict_clean_census_and_no_bad_skips():
    totals = {"PASS": 10, "WARN": 0, "FAIL": 0, "SKIP": 1, "Disappeared": 0, "Downgrades": 0,
              "Upgrades": 0, "NewKnown": 0, "NewUpgraded": 0, "NewUnknown": 0}
    crit = gate._compute_pass_criteria(totals)
    exp = {"pcb": 5, "schematic": 5}
    gp = gate.compute_gate_pass(crit, dict(ZERO, not_applicable=1), exp, exp)
    assert gp["pass"] is True
    for bad in ("both_failed", "dependency_missing", "snapshot_read_error"):
        gp = gate.compute_gate_pass(crit, dict(ZERO, **{bad: 1}), exp, exp)
        assert gp["pass"] is False and gp["skips_ok"] is False, bad
    gp = gate.compute_gate_pass(crit, dict(ZERO, not_applicable=1), exp, {"pcb": 4, "schematic": 5})
    assert gp["pass"] is False and gp["census_ok"] is False
    crit_warn = gate._compute_pass_criteria(dict(totals, WARN=1))
    gp = gate.compute_gate_pass(crit_warn, ZERO, {}, {})
    assert gp["pass"] is False and gp["strict_clean"] is False


def test_aggregate_tolerates_skip_records_without_diff_keys():
    recs = [dict(_rec("thermal", "o/r", "a.kicad_sch", "skipped", "skipped", verdict="SKIP"),
                 reason="not_applicable"),
            dict(_rec("schematic", "o/r", "b.kicad_sch", "x", "x", verdict="SKIP"),
                 reason="snapshot_read_error")]
    agg = gate.aggregate(recs)
    assert agg["skip_breakdown"]["not_applicable"] == 1
    assert agg["skip_breakdown"]["snapshot_read_error"] == 1
    assert agg["by_analyzer"]["thermal"]["SKIP"] == 1


def test_aggregate_census_counts_phase_b_but_not_dependency_missing():
    recs = [dict(_rec("schematic", "o/r", "a.kicad_sch", "ok", "ok"), disappeared_count=0),
            dict(_rec("emc", "o/r", "a.kicad_sch", "ok", "ok"), disappeared_count=0),
            dict(_rec("thermal", "o/r", "a.kicad_sch", "skipped", "skipped", verdict="SKIP"),
                 reason="not_applicable"),
            dict(_rec("emc", "o/r", "b.kicad_sch", "skipped", "skipped", verdict="SKIP"),
                 reason="dependency_missing")]
    ex = gate.aggregate(recs)["executed_census"]
    assert ex == {"schematic": 1, "emc": 1, "thermal": 1}


def _git(p):
    p.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(p), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(p), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"], check=True)


def _spec(tmp_path, cand_name="cand"):
    base, cand, harness = tmp_path / "base", tmp_path / cand_name, tmp_path / "h"
    for p in (base, cand, harness):
        if not p.exists():
            _git(p)
    return ident.RunSpec(kind="gate", profile="standard", harness=ident.git_worktree_ref(harness),
                         baseline=ident.git_worktree_ref(base), candidate=ident.git_worktree_ref(cand),
                         argv=("--cross-section", "smoke"), selection_source="cross_section:smoke",
                         unit_ids=("o/r/a.kicad_sch",), normalization_policy="volatile-leaves-v1", env=())


def _logged_unit(lay, log, slots=("baseline", "candidate"), input_sha="in1"):
    shas = {}
    for slot in slots:
        snap = lay.snap(slot, "schematic", "o/r", "a.kicad_sch")
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text("{}")
        shas[slot] = {"status": "ok", "output_sha256": ident.sha256_file(snap)}
    log.append({"analyzer": "schematic", "repo": "o/r", "unit_id": "o/r/a.kicad_sch",
                "input_sha256": input_sha, "verdict": "PASS", **shas})


def test_resume_reuses_only_on_identity_match(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    spec = _spec(tmp_path)
    ident.write_manifest(lay.root, spec, run_id="r1", expected_census={"schematic": 1},
                         input_digest="d", runtime={})
    _logged_unit(lay, ident.UnitLog(lay.root))
    reusable, reasons = gate.resume_plan(lay, spec, input_shas={"schematic/o/r/a.kicad_sch": "in1"})
    assert reasons == [] and "schematic/o/r/a.kicad_sch" in reusable


def test_resume_requires_both_sides_current(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    spec = _spec(tmp_path)
    ident.write_manifest(lay.root, spec, run_id="r1", expected_census={}, input_digest="d", runtime={})
    _logged_unit(lay, ident.UnitLog(lay.root))
    key = "schematic/o/r/a.kicad_sch"
    # input changed
    assert key not in gate.resume_plan(lay, spec, input_shas={key: "other"})[0]
    # unit absent from the input map
    assert key not in gate.resume_plan(lay, spec, input_shas={})[0]
    # baseline snapshot tampered
    lay.snap("baseline", "schematic", "o/r", "a.kicad_sch").write_text('{"x": 1}')
    assert key not in gate.resume_plan(lay, spec, input_shas={key: "in1"})[0]


def test_resume_does_not_reuse_skip_or_failed_sides(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    spec = _spec(tmp_path)
    ident.write_manifest(lay.root, spec, run_id="r1", expected_census={}, input_digest="d", runtime={})
    log = ident.UnitLog(lay.root)
    log.append({**_rec("thermal", "o/r", "a.kicad_sch", "skipped", "skipped", verdict="SKIP"),
                "reason": "not_applicable"})
    log.append(_rec("emc", "o/r", "a.kicad_sch", "ok", "crash", verdict="FAIL"))
    assert gate.resume_plan(lay, spec)[0] == {}


def test_resume_rejects_changed_candidate_sha(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    spec = _spec(tmp_path)
    ident.write_manifest(lay.root, spec, run_id="r1", expected_census={}, input_digest="d", runtime={})
    _logged_unit(lay, ident.UnitLog(lay.root))
    cand2 = tmp_path / "cand"
    subprocess.run(["git", "-C", str(cand2), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "y"], check=True)
    spec2 = _spec(tmp_path)
    assert spec2.candidate.sha != spec.candidate.sha
    reusable, reasons = gate.resume_plan(lay, spec2)
    assert reusable == {} and any(r.startswith("candidate_sha:") for r in reasons)


def test_resume_without_manifest_reuses_nothing(tmp_path):
    reusable, reasons = gate.resume_plan(gate.GateLayout(tmp_path / "g"), _spec(tmp_path))
    assert reusable == {} and reasons


def test_write_rollup_carries_identity_and_modes(tmp_path):
    lay = gate.GateLayout(tmp_path / "g")
    spec = _spec(tmp_path)
    ident.write_manifest(lay.root, spec, run_id="r1", expected_census={"schematic": 1},
                         input_digest="d", runtime={})
    recs = [dict(_rec("schematic", "o/r", "a.kicad_sch", "ok", "ok"), disappeared_count=0,
                 severity_downgrades=0, severity_upgrades=0, new_known_count=0,
                 new_upgraded_count=0, new_unknown_count=0)]
    agg = gate.aggregate(recs)
    report = gate.write_rollup(recs, agg, "smoke", lay, ident.read_manifest(lay.root))
    assert report["identity"]["candidate_sha"] == spec.candidate.sha
    assert report["identity"]["run_id"] == "r1"
    assert report["modes"] == {"findings_summary": "strict_clean"}
    assert report["gate_pass"]["pass"] is True
    assert json.loads(lay.rollup("smoke").read_text())["gate_pass"]["pass"] is True


# --- end-to-end through main() with fake worktrees -------------------------

def _fake_worktree(tmp_path, name, mode):
    wt = tmp_path / name
    for rel, typ in (("skills/kicad/scripts/analyze_schematic.py", "schematic"),
                     ("skills/kicad/scripts/analyze_pcb.py", "pcb"),
                     ("skills/kicad/scripts/analyze_gerbers.py", "gerber"),
                     ("skills/kicad/scripts/analyze_thermal.py", "thermal"),
                     ("skills/emc/scripts/analyze_emc.py", "emc"),
                     ("skills/kicad/scripts/cross_analysis.py", "cross_analysis")):
        p = wt / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            "import sys, subprocess\n"
            "a = sys.argv\n"
            "o = a[a.index('-o') + 1] if '-o' in a else a[a.index('--output') + 1]\n"
            f"sys.exit(subprocess.call([sys.executable, {str(FAKE)!r}, {mode!r}, '-o', o, '--type', {typ!r}]))\n")
    _git(wt)
    return wt


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    repo = tmp_path / "repos" / "o" / "r"
    repo.mkdir(parents=True)
    (repo / "b.kicad_sch").write_text("(kicad_sch)")
    (repo / "b.kicad_pcb").write_text("(kicad_pcb)")
    mf = tmp_path / "manifests"
    mf.mkdir()
    (mf / "all_schematics.txt").write_text(str(repo / "b.kicad_sch") + "\n")
    (mf / "all_pcbs.txt").write_text(str(repo / "b.kicad_pcb") + "\n")
    (mf / "all_gerbers.txt").write_text("")
    monkeypatch.setattr(gate, "MANIFESTS_DIR", mf)
    hroot = tmp_path / "hroot"          # hermetic, clean "harness" checkout
    _git(hroot)
    monkeypatch.setattr(gate, "HARNESS_DIR", hroot)
    return tmp_path


def _run_main(argv):
    with pytest.raises(SystemExit) as e:
        gate.main(argv)
    return e.value.code


def test_main_end_to_end_pass_resume_and_fail(corpus, capsys):
    base = _fake_worktree(corpus, "base", "ok")
    cand = _fake_worktree(corpus, "cand", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(cand), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1", "--label", "t"]
    assert _run_main(argv) == 0
    man = ident.read_manifest(gd)
    assert man["finished_at"] and man["expected_census"] == {"schematic": 1, "pcb": 1}
    rollup = json.loads((gd / "rollup_t.json").read_text())
    gp = rollup["gate_pass"]
    assert gp["pass"] and gp["census_ok"]
    # every Phase B analyzer ran/skip-balanced against its expectation
    assert gp["expected_census"]["emc"] == gp["executed_census"]["emc"] == 1
    assert gp["expected_census"]["thermal"] == gp["executed_census"]["thermal"] == 1
    assert len(list(ident.UnitLog(gd))) == 5
    # identity-matched resume reuses everything
    assert _run_main(argv + ["--resume"]) == 0
    recs = list(ident.UnitLog(gd))
    assert len(recs) == 5 and all(r.get("reused") for r in recs)
    # a failing candidate flips the exit code
    cand_bad = _fake_worktree(corpus, "cand_bad", "exit2")
    argv_bad = ["--baseline-dir", str(base), "--candidate-dir", str(cand_bad),
                "--gate-dir", str(corpus / "gd2"), "--repo", "o/r", "--jobs", "1", "--label", "t"]
    assert _run_main(argv_bad) == 1


def test_main_dirty_worktree_exits_2_unless_aa(corpus):
    base = _fake_worktree(corpus, "base", "ok")
    cand = _fake_worktree(corpus, "cand", "ok")
    (cand / "dirty.txt").write_text("x")
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(cand),
            "--gate-dir", str(corpus / "gd"), "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 2
    assert _run_main(argv + ["--kind", "aa"]) == 0


def test_main_requires_explicit_selection(corpus):
    base = _fake_worktree(corpus, "base", "ok")
    assert _run_main(["--baseline-dir", str(base), "--candidate-dir", str(base),
                      "--gate-dir", str(corpus / "gd")]) == 2


def test_nonempty_gate_dir_without_resume_exits_2(corpus):
    base = _fake_worktree(corpus, "base", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(base), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 0
    run_id = ident.read_manifest(gd)["run_id"]
    assert _run_main(argv) == 2
    assert ident.read_manifest(gd)["run_id"] == run_id


def test_resume_mismatch_exits_2_and_leaves_tree_untouched(corpus, capsys):
    base = _fake_worktree(corpus, "base", "ok")
    cand = _fake_worktree(corpus, "cand", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(cand), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 0
    old = ident.read_manifest(gd)
    before = sorted(p.name for p in gd.iterdir())
    subprocess.run(["git", "-C", str(cand), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "y"], check=True)
    capsys.readouterr()
    assert _run_main(argv + ["--resume"]) == 2
    assert "identity mismatch" in capsys.readouterr().err
    assert ident.read_manifest(gd)["run_id"] == old["run_id"]
    assert sorted(p.name for p in gd.iterdir()) == before     # nothing archived or rewritten


@pytest.mark.parametrize("legacy", ["v131", "v14", "baseline", "diff"])
def test_legacy_or_partial_gate_dir_is_refused(corpus, legacy):
    base = _fake_worktree(corpus, "base", "ok")
    gd = corpus / "gd"
    (gd / legacy).mkdir(parents=True)
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(base), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 2
    assert _run_main(argv + ["--resume"]) == 2
    assert not (gd / "manifest.json").exists()


def test_gerber_directory_unit_end_to_end(corpus):
    gdir = corpus.joinpath("repos", "o", "r", "fab")
    gdir.mkdir()
    (gdir / "a.gbr").write_text("G04*")
    (corpus / "manifests" / "all_gerbers.txt").write_text(str(gdir) + "\n")
    base = _fake_worktree(corpus, "base", "ok")
    cand = _fake_worktree(corpus, "cand", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(cand), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 0
    recs = {r["analyzer"]: r for r in ident.UnitLog(gd)}
    assert recs["gerber"]["input_sha256"] == ident.sha256_path(gdir)
    assert _run_main(argv + ["--resume"]) == 0
    assert all(r.get("reused") for r in ident.UnitLog(gd))
    (gdir / "a.gbr").write_text("G04 changed*")
    assert _run_main(argv + ["--resume"]) == 0
    assert not {r["analyzer"]: r for r in ident.UnitLog(gd)}["gerber"].get("reused")


def test_worker_exception_is_fail_unit_and_run_completes(corpus, monkeypatch):
    extra = corpus.joinpath("repos", "o", "r", "c.kicad_pcb")
    extra.write_text("(kicad_pcb)")
    mf = corpus / "manifests" / "all_pcbs.txt"
    mf.write_text(mf.read_text() + str(extra) + "\n")
    real = gate.phase_a_job

    def flaky(job):
        if job[1].endswith("c.kicad_pcb"):
            raise RuntimeError("boom")
        return real(job)

    monkeypatch.setattr(gate, "phase_a_job", flaky)
    base = _fake_worktree(corpus, "base", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(base), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1", "--label", "t"]
    assert _run_main(argv) == 1
    recs = {f"{r['analyzer']}/{r['unit_id']}": r for r in ident.UnitLog(gd)}
    bad = recs["pcb/o/r/" + gate.safe_name(str(extra))]
    assert bad["verdict"] == "FAIL" and bad["reason"] == "worker_exception"
    assert "boom" in bad["detail"] and bad["baseline"] is None and bad["candidate"] is None
    assert any(r["analyzer"] == "schematic" and r["verdict"] == "PASS" for r in recs.values())
    assert json.loads((gd / "rollup_t.json").read_text())["gate_pass"]["pass"] is False


def test_records_are_logged_as_each_unit_completes(corpus, monkeypatch):
    seen = []
    real = gate.phase_b_job

    def spy(job):
        # at Phase B start every Phase A record must already be on disk
        seen.append(sorted({r["analyzer"] for r in ident.UnitLog(gd)}))
        return real(job)

    monkeypatch.setattr(gate, "phase_b_job", spy)
    base = _fake_worktree(corpus, "base", "ok")
    gd = corpus / "gd"
    assert _run_main(["--baseline-dir", str(base), "--candidate-dir", str(base),
                      "--gate-dir", str(gd), "--repo", "o/r", "--jobs", "1"]) == 0
    assert seen and "pcb" in seen[0] and "schematic" in seen[0]


def test_resume_match_archives_log_under_run_id(corpus):
    base = _fake_worktree(corpus, "base", "ok")
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(base), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 0
    old_id = ident.read_manifest(gd)["run_id"]
    assert _run_main(argv + ["--resume"]) == 0
    assert (gd / f"units.{old_id}.jsonl").exists()


def test_phase_b_not_reused_after_pcb_dependency_disappears(corpus):
    base = _fake_worktree(corpus, "base", "ok")
    cand = _fake_worktree(corpus, "cand", "ok")
    flag = corpus / "pcbmode.txt"
    flag.write_text("ok")
    (cand / "skills/kicad/scripts/analyze_pcb.py").write_text(
        "import sys, subprocess\n"
        "a = sys.argv\n"
        f"mode = open({str(flag)!r}).read().strip()\n"
        f"sys.exit(subprocess.call([sys.executable, {str(FAKE)!r}, mode, '-o', a[a.index('-o') + 1], '--type', 'pcb']))\n")
    subprocess.run(["git", "-C", str(cand), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(cand), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "-m", "flag"], check=True)
    gd = corpus / "gd"
    argv = ["--baseline-dir", str(base), "--candidate-dir", str(cand), "--gate-dir", str(gd),
            "--repo", "o/r", "--jobs", "1"]
    assert _run_main(argv) == 0
    assert all(r["deps"]["pcb"] for r in ident.UnitLog(gd) if r["analyzer"] in ("thermal", "emc", "cross_analysis"))
    flag.write_text("exit2")
    Path((corpus / "manifests" / "all_pcbs.txt").read_text().strip()).write_text("(kicad_pcb changed)")  # input change forces a pcb rerun
    assert _run_main(argv + ["--resume"]) == 1   # pcb candidate now fails
    recs = {r["analyzer"]: r for r in ident.UnitLog(gd)}
    assert recs["thermal"]["verdict"] == "SKIP" and recs["thermal"]["reason"] == "not_applicable"
    for a in ("emc", "cross_analysis"):
        assert not recs[a].get("reused") and recs[a]["deps"]["pcb"] is None
    assert recs["schematic"].get("reused")
