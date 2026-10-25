"""Tools that write tracked reference data honour their dry-run and never guess a target."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "regression"))
from regression import seed_structural  # noqa: E402

pytestmark = pytest.mark.unit


def _structural_tree(tmp_path, monkeypatch):
    outputs, data = tmp_path / "outputs", tmp_path / "data"
    out = outputs / "schematic" / "o" / "r" / "main.kicad_sch.json"
    out.parent.mkdir(parents=True)
    out.write_text(json.dumps({"statistics": {"total_components": 1}, "findings": []}))  # below threshold
    stale = data / "o" / "r" / "p" / "assertions" / "schematic" / "main.kicad_sch_structural.json"
    stale.parent.mkdir(parents=True)
    stale.write_text(json.dumps({"generated_by": "seed_structural.py", "assertions": [{"id": "STRUCT-1"}]}))
    monkeypatch.setattr(seed_structural, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(seed_structural, "discover_projects", lambda repo: [{"name": "p", "path": "."}])
    monkeypatch.setattr(seed_structural, "filter_project_outputs", lambda d, p: sorted(d.glob("*.json")))
    monkeypatch.setattr(seed_structural, "data_dir", lambda repo, proj, sub: data / repo / proj / sub)
    return stale


def test_structural_dry_run_never_unlinks(tmp_path, monkeypatch, capsys):
    """code A2-F7: --dry-run reported, but the stale-file branch ran before the dry-run guard."""
    stale = _structural_tree(tmp_path, monkeypatch)
    seed_structural.generate_for_repo("o/r", "schematic", True, 10, dry_run=True)
    assert stale.exists()
    assert "would remove main.kicad_sch_structural.json" in capsys.readouterr().out
    seed_structural.generate_for_repo("o/r", "schematic", True, 10, dry_run=False)
    assert not stale.exists()


def test_bugfix_path_guesses_are_never_applied(tmp_path, monkeypatch, capsys):
    """code A2-F8: a prefix_adjusted / fuzzy suggestion names an unrelated output; --fix must
    not write it into the registry. An exact project/extension correction still applies."""
    import audit_bugfix_paths as abp
    reg = tmp_path / "bugfix_registry.json"
    entries = [{"issue": "KH-1", "assertions": [
        {"repo": "o/r", "project": "p", "source_file": "a.kicad_sch"},
        {"repo": "o/r", "project": "p", "source_file": "b.kicad_sch"},
        {"repo": "o/r", "project": "p", "source_file": "c.sch"}]}]
    reg.write_text(json.dumps(entries))
    monkeypatch.setattr(abp, "REGISTRY_FILE", reg)
    results = [
        {"issue": "KH-1", "index": 1, "matched": False,
         "suggestion": {"project": "q", "source_file": "other.kicad_sch", "match": "x", "note": "prefix_adjusted"}},
        {"issue": "KH-1", "index": 2, "matched": False, "suggestion": {"match": "y", "note": "fuzzy"}},
        {"issue": "KH-1", "index": 3, "matched": False,
         "suggestion": {"project": "p", "source_file": "c.kicad_sch", "match": "c.kicad_sch.json"}},
    ]
    assert abp.apply_fixes(results) == 1
    got = json.loads(reg.read_text())[0]["assertions"]
    assert [a["source_file"] for a in got] == ["a.kicad_sch", "b.kicad_sch", "c.kicad_sch"]
    assert [a["project"] for a in got] == ["p", "p", "p"]
    assert "not applied (prefix_adjusted guess" in capsys.readouterr().out


def test_atomic_write_replaces_in_one_step(tmp_path, monkeypatch):
    """code A5-F11 / A7-F10: repos.md and findings.json go through temp + os.replace."""
    import os
    import utils
    target = tmp_path / "repos.md"
    target.write_text("old\n")
    seen = []
    real = os.replace
    monkeypatch.setattr(utils.os, "replace", lambda a, b: (seen.append((Path(a).name, Path(b).name)), real(a, b)))
    utils.atomic_write_text(target, "new\n")
    assert target.read_text() == "new\n" and seen == [(f"repos.md.tmp-{os.getpid()}", "repos.md")]
    assert not list(tmp_path.glob("*.tmp-*"))


def test_save_findings_and_repos_md_use_the_atomic_writer(tmp_path, monkeypatch):
    import utils
    calls = []
    monkeypatch.setattr(utils, "atomic_write_text", lambda p, t: calls.append(Path(p).name))
    import findings as fnd
    monkeypatch.setattr(fnd, "atomic_write_text", lambda p, t: calls.append(Path(p).name))
    monkeypatch.setattr(fnd, "data_dir", lambda *parts: tmp_path)
    fnd.save_findings("o/r", "p", {"findings": []})
    sys.path.insert(0, str(HARNESS / "tools"))
    import add_repos
    monkeypatch.setattr(add_repos, "atomic_write_text", lambda p, t: calls.append(Path(p).name))
    monkeypatch.setattr(add_repos, "REPOS_MD", tmp_path / "repos.md")
    (tmp_path / "repos.md").write_text("## Cat\n- https://github.com/o/r\n")
    add_repos.remove_from_repos_md("https://github.com/o/r")
    assert calls[0] == "findings.json" and calls[-1] == "repos.md"
