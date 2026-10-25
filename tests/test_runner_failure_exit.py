"""Download, checkout and clone failures reach the exit status unless --best-effort
(code A3-F10, A3-F7; ruling R7)."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "run"))

pytestmark = pytest.mark.unit


def _ds_tree(tmp_path, monkeypatch, sync_src):
    import run_datasheets as rd
    (tmp_path / "checkouts" / "o" / "r").mkdir(parents=True)
    out = tmp_path / "outputs" / "schematic" / "o" / "r"
    out.mkdir(parents=True)
    (out / "x.kicad_sch.json").write_text("{}")
    sync = tmp_path / "sync.py"
    sync.write_text(sync_src)
    monkeypatch.setattr(rd, "REPOS_DIR", tmp_path / "checkouts")
    monkeypatch.setattr(rd, "OUTPUTS_DIR", tmp_path / "outputs")
    return rd, sync


def test_failed_sync_is_reported_not_zero(tmp_path, monkeypatch):
    rd, sync = _ds_tree(tmp_path, monkeypatch, "import sys; sys.stderr.write('auth failed\\n'); sys.exit(3)\n")
    downloaded, failed, errors = rd.download_datasheets("o/r", sync)
    assert (downloaded, failed) == (0, 0)
    assert errors == ["x.kicad_sch.json: exit 3 auth failed"]


@pytest.mark.parametrize("best_effort,code", [(False, 1), (True, 0)])
def test_datasheet_cli_exit_follows_sync_errors(tmp_path, monkeypatch, best_effort, code):
    import run_datasheets as rd
    monkeypatch.setattr(rd, "process_repo", lambda repo, *a, **k: {
        "repo": repo, "downloaded": 0, "download_failed": 0, "sync_errors": ["x: exit 3"],
        "db_ingested": 0, "db_merged": 0, "report": None})
    monkeypatch.setattr(rd, "_kicad_happy", tmp_path)
    sync = tmp_path / "skills" / "digikey" / "scripts" / "sync_datasheets_digikey.py"
    sync.parent.mkdir(parents=True)
    sync.write_text("")
    monkeypatch.setattr(rd, "OUTPUTS_DIR", tmp_path / "outputs")
    argv = ["run_datasheets.py", "--repo", "o/r", "--download-only", "--jobs", "1"]
    monkeypatch.setattr(sys, "argv", argv + (["--best-effort"] if best_effort else []))
    with pytest.raises(SystemExit) as ex:
        rd.main()
        raise SystemExit(0)
    assert ex.value.code == code


def _git(*args, cwd):
    import subprocess
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args], cwd=cwd, check=True,
                   capture_output=True)


def test_checkout_pin_failure_counts_as_failure(tmp_path, monkeypatch, capsys):
    """code A3-F7: a pin failure on a new clone printed OK and counted as cloned."""
    import checkout
    src = tmp_path / "src" / "o" / "r"
    src.mkdir(parents=True)
    _git("init", "-q", cwd=src)
    _git("commit", "-q", "--allow-empty", "-m", "x", cwd=src)
    monkeypatch.setattr(checkout, "CLONE_DIR", tmp_path / "clones")
    monkeypatch.setattr(checkout, "_repo_name_from_url", lambda url: "o/r")
    repos = [{"url": f"file://{src}", "hash": "f" * 40, "shallow": True}]
    assert checkout.clone_repos(repos, 0) == 1
    out = capsys.readouterr().out
    assert "pin failed" in out and "Cloned:  0" in out and "Failed:  1" in out
