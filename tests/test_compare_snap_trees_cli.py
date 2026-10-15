# tests/test_compare_snap_trees_cli.py
import json
from pathlib import Path

import pytest

from regression import compare_snap_trees as cli

pytestmark = pytest.mark.unit

RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"
FIX = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "budgets"


def _env(run_id, sev="warning", nets=3):
    return {"analyzer_type": "schematic", "inputs": {"run_id": run_id, "source_files": [], "source_hashes": {}},
            "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
            "findings": [{"rule_id": "RS-001", "detector": "audit_rail_sources", "severity": sev}],
            "statistics": {"total_nets": nets}}


def _tree(root, unit, doc):
    p = root / unit / "snap.json"; p.parent.mkdir(parents=True); p.write_text(json.dumps(doc))


def test_strict_clean_exits_0_and_writes_report(tmp_path):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A)); _tree(tmp_path / "b", "schematic/u", _env(RUN_B))
    out = tmp_path / "r.json"
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "strict", "-o", str(out)])
    assert rc == 0
    rep = json.loads(out.read_text())
    assert rep["verdict"] == "clean" and rep["policy"] == "volatile-leaves-v1"


def test_raw_on_same_trees_exits_1_with_bytes_delta(tmp_path):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A)); _tree(tmp_path / "b", "schematic/u", _env(RUN_B))
    out = tmp_path / "r.json"
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "raw", "-o", str(out)])
    assert rc == 1
    assert json.loads(out.read_text())["summary"]["by_op"] == {"bytes": 1}


def test_budgeted_clean_and_residual_exit_codes(tmp_path):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A, "warning")); _tree(tmp_path / "b", "schematic/u", _env(RUN_B, "info"))
    out = tmp_path / "r.json"
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "budgeted",
                   "--budget", str(FIX / "rs001_only.json"), "-o", str(out)])
    assert rc == 0
    rep = json.loads(out.read_text())
    assert rep["verdict"] == "clean" and rep["budget"]["claimed_counts"] == {"rs001-severity-down": 1}
    _tree(tmp_path / "c", "schematic/u", _env(RUN_B, "info", nets=4))
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "c"), "--mode", "budgeted",
                   "--budget", str(FIX / "rs001_only.json"), "-o", str(out)])
    assert rc == 1
    rep = json.loads(out.read_text())
    assert rep["verdict"] == "residuals" and [r["path"] for r in rep["budget"]["residuals"]] == ["/statistics/total_nets"]


def test_budgeted_requires_budget(tmp_path):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A)); _tree(tmp_path / "b", "schematic/u", _env(RUN_A))
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "budgeted", "-o", str(tmp_path / "r.json")])
    assert rc == 2


def test_cli_missing_unit_exits_2(tmp_path):
    # default unexplained_missing_units_allowed is 0 → error exit 2 in strict mode
    _tree(tmp_path / "a", "schematic/u1", _env(RUN_A)); _tree(tmp_path / "a", "schematic/u2", _env(RUN_A))
    _tree(tmp_path / "b", "schematic/u1", _env(RUN_A))
    out = tmp_path / "r.json"
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "strict", "-o", str(out)])
    assert rc == 2
    assert json.loads(out.read_text())["summary"]["missing"] == 1


def test_missing_root_exits_2(tmp_path):
    rc = cli.main([str(tmp_path / "nope"), str(tmp_path / "nope2"), "--mode", "strict", "-o", str(tmp_path / "r.json")])
    assert rc == 2


def test_policy_none_disables_masking(tmp_path):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A)); _tree(tmp_path / "b", "schematic/u", _env(RUN_B))
    out = tmp_path / "r.json"
    rc = cli.main([str(tmp_path / "a"), str(tmp_path / "b"), "--mode", "strict", "--policy", "none", "-o", str(out)])
    assert rc == 1
    assert {d["path"] for d in json.loads(out.read_text())["deltas"]} == {"/inputs/run_id", "/capability_mode_ref/run_id"}


def _pair(tmp_path, sa="warning", sb="info"):
    _tree(tmp_path / "a", "schematic/u", _env(RUN_A, sa)); _tree(tmp_path / "b", "schematic/u", _env(RUN_B, sb))
    return str(tmp_path / "a"), str(tmp_path / "b")


def test_unloadable_predicate_exits_2(tmp_path):
    a, b = _pair(tmp_path)
    bud = json.loads((FIX / "rs001_only.json").read_text())
    bud["classes"][0]["predicate"] = "nomod:nofn"
    bp = tmp_path / "bud.json"; bp.write_text(json.dumps(bud))
    assert cli.main([a, b, "--mode", "budgeted", "--budget", str(bp), "-o", str(tmp_path / "r.json")]) == 2


@pytest.mark.parametrize("mode", ["raw", "strict"])
def test_budget_outside_budgeted_mode_exits_2(tmp_path, mode):
    a, b = _pair(tmp_path)
    assert cli.main([a, b, "--mode", mode, "--budget", str(FIX / "rs001_only.json"),
                     "-o", str(tmp_path / "r.json")]) == 2


def test_budgeted_policy_none_writes_null_policy(tmp_path):
    a, b = _pair(tmp_path)
    out = tmp_path / "r.json"
    bud = json.loads((FIX / "rs001_only.json").read_text())
    del bud["normalization_policy"]          # a budget naming a policy must match it (I8)
    bp = tmp_path / "bud.json"; bp.write_text(json.dumps(bud))
    rc = cli.main([a, b, "--mode", "budgeted", "--policy", "none", "--budget", str(bp),
                   "-o", str(out)])
    assert rc in (0, 1)
    assert json.loads(out.read_text())["policy"] is None


def test_unknown_policy_exits_2(tmp_path):
    a, b = _pair(tmp_path)
    assert cli.main([a, b, "--mode", "strict", "--policy", "bogus", "-o", str(tmp_path / "r.json")]) == 2
