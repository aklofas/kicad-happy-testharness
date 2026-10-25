"""Corpus expansion: stages gate on success, repos.md edits match exact URLs and check the
destination first (code A5-F3 A5-F4 A5-F8)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "tools"))
sys.path.insert(0, str(HARNESS))
import add_repos  # noqa: E402
import reclassify_repos  # noqa: E402

pytestmark = pytest.mark.unit

MD = """## Boards
- https://github.com/Jana-Marie/OtterPill @ aaaa
- https://github.com/Jana-Marie/OtterPill-CAN-Adapter @ bbbb

## Keyboards
"""


def test_remove_matches_the_exact_url(tmp_path, monkeypatch):
    md = tmp_path / "repos.md"
    md.write_text(MD)
    monkeypatch.setattr(add_repos, "REPOS_MD", md)
    add_repos.remove_from_repos_md("https://github.com/Jana-Marie/OtterPill")
    assert "OtterPill-CAN-Adapter" in md.read_text() and "OtterPill @ aaaa" not in md.read_text()


def test_reclassify_refuses_a_missing_destination_before_editing(tmp_path, monkeypatch):
    md = tmp_path / "repos.md"
    md.write_text(MD)
    monkeypatch.setattr(reclassify_repos, "REPOS_MD", md)
    line = "- https://github.com/Jana-Marie/OtterPill @ aaaa"
    with pytest.raises(ValueError, match="no section"):
        reclassify_repos.reclassify_in_repos_md([("Jana-Marie/OtterPill", line, "Boards", "Nowhere")])
    assert md.read_text() == MD
    assert reclassify_repos._url_repo(line) == "Jana-Marie/OtterPill"


def test_pipeline_stops_at_a_failed_required_stage(tmp_path, monkeypatch):
    calls = []

    def fake_step(name, cmd, timeout=600):
        calls.append(name)
        return (name != "Schematic analysis"), f"[{name}]"
    mdir = tmp_path / "manifests" / "o" / "r"
    mdir.mkdir(parents=True)
    (mdir / "schematics.txt").write_text("repos/o/r/a.kicad_sch\n")
    monkeypatch.setattr(add_repos, "run_pipeline_step", fake_step)
    monkeypatch.setattr(add_repos, "MANIFESTS_DIR", tmp_path / "manifests")
    res = add_repos._pipeline_one_repo("o/r", skip_spice=True, skip_emc=True)
    assert res["status"] == "failed" and res["error"] == "schematic failed"
    assert calls == ["Clone", "Discover", "Schematic analysis"]   # no PCB/gerber in the repo
