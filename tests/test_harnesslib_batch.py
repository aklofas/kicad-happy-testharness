"""harnesslib.batch: the batch lifecycle behind utils.run_analyzer, and the two output
validators named for their distinct contracts."""
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
FAKE = HARNESS / "tests" / "fixtures" / "h0" / "plan2" / "fake_analyzer.py"
pytestmark = pytest.mark.unit

from harnesslib import batch, execution  # noqa: E402


def _git_init(p):
    p.mkdir(parents=True, exist_ok=True)
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "x"]):
        subprocess.run(["git", "-C", str(p), "-c", "user.email=t@t", "-c", "user.name=t", *cmd],
                       check=True, capture_output=True)


def test_validators_have_distinct_names():
    assert hasattr(execution, "validate_analyzer_envelope") and not hasattr(execution, "validate_output")
    assert batch.EXPECTED_KEYS["pcb"] and callable(batch.validate_required_keys)


def test_type_only_document_fails_the_required_key_check(tmp_path):
    p = tmp_path / "x.json"
    p.write_text('{"analyzer_type": "pcb"}')
    assert execution.validate_analyzer_envelope(p, "pcb")[0] is True
    assert batch.validate_required_keys(p, "pcb")[0] is False


def _config():
    return batch.BatchConfig(type_name="pcb", analyzer_script="analyze_pcb.py",
                             manifest_file="all_pcbs.txt", output_subdir="pcb",
                             summarize=lambda d: "ok", extra_args=("--mode", "ok"))


def _settings():
    return batch.BatchSettings(jobs=1, validate=False, json=False, resume=False,
                               online=False, timeout=20)


def _paths(tmp_path, *, script=True, manifest_lines=None):
    product = tmp_path / "product"
    scripts = product / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    if script:
        (scripts / "analyze_pcb.py").write_text(FAKE.read_text())
    manifests = tmp_path / "manifests"
    manifests.mkdir(exist_ok=True)
    if manifest_lines is not None:
        (manifests / "all_pcbs.txt").write_text("".join(f"{l}\n" for l in manifest_lines))
    return batch.BatchPaths(harness_dir=tmp_path / "harness", product_root=product,
                            repos_dir=tmp_path / "repos", outputs_dir=tmp_path / "outputs",
                            manifests_dir=manifests)


def _run(paths, repo_list=("o/r",)):
    return batch.run_batch(_config(), _settings(), paths,
                           repo_list=list(repo_list) if repo_list is not None else None,
                           selection_source="repo:o/r", argv=("--repo", "o/r"))


def test_run_batch_returns_exit_codes_instead_of_exiting(tmp_path, capsys):
    repo = tmp_path / "repos" / "o" / "r"
    (repo / "a").mkdir(parents=True)
    one, two = repo / "a" / "b.kicad_pcb", repo / "a_b.kicad_pcb"
    for b in (one, two):
        b.write_text("(kicad_pcb)")

    assert _run(_paths(tmp_path / "s", script=False, manifest_lines=[])) == 1
    assert "not found" in capsys.readouterr().err
    assert _run(_paths(tmp_path / "m")) == 1
    assert "Run discover.py first" in capsys.readouterr().err
    assert _run(_paths(tmp_path / "e", manifest_lines=[one]), repo_list=["x/y"]) == 1
    assert "No pcbs found for x/y" in capsys.readouterr().err

    paths = batch.BatchPaths(**{**_paths(tmp_path / "c", manifest_lines=[one, two]).__dict__,
                                "repos_dir": tmp_path / "repos"})
    assert _run(paths) == 2
    assert "collide" in capsys.readouterr().err
    assert not (paths.outputs_dir / "pcb" / "manifest.json").exists()


def test_run_analyzer_honours_patched_utils_globals(monkeypatch, tmp_path, capsys):
    import utils
    product = tmp_path / "product"
    scripts = product / "skills" / "kicad" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "analyze_pcb.py").write_text(FAKE.read_text())
    _git_init(product)
    _git_init(tmp_path / "harness")
    board = tmp_path / "repos" / "o" / "r" / "ok.kicad_pcb"
    board.parent.mkdir(parents=True)
    board.write_text("(kicad_pcb)")
    (tmp_path / "manifests").mkdir()
    (tmp_path / "manifests" / "all_pcbs.txt").write_text(f"{board}\n")
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("KICAD_HAPPY_DIR", str(product))
    monkeypatch.setattr(utils, "HARNESS_DIR", tmp_path / "harness")
    monkeypatch.setattr(utils, "REPOS_DIR", tmp_path / "repos")
    monkeypatch.setattr(utils, "MANIFESTS_DIR", tmp_path / "manifests")
    monkeypatch.setattr(utils, "OUTPUTS_DIR", tmp_path / "outputs")
    cfg = {"type_name": "pcb", "analyzer_script": "analyze_pcb.py",
           "manifest_file": "all_pcbs.txt", "output_subdir": "pcb",
           "summarize": lambda d: "ok", "extra_args": ["--mode", "ok"]}
    args = SimpleNamespace(repo="o/r", cross_section=None, repo_list=None, all_repos=False,
                           jobs=1, validate=False, json=False, resume=False, timeout=20)
    utils.run_analyzer(cfg, args=args)
    out = tmp_path / "outputs" / "pcb" / "o" / "r" / "ok.kicad_pcb.json"
    assert json.loads(out.read_text())["analyzer_type"] == "pcb"
    m = json.loads((tmp_path / "outputs" / "pcb" / "manifest.json").read_text())
    assert m["totals"]["ok"] == 1
    assert "PASS" in capsys.readouterr().out
