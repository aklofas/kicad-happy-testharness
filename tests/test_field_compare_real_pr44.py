"""Real-shape check of the comparator on two retained PR #44 gate pairs."""
import json
import shutil
from pathlib import Path

import pytest

from regression.field_compare import compare_trees, load_budget, load_policy, run_modes, evaluate_budget, Delta

pytestmark = pytest.mark.unit

REAL = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "real"
IDENT, FLIP = REAL / "identical", REAL / "rail_flip"


def test_identical_code_pair_raw_differs_strict_clean():
    pol = load_policy("volatile-leaves-v1")
    raw = compare_trees(IDENT / "baseline", IDENT / "candidate", mode="raw", policy=None)
    strict = compare_trees(IDENT / "baseline", IDENT / "candidate", mode="strict", policy=pol)
    assert raw["verdict"] == "deltas" and raw["summary"]["by_op"] == {"bytes": 1}
    assert raw["summary"]["run_id_differs"] == 1 and "/inputs/run_id" in raw["note"]
    assert [d["path"] for d in raw["deltas"]] == ["/snap.json"]
    assert strict["verdict"] == "clean" and strict["policy_violations"] == []
    bare = compare_trees(IDENT / "baseline", IDENT / "candidate", mode="strict", policy=None)
    assert {d["path"] for d in bare["deltas"]} == {"/inputs/run_id", "/capability_mode_ref/run_id"}


def test_rail_flip_pair_strict_reports_the_known_deltas_completely():
    pol = load_policy("volatile-leaves-v1")
    rep = compare_trees(FLIP / "baseline", FLIP / "candidate", mode="strict", policy=pol)
    paths = {d["path"]: d for d in rep["deltas"]}
    assert rep["verdict"] == "deltas" and rep["policy_violations"] == []
    assert "/inputs/run_id" not in paths and "/capability_mode_ref/run_id" not in paths
    assert paths["/findings/0/rule_id"]["before"] == "LB-001" and paths["/findings/0/rule_id"]["after"] == "RS-001"
    assert paths["/findings/0/severity"]["before"] == "info" and paths["/findings/0/severity"]["after"] == "warning"
    assert paths["/design_analysis/net_classification/12V"]["before"] == "signal"
    assert paths["/findings/0/aliases"]["op"] == "removed"
    assert paths["/summary/by_severity/warning"]["after"] == 1
    assert rep["summary"]["deltas"] > 20 and len(rep["deltas"]) == rep["summary"]["deltas"]


def test_rail_flip_pair_budget_claims_everything_with_zero_residuals():
    pol = load_policy("volatile-leaves-v1")
    rep = compare_trees(FLIP / "baseline", FLIP / "candidate", mode="strict", policy=pol)
    budget = load_budget(REAL / "pr44_rail_flip_budget.json")
    unit = rep["units"][0]["unit"]
    docs = {unit: (json.loads((FLIP / "baseline" / rep["units"][0]["a"]).read_text()),
                   json.loads((FLIP / "candidate" / rep["units"][0]["b"]).read_text()))}
    ev = evaluate_budget([Delta(**d) for d in rep["deltas"]], budget, docs=docs)
    assert ev["residuals"] == [], ev["residuals"]
    assert ev["clean"] is True
    assert set(ev["claimed_counts"]) == {"rail-flip-finding", "rail-flip-net-classification", "rail-flip-statistics",
                                         "rail-flip-summaries", "rail-flip-audience", "rail-flip-test-coverage"}
    # sound only because the six classes' path domains are pairwise disjoint on this data;
    # evaluate_budget allows multi-claiming, which would double-count in this sum
    claimed_paths = [d["path"] for c in ev["claimed"].values() for d in c]
    assert len(claimed_paths) == len(set(claimed_paths)), "a delta was claimed by two classes"
    assert sum(ev["claimed_counts"].values()) == rep["summary"]["deltas"]


def test_budget_does_not_launder_an_injected_unrelated_delta(tmp_path):
    """Copy the flip pair, inject one extra change, and prove the same budget leaves a residual."""
    shutil.copytree(FLIP, tmp_path / "flip")
    cand = next((tmp_path / "flip" / "candidate").rglob("snap.json"))
    doc = json.loads(cand.read_text()); doc["statistics"]["total_components"] = 999; cand.write_text(json.dumps(doc))
    m = run_modes(tmp_path / "flip", budget_path=REAL / "pr44_rail_flip_budget.json")
    assert m["budgeted"]["verdict"] == "residuals" and m["budgeted"]["residuals"] == 1
    rep = json.loads((tmp_path / "flip" / "field_report_budgeted.json").read_text())
    assert [r["path"] for r in rep["budget"]["residuals"]] == ["/statistics/total_components"]
    assert m["strict_field_clean"] is False
