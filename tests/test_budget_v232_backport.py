"""The v2.3.2 backport budget (6a91aaa -> 4701c26): predicate module + record, on real pairs
and on injected violations. Fixtures: tests/fixtures/v232_backport/README.md."""
import copy
import json
from pathlib import Path

import pytest

from regression.budgets import v232_backport as m
from regression.field_compare import (Delta, compare_strict, compare_trees, docs_for_report, evaluate_budget,
                                      load_budget, load_policy)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "v232_backport"
BUDGET = ROOT / "regression" / "budgets" / "v232-backport.json"
PAIRS = [("a_rs001", {"A": 1}), ("b_pu001", {"B": 1}), ("b_pu001_renumbered", {"A": 1, "B": 1}), ("c_pp001", {"C": 1})]


def _pair(name):
    rep = compare_trees(FIX / name / "baseline", FIX / name / "candidate", mode="strict",
                        policy=load_policy("volatile-leaves-v1"))
    u = rep["units"][0]
    a = json.loads((FIX / name / "baseline" / u["a"]).read_text())
    b = json.loads((FIX / name / "candidate" / u["b"]).read_text())
    return rep, u["unit"], a, b


def _deltas_for(a, b, unit):
    ds, viol = compare_strict(copy.deepcopy(a), copy.deepcopy(b), load_policy("volatile-leaves-v1"),
                              unit=unit, analyzer="schematic", root_prefixes=((), ()))
    assert viol == []
    return ds


def _evaluate(deltas, unit, a, b):
    return evaluate_budget(deltas, load_budget(BUDGET), docs={unit: (a, b)})


def _inject(doc, mutate):
    d2 = copy.deepcopy(doc)
    mutate(d2)
    return d2


def _base(fid):
    return fid.split("#")[0]


# ---- single-finding predicates ------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("BST", True), ("BOOT", True), ("CBST", True), ("BOOTSTRAP", True), ("BOOT1", True), ("BST_A", True),
    ("BST_N", True), ("VB/BST", True), ("bst", True), ("VBOOST", False), ("VIN", False), ("", False),
    ("BOOTX", False), ("SW", False),
])
def test_bootstrap_pin_tokens_mirror_the_product(name, expected):
    assert m.is_bootstrap_pin_name(name) is expected


def test_pp_pin_name_reads_the_parenthesised_token():
    assert m.pp_pin_name({"pins": ["U1201.20 (BST)"]}) == "BST"
    assert m.pp_pin_name({"pins": ["U1.4 (VB/BST)"]}) == "VB/BST"
    assert m.pp_pin_name({"pins": [{"ref": "U1"}]}) is None
    assert m.pp_pin_name({"pins": []}) is None


def _rs(pins, conf="deterministic", load=m.RS_OLD):
    return {"rule_id": "RS-001", "confidence": conf, "pins": pins, "nets": ["12v"],
            "description": f"Net 12v {load} but has no power_out pin.",
            "provenance": {"evidence": "rs_rail_audit", "confidence": conf}, "finding_id": "schematic:RS-001:12v"}


def test_class_a_requires_empty_pins_and_exactly_the_three_fields():
    assert m.is_class_a(_rs([]), _rs([], "heuristic", m.RS_NEW))
    assert not m.is_class_a(_rs(["#PWR01.1"]), _rs(["#PWR01.1"], "heuristic", m.RS_NEW))   # pins != []
    assert not m.is_class_a(_rs([]), _rs([]))                                               # nothing moved
    assert not m.is_class_a(_rs([]), _rs([], "heuristic"))                                  # description stale
    y = _rs([], "heuristic", m.RS_NEW); y["severity"] = "error"
    assert not m.is_class_a(_rs([]), y)                                                     # extra field


def test_class_b_needs_a_single_pin_no_connect_net_on_the_baseline_side():
    f = {"rule_id": "PU-001", "nets": ["INT"]}
    assert m.is_class_b(f, {"nets": {"INT": {"no_connect": True, "pins": [{"component": "U1"}]}}})
    assert m.is_class_b(f, {"nets": {"INT": {"no_connect": True, "pins": []}}})
    assert not m.is_class_b(f, {"nets": {"INT": {"no_connect": False, "pins": [{"component": "U1"}]}}})
    assert not m.is_class_b(f, {"nets": {"INT": {"no_connect": True, "pins": [{}, {}]}}})
    assert not m.is_class_b(f, {"nets": {}})
    assert not m.is_class_b({"rule_id": "PP-001", "nets": ["INT"]}, {"nets": {"INT": {"no_connect": True, "pins": []}}})


def test_class_c_is_pp001_on_a_bootstrap_pin_only():
    assert m.is_class_c({"rule_id": "PP-001", "pins": ["U1.4 (BST)"]})
    assert not m.is_class_c({"rule_id": "PP-001", "pins": ["U1.4 (VIN)"]})
    assert not m.is_class_c({"rule_id": "PU-001", "pins": ["U1.4 (BST)"]})


# ---- real pairs: each class is explained completely, with zero residuals ------------------

@pytest.mark.parametrize("name,classes", PAIRS)
def test_real_pair_is_explained_and_fully_claimed(name, classes):
    rep, unit, a, b = _pair(name)
    assert rep["verdict"] == "deltas" and rep["summary"]["deltas"] > 0 and rep["policy_violations"] == []
    an = m.analyze_unit(a, b)
    assert an["explained"] and an["derived_ok"], (an["reasons"], an["derived_reasons"])
    assert {k: an[k] for k in "ABC"} == {k: classes.get(k, 0) for k in "ABC"}
    ev = _evaluate([Delta(**d) for d in rep["deltas"]], unit, a, b)
    assert ev["residuals"] == [] and ev["clean"] is True
    assert sum(ev["claimed_counts"].values()) == rep["summary"]["deltas"]
    claimed = [d["path"] for c in ev["claimed"].values() for d in c]
    assert len(claimed) == len(set(claimed)), "a delta was claimed twice"


@pytest.mark.parametrize("name,_", PAIRS)
def test_real_pairs_derived_blocks_match_the_mirrored_builders_on_both_sides(name, _):
    for side in ("baseline", "candidate"):
        doc = json.loads(next((FIX / name / side).rglob("snap.json")).read_text())
        assert m.derived_mismatches(doc, side) == [], (name, side)


def test_pu001_cascade_removes_exactly_the_no_connect_finding():
    _, _, a, b = _pair("b_pu001")
    gone = [f for f in a["findings"] if f["finding_id"] not in {g["finding_id"] for g in b["findings"]}]
    assert [f["rule_id"] for f in gone] == ["PU-001"]
    net = a["nets"][gone[0]["nets"][0]]
    assert net["no_connect"] is True and len(net["pins"]) == 1
    assert len(a["findings"]) == len(b["findings"]) + 1


def test_pu001_removal_renumbers_a_duplicate_finding_id_and_is_still_explained():
    """Two PU-001 share a detection hash (`…` and `…#1`); removing the first renumbers the
    survivor, so a finding_id-keyed pairing would see one change + one unrelated removal."""
    _, _, a, b = _pair("b_pu001_renumbered")
    ids_a, ids_b = [f["finding_id"] for f in a["findings"]], [f["finding_id"] for f in b["findings"]]
    gone = [i for i in ids_a if i not in ids_b]
    assert len(gone) == 1 and gone[0].endswith("#1") and _base(gone[0]) in ids_b
    assert [f["rule_id"] for f in a["findings"] if f["finding_id"] == gone[0]] == ["PU-001"]
    assert len(a["findings"]) == len(b["findings"]) + 1
    an = m.analyze_unit(a, b)
    assert an["explained"] and an["B"] == 1 and an["reasons"] == []


def test_pp001_cascade_removes_exactly_the_bst_finding():
    _, _, a, b = _pair("c_pp001")
    gone = [f for f in a["findings"] if f["finding_id"] not in {g["finding_id"] for g in b["findings"]}]
    assert [(f["rule_id"], m.pp_pin_name(f)) for f in gone] == [("PP-001", "BST")]


# ---- the budget does not launder ----------------------------------------------------------

def test_rs001_flip_with_pins_is_a_residual_and_names_the_violation():
    _, unit, a, b = _pair("a_rs001")
    idx = next(i for i, f in enumerate(a["findings"])
               if f["rule_id"] == "RS-001" and f["confidence"] != b["findings"][i]["confidence"])
    a2 = _inject(a, lambda d: d["findings"][idx].__setitem__("pins", ["#PWR01.1"]))
    b2 = _inject(b, lambda d: d["findings"][idx].__setitem__("pins", ["#PWR01.1"]))
    an = m.analyze_unit(a2, b2)
    assert not an["explained"] and any(r.startswith("A-violation") for r in an["reasons"]), an["reasons"]
    ds = _deltas_for(a2, b2, unit)
    ev = _evaluate(ds, unit, a2, b2)
    assert ev["clean"] is False and len(ev["residuals"]) == len(ds)


def test_unrelated_change_in_the_same_unit_leaves_every_delta_as_residual():
    _, unit, a, b = _pair("c_pp001")
    b2 = _inject(b, lambda d: d["findings"][0].__setitem__("severity", "error"))
    an = m.analyze_unit(a, b2)
    assert not an["explained"] and an["C"] == 1
    ev = _evaluate(_deltas_for(a, b2, unit), unit, a, b2)
    assert ev["clean"] is False and ev["claimed_counts"] == {}


def test_added_finding_is_never_in_budget():
    _, _, a, b = _pair("b_pu001")
    extra = dict(b["findings"][0], finding_id="schematic:XX-999:new", rule_id="XX-999")
    b2 = _inject(b, lambda d: d["findings"].append(extra))
    an = m.analyze_unit(a, b2)
    assert not an["explained"] and any(r.startswith("added finding") for r in an["reasons"])


def test_removal_outside_b_c_is_a_residual():
    _, _, a, b = _pair("a_rs001")
    b2 = _inject(b, lambda d: d["findings"].pop(0))
    an = m.analyze_unit(a, b2)
    assert not an["explained"] and any("removed finding outside B/C" in r for r in an["reasons"])


def test_finding_id_renumber_without_a_removal_is_not_explained():
    _, _, a, b = _pair("a_rs001")
    b2 = _inject(b, lambda d: d["findings"][0].__setitem__("finding_id", d["findings"][0]["finding_id"] + "#1"))
    an = m.analyze_unit(a, b2)
    assert not an["explained"] and any("renumbered without a removal" in r for r in an["reasons"])


def test_derived_block_not_following_findings_makes_the_derived_deltas_residual():
    _, unit, a, b = _pair("a_rs001")
    b2 = _inject(b, lambda d: d["trust_summary"].__setitem__(
        "by_confidence", dict(d["trust_summary"]["by_confidence"], heuristic=99)))
    an = m.analyze_unit(a, b2)
    assert an["explained"] and not an["derived_ok"]
    ds = _deltas_for(a, b2, unit)
    ev = _evaluate(ds, unit, a, b2)
    derived = sorted(d.path for d in ds if not d.path.startswith("/findings/"))
    assert sorted(r["path"] for r in ev["residuals"]) == derived
    assert "/trust_summary/by_confidence/heuristic" in derived
    assert ev["claimed_counts"].get("findings-A-B-C")   # the findings movement itself is still claimed


def test_predicates_refuse_without_docs():
    d = Delta("schematic/x", "schematic", "/findings/0/confidence", "changed", "deterministic", "heuristic")
    assert m.findings_explained(d, None, None) is False
    assert m.derived_explained(d, None, None) is False


def test_other_analyzers_and_other_paths_are_never_claimed():
    _, unit, a, b = _pair("a_rs001")
    ds = [Delta(unit.replace("schematic/", "emc/"), "emc", "/findings/0/confidence", "changed", "x", "y"),
          Delta(unit, "schematic", "/statistics/total_components", "changed", 1, 2)]
    ev = _evaluate(ds, unit, a, b)
    assert len(ev["residuals"]) == 2 and ev["claimed_counts"] == {}


# ---- lazy docs + summary helper -----------------------------------------------------------

def test_docs_for_report_loads_on_access_and_bounds_memory():
    rep, unit, a, b = _pair("c_pp001")
    docs = docs_for_report(rep, FIX / "c_pp001" / "baseline", FIX / "c_pp001" / "candidate")
    assert len(docs) == 1 and list(docs) == [unit] and docs.get("nope") is None
    assert docs.get(unit)[0] == a and docs[unit][1] == b
    assert len(docs._loaded) == 1


def test_summarize_reports_class_magnitudes(tmp_path):
    rep, unit, a, b = _pair("c_pp001")
    (tmp_path / "field_report_strict.json").write_text(json.dumps(rep))
    out = m.summarize(tmp_path)
    assert out["classes"]["C"] == {"findings": 1, "units": 1, "repos": 1}
    assert out["classes"]["A"]["findings"] == 0 and out["unexplained_units"] == [] and out["c_pin_names"] == {"BST": 1}
