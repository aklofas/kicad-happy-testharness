import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import aa_run  # noqa: E402

pytestmark = pytest.mark.unit

FIX = ROOT / "tests" / "fixtures" / "h0" / "plan6"
REPORT = json.loads((FIX / "field_report_aa.json").read_text())


def test_generalize_pointer_replaces_indices_only():
    assert aa_run.generalize_pointer("/findings/12/evidence/score") == "/findings/*/evidence/score"
    assert aa_run.generalize_pointer("/inputs/run_id") == "/inputs/run_id"
    assert aa_run.generalize_pointer("/a/0/b/00/c") == "/a/*/b/*/c"


def test_guess_shape():
    assert aa_run.guess_shape(["0f1e2d3c-4b5a-4697-8899-aabbccddeeff"]) == "uuid"
    assert aa_run.guess_shape(["2026-10-14T10:00:00Z"]) == "iso8601"
    assert aa_run.guess_shape([0.3, 1]) == "number"
    assert aa_run.guess_shape(["/x/aa/baseline/skills/x.kicad_pcb"]) == "abs_path"
    assert aa_run.guess_shape(["abc", 1]) == "mixed"


def test_summarize_groups_by_generalized_pointer():
    rep = aa_run.summarize_strict_report(REPORT)
    assert rep["report_version"] == 1 and rep["clean"] is False
    by = {l["pointer_glob"]: l for l in rep["leaves"]}
    assert by["/inputs/run_id"]["unit_count"] == 2
    assert by["/inputs/run_id"]["shape"] == "uuid"
    assert by["/inputs/generated_at"]["shape"] == "iso8601"
    assert by["/inputs/files/*/path"]["shape"] == "abs_path"
    assert all(len(l["examples"]) <= 3 for l in rep["leaves"])


def test_summarize_singleton_leaf_is_listed_not_merged():
    rep = aa_run.summarize_strict_report(REPORT)
    by = {l["pointer_glob"]: l for l in rep["leaves"]}
    assert by["/findings/*/evidence/score"]["unit_count"] == 1
    assert by["/findings/*/evidence/score"]["shape"] == "number"
    assert sum(1 for l in rep["leaves"] if l["pointer_glob"].startswith("/findings/")) == 1


def test_summarize_clean_report():
    clean = dict(REPORT, deltas=[], verdict="clean")
    rep = aa_run.summarize_strict_report(clean)
    assert rep["clean"] is True and rep["leaves"] == []


def test_propose_policy_adds_only_new_leaves_and_never_writes_policy():
    policy = {"name": "volatile-leaves-v1",
              "leaves": [{"pointer": "/inputs/run_id", "shape": "^[0-9a-f-]{36}$"}],
              "root_prefixes": "from manifest"}
    rep = aa_run.summarize_strict_report(REPORT)
    prop = aa_run.propose_policy(rep, policy)
    assert prop["name"] == "volatile-leaves-v1-proposed"
    added = {a["pointer_glob"] if "pointer_glob" in a else a["pointer"] for a in prop["added"]}
    assert "/inputs/run_id" not in added
    assert {"/inputs/generated_at", "/findings/*/evidence/score", "/inputs/files/*/path"} <= added
    numeric = [a for a in prop["added"] if a.get("pointer_glob") == "/findings/*/evidence/score"][0]
    assert numeric["review"].startswith("pointer is outside metadata roots")
    rid = [a for a in prop["added"] if a.get("pointer") == "/inputs/generated_at"][0]
    assert "review" not in rid
    assert policy["leaves"] == [{"pointer": "/inputs/run_id", "shape": "^[0-9a-f-]{36}$"}]


def test_propose_policy_tolerates_real_policy_shapes():
    policy = {"name": "p", "root_prefixes": "from_manifest",
              "leaves": [{"pointer_glob": "/inputs/files/*/path", "rewrite": "x", "note": "n"},
                         {"pointer": "/a", "equals": 1}]}
    prop = aa_run.propose_policy(aa_run.summarize_strict_report(REPORT), policy)
    assert "/inputs/files/*/path" in prop["existing"]
    assert all(a.get("pointer_glob") != "/inputs/files/*/path" for a in prop["added"])


def test_build_commands_use_same_sha_both_slots(tmp_path):
    cmds = aa_run.build_commands(product_dir=tmp_path / "kh", gate_dir=tmp_path / "aa",
                                 selection=["--cross-section", "smoke"], jobs=8, profile="standard")
    gate, cmp = cmds
    assert "--kind" in gate and gate[gate.index("--kind") + 1] == "aa"
    assert gate[gate.index("--baseline-dir") + 1] == gate[gate.index("--candidate-dir") + 1]
    assert cmp[-1].endswith("field_report.json") and "--mode" in cmp and cmp[cmp.index("--mode") + 1] == "strict"


def _leaf(glob, shape, units, examples=()):
    return {"pointer_glob": glob, "unit_count": units, "delta_count": units, "ops": {},
            "shape": shape, "examples": list(examples)}


def test_propose_policy_flags_outside_metadata_roots_and_vocabulary():
    rep = {"leaves": [_leaf("/findings/*/evidence/score", "number", 5),
                      _leaf("/findings/*/id", "uuid", 3),
                      _leaf("/assessments/*/t", "iso8601", 2),
                      _leaf("/inputs/run_id", "uuid", 9),
                      _leaf("/inputs/generated_at", "iso8601", 9),
                      _leaf("/inputs/n", "number", 9),
                      _leaf("/inputs/files/*/path", "abs_path", 2),
                      _leaf("/inputs/label", "string", 2)]}
    prop = aa_run.propose_policy(rep, {"name": "p", "leaves": []})
    by = {a.get("pointer_glob") or a["pointer"]: a for a in prop["added"]}
    for k in ("/findings/*/evidence/score", "/findings/*/id", "/assessments/*/t"):
        assert by[k]["review"].startswith("pointer is outside metadata roots")
    assert "review" not in by["/inputs/generated_at"]
    assert by["/inputs/run_id"]["shape"] == aa_run._UUID_RX  # uuid is not the named run_id form
    assert by["/inputs/run_id"]["review"].startswith("uuid-shaped leaf")
    assert by["/inputs/generated_at"]["shape"] == "iso8601"
    assert by["/inputs/n"]["review"].startswith("numeric drift across units")
    assert by["/inputs/files/*/path"]["rewrite"] == "strip_root_prefix"
    assert "shape" not in by["/inputs/files/*/path"]
    assert "shape" not in by["/inputs/label"] and "review" in by["/inputs/label"]


def test_skip_run_without_reports_returns_2(tmp_path):
    assert aa_run.main(["--product", str(tmp_path), "--gate-dir", str(tmp_path / "g"),
                        "--cross-section", "smoke", "--skip-run"]) == 2


def test_skip_run_uses_strict_report(tmp_path):
    g = tmp_path / "g"
    g.mkdir()
    (g / "field_report_strict.json").write_text(json.dumps(REPORT))
    rc = aa_run.main(["--product", str(tmp_path), "--gate-dir", str(g),
                      "--cross-section", "smoke", "--skip-run"])
    assert rc == 1 and (g / "aa_report.json").exists() and (g / "field_report.json").exists()


def test_timestamp_run_id_maps_to_named_shape():
    rep = {"deltas": [{"unit": "u", "path": "/inputs/upstream_artifacts/0/run_id", "op": "changed",
                       "before": "20260913T072438Z-aefff9", "after": "20260913T072500Z-bb0012"}]}
    prop = aa_run.propose_policy(aa_run.summarize_strict_report(rep), {"name": "p", "leaves": []})
    (entry,) = prop["added"]
    assert entry["pointer_glob"] == "/inputs/upstream_artifacts/*/run_id"
    assert entry["shape"] == "run_id" and "review" not in entry


def test_proposal_note_names_keys_to_strip():
    prop = aa_run.propose_policy({"leaves": []}, {"name": "p", "leaves": []})
    for k in ("observed_units", "observed_deltas", "review"):
        assert k in prop["note"]


def _run_main(monkeypatch, tmp_path, rc, strict_age):
    g = tmp_path / "g"
    g.mkdir()
    if strict_age is not None:
        sp = g / "field_report_strict.json"
        sp.write_text(json.dumps(REPORT))
        old = sp.stat().st_mtime - strict_age
        os.utime(sp, (old, old))
    calls = []

    def fake_run(cmd, *a, **k):
        calls.append(cmd)
        if len(calls) == 2:  # compare writes the report
            (g / "field_report.json").write_text(json.dumps(dict(REPORT, deltas=[])))

        class R:
            returncode = rc if len(calls) == 1 else 0
        return R()

    monkeypatch.setattr(aa_run.subprocess, "run", fake_run)
    out = aa_run.main(["--product", str(tmp_path), "--gate-dir", str(g), "--cross-section", "smoke"])
    return out, calls


def test_stale_strict_report_falls_back_to_compare(monkeypatch, tmp_path):
    rc, calls = _run_main(monkeypatch, tmp_path, 0, strict_age=3600)
    assert len(calls) == 2 and calls[1][1] == str(aa_run.COMPARE)
    assert rc == 0  # compare output (no deltas) was used, not the stale strict report


def test_gate_unexpected_exit_code_returns_2_without_compare(monkeypatch, tmp_path):
    rc, calls = _run_main(monkeypatch, tmp_path, 3, strict_age=None)
    assert rc == 2 and len(calls) == 1
