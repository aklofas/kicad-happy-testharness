"""budgeted_report: the one budgeted verdict shared by the CLI and run_modes (I5),
lazy docs (I1), and budget/run identity binding (I8)."""
import json
from pathlib import Path

import pytest

from regression import compare_snap_trees as cli
from regression.field_compare import (BudgetError, budgeted_report, compare_trees, docs_for_report,
                                      load_budget, load_policy, run_modes)

pytestmark = pytest.mark.unit

RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"
FIX = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "budgets"


def _env(run_id, sev="warning", nets=3):
    return {"analyzer_type": "schematic", "inputs": {"run_id": run_id, "source_files": [], "source_hashes": {}},
            "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
            "findings": [{"rule_id": "RS-001", "detector": "audit_rail_sources", "severity": sev}],
            "statistics": {"total_nets": nets}}


def _gate(root, manifest=None):
    """baseline/candidate with one identical unit and one RS-001 severity flip."""
    for slot, run, sev in (("baseline", RUN_A, "warning"), ("candidate", RUN_B, "info")):
        for unit, s in (("schematic/o/r/same", "warning"), ("schematic/o/r/flip", sev)):
            p = root / slot / unit / "snap.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(_env(run, s)))
    if manifest is not None:
        (root / "manifest.json").write_text(json.dumps(manifest))
    return root / "baseline", root / "candidate"


def _manifest(base="0000000000000000000000000000000000000000", cand="1111111111111111111111111111111111111111",
              policy="volatile-leaves-v1"):
    return {"run_id": "r-1", "normalization_policy": policy,
            "product": {"baseline": {"sha": base}, "candidate": {"sha": cand}}}


def _strict(a, b):
    return compare_trees(a, b, mode="strict", policy=load_policy("volatile-leaves-v1"))


def test_docs_for_report_loads_only_units_with_deltas(tmp_path):
    a, b = _gate(tmp_path)
    docs = docs_for_report(_strict(a, b), a, b)
    assert list(docs) == ["schematic/o/r/flip"]


def test_cli_and_run_modes_produce_equal_budgeted_reports(tmp_path):
    a, b = _gate(tmp_path)
    out = tmp_path / "cli.json"
    rc = cli.main([str(a), str(b), "--mode", "budgeted", "--budget", str(FIX / "rs001_only.json"),
                   "--jobs", "1", "-o", str(out)])
    m = run_modes(tmp_path, budget_path=FIX / "rs001_only.json")
    via_cli = json.loads(out.read_text())
    via_gate = json.loads((tmp_path / "field_report_budgeted.json").read_text())
    assert rc == 0 and m["budgeted"]["verdict"] == "clean"
    assert via_cli == via_gate
    assert via_cli["budget"]["bound_status"] == {"rs001-severity-down": {
        "max_units": 2, "units": 1, "ok": True, "expected_magnitude": None, "deltas": 1, "over_budget": False}}


def test_budget_policy_mismatch_is_budget_error(tmp_path):
    a, b = _gate(tmp_path)
    bud = load_budget(FIX / "rs001_only.json")
    with pytest.raises(BudgetError, match="normalization_policy"):
        budgeted_report(compare_trees(a, b, mode="strict", policy=None), bud, a, b)
    out = tmp_path / "r.json"
    assert cli.main([str(a), str(b), "--mode", "budgeted", "--policy", "none",
                     "--budget", str(FIX / "rs001_only.json"), "-o", str(out)]) == 2


def test_budget_sha_mismatch_with_manifest_is_budget_error(tmp_path):
    _gate(tmp_path, manifest=_manifest(cand="2222222222222222222222222222222222222222"))
    with pytest.raises(BudgetError, match="candidate_sha"):
        run_modes(tmp_path, budget_path=FIX / "rs001_only.json")
    assert not (tmp_path / "field_report_budgeted.json").exists()


def test_budget_manifest_policy_mismatch_is_budget_error(tmp_path):
    _gate(tmp_path, manifest=_manifest(policy="volatile-leaves-v0"))
    with pytest.raises(BudgetError, match="manifest"):
        run_modes(tmp_path, budget_path=FIX / "rs001_only.json")


def test_budget_sha_prefix_match_allowed(tmp_path):
    _gate(tmp_path, manifest=_manifest())
    bud = json.loads((FIX / "rs001_only.json").read_text())
    bud["baseline_sha"], bud["candidate_sha"] = "0000000", "1111111"
    bp = tmp_path / "short.json"; bp.write_text(json.dumps(bud))
    assert run_modes(tmp_path, budget_path=bp)["budgeted"]["verdict"] == "clean"
    assert run_modes(tmp_path, budget_path=FIX / "rs001_only.json")["budgeted"]["verdict"] == "clean"


def test_no_manifest_skips_sha_check(tmp_path):
    """The fixture budget's SHAs are placeholders; without a manifest nothing contradicts them."""
    a, b = _gate(tmp_path)
    rep = budgeted_report(_strict(a, b), load_budget(FIX / "rs001_only.json"), a, b)
    assert rep["verdict"] == "clean" and rep["mode"] == "budgeted"


# ---- over_budget verdict precedence ------------------------------------------

def _synthetic_strict(n_deltas, *, policy_violations=(), missing=0):
    deltas = [{"unit": "schematic/o/r/u", "analyzer": "schematic", "path": f"/a/{i}", "op": "changed",
               "before": 0, "after": 1} for i in range(n_deltas)]
    return {"policy": "volatile-leaves-v1", "identity": {}, "units": [], "deltas": deltas,
            "policy_violations": list(policy_violations),
            "summary": {"missing": missing, "parse_errors": 0}}


def _b(classes, allowed=0):
    return {"budget_id": "t", "classes": classes, "unexplained_deltas_allowed": allowed,
            "unexplained_missing_units_allowed": 0, "relock": False}


def test_verdict_over_budget_beats_residuals(tmp_path):
    strict = _synthetic_strict(3)
    strict["deltas"].append({**strict["deltas"][0], "path": "/unclaimed"})
    rep = budgeted_report(strict, _b([{"id": "c", "path_glob": "/a/*", "expected_magnitude": 1}]),
                          tmp_path, tmp_path)
    assert rep["verdict"] == "over_budget" and rep["budget"]["over_budget"] == ["c"]


def test_verdict_error_beats_over_budget(tmp_path):
    strict = _synthetic_strict(3, policy_violations=["v"])
    rep = budgeted_report(strict, _b([{"id": "c", "path_glob": "/a/*", "expected_magnitude": 1}]),
                          tmp_path, tmp_path)
    assert rep["verdict"] == "error"


def test_verdict_residuals_and_clean(tmp_path):
    rep = budgeted_report(_synthetic_strict(2), _b([{"id": "c", "path_glob": "/x/*"}]), tmp_path, tmp_path)
    assert rep["verdict"] == "residuals"
    rep = budgeted_report(_synthetic_strict(2), _b([{"id": "c", "path_glob": "/a/*", "expected_magnitude": 1}]),
                          tmp_path, tmp_path)
    assert rep["verdict"] == "clean"


def test_cli_prints_over_budget_classes_and_exits_1(tmp_path, capsys):
    a, b = _gate(tmp_path)
    budget = json.loads((FIX / "rs001_only.json").read_text())
    budget["classes"][0]["expected_magnitude"] = 0
    bp = tmp_path / "ob.json"
    bp.write_text(json.dumps(budget))
    rc = cli.main([str(a), str(b), "--mode", "budgeted", "--budget", str(bp), "--jobs", "1",
                   "-o", str(tmp_path / "r.json")])
    out = capsys.readouterr().out
    assert rc == 1
    assert "budgeted: over_budget" in out
    assert "over_budget: rs001-severity-down claimed 1 deltas > 2x expected_magnitude 0" in out
