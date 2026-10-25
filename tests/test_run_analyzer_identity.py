"""utils.run_analyzer writes a batch manifest + units.jsonl, fails closed on
invalid output, and resumes only on identity match (H0-1 §2.5, report B12)."""
TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FAKE = ROOT / "tests" / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"


def _git_init(p: Path):
    p.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(p), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "x"], check=True)


@pytest.fixture
def env(tmp_path, monkeypatch):
    data = tmp_path / "data"
    product = tmp_path / "product"
    _git_init(product)
    scripts = product / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "analyze_pcb.py").write_text(FAKE.read_text())
    subprocess.run(["git", "-C", str(product), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(product), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "-m", "scripts"], check=True)
    repos = tmp_path / "repos" / "o" / "r"
    repos.mkdir(parents=True)
    board = repos / "ok.kicad_pcb"
    board.write_text("(kicad_pcb)")
    harness = tmp_path / "harness"
    _git_init(harness)
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(data))
    monkeypatch.setenv("KICAD_HAPPY_DIR", str(product))
    import importlib, utils
    importlib.reload(utils)
    monkeypatch.setattr(utils, "HARNESS_DIR", harness)
    monkeypatch.setattr(utils, "REPOS_DIR", tmp_path / "repos")
    monkeypatch.setattr(utils, "MANIFESTS_DIR", tmp_path / "manifests")
    (tmp_path / "manifests").mkdir()
    (tmp_path / "manifests" / "all_pcbs.txt").write_text(f"{board}\n")
    return SimpleNamespace(utils=utils, tmp=tmp_path, board=board, data=data, product=product)


def _args(**over):
    a = dict(repo="o/r", cross_section=None, repo_list=None, all_repos=False,
             jobs=1, validate=False, json=False, resume=False, timeout=20)
    a.update(over)
    return SimpleNamespace(**a)


def _config(mode):
    # the fake takes <mode> as first positional; run_analyzer passes the board
    # path first, so route mode through extra_args consumed by the fake's argv
    return {"type_name": "pcb", "analyzer_script": "analyze_pcb.py",
            "manifest_file": "all_pcbs.txt", "output_subdir": "pcb",
            "summarize": lambda d: "ok", "extra_args": ["--mode", mode]}


def test_batch_writes_manifest_and_units(env, capsys):
    env.utils.run_analyzer(_config("ok"), _args())
    out_root = env.data / "results" / "outputs" / "pcb"
    m = json.loads((out_root / "manifest.json").read_text())
    assert m["kind"] == "batch" and m["product"]["baseline"] is None
    assert len(m["product"]["candidate"]["sha"]) == 40
    assert m["selection"]["source"] == "repo:o/r" and m["expected_census"] == {"pcb": 1}
    assert m["totals"]["ok"] == 1
    units = [json.loads(l) for l in (out_root / "units.jsonl").read_text().splitlines()]
    assert units[0]["status"] == "ok" and units[0]["exit_code"] == 0
    assert "PASS" in capsys.readouterr().out


def test_garbage_output_is_fail_not_parse_error_pass(env, capsys):
    with pytest.raises(SystemExit) as ei:
        env.utils.run_analyzer(_config("garbage"), _args())
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "parse_error" not in out and "FAIL" in out and "invalid_output" in out


def test_resume_skips_only_identical_input_and_output(env, capsys):
    env.utils.run_analyzer(_config("ok"), _args())
    env.utils.run_analyzer(_config("ok"), _args(resume=True))
    assert "Skip:  1" in capsys.readouterr().out
    env.board.write_text("(kicad_pcb (changed))")
    env.utils.run_analyzer(_config("ok"), _args(resume=True))
    out = capsys.readouterr().out
    assert "Skip:" not in out and "PASS" in out


def test_all_corpus_without_all_flag_exits_2(env):
    with pytest.raises(SystemExit) as ei:
        env.utils.run_analyzer(_config("ok"), _args(repo=None))
    assert ei.value.code == 2


def _resume_after(env, capsys, mutate=None, extra=()):
    env.utils.run_analyzer(_config("ok"), _args())
    capsys.readouterr()
    if mutate:
        mutate()
    cfg = _config("ok")
    cfg["extra_args"] = cfg["extra_args"] + list(extra)
    env.utils.run_analyzer(cfg, _args(resume=True))
    return capsys.readouterr().out


def test_resume_disabled_when_product_sha_changes(env, capsys):
    def commit():
        subprocess.run(["git", "-C", str(env.product), "-c", "user.email=t@t",
                        "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "y"],
                       check=True)
    out = _resume_after(env, capsys, commit)
    assert "resume disabled" in out and "Skip:" not in out


def test_resume_disabled_when_extra_args_change(env, capsys):
    out = _resume_after(env, capsys, extra=("--type", "pcb"))
    assert "resume disabled" in out and "Skip:" not in out


def test_resume_disabled_on_dirty_worktree(env, capsys):
    out = _resume_after(env, capsys, lambda: (env.product / "junk.txt").write_text("x"))
    assert "resume disabled: dirty worktree" in out and "Skip:" not in out


def _second_board(env):
    b2 = env.board.with_name("ok2.kicad_pcb")
    b2.write_text("(kicad_pcb 2)")
    (env.tmp / "manifests" / "all_pcbs.txt").write_text(f"{env.board}\n{b2}\n")
    return b2


def test_resume_after_crashed_new_sha_run_reruns_unreached_units(env, capsys):
    _second_board(env)
    out_root = env.data / "results" / "outputs" / "pcb"
    env.utils.run_analyzer(_config("ok"), _args())          # run A at product SHA A
    subprocess.run(["git", "-C", str(env.product), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "B"], check=True)
    env.utils.run_analyzer(_config("ok"), _args())          # run B at SHA B (non-resume)
    m = json.loads((out_root / "manifest.json").read_text())
    # simulate a crash after one unit: keep only B's first record, no totals
    recs = [json.loads(l) for l in (out_root / "units.jsonl").read_text().splitlines()]
    b_recs = [r for r in recs if r["run_id"] == m["run_id"]]
    assert len(b_recs) == 2
    (out_root / "units.jsonl").write_text(json.dumps(b_recs[0]) + "\n")
    m["totals"] = None
    (out_root / "manifest.json").write_text(json.dumps(m))
    capsys.readouterr()
    env.utils.run_analyzer(_config("ok"), _args(resume=True))
    out = capsys.readouterr().out
    assert "Skip:  1" in out and out.count("PASS [") == 1     # unreached unit reran
    # A's records were archived, never deleted
    assert list(out_root.glob("units.*.jsonl"))


def test_unit_records_carry_run_id(env):
    env.utils.run_analyzer(_config("ok"), _args())
    out_root = env.data / "results" / "outputs" / "pcb"
    m = json.loads((out_root / "manifest.json").read_text())
    recs = [json.loads(l) for l in (out_root / "units.jsonl").read_text().splitlines()]
    assert recs and all(r["run_id"] == m["run_id"] for r in recs)


def test_gerber_directory_unit_runs(env, capsys):
    gdir = env.tmp / "repos" / "o" / "r" / "gerbers"
    gdir.mkdir()
    (gdir / "a.gbr").write_text("G04*")
    (env.tmp / "manifests" / "all_gerbers.txt").write_text(f"{gdir}\n")
    cfg = {"type_name": "gerber", "analyzer_script": "analyze_pcb.py",
           "manifest_file": "all_gerbers.txt", "output_subdir": "gerber",
           "summarize": lambda d: "ok", "extra_args": ["--mode", "ok", "--type", "gerber"]}
    env.utils.run_analyzer(cfg, _args())
    assert "PASS" in capsys.readouterr().out
    env.utils.run_analyzer(cfg, _args(resume=True))
    assert "Skip:  1" in capsys.readouterr().out
    (gdir / "a.gbr").write_text("G04 changed*")
    env.utils.run_analyzer(cfg, _args(resume=True))
    assert "Skip:" not in capsys.readouterr().out


def test_validation_failure_is_recorded_and_never_resumed(env, capsys):
    """code A3-F2: a --validate VFAIL logged status ok, so --validate --resume skipped the
    unit and exited 0. The fake's pcb envelope lacks footprints/statistics/connectivity."""
    for resume in (False, True):
        with pytest.raises(SystemExit) as ei:
            env.utils.run_analyzer(_config("ok"), _args(validate=True, resume=resume))
        assert ei.value.code == 1
        out = capsys.readouterr().out
        assert "VFAIL" in out and "Skip:" not in out
    out_root = env.data / "results" / "outputs" / "pcb"
    units = [json.loads(l) for l in (out_root / "units.jsonl").read_text().splitlines()]
    assert units[-1]["status"] == "validation_failed"
    assert json.loads((out_root / "manifest.json").read_text())["totals"]["validation_failed"] == 1


def test_colliding_output_names_are_rejected_before_work(env, capsys):
    """code A3-F1: `a/b.kicad_pcb` and `a_b.kicad_pcb` share one flat output name."""
    (env.tmp / "repos" / "o" / "r" / "a").mkdir()
    one = env.tmp / "repos" / "o" / "r" / "a" / "b.kicad_pcb"
    two = env.tmp / "repos" / "o" / "r" / "a_b.kicad_pcb"
    for b in (one, two):
        b.write_text("(kicad_pcb)")
    (env.tmp / "manifests" / "all_pcbs.txt").write_text(f"{one}\n{two}\n")
    with pytest.raises(SystemExit) as ei:
        env.utils.run_analyzer(_config("ok"), _args())
    assert ei.value.code == 2 and "collide" in capsys.readouterr().err
    assert not (env.data / "results" / "outputs" / "pcb" / "manifest.json").exists()
