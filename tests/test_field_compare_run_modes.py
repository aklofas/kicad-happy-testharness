import json
from pathlib import Path

import pytest

from regression.field_compare import run_modes

pytestmark = pytest.mark.unit

RUN_A, RUN_B = "20260913T072438Z-aefff9", "20260913T072438Z-e639ad"
FIX = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "h0" / "plan3" / "budgets"


def _env(run_id, sev="warning"):
    return {"analyzer_type": "schematic", "inputs": {"run_id": run_id, "source_files": [], "source_hashes": {}},
            "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": run_id},
            "findings": [{"rule_id": "RS-001", "detector": "audit_rail_sources", "severity": sev}]}


def _gate(root, slots=("baseline", "candidate"), sev_b="warning"):
    for slot, run, sev in ((slots[0], RUN_A, "warning"), (slots[1], RUN_B, sev_b)):
        p = root / slot / "schematic" / "o" / "r" / "k" / "snap.json"
        p.parent.mkdir(parents=True); p.write_text(json.dumps(_env(run, sev)))


def test_run_modes_raw_and_strict_on_baseline_candidate(tmp_path):
    _gate(tmp_path)
    m = run_modes(tmp_path)
    assert m["raw"]["verdict"] == "deltas" and m["strict"]["verdict"] == "clean"
    assert m["budgeted"] == {"verdict": "n/a"} and m["strict_field_clean"] is True
    assert (tmp_path / "field_report_raw.json").exists() and (tmp_path / "field_report_strict.json").exists()
    assert m["policy"] == "volatile-leaves-v1"


def test_run_modes_falls_back_to_historical_slot_names(tmp_path):
    _gate(tmp_path, slots=("v131", "v14"))
    m = run_modes(tmp_path)
    assert m["strict"]["verdict"] == "clean"


def test_run_modes_budgeted_drives_strict_field_clean(tmp_path):
    _gate(tmp_path, sev_b="info")
    m = run_modes(tmp_path)
    assert m["strict"]["verdict"] == "deltas" and m["strict_field_clean"] is False
    m = run_modes(tmp_path, budget_path=FIX / "rs001_only.json")
    assert m["budgeted"]["verdict"] == "clean" and m["budgeted"]["budget_id"] == "fixture-rs001-severity"
    assert m["budgeted"]["claimed_counts"] == {"rs001-severity-down": 1}
    assert m["strict_field_clean"] is True
    assert (tmp_path / "field_report_budgeted.json").exists()


def test_run_modes_requires_two_slots(tmp_path):
    (tmp_path / "baseline").mkdir()
    with pytest.raises(FileNotFoundError, match="candidate"):
        run_modes(tmp_path)
