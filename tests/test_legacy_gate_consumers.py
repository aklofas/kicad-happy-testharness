"""Gate consumers read the current baseline/candidate slots and never report a clean empty
result (code A1-F9 A1-F12 A1-F11, arch A3-F8; ruling R5)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "regression"))

pytestmark = pytest.mark.unit


def _snap(root, slot, rule_ids, severity="warning"):
    p = root / slot / "schematic" / "o" / "r" / "a.kicad_sch" / "snap.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    findings = [{"rule_id": r, "severity": severity, "detector": "d"} for r in rule_ids]
    p.write_text(json.dumps({"analyzer_type": "schematic", "findings": findings,
                             "summary": {"total_findings": len(findings),
                                         "by_severity": {"error": 0, "warning": len(findings), "info": 0}}}))


def _delta(gate):
    return subprocess.run([sys.executable, str(HARNESS / "tools" / "gate_rule_delta.py"), str(gate)],
                          capture_output=True, text=True, timeout=60)


def test_gate_rule_delta_reads_baseline_candidate(tmp_path):
    _snap(tmp_path, "baseline", ["RS-001"])
    _snap(tmp_path, "candidate", ["RS-001", "RS-001"])
    r = _delta(tmp_path)
    assert r.returncode == 0 and "units with any rule-count delta: 1" in r.stdout


def test_gate_rule_delta_refuses_a_dir_without_slots(tmp_path):
    r = _delta(tmp_path)
    assert r.returncode == 2 and "no baseline/+candidate/" in r.stderr


def test_contract_gate_reads_candidate_and_reports_skips(tmp_path, monkeypatch, capsys):
    import run_v14_default_contract_gate as cg
    monkeypatch.setattr(cg, "OUT_DIR", tmp_path / "out")
    _snap(tmp_path / "gate", "candidate", ["RS-001"])
    assert cg.candidate_snap_dir(tmp_path / "gate") == tmp_path / "gate" / "candidate"
    assert cg.main(["--gate-dir", str(tmp_path / "gate"), "--no-schema", "--jobs", "1"]) == 0
    out = capsys.readouterr().out
    assert "Total snapshots: 1" in out
    rollup = json.loads((tmp_path / "out" / "rollup.json").read_text())
    assert "contract_skips" in rollup["corpus"]
    assert cg.main(["--gate-dir", str(tmp_path / "empty"), "--no-schema"]) == 2


def test_contract_gate_rollup_counts_skipped_contracts():
    import run_v14_default_contract_gate as cg
    rec = {"analyzer": "schematic", "verdict": "PASS", "identity": "o/r/a",
           "contracts": {"schema_validates": ("SKIP", "no jsonschema"), "summary": ("PASS", "")}}
    agg = cg._aggregate([rec])
    assert agg["corpus"]["contract_skips"] == {"schema_validates": 1}


def test_regression_diff_cli_counts_rewrite_downgrades(tmp_path):
    def env(summary, severity):
        return {"analyzer_type": "schematic", "findings": [
            {"rule_id": "PM-002", "severity": severity, "components": ["U1"], "nets": ["VOUT"],
             "pins": [], "summary": summary, "detector": "d"}]}
    (tmp_path / "a.json").write_text(json.dumps(env("Pin U1.3 unconnected", "error")))
    (tmp_path / "b.json").write_text(json.dumps(env("U1 pin 3 is not connected", "warning")))
    r = subprocess.run([sys.executable, str(HARNESS / "regression" / "regression_diff.py"),
                        "--before", str(tmp_path / "a.json"), "--after", str(tmp_path / "b.json"), "--json"],
                       capture_output=True, text=True, timeout=60)
    report = json.loads(r.stdout)
    assert report["rewrites_count"] == 1 and report["severity_downgrades"] == 1
