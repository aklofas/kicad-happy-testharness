"""The schema inventory covers PCB findings[] and thermal outputs (code A4-F3): the relock
`diff` step was blind to field changes there."""
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS / "validate"))
sys.path.insert(0, str(HARNESS))
import validate_schema as vs  # noqa: E402

pytestmark = pytest.mark.unit


def test_pcb_findings_and_thermal_are_inventoried(tmp_path, monkeypatch):
    out = tmp_path / "outputs"
    for kind, doc in (("pcb", {"findings": [{"detector": "analyze_dfm", "rule_id": "DF-1", "x": 1}]}),
                      ("thermal", {"findings": [{"detector": "analyze_thermal_pads", "tj": 80}]})):
        d = out / kind / "o" / "r"
        d.mkdir(parents=True)
        (d / "a.json").write_text(json.dumps(doc))
    monkeypatch.setattr(vs, "OUTPUTS_DIR", out)
    inv = vs.build_inventory(["o/r"])
    assert inv["pcb"]["findings.analyze_dfm"] == {"detector": 1, "rule_id": 1, "x": 1}
    assert inv["thermal"]["analyze_thermal_pads"] == {"detector": 1, "tj": 1}
    saved = json.loads(json.dumps(inv))
    del saved["thermal"]["analyze_thermal_pads"]["tj"]
    changes = vs.diff_inventories(saved, inv)
    assert [(c["category"], c["field"], c["change_type"]) for c in changes] == [("thermal", "tj", "added")]
