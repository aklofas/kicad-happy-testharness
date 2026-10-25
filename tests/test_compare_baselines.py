"""compare.py reports every changed manifest key and buckets unparseable outputs as errors
(code A2-F2)."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(HARNESS / "regression"))
import compare  # noqa: E402

pytestmark = pytest.mark.unit


def test_compare_reports_every_key_kind():
    base = {"total_findings": 3, "by_severity": {"error": 1, "warning": 2},
            "by_type": {"pdn": 1}, "target_standard": "fcc"}
    curr = {"total_findings": 3, "by_severity": {"error": 2, "warning": 1},
            "by_type": {"pdn": 1}, "target_standard": "cispr32"}
    got = compare._compare_manifest_entries(base, curr)
    assert set(got) == {"by_severity", "target_standard"}
    assert got["by_severity"]["error"] == {"baseline": 1, "current": 2}
    assert got["target_standard"] == {"baseline": "fcc", "current": "cispr32"}


def test_unparseable_output_is_an_error_not_compared(tmp_path, monkeypatch):
    data, outputs = tmp_path / "data", tmp_path / "outputs"
    (data / "o" / "r" / "p" / "baselines").mkdir(parents=True)
    (data / "o" / "r" / "p" / "baselines" / "emc.json").write_text(json.dumps({"x.json": {"total_findings": 1}}))
    (outputs / "emc" / "o" / "r").mkdir(parents=True)
    (outputs / "emc" / "o" / "r" / "x.json").write_text("{torn")
    monkeypatch.setattr(compare, "DATA_DIR", data)
    monkeypatch.setattr(compare, "OUTPUTS_DIR", outputs)
    r = compare.compare_project("o/r", "p", ".", "emc")
    assert r["files_compared"] == 0 and r["files_with_errors"] == ["x.json"]
