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


def _promote_env(tmp_path, monkeypatch, assertions, changes):
    import promote
    out = tmp_path / "outputs" / "schematic" / "o" / "r"
    out.mkdir(parents=True)
    (out / "x.json").write_text("{}")
    monkeypatch.setattr(promote, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(promote, "check_assertions", lambda d, repo_name=None: assertions)
    monkeypatch.setattr(promote, "check_baseline_changes", lambda r: changes)
    applied = []
    monkeypatch.setattr(promote, "create_snapshot", lambda r: applied.append("snapshot"))
    monkeypatch.setattr(promote, "generate_for_repo", lambda *a: applied.append("seed") or (0, 0, 0))
    return promote, applied


CHANGED = [{"project": "p", "type": "schematic", "status": "changed", "compared": 1, "changed": 1, "new_files": 0}]


@pytest.mark.parametrize("assertions,changes,why", [
    ({"total": 3, "passed": 2, "failed": 1, "errors": 0}, CHANGED, "failing"),
    ({"total": 3, "passed": 3, "failed": 0, "errors": 0},
     CHANGED + [{"project": "p", "type": "pcb", "status": "partial", "missing": 2}], "partial result tree"),
])
def test_promote_refuses_failing_assertions_and_partial_trees(tmp_path, monkeypatch, capsys,
                                                              assertions, changes, why):
    """code A2-F6 (ruling R11): promotion is a reviewed adoption; it never adopts failing
    outputs or a partial tree."""
    promote, applied = _promote_env(tmp_path, monkeypatch, assertions, changes)
    assert promote.promote_repo("o/r", dry_run=False) is False
    assert applied == [] and why in capsys.readouterr().out


def test_promote_applies_a_clean_complete_tree(tmp_path, monkeypatch):
    promote, applied = _promote_env(tmp_path, monkeypatch,
                                    {"total": 3, "passed": 3, "failed": 0, "errors": 0}, CHANGED)
    assert promote.promote_repo("o/r", dry_run=False) is True
    assert applied[0] == "snapshot"


def test_data_dir_override_moves_every_corpus_path(tmp_path):
    """code A3-F5: the override moved only reference/ and results/outputs; checkouts,
    manifests, cross-sections, review metrics and the datasheet store stayed live."""
    import os
    import subprocess
    code = (
        "import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'run');"
        "import utils, checkout, run_review_metrics as rm;"
        "from validate.datasheet_db import storage, manifest;"
        "print('\\n'.join(str(p) for p in (utils.REPOS_DIR, utils.DATA_DIR, utils.OUTPUTS_DIR,"
        " utils.MANIFESTS_DIR, utils.CROSS_SECTIONS_FILE, checkout.CLONE_DIR, rm.DEFAULT_OUTPUT_ROOT,"
        " storage.STORE_DIR, storage.REPOS_DIR, manifest.MANIFEST_DIR)))")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DATASHEET_DB_")}
    env["KICAD_HAPPY_TESTHARNESS_DATA_DIR"] = str(tmp_path)
    r = subprocess.run([sys.executable, "-c", code], cwd=HARNESS, env=env, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    paths = r.stdout.split()
    assert len(paths) == 10 and all(p.startswith(str(tmp_path)) for p in paths), paths
