"""Memory-bounded comparator: deltas spill to JSONL sidecars past INLINE_DELTAS_MAX, the budget
is evaluated per unit inside the workers, and the pool holds a bounded window of units."""
import json
from pathlib import Path

import pytest

from regression import compare_snap_trees as cli
from regression import field_compare as fc
from regression.field_compare import (budgeted_report, compare_budgeted, compare_trees, iter_report_deltas,
                                      load_budget, load_policy, run_modes)

pytestmark = pytest.mark.unit

RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"
FIX = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "budgets"


def _env(run_id, sev="warning", nets=3):
    return {"analyzer_type": "schematic", "inputs": {"run_id": run_id, "source_files": [], "source_hashes": {}},
            "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
            "findings": [{"rule_id": "RS-001", "detector": "audit_rail_sources", "severity": sev}],
            "statistics": {"total_nets": nets}}


def _gate(root, n=6):
    """n units: even ones flip RS-001 warning->info (claimed by rs001_only), odd ones also move
    total_nets (a residual); plus one identical unit."""
    for slot, run in (("baseline", RUN_A), ("candidate", RUN_B)):
        for i in range(n):
            cand = slot == "candidate"
            doc = _env(run, "info" if cand else "warning", nets=3 + (i % 2 and cand))
            p = root / slot / f"schematic/o/r/u{i:02d}" / "snap.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(doc))
        p = root / slot / "schematic/o/r/same" / "snap.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(_env(run)))
    return root / "baseline", root / "candidate"


def _pol():
    return load_policy("volatile-leaves-v1")


def test_spilled_strict_report_matches_inline(tmp_path, monkeypatch):
    a, b = _gate(tmp_path)
    inline = compare_trees(a, b, mode="strict", policy=_pol())
    assert inline["deltas_file"] is None and len(inline["deltas"]) == 9
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    side = tmp_path / "r.deltas.jsonl"
    spilled = compare_trees(a, b, mode="strict", policy=_pol(), jobs=3, deltas_path=side)
    assert spilled["deltas"] is None and spilled["deltas_file"] == "r.deltas.jsonl"
    assert list(iter_report_deltas(spilled, tmp_path)) == inline["deltas"]
    assert {k: v for k, v in spilled.items() if k not in ("deltas", "deltas_file")} == \
        {k: v for k, v in inline.items() if k not in ("deltas", "deltas_file")}


def test_small_report_stays_inline_and_removes_a_stale_sidecar(tmp_path):
    a, b = _gate(tmp_path)
    side = tmp_path / "r.deltas.jsonl"
    side.write_text("stale\n")
    rep = compare_trees(a, b, mode="strict", policy=_pol(), deltas_path=side)
    assert rep["deltas_file"] is None and len(rep["deltas"]) == 9 and not side.exists()


def test_in_pass_budget_equals_post_hoc_budget(tmp_path):
    a, b = _gate(tmp_path)
    budget = load_budget(FIX / "rs001_only.json")
    post = budgeted_report(compare_trees(a, b, mode="strict", policy=_pol()), budget, a, b)
    for jobs in (1, 3):
        strict, inpass = compare_budgeted(a, b, budget, policy=_pol(), jobs=jobs)
        assert json.dumps(inpass, indent=1) == json.dumps(post, indent=1)
        assert strict["mode"] == "strict" and strict["budget"] is None
    assert post["budget"]["claimed_counts"] == {"rs001-severity-down": 6}
    assert post["budget"]["residual_count"] == 3 and post["verdict"] == "residuals"


def test_unit_bound_and_magnitude_are_judged_on_totals(tmp_path):
    """Feeding one unit at a time must not hide a cross-unit bound."""
    a, b = _gate(tmp_path)
    budget = load_budget(FIX / "rs001_only.json")
    budget["classes"][0]["unit_bound"] = {"max_units": 5}
    budget["classes"][0]["expected_magnitude"] = 2
    budget["classes"].append({"id": "nets", "path_glob": "/statistics/total_nets"})
    _, rep = compare_budgeted(a, b, budget, policy=_pol(), jobs=3)
    st = rep["budget"]["bound_status"]["rs001-severity-down"]
    assert (st["units"], st["ok"], st["deltas"], st["over_budget"]) == (6, False, 6, True)
    assert rep["verdict"] == "over_budget"


def test_spilled_budgeted_report_keeps_counts_and_writes_sidecars(tmp_path, monkeypatch):
    a, b = _gate(tmp_path)
    budget = load_budget(FIX / "rs001_only.json")
    _, inline = compare_budgeted(a, b, budget, policy=_pol())
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    paths = {k: tmp_path / f"r.{k}.jsonl" for k in ("deltas", "residuals", "claims")}
    _, rep = compare_budgeted(a, b, budget, policy=_pol(), jobs=2, deltas_path=paths["deltas"],
                              residuals_path=paths["residuals"], claims_path=paths["claims"])
    ev, ev0 = rep["budget"], inline["budget"]
    assert ev["claimed"] is None and ev["residuals"] is None
    assert ev["residuals_file"] == "r.residuals.jsonl" and ev["claims_file"] == "r.claims.jsonl"
    for k in ("claimed_counts", "claimed_units", "bound_status", "over_budget", "violations",
              "residual_count", "clean"):
        assert ev[k] == ev0[k], k
    assert rep["verdict"] == inline["verdict"] == "residuals"
    assert [json.loads(x) for x in paths["residuals"].read_text().splitlines()] == ev0["residuals"]
    rows = [json.loads(x) for x in paths["claims"].read_text().splitlines()]
    assert [r["unit"] for r in rows] == [f"schematic/o/r/u{i:02d}" for i in range(6)]
    assert rows[1] == {"unit": "schematic/o/r/u01", "analyzer": "schematic", "deltas": 2,
                       "claimed": {"rs001-severity-down": 1}, "residuals": 1}


def test_budgeted_report_refuses_a_spilled_strict_report(tmp_path, monkeypatch):
    a, b = _gate(tmp_path)
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    strict = compare_trees(a, b, mode="strict", policy=_pol(), deltas_path=tmp_path / "s.deltas.jsonl")
    with pytest.raises(ValueError, match="sidecar"):
        budgeted_report(strict, load_budget(FIX / "rs001_only.json"), a, b)


def test_run_modes_spills_beside_its_reports(tmp_path, monkeypatch):
    _gate(tmp_path)
    m0 = run_modes(tmp_path, budget_path=FIX / "rs001_only.json")
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    m = run_modes(tmp_path, budget_path=FIX / "rs001_only.json", jobs=2)
    assert m == m0 and m["budgeted"]["residuals"] == 3
    strict = json.loads((tmp_path / "field_report_strict.json").read_text())
    budgeted = json.loads((tmp_path / "field_report_budgeted.json").read_text())
    assert strict["deltas_file"] == budgeted["deltas_file"] == "field_report_strict.deltas.jsonl"
    assert len(list(iter_report_deltas(strict, tmp_path))) == 9
    assert budgeted["budget"]["claims_file"] == "field_report_budgeted.claims.jsonl"
    assert (tmp_path / "field_report_raw.deltas.jsonl").exists()


def test_cli_budgeted_spill_and_validation_md_reads_its_claims(tmp_path, monkeypatch):
    from tools.generate_validation_md import _unit_claims
    a, b = _gate(tmp_path)
    out = tmp_path / "rep" / "b.json"
    argv = [str(a), str(b), "--mode", "budgeted", "--budget", str(FIX / "rs001_only.json"), "--jobs", "2",
            "-o", str(out)]
    assert cli.main(argv) == 1
    inline_claims = _unit_claims(out)
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    assert cli.main(argv) == 1
    rep = json.loads(out.read_text())
    assert rep["budget"]["claimed"] is None and (out.parent / "b.claims.jsonl").exists()
    assert _unit_claims(out) == inline_claims
    assert inline_claims["schematic/o/r/u01"] == (frozenset({"rs001-severity-down"}), 1)


def test_pool_keeps_a_bounded_window_of_units_in_flight(tmp_path, monkeypatch):
    import concurrent.futures as cf
    for i in range(40):
        for slot, run in (("a", RUN_A), ("b", RUN_B)):
            p = tmp_path / slot / f"schematic/u{i:02d}" / "snap.json"
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(_env(run, nets=i if slot == "b" else 0)))
    state = {"out": 0, "max": 0}

    class Counting(cf.ProcessPoolExecutor):
        def submit(self, fn, *args):
            fut = super().submit(fn, *args)
            state["out"] += 1
            state["max"] = max(state["max"], state["out"])
            res = fut.result

            def result(*a, **k):
                state["out"] -= 1
                return res(*a, **k)
            fut.result = result
            return fut

    monkeypatch.setattr(cf, "ProcessPoolExecutor", Counting)
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=_pol(), jobs=2)
    assert rep["summary"]["with_deltas"] == 39
    assert 1 < state["max"] <= 2 * fc._IN_FLIGHT_PER_JOB


def test_scratch_spool_is_removed(tmp_path, monkeypatch):
    a, b = _gate(tmp_path)
    monkeypatch.setattr(fc, "INLINE_DELTAS_MAX", 2)
    out = tmp_path / "out"
    out.mkdir()
    compare_budgeted(a, b, load_budget(FIX / "rs001_only.json"), policy=_pol(), jobs=2,
                     deltas_path=out / "r.deltas.jsonl", residuals_path=out / "r.residuals.jsonl",
                     claims_path=out / "r.claims.jsonl")
    assert sorted(p.name for p in out.iterdir()) == ["r.claims.jsonl", "r.deltas.jsonl", "r.residuals.jsonl"]


def test_in_worker_predicates_match_post_hoc_on_real_pairs(tmp_path):
    """The v2.3.2 backport budget's predicates run inside the pool workers (real pairs, one tree)."""
    import shutil
    root = Path(__file__).resolve().parents[1]
    for name in ("a_rs001", "b_pu001_renumbered", "c_pp001"):
        for slot in ("baseline", "candidate"):
            shutil.copytree(root / "tests" / "fixtures" / "v232_backport" / name / slot, tmp_path / slot,
                            dirs_exist_ok=True)
    budget = load_budget(root / "regression" / "budgets" / "v232-backport.json")
    a, b = tmp_path / "baseline", tmp_path / "candidate"
    post = budgeted_report(compare_trees(a, b, mode="strict", policy=_pol()), budget, a, b)
    _, inpass = compare_budgeted(a, b, budget, policy=_pol(), jobs=3)
    assert inpass == post and post["verdict"] == "clean"
    assert post["summary"]["with_deltas"] == 3 and "findings-A-B-C" in post["budget"]["claimed_counts"]
