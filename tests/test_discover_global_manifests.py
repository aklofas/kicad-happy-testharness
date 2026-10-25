"""discover.py --repo must not shrink the flat all_*.txt manifests to one repo: the globals are
rebuilt from every per-repo manifest and described by census.json, which the gate checks."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import discover  # noqa: E402

pytestmark = pytest.mark.unit


def _corpus(tmp_path, monkeypatch):
    checkouts, mdir = tmp_path / "checkouts", tmp_path / "manifests"
    for repo, boards in {"o/a": ["x.kicad_pcb", "y.kicad_pcb"], "o/b": ["z.kicad_pcb"]}.items():
        for b in boards:
            f = checkouts / repo / b
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("(kicad_pcb)")
    monkeypatch.setattr(discover, "REPOS_DIR", checkouts)
    monkeypatch.setattr(discover, "MANIFESTS_DIR", mdir)
    monkeypatch.setattr(discover, "list_repos", lambda: ["o/a", "o/b"])
    return checkouts, mdir


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["discover.py", *argv])
    discover.main()


def _pcbs(mdir):
    return [Path(ln).name for ln in (mdir / "all_pcbs.txt").read_text().splitlines()]


def test_repo_discover_keeps_every_repo_in_the_globals(tmp_path, monkeypatch):
    checkouts, mdir = _corpus(tmp_path, monkeypatch)
    _run(monkeypatch)
    assert _pcbs(mdir) == ["x.kicad_pcb", "y.kicad_pcb", "z.kicad_pcb"]
    (checkouts / "o/b/w.kicad_pcb").write_text("(kicad_pcb)")
    _run(monkeypatch, "--repo", "o/b")
    assert _pcbs(mdir) == ["x.kicad_pcb", "y.kicad_pcb", "w.kicad_pcb", "z.kicad_pcb"]


def test_census_records_counts_digests_and_floor(tmp_path, monkeypatch):
    checkouts, mdir = _corpus(tmp_path, monkeypatch)
    _run(monkeypatch)
    census = json.loads((mdir / "census.json").read_text())
    assert census["mode"] == "full" and census["counts"]["pcbs"] == 3 and census["floor"]["pcbs"] == 3
    import hashlib
    assert census["sha256"]["pcbs"] == hashlib.sha256((mdir / "all_pcbs.txt").read_bytes()).hexdigest()
    # a --repo refresh that loses a board keeps the full floor; the next full discover resets it
    (checkouts / "o/a/y.kicad_pcb").unlink()
    _run(monkeypatch, "--repo", "o/a")
    census = json.loads((mdir / "census.json").read_text())
    assert census["mode"] == "repo" and census["counts"]["pcbs"] == 2 and census["floor"]["pcbs"] == 3
    _run(monkeypatch)
    assert json.loads((mdir / "census.json").read_text())["floor"]["pcbs"] == 2


def test_globals_are_replaced_atomically(tmp_path, monkeypatch):
    _, mdir = _corpus(tmp_path, monkeypatch)
    _run(monkeypatch)
    assert not list(mdir.glob("*.tmp-*"))
