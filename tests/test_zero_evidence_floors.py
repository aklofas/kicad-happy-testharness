"""Side comparators never report equality over zero compared units (ruling R3)."""
import sys
import types
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import compare_snap_trees, compare_spice_offline  # noqa: E402
from regression import run_distributor_offline_gate as do  # noqa: E402
from regression.field_compare import compare_trees  # noqa: E402
from regression.run_hierarchy_regression_gate import gate_clean  # noqa: E402

pytestmark = pytest.mark.unit


def test_empty_snap_trees_are_an_error(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert rep["summary"]["compared"] == 0 and rep["verdict"] == "error"
    rc = compare_snap_trees.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "strict",
                                  "-o", str(tmp_path / "r.json")])
    assert rc == 2


def test_empty_spice_trees_are_not_identical(tmp_path, capsys):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    assert compare_spice_offline.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 1
    assert "NO COMPARED REPORTS" in capsys.readouterr().out


def test_one_shared_spice_report_is_evidence(tmp_path):
    for side in ("a", "b"):
        (tmp_path / side / "o" / "r").mkdir(parents=True)
        (tmp_path / side / "o" / "r" / "x.json").write_text('{"simulation_results": []}')
    assert compare_spice_offline.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 0


def _rollup(p, f, s):
    return {"summary": {"PASS": p, "FAIL": f, "SKIP": s, "contract_fails": {}}}


def test_hierarchy_gate_needs_every_curated_board():
    assert gate_clean(_rollup(3, 0, 0))
    assert not gate_clean(_rollup(0, 0, 3))   # every curated sub-sheet missing
    assert not gate_clean(_rollup(2, 0, 1))   # one curated board dropped by a re-clone
    assert not gate_clean(_rollup(2, 1, 0))


def test_distributor_timeout_record_is_text(tmp_path, monkeypatch):
    tree = tmp_path / "tree"
    (tree / "tools").mkdir(parents=True)
    (tree / do.ORACLE).write_text("import sys, time\nprint('started', flush=True)\ntime.sleep(30)\n")
    monkeypatch.setattr(do, "PROFILE", types.SimpleNamespace(timeout_s=1, name="distributor-offline"))
    res = do.run_oracle(tree, tmp_path, [])
    assert res["timed_out"] is True and isinstance(res["stdout"], str) and isinstance(res["stderr"], str)
