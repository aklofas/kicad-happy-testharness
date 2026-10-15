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
    assert rep["identity"]["a"] == {"run_id": None, "profile": "standard", "harness": {"sha": "h" * 40},
                                    "product": man["product"], "selection": man["selection"],
                                    "normalization_policy": None}
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


def test_identity_carries_run_id_and_policy(tmp_path):
    _write(tmp_path / "baseline", "schematic/u", _env(RUN_A))
    _write(tmp_path / "candidate", "schematic/u", _env(RUN_A))
    (tmp_path / "manifest.json").write_text(json.dumps({"run_id": "r-1", "normalization_policy": "volatile-leaves-v1"}))
    rep = compare_trees(tmp_path / "baseline", tmp_path / "candidate", mode="strict", policy=None)
    assert rep["identity"]["a"]["run_id"] == "r-1"
    assert rep["identity"]["b"]["normalization_policy"] == "volatile-leaves-v1"


# ---- I3: raw says so --------------------------------------------------------

def test_raw_report_states_run_id_note_and_counts(tmp_path):
    _write(tmp_path / "a", "schematic/u1", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u1", _env(RUN_B))                       # run id differs
    _write(tmp_path / "a", "schematic/u2", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u2", _env(RUN_A, statistics={"total_nets": 7}))  # same run id
    _write(tmp_path / "a", "schematic/u3", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u3", _env(RUN_A))                       # byte-identical
    raw = compare_trees(tmp_path / "a", tmp_path / "b", mode="raw", policy=None)
    assert "/inputs/run_id" in raw["note"] and "strict" in raw["note"]
    assert raw["summary"]["run_id_differs"] == 1 and raw["summary"]["with_deltas"] == 2
    strict = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert "note" not in strict and "run_id_differs" not in strict["summary"]


# ---- I4: raw compares the per-unit file set ---------------------------------

def test_raw_compares_unit_file_set(tmp_path):
    pa = _write(tmp_path / "a", "emc/u", _env(RUN_A))
    pb = _write(tmp_path / "b", "emc/u", _env(RUN_A))           # snap.json byte-identical
    (pa.parent / "capability_mode.json").write_text('{"run_id": "1"}')
    (pb.parent / "capability_mode.json").write_text('{"run_id": "2"}')
    (pa.parent / "extra.json").write_text("{}")                  # sidecar only on side a
    (pb.parent / "snap.json.stale").write_text("old")            # quarantine: ignored
    (pb.parent / "snap.json.tmp-1-ab").write_text("partial")     # in-flight temp: ignored
    raw = compare_trees(tmp_path / "a", tmp_path / "b", mode="raw", policy=None)
    got = [(d["path"], d["op"]) for d in raw["deltas"]]
    assert got == [("/capability_mode.json", "bytes"), ("/extra.json", "removed")]
    assert raw["verdict"] == "deltas" and raw["summary"]["run_id_differs"] == 0
    # strict stays snap.json fields only
    strict = compare_trees(tmp_path / "a", tmp_path / "b", mode="strict", policy=None)
    assert strict["verdict"] == "clean"


def test_raw_snap_bytes_delta_names_the_file(tmp_path):
    _write(tmp_path / "a", "schematic/u", _env(RUN_A))
    _write(tmp_path / "b", "schematic/u", _env(RUN_B))
    raw = compare_trees(tmp_path / "a", tmp_path / "b", mode="raw", policy=None)
    assert [(d["path"], d["op"]) for d in raw["deltas"]] == [("/snap.json", "bytes")]


# ---- I6: lexical_numeric complete + reorder-safe ----------------------------

def test_lexical_numeric_is_complete_not_a_sample(tmp_path):
    a = _write(tmp_path / "a", "schematic/u", None, text=json.dumps({f"k{i}": 1 for i in range(60)}))
    b = _write(tmp_path / "b", "schematic/u", None,
               text=json.dumps({f"k{i}": 1 for i in range(60)}).replace(": 1", ": 1.0"))
    raw = compare_raw(a, b, unit="schematic/u", analyzer="schematic")
    lex = [d for d in raw if d.op == "lexical_numeric"]
    assert len(lex) == 1 and lex[0].before == ["1"] * 60 and lex[0].after == ["1.0"] * 60


def test_lexical_numeric_ignores_pure_key_reorder(tmp_path):
    a = _write(tmp_path / "a", "schematic/u", None, text='{"x": 1, "y": 2.0}')
    b = _write(tmp_path / "b", "schematic/u", None, text='{"y": 2.0, "x": 1}')
    raw = compare_raw(a, b, unit="schematic/u", analyzer="schematic")
    assert [d.op for d in raw] == ["bytes"]


# ---- I2: parallel comparison is byte-identical ------------------------------

def test_jobs_1_and_4_reports_byte_identical(tmp_path, monkeypatch):
    import concurrent.futures as cf
    pools = []

    class Recording(cf.ProcessPoolExecutor):
        def __init__(self, *a, **k):
            pools.append(k.get("max_workers"))
            super().__init__(*a, **k)
    monkeypatch.setattr(cf, "ProcessPoolExecutor", Recording)
    for i in range(12):
        _write(tmp_path / "a", f"schematic/u{i:02d}", _env(RUN_A))
        _write(tmp_path / "b", f"schematic/u{i:02d}", _env(RUN_B, statistics={"total_nets": i}))
    _write(tmp_path / "a", "pcb/only_a", _env(RUN_A))
    _write(tmp_path / "a", "pcb/bad", _env(RUN_A))
    _write(tmp_path / "b", "pcb/bad", None, text="{not json")
    pol = load_policy("volatile-leaves-v1")
    for mode, policy in (("raw", None), ("strict", pol)):
        one = compare_trees(tmp_path / "a", tmp_path / "b", mode=mode, policy=policy, jobs=1)
        four = compare_trees(tmp_path / "a", tmp_path / "b", mode=mode, policy=policy, jobs=4)
        assert json.dumps(one, indent=1) == json.dumps(four, indent=1)
    assert pools == [4, 4]                           # jobs=4 really ran in a pool (raw + strict)
    assert one["summary"]["missing"] == 1 and one["summary"]["parse_errors"] == 1
    assert one["summary"]["with_deltas"] == 11       # u03's total_nets equals the env's 3


# ---- I7 / M2: symlinked slot root; posix unit paths --------------------------

def test_symlinked_gate_root_strips_both_forms(tmp_path):
    real = tmp_path / "real_gate"
    link = tmp_path / "link_gate"
    link.symlink_to(real, target_is_directory=True)
    pol = load_policy("volatile-leaves-v1")
    for recorded in (link, real):         # envelopes may record either form
        for slot, run in (("baseline", RUN_A), ("candidate", RUN_B)):
            d = _env(run)
            d["inputs"]["source_files"] = [str(recorded / slot / "schematic" / "u" / "snap.json")]
            p = real / slot / "pcb" / "u" / "snap.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(d))
        rep = compare_trees(link / "baseline", link / "candidate", mode="strict", policy=pol)
        assert rep["verdict"] == "clean", (recorded, rep["deltas"])
    assert rep["units"][0]["a"] == "pcb/u/snap.json"
