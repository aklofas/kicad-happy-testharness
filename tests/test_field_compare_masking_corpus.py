"""volatile-leaves-v1 on a real corpus envelope (reads results/; corpus tier, not unit)."""
import json
from pathlib import Path

import pytest

from regression.field_compare import compare_strict, load_policy

pytestmark = pytest.mark.corpus

RUN_B = "20260913T072438Z-e639ad"
ROOT = Path(__file__).resolve().parent.parent


def test_real_policy_on_real_envelope(tmp_path):
    src = ROOT / "results/v22x_pr44_gate/v14/schematic/JustinHsu845/PiEDB-Y15/USBTTL_USBTTL.kicad_sch/snap.json"
    if not src.exists():
        pytest.skip("corpus snap not present")
    a = json.loads(src.read_text())
    (tmp_path / "snap.json").write_text(json.dumps(a))      # tmp copy, source untouched
    b = json.loads((tmp_path / "snap.json").read_text())
    b["inputs"]["run_id"] = RUN_B
    b["capability_mode_ref"]["run_id"] = RUN_B
    pol = load_policy("volatile-leaves-v1")
    rp = (str(ROOT), str(ROOT))
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, unit="schematic/x", analyzer="schematic")
    assert deltas == [] and viol == []
    b["capability_mode_ref"]["run_id"] = "20260101T000000Z-000000"
    deltas, viol = compare_strict(a, b, pol, root_prefixes=rp, unit="schematic/x", analyzer="schematic")
    assert any("equals /inputs/run_id" in v and "side b" in v for v in viol)
