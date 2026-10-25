"""run_corpus_gate preflight: missing manifests and colliding unit keys stop the run before
any unit executes; --recheck refuses an unfinished or mismatched gate dir."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import run_corpus_gate as gate  # noqa: E402

pytestmark = pytest.mark.unit


def _in(*parts):
    """A synthetic manifest line (nothing is read from the corpus)."""
    return str(Path("repos", *parts))

RECHECK = HARNESS / "tests" / "fixtures" / "h0" / "round2" / "recheck_gate"
LEDGER = HARNESS / "tests" / "fixtures" / "h0" / "round2" / "ledger_6a91aaa_timeouts.json"


def _main_exit(tmp_path, monkeypatch, manifests):
    monkeypatch.setenv("KICAD_HAPPY_TESTHARNESS_DATA_DIR", str(tmp_path / "data"))
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    for name, lines in manifests.items():
        (mdir / name).write_text("".join(f"{ln}\n" for ln in lines), encoding="utf-8")
    _write_census(mdir)
    monkeypatch.setattr(gate, "MANIFESTS_DIR", mdir)
    monkeypatch.setattr(gate, "git_worktree_ref", lambda p: _Ref())
    wt = tmp_path / "wt"
    wt.mkdir()
    with pytest.raises(SystemExit) as ex:
        gate.main(["--baseline-dir", str(wt), "--candidate-dir", str(wt), "--gate-dir", str(tmp_path / "g"),
                   "--all", "--kind", "aa"])
    return ex.value.code


def _write_census(mdir, floor=None):
    sha, counts = {}, {}
    for f in mdir.glob("all_*.txt"):
        kind = f.name[len("all_"):-len(".txt")]
        sha[kind] = hashlib.sha256(f.read_bytes()).hexdigest()
        counts[kind] = sum(1 for ln in f.read_text().splitlines() if ln.strip())
    (mdir / "census.json").write_text(json.dumps({"counts": counts, "sha256": sha,
                                                  "floor": floor or counts, "mode": "full"}))


class _Ref:
    sha = "0" * 40
    dirty = False


def test_missing_profile_manifest_is_preflight_error(tmp_path, monkeypatch, capsys):
    # standard profile runs schematic/pcb/gerber; only the schematic manifest exists
    code = _main_exit(tmp_path, monkeypatch, {"all_schematics.txt": [_in("o", "r", "a.kicad_sch")]})
    assert code == 2
    assert "all_pcbs.txt missing" in capsys.readouterr().err
    assert not (tmp_path / "g").exists()


def test_colliding_unit_keys_are_rejected(tmp_path, monkeypatch, capsys):
    code = _main_exit(tmp_path, monkeypatch, {
        "all_schematics.txt": [_in("o", "r", "a", "b.kicad_sch"), _in("o", "r", "a_b.kicad_sch")],
        "all_pcbs.txt": [], "all_gerbers.txt": []})
    assert code == 2
    err = capsys.readouterr().err
    assert "collide" in err and "schematic/o/r/a_b.kicad_sch" in err
    assert not (tmp_path / "g").exists()


def test_duplicate_unit_keys_helper():
    jobs = [("pcb", _in("o", "r", "x", "y.kicad_pcb"), "o/r"), ("pcb", _in("o", "r", "x_y.kicad_pcb"), "o/r"),
            ("schematic", _in("o", "r", "x", "y.kicad_sch"), "o/r")]
    assert gate.duplicate_unit_keys(jobs) == [
        "pcb/o/r/x_y.kicad_pcb: repos/o/r/x/y.kicad_pcb, repos/o/r/x_y.kicad_pcb"]


def test_recheck_refuses_unfinished_run(tmp_path):
    d = tmp_path / "g"
    shutil.copytree(RECHECK, d)
    m = json.loads((d / "manifest.json").read_text())
    m["finished_at"] = None
    (d / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="finished_at"):
        gate.recheck_gate_pass(d, ledger=str(LEDGER))


def test_recheck_refuses_rollup_from_another_run(tmp_path):
    d = tmp_path / "g"
    shutil.copytree(RECHECK, d)
    m = json.loads((d / "manifest.json").read_text())
    m["run_id"] = "another-run"
    (d / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="run_id"):
        gate.recheck_gate_pass(d, ledger=str(LEDGER))


def _census_dir(tmp_path, monkeypatch, sch_lines):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    for name, lines in {"all_schematics.txt": sch_lines, "all_pcbs.txt": [], "all_gerbers.txt": []}.items():
        (mdir / name).write_text("".join(f"{ln}\n" for ln in lines))
    monkeypatch.setattr(gate, "MANIFESTS_DIR", mdir)
    return mdir


def test_full_run_needs_a_census(tmp_path, monkeypatch):
    _census_dir(tmp_path, monkeypatch, [_in("o", "r", "a.kicad_sch")])
    with pytest.raises(gate.PreflightError, match="run discover.py"):
        gate.check_manifest_census(gate.PROFILES["standard"])


def test_manifest_written_outside_discover_is_refused(tmp_path, monkeypatch):
    mdir = _census_dir(tmp_path, monkeypatch, [_in("o", "r", "a.kicad_sch"), _in("o", "s", "b.kicad_sch")])
    _write_census(mdir)
    (mdir / "all_schematics.txt").write_text(f"{_in('o', 'r', 'a.kicad_sch')}\n")   # a one-repo rewrite
    with pytest.raises(gate.PreflightError, match="differs from the census"):
        gate.check_manifest_census(gate.PROFILES["standard"])


def test_census_below_floor_needs_explicit_allowance(tmp_path, monkeypatch):
    mdir = _census_dir(tmp_path, monkeypatch, [_in("o", "r", "a.kicad_sch")])
    _write_census(mdir, floor={"schematics": 2, "pcbs": 0, "gerbers": 0})
    with pytest.raises(gate.PreflightError, match="below the census floor"):
        gate.check_manifest_census(gate.PROFILES["standard"])
    rec = gate.check_manifest_census(gate.PROFILES["standard"], allow_drop=True)
    assert rec["checked"]["schematics"] == {"count": 1, "floor": 2} and rec["drop_allowed"] is True


def test_census_recorded_in_run_manifest(tmp_path, monkeypatch):
    mdir = _census_dir(tmp_path, monkeypatch, [_in("o", "r", "a.kicad_sch")])
    _write_census(mdir)
    rec = gate.check_manifest_census(gate.PROFILES["standard"])
    from harnesslib.identity import RunSpec, WorktreeRef, write_manifest, read_manifest
    ref = WorktreeRef(sha="0" * 40, path="h", dirty=False)
    spec = RunSpec(kind="aa", profile="standard", harness=ref, baseline=None, candidate=None, argv=(),
                   selection_source="all", unit_ids=(), normalization_policy="x", env=())
    write_manifest(tmp_path / "g", spec, run_id="r", expected_census={}, input_digest="d", runtime={},
                   census=rec)
    assert read_manifest(tmp_path / "g")["manifest_census"]["checked"]["schematics"]["count"] == 1
