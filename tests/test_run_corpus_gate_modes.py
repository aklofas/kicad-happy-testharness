"""run_corpus_gate.main() runs the three comparator modes after phase B and ANDs
strict_field_clean into gate_pass (spec 2.4 / 3.5)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import run_corpus_gate as gate  # noqa: E402

pytestmark = pytest.mark.unit


def test_apply_modes_ands_strict_field_clean():
    report = {"gate_pass": {"pass": True, "strict_clean": True, "census_ok": True, "skips_ok": True},
              "modes": {"findings_summary": "strict_clean"}}
    modes = {"raw": {"verdict": "fail"}, "strict": {"verdict": "deltas"},
             "budgeted": {"verdict": "n/a"}, "strict_field_clean": False}
    out = gate.apply_modes(report, modes)
    assert out["modes"]["strict"]["verdict"] == "deltas"
    assert out["modes"]["findings_summary"] == "strict_clean"
    assert out["gate_pass"]["strict_field_clean"] is False
    assert out["gate_pass"]["pass"] is False


def test_apply_modes_keeps_pass_when_strict_clean():
    report = {"gate_pass": {"pass": True}, "modes": {"findings_summary": "strict_clean"}}
    modes = {"raw": {"verdict": "fail"}, "strict": {"verdict": "clean"},
             "budgeted": {"verdict": "n/a"}, "strict_field_clean": True}
    out = gate.apply_modes(report, modes)
    assert out["gate_pass"]["pass"] is True and out["gate_pass"]["strict_field_clean"] is True


def test_main_accepts_budget_flag(tmp_path):
    ap = gate.build_arg_parser()
    ns = ap.parse_args(["--baseline-dir", "a", "--candidate-dir", "b", "--gate-dir", str(tmp_path),
                        "--repo", "x", "--budget", "regression/budgets/example.json"])
    assert ns.budget == "regression/budgets/example.json"
