"""The gate acceptance rule is pure policy, importable without the gate driver."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))

pytestmark = pytest.mark.unit


def test_moved_names_are_reexported_as_same_objects():
    import regression.gate_policy as p
    import regression.run_corpus_gate as g
    for n in ("_compute_pass_criteria", "compute_gate_pass", "apply_modes", "split_bad_skips",
              "ledger_identity", "_both_ok", "_ok", "BAD_SKIP_REASONS", "KIND_CHOICES",
              "CANDIDATE_FAILED_REASON", "WORKER_EXCEPTION_REASON", "BUDGETED_KINDS", "CRITERIA",
              "final_pass"):
        assert getattr(g, n) is getattr(p, n), n


@pytest.mark.parametrize("kind, gp, modes, expected", [
    ("structural", {"pass": True}, {"strict_field_clean": True}, True),
    ("structural", {"pass": True}, {"strict_field_clean": False}, False),
    ("structural", {"pass": False}, {"strict_field_clean": True}, False),
    ("aa", {"pass": True}, {"strict_field_clean": True}, True),
    ("relock", {"pass": False, "census_ok": True, "skips_ok": True, "compared_units": None},
     {"budgeted": {"verdict": "clean"}}, True),        # counts-only: None != 0
    ("relock", {"census_ok": True, "skips_ok": True, "compared_units": 0},
     {"budgeted": {"verdict": "clean"}}, False),
    ("relock", {"census_ok": True, "skips_ok": True}, {"budgeted": {"verdict": "over_budget"}}, False),
    ("relock", {"census_ok": True, "skips_ok": True}, {}, False),
    ("output-changing", {"census_ok": True, "skips_ok": True, "worker_exceptions": 1},
     {"budgeted": {"verdict": "clean"}}, False),
    ("output-changing", {"census_ok": True, "skips_ok": True, "candidate_failures": 1},
     {"budgeted": {"verdict": "clean"}}, False),
    ("output-changing", {"census_ok": False, "skips_ok": True},
     {"budgeted": {"verdict": "clean"}}, False),
    ("output-changing", {"census_ok": True, "skips_ok": False},
     {"budgeted": {"verdict": "clean"}}, False),
])
def test_final_pass(kind, gp, modes, expected):
    from regression.gate_policy import final_pass
    assert final_pass(gp, modes, kind) is expected


def test_apply_modes_stores_final_pass():
    from regression.gate_policy import apply_modes
    report = {"gate_pass": {"pass": True}}
    out = apply_modes(report, {"strict_field_clean": True}, kind="structural")
    assert out["gate_pass"]["pass"] is True and out["gate_pass"]["strict_field_clean"] is True


def test_gate_policy_does_not_import_the_driver():
    import regression.gate_policy as p
    assert "run_corpus_gate" not in Path(p.__file__).read_text()
