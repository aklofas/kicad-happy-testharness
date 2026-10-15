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
    repos = tmp_path / "repos" / "o" / "r"
    repos.mkdir(parents=True)
    board = repos / "ok.kicad_pcb"
    board.write_text("(kicad_pcb)")
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(data))
    monkeypatch.setenv("KICAD_HAPPY_DIR", str(product))
    import importlib, utils
    importlib.reload(utils)
    monkeypatch.setattr(utils, "REPOS_DIR", tmp_path / "repos")
    monkeypatch.setattr(utils, "MANIFESTS_DIR", tmp_path / "manifests")
    (tmp_path / "manifests").mkdir()
    (tmp_path / "manifests" / "all_pcbs.txt").write_text(f"{board}\n")
    return SimpleNamespace(utils=utils, tmp=tmp_path, board=board, data=data)


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
