# tests/test_field_compare_trees.py
import json
from pathlib import Path

from regression.field_compare import Policy, compare_raw, compare_trees, iter_units, load_policy

RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"


def _env(run_id, **over):
    d = {"analyzer_type": "schematic", "inputs": {"run_id": run_id, "source_files": [], "source_hashes": {}},
         "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
         "findings": [{"rule_id": "RS-001", "detector": "audit_rail_sources", "severity": "warning"}],
         "statistics": {"total_nets": 3}}
    d.update(over)
    return d


def _write(root: Path, unit: str, doc, text=None):
    p = root / unit / "snap.json"
    p.parent.mkdir(parents=True)
    p.write_text(text if text is not None else json.dumps(doc), encoding="utf-8")
    return p


def test_iter_units_uses_parent_dir_as_unit_id(tmp_path):
    _write(tmp_path, "schematic/o/r/k.kicad_sch", _env(RUN_A))
    _write(tmp_path, "pcb/o/r/b.kicad_pcb", _env(RUN_A, analyzer_type="pcb"))
    units = iter_units(tmp_path)
    assert [(u, a) for u, a, _ in units] == [("pcb/o/r/b.kicad_pcb", "pcb"), ("schematic/o/r/k.kicad_sch", "schematic")]


def test_compare_raw_reports_bytes_delta_with_hashes(tmp_path):
    a = _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    b = _write(tmp_path / "b", "schematic/u", _env(RUN_B))
    deltas = compare_raw(a, b, unit="schematic/u", analyzer="schematic")
    assert [d.op for d in deltas] == ["bytes"]
    assert len(deltas[0].before) == 64 and deltas[0].before != deltas[0].after


def test_lexical_numeric_reported_only_in_raw(tmp_path):
    a = _write(tmp_path / "a", "schematic/u", None, text='{"x": 1}')
    b = _write(tmp_path / "b", "schematic/u", None, text='{"x": 1.0}')
    raw = compare_raw(a, b, unit="schematic/u", analyzer="schematic")
    assert sorted(d.op for d in raw) == ["bytes", "lexical_numeric"]
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert rep["summary"]["deltas"] == 0 and rep["verdict"] == "clean"


def test_strict_tree_identical_modulo_policy_is_clean(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_B))
    pol = load_policy("volatile-leaves-v1")
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=pol)
    assert rep["report_version"] == 1 and rep["mode"] == "strict" and rep["policy"] == "volatile-leaves-v1"
    assert rep["verdict"] == "clean"
    assert rep["summary"] == {"units": 1, "compared": 1, "identical": 1, "with_deltas": 0, "missing": 0,
                              "parse_errors": 0, "deltas": 0, "by_op": {}, "by_analyzer": {}}
    assert rep["units"][0]["status"] == "compared" and rep["units"][0]["delta_count"] == 0
    assert rep["identity"] == {"a": None, "b": None}
    # raw mode on the same trees legitimately fails and says why
    raw = compare_trees(tmp_path / "a", tmp_path / "b", mode="raw", policy=None)
    assert raw["verdict"] == "deltas" and raw["summary"]["by_op"] == {"bytes": 1}


def test_strict_tree_reports_complete_deltas_not_samples(tmp_path):
    a_doc = _env(RUN_A)
    b_doc = _env(RUN_A, statistics={"total_nets": 4})
    b_doc["findings"] = [dict(a_doc["findings"][0], severity="info")] + [{"rule_id": f"X-{i:03d}"} for i in range(10)]
    _write(tmp_path / "a", "schematic/u", a_doc)
    _write(tmp_path / "b", "schematic/u", b_doc)
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    paths = [d["path"] for d in rep["deltas"]]
    assert "/statistics/total_nets" in paths and "/findings/0/severity" in paths
    assert sum(p.startswith("/findings/") and rep["deltas"][i]["op"] == "added" for i, p in enumerate(paths)) == 10
    assert rep["summary"]["deltas"] == 12 and rep["summary"]["by_op"] == {"added": 10, "changed": 2}
    assert rep["summary"]["by_analyzer"] == {"schematic": 12}


def test_missing_unit_is_reported_not_ignored(tmp_path):
    _write(tmp_path / "a", "schematic/u1", _env(RUN_A))
    _write(tmp_path / "a", "schematic/u2", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u1", _env(RUN_A))
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    st = {u["unit"]: u["status"] for u in rep["units"]}
    assert st == {"schematic/u1": "compared", "schematic/u2": "missing_b"}
    assert rep["summary"]["missing"] == 1 and rep["verdict"] == "error"


def test_parse_error_is_a_unit_status(tmp_path):
    _write(tmp_path / "a", "schematic/u", None, text="{not json")
    _write(tmp_path / "b", "schematic/u", _env(RUN_A))
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert rep["units"][0]["status"] == "parse_error_a" and rep["summary"]["parse_errors"] == 1
    assert rep["verdict"] == "error"


def test_identity_copied_from_manifests(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_A))
    man = {"manifest_version": 1, "profile": "standard", "harness": {"sha": "h" * 40},
           "product": {"baseline": {"sha": "a" * 40}, "candidate": {"sha": "b" * 40}},
           "selection": {"source": "cross_section:smoke", "digest": "d", "unit_count": 1}, "argv": ["x"]}
    (tmp_path / "a" / "manifest.json").write_text(json.dumps(man))
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert rep["identity"]["a"] == {"profile": "standard", "harness": {"sha": "h" * 40},
                                    "product": man["product"], "selection": man["selection"]}
    assert rep["identity"]["b"] is None


def test_policy_violation_forces_error_verdict(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_A))
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=Policy(name="p", leaves=[{"pointer": "/inputs"}]))
    assert rep["policy_violations"] and rep["verdict"] == "error"


def test_identity_falls_back_to_gate_dir_manifest(tmp_path):
    _write(tmp_path / "baseline", "schematic/u", _env(RUN_A))
    _write(tmp_path / "candidate", "schematic/u", _env(RUN_A))
    man = {"profile": "standard", "harness": {"sha": "h"}, "product": {"baseline": {"sha": "a"}},
           "selection": {"unit_count": 1}}
    (tmp_path / "manifest.json").write_text(json.dumps(man))
    rep = compare_trees(tmp_path / "baseline", tmp_path / "candidate", mode="strict", policy=None)
    assert rep["identity"]["a"]["product"] == man["product"] and rep["identity"]["b"]["profile"] == "standard"


def test_unreadable_manifest_gives_null_identity(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_A))
    (tmp_path / "a" / "manifest.json").write_text("{bad")
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert rep["identity"] == {"a": None, "b": None}


def test_by_op_and_by_analyzer_reconcile_with_deltas(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_A, statistics={"total_nets": 9}))
    _write(tmp_path / "a", "pcb/u", _env(RUN_A, analyzer_type="pcb"))
    _write(tmp_path / "b", "pcb/u", _env(RUN_A, analyzer_type="pcb", statistics={"total_nets": 8}))
    rep = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    s = rep["summary"]
    assert s["deltas"] == len(rep["deltas"]) == sum(s["by_op"].values()) == sum(s["by_analyzer"].values())
    assert sum(u["delta_count"] for u in rep["units"]) == s["deltas"]
