"""KH-198 regression: two distinct capacitors that share a reference on one LC net count once.

The corpus anchor (Caffeinated-AFTONSPARV) dissolved in the v2.0 mirror fix and no corpus board
has the shape any more (2026-11-06 scan of 36,463 outputs: no LC-DET net with a capacitor ref on
two or more of its pins), so the lock lives on this fixture instead (TH-047)."""
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, pin1, pin2  # noqa: E402
from tests.product_root import PRODUCT_ROOT  # noqa: E402

pytestmark = pytest.mark.unit


def _lc_with_colliding_caps():
    # L1 from IN to LX; two capacitors, both referenced C5 (a pasted-in sub-project), LX to GND
    return (Schematic()
            .inductor("L1", "10uH", at=(50, 50))
            .capacitor("C5", "10uF", at=(60, 62))
            .capacitor("C5", "10uF", at=(70, 62))
            .label("IN", at=pin1(50, 50))
            .power("GND", at=(60, 72)).power("GND", at=(70, 72))
            .wire(pin2(50, 50), (50, 56)).wire((50, 56), (60, 56)).wire((60, 56), (70, 56))
            .wire((60, 56), pin1(60, 62)).wire((70, 56), pin1(70, 62))
            .wire(pin2(60, 62), (60, 72)).wire(pin2(70, 62), (70, 72)))


def test_colliding_capacitor_ref_counts_once_in_the_lc_group():
    script = Path(PRODUCT_ROOT) / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
    with tempfile.TemporaryDirectory() as tmp:
        sch = _lc_with_colliding_caps().write(str(Path(tmp) / "lc.kicad_sch"))
        out = Path(tmp) / "out.json"
        r = subprocess.run([sys.executable, str(script), sch, "--output", str(out)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-500:]
        d = json.loads(out.read_text(encoding="utf-8"))
    lc = [f for f in d["findings"] if f.get("rule_id") == "LC-DET"]
    assert len(lc) == 1, [f.get("summary") for f in lc]
    assert sorted(lc[0]["components"]) == ["C5", "L1"]
    # one 10 uF capacitor, not the two C5 instances (or their pins) summed in parallel
    assert lc[0]["resonant_hz"] == pytest.approx(1 / (2 * math.pi * math.sqrt(10e-6 * 10e-6)), rel=0.01)
