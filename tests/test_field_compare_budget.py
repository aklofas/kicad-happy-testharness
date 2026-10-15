import json
from pathlib import Path

import pytest

from regression.field_compare import BudgetError, Delta, evaluate_budget, load_budget

FIX = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "budgets"
U = dict(unit="schematic/o/r/k", analyzer="schematic")


def _d(path, op="changed", before=None, after=None, **kw):
    return Delta(path=path, op=op, before=before, after=after, **{**U, **kw})


def _docs(rule_a="RS-001", rule_b="RS-001"):
    a = {"findings": [{"rule_id": rule_a, "detector": "audit_rail_sources", "severity": "warning"}]}
    b = {"findings": [{"rule_id": rule_b, "detector": "audit_rail_sources", "severity": "info"}]}
    return {U["unit"]: (a, b)}


def _budget(classes, **kw):
    return {"budget_id": "t", "unexplained_deltas_allowed": 0, "unexplained_missing_units_allowed": 0,
            "relock": False, "classes": classes, **kw}


def _write(tmp_path, obj):
    p = tmp_path / "b.json"
    p.write_text(json.dumps(obj))
    return p


def test_load_budget_validates_required_keys(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"budget_id": "x", "classes": []}))
    with pytest.raises(BudgetError, match="unexplained_deltas_allowed"):
        load_budget(p)
    p.write_text(json.dumps({"budget_id": "x", "classes": [{"id": "c"}],
                             "unexplained_deltas_allowed": 0, "unexplained_missing_units_allowed": 0, "relock": False}))
    with pytest.raises(BudgetError, match="path_glob"):
        load_budget(p)
    p.write_text(json.dumps({"budget_id": "x", "classes": [{"id": "c", "path_glob": "/a", "op": ["teleported"]}],
                             "unexplained_deltas_allowed": 0, "unexplained_missing_units_allowed": 0, "relock": False}))
    with pytest.raises(BudgetError, match="op"):
        load_budget(p)


@pytest.mark.parametrize("extra,match", [
    ({"bogus": 1}, "unknown key"),
    ({"direction": "sideways"}, "direction"),
    ({"value_relation": "renamed_from"}, "value_relation"),
    ({"where": {"nope": ["x"]}}, "where"),
    ({"unit_bound": {"max_units": "two"}}, "unit_bound"),
    ({"unit_bound": 3}, "unit_bound"),
    ({"predicate": "no_colon"}, "predicate"),
    ({"path_glob": "/a/**/b"}, "path_glob"),
])
def test_load_budget_rejects_malformed_class(tmp_path, extra, match):
    cls = {"id": "c", "path_glob": "/a", **extra}
    with pytest.raises(BudgetError, match=match):
        load_budget(_write(tmp_path, _budget([cls])))


def test_load_budget_rejects_unreadable_and_bad_counts(tmp_path):
    with pytest.raises(BudgetError):
        load_budget(tmp_path / "missing.json")
    with pytest.raises(BudgetError, match="unexplained_deltas_allowed"):
        load_budget(_write(tmp_path, _budget([], unexplained_deltas_allowed="0")))


def test_fixture_budget_loads():
    b = load_budget(FIX / "rs001_only.json")
    assert b["budget_id"] == "fixture-rs001-severity"


def test_class_claims_matching_delta_and_reports_counts():
    b = load_budget(FIX / "rs001_only.json")
    res = evaluate_budget([_d("/findings/0/severity", before="warning", after="info")], b, docs=_docs())
    assert res["clean"] is True
    assert res["claimed_counts"] == {"rs001-severity-down": 1}
    assert res["claimed_units"] == {"rs001-severity-down": 1}
    assert res["residuals"] == [] and res["violations"] == []


def test_class_does_not_excuse_unrelated_delta_same_unit():
    b = load_budget(FIX / "rs001_only.json")
    deltas = [_d("/findings/0/severity", before="warning", after="info"),
              _d("/statistics/total_nets", before=3, after=4)]
    res = evaluate_budget(deltas, b, docs=_docs())
    assert res["clean"] is False
    assert [r["path"] for r in res["residuals"]] == ["/statistics/total_nets"]


def test_where_resolves_rule_from_either_side():
    b = load_budget(FIX / "rs001_only.json")
    res = evaluate_budget([_d("/findings/0/severity", before="warning", after="info")], b, docs=_docs("LB-001", "RS-001"))
    assert res["claimed_counts"] == {"rs001-severity-down": 1} and res["residuals"] == []
    res = evaluate_budget([_d("/findings/0/severity", before="warning", after="info")], b, docs=_docs("LB-001", "LB-001"))
    assert res["claimed_counts"] == {} and len(res["residuals"]) == 1


def test_where_detector_selector_positive_and_negative():
    b = _budget([{"id": "det", "path_glob": "/findings/*/severity", "where": {"detector": ["audit_rail_sources"]}}])
    d = [_d("/findings/0/severity", before="warning", after="info")]
    assert evaluate_budget(d, b, docs=_docs())["clean"]
    b["classes"][0]["where"]["detector"] = ["other"]
    assert not evaluate_budget(d, b, docs=_docs())["clean"]


def test_where_without_docs_does_not_claim():
    b = load_budget(FIX / "rs001_only.json")
    res = evaluate_budget([_d("/findings/0/severity", before="warning", after="info")], b)
    assert len(res["residuals"]) == 1


def test_where_applies_under_assessments():
    b = _budget([{"id": "as", "path_glob": "/assessments/*/severity", "where": {"rule_id": ["XV-1"]}}])
    docs = {U["unit"]: ({"assessments": [{"rule_id": "XV-1"}]}, {"assessments": [{"rule_id": "XV-1"}]})}
    assert evaluate_budget([_d("/assessments/0/severity", before="a", after="b")], b, docs=docs)["clean"]


def test_direction_down_rejects_upgrade():
    b = load_budget(FIX / "rs001_only.json")
    res = evaluate_budget([_d("/findings/0/severity", before="info", after="warning")], b, docs=_docs())
    assert res["clean"] is False and len(res["residuals"]) == 1


@pytest.mark.parametrize("direction,before,after,ok", [
    ("up", "info", "error", True), ("up", "error", "info", False),
    ("down", "error", "info", True), ("none", "info", "info", True),
    ("none", "info", "warning", False), ("up", "info", "bogus", False),
    ("any", "info", "bogus", True),
])
def test_direction_matrix(direction, before, after, ok):
    b = _budget([{"id": "c", "path_glob": "/findings/*/severity", "direction": direction}])
    res = evaluate_budget([_d("/findings/0/severity", before=before, after=after)], b)
    assert res["clean"] is ok


def test_direction_non_severity_path_fails_directional():
    b = _budget([{"id": "c", "path_glob": "/findings/*/title", "direction": "up"}])
    assert not evaluate_budget([_d("/findings/0/title", before="a", after="b")], b)["clean"]
    b["classes"][0]["direction"] = "any"
    assert evaluate_budget([_d("/findings/0/title", before="a", after="b")], b)["clean"]


def test_where_class_never_matches_outside_findings():
    b = load_budget(FIX / "rs001_only.json")
    res = evaluate_budget([_d("/audience_summary/x/severity", before="warning", after="info")], b, docs=_docs())
    assert len(res["residuals"]) == 1


def test_analyzer_selector_positive_and_negative():
    b = load_budget(FIX / "rs001_only.json")
    d = _d("/findings/0/severity", before="warning", after="info", analyzer="pcb")
    res = evaluate_budget([d], b, docs=_docs())
    assert len(res["residuals"]) == 1
    b["classes"][0]["analyzer"] = "pcb"
    assert evaluate_budget([d], b, docs=_docs())["clean"]


def test_op_selector_negative():
    b = load_budget(FIX / "rs001_only.json")
    d = _d("/findings/0/severity", op="removed", before="warning")
    assert len(evaluate_budget([d], b, docs=_docs())["residuals"]) == 1


def test_glob_single_star_is_one_segment():
    b = _budget([{"id": "c", "path_glob": "/a/*/c"}])
    assert evaluate_budget([_d("/a/x/c")], b)["clean"]
    assert not evaluate_budget([_d("/a/x/y/c")], b)["clean"]
    assert not evaluate_budget([_d("/a/c")], b)["clean"]
    assert not evaluate_budget([_d("/a/x/c/d")], b)["clean"]


def test_unit_bound_violation():
    b = load_budget(FIX / "rs001_only.json")
    deltas = [_d("/findings/0/severity", before="warning", after="info", unit=f"schematic/o/r/k{i}") for i in range(3)]
    docs = {f"schematic/o/r/k{i}": _docs()[U["unit"]] for i in range(3)}
    res = evaluate_budget(deltas, b, docs=docs)
    assert res["clean"] is False
    assert any("max_units 2" in v and "rs001-severity-down" in v for v in res["violations"])


def test_unit_bound_counts_distinct_units_not_deltas():
    b = _budget([{"id": "c", "path_glob": "/x/*", "unit_bound": {"max_units": 1}}])
    res = evaluate_budget([_d("/x/a"), _d("/x/b"), _d("/x/c")], b)
    assert res["clean"] and res["claimed_counts"] == {"c": 3} and res["claimed_units"] == {"c": 1}


@pytest.fixture
def pred_mod(monkeypatch):
    import sys
    from tests.fixtures.h0.plan3.budgets import pred_mod as m
    monkeypatch.setitem(sys.modules, "regression.budgets.pred_mod", m)


def test_predicate_module_is_consulted(pred_mod):
    b = load_budget(FIX / "rs001_only.json")
    b["classes"].append({"id": "pred-class", "path_glob": "/statistics/**",
                         "predicate": "pred_mod:nets_grew_by_one"})
    ok = evaluate_budget([_d("/statistics/total_nets", before=3, after=4)], b, docs=_docs())
    bad = evaluate_budget([_d("/statistics/total_nets", before=3, after=9)], b, docs=_docs())
    assert ok["clean"] and not bad["clean"]


@pytest.mark.parametrize("spec", ["no_such_mod_xyz:fn", "pred_mod:missing_fn"])
def test_predicate_import_failure_is_budget_error(spec, pred_mod):
    b = _budget([{"id": "c", "path_glob": "/a", "predicate": spec}])
    with pytest.raises(BudgetError, match="predicate"):
        evaluate_budget([_d("/a")], b)


@pytest.mark.parametrize("spec", ["os:getcwd", "os.path:join", "tests.fixtures.h0.plan3.budgets.pred_mod:nets_grew_by_one",
                                  "regression.budgets.x:f", ":f", "pred_mod:", "pred_mod"])
def test_predicate_scope_rejected(tmp_path, spec):
    cls = {"id": "c", "path_glob": "/a", "predicate": spec}
    if spec != "os:getcwd":     # bare names pass load; they fail on import under regression.budgets
        with pytest.raises(BudgetError, match="class c"):
            load_budget(_write(tmp_path, _budget([cls])))
    with pytest.raises(BudgetError, match="class c"):
        evaluate_budget([_d("/a")], _budget([cls]))


def test_duplicate_or_bad_class_ids_rejected(tmp_path):
    with pytest.raises(BudgetError, match="duplicate class id 'c'"):
        load_budget(_write(tmp_path, _budget([{"id": "c", "path_glob": "/a"}, {"id": "c", "path_glob": "/b"}])))
    for bad in ("", 3, None):
        with pytest.raises(BudgetError, match="id"):
            load_budget(_write(tmp_path, _budget([{"id": bad, "path_glob": "/a"}])))


def test_evaluate_keeps_state_per_class_even_with_unvalidated_duplicate_ids(pred_mod):
    b = _budget([{"id": "x", "path_glob": "/s/*", "predicate": "pred_mod:nets_grew_by_one"},
                 {"id": "y", "path_glob": "/t/*", "unit_bound": {"max_units": 0}}])
    res = evaluate_budget([_d("/s/a", before=1, after=9), _d("/t/a")], b)
    assert [r["path"] for r in res["residuals"]] == ["/s/a"]
    assert res["claimed_counts"] == {"y": 1} and len(res["violations"]) == 1
    dup = _budget([{"id": "x", "path_glob": "/s/*", "predicate": "pred_mod:nets_grew_by_one"},
                   {"id": "x", "path_glob": "/t/*"}])
    res = evaluate_budget([_d("/s/a", before=1, after=9)], dup)
    assert len(res["residuals"]) == 1     # first class's predicate not overwritten by second


def test_double_star_glob_and_op_filter():
    b = _budget([{"id": "aud", "path_glob": "/audience_summary/**", "op": ["added", "changed"]}])
    res = evaluate_budget([_d("/audience_summary/designer/top_issues/0/rule_id", op="added", after="RS-001"),
                           _d("/audience_summary/manager/risk_level", before="none", after="low"),
                           _d("/audience_summary/designer/by_category/labels", op="removed", before=1)], b)
    assert res["claimed_counts"] == {"aud": 2}
    assert [r["path"] for r in res["residuals"]] == ["/audience_summary/designer/by_category/labels"]


def test_value_relation_equal_for_key_order():
    b = _budget([{"id": "ko", "path_glob": "**", "op": ["key_order"], "value_relation": "equal"}])
    same = _d("", op="key_order", before=["a", "b"], after=["b", "a"])
    assert not evaluate_budget([same], b)["clean"]
    b["classes"][0]["value_relation"] = "any"
    assert evaluate_budget([same], b)["clean"]
    b["classes"][0]["value_relation"] = "equal"
    assert evaluate_budget([_d("", op="key_order", before=["a"], after=["a"])], b)["clean"]


def test_missing_units_allowance():
    b = _budget([], unexplained_missing_units_allowed=1)
    assert evaluate_budget([], b, missing_units=1)["clean"]
    res = evaluate_budget([], b, missing_units=2)
    assert not res["clean"] and any("missing" in v for v in res["violations"])


def test_residual_allowance_honoured():
    b = _budget([], unexplained_deltas_allowed=1)
    assert evaluate_budget([_d("/a")], b)["clean"]
    assert not evaluate_budget([_d("/a"), _d("/b")], b)["clean"]
