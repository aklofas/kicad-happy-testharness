"""KH-388: VD-DET feedback-divider findings must not be duplicated at flatten.

`detect_voltage_dividers` (signal_detectors.py) deliberately appends the SAME
divider dict object to both `feedback_networks` and `voltage_dividers` when
the divider's midpoint connects to an IC FB pin (see the 8c36212 cascade
warning at signal_detectors.py:324-346 — that double-emission must stay, it
feeds `detect_rc_filters`'s exclusion set among other consumers). But
`analyze_schematic.py`'s flatten step, which merges every `signal_analysis`
list into the top-level `findings[]`, must not let the same object end up as
two duplicate entries in the output.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixtures._build_sch import Schematic, pin1, pin2, ic_pin_pos

HARNESS_DIR = Path(__file__).resolve().parent.parent


def run_analyzer(sch):
    """Build schematic, run analyzer, return parsed JSON or None."""
    kh_dir = os.environ.get("KICAD_HAPPY_DIR",
                str(HARNESS_DIR.parent / "kicad-happy"))
    script = Path(kh_dir) / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
    if not script.exists():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        sch_path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        out_path = str(Path(tmp) / "output.json")
        result = subprocess.run(
            [sys.executable, str(script), sch_path, "--output", out_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise AssertionError(f"Analyzer failed: {result.stderr[:300]}")
        return json.loads(Path(out_path).read_text(encoding="utf-8"))


def _feedback_divider_schematic():
    """LM317 adjustable regulator with FB divider — crib of test_kh238.

    R1/R2 midpoint wires to the FB pin, so detect_voltage_dividers appends
    the same divider dict to both feedback_networks and voltage_dividers.
    """
    REG_PINS = [
        ("VIN",  "1", -5.08, 0, "input"),
        ("GND",  "2", 0, 5.08, "power_in"),
        ("VOUT", "3", 5.08, -2.54, "output"),
        ("FB",   "4", 5.08, 2.54, "input"),
    ]
    cx, cy = 50, 50
    Rt_cx, Rt_cy = 70, 47  # R_top center
    Rb_cx, Rb_cy = 70, 60  # R_bottom center

    return (
        Schematic()
        .ic("U1", "LM317", "Regulator_Linear:LM317_SOT-223", REG_PINS, at=(cx, cy))
        .resistor("R1", "240", at=(Rt_cx, Rt_cy))
        .resistor("R2", "390", at=(Rb_cx, Rb_cy))
        .power("+12V", at=(35, cy))
        .power("GND", at=(cx, 70))
        .power("GND", at=(Rb_cx, 75))
        .wire((35, cy), ic_pin_pos(cx, cy, "VIN", REG_PINS))
        .wire(ic_pin_pos(cx, cy, "GND", REG_PINS), (cx, 70))
        .wire(ic_pin_pos(cx, cy, "VOUT", REG_PINS), (Rt_cx, cy - 2.54))
        .wire((Rt_cx, cy - 2.54), pin1(Rt_cx, Rt_cy))
        .wire(ic_pin_pos(cx, cy, "FB", REG_PINS), (Rt_cx, cy + 2.54))
        .wire(pin2(Rt_cx, Rt_cy), (Rt_cx, cy + 2.54))
        .wire((Rt_cx, cy + 2.54), pin1(Rb_cx, Rb_cy))
        .wire(pin2(Rb_cx, Rb_cy), (Rb_cx, 75))
    )


def test_kh238_fixture_still_produces_feedback_divider():
    """Sanity: the crib still triggers the double-emission path (pre-req)."""
    data = run_analyzer(_feedback_divider_schematic())
    if data is None:
        return
    regs = [f for f in data.get("findings", []) if f.get("detector") == "detect_power_regulators"]
    u1 = [r for r in regs if r.get("ref") == "U1"]
    assert len(u1) >= 1, "U1 not found in power_regulators"
    assert u1[0].get("feedback_divider") is not None, \
        "fixture no longer triggers the FB divider path this test depends on"


def test_kh388_no_duplicate_finding_ids():
    """KH-388: flattened findings[] must not contain two entries with the
    same finding_id."""
    data = run_analyzer(_feedback_divider_schematic())
    if data is None:
        return
    findings = data.get("findings", [])
    ids = [f.get("finding_id") for f in findings if f.get("finding_id")]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"KH-388 regression: duplicate finding_id(s) in findings[]: {dupes}"


def test_kh388_no_duplicate_vddet_entries():
    """KH-388: no two VD-DET entries share (detector, tuple(components)) —
    the aliased feedback-divider dict must not appear twice in findings[]."""
    data = run_analyzer(_feedback_divider_schematic())
    if data is None:
        return
    vd_findings = [f for f in data.get("findings", [])
                   if f.get("rule_id") == "VD-DET" or f.get("detector") == "detect_voltage_dividers"]
    assert len(vd_findings) >= 1, "expected at least one VD-DET finding from the FB divider"
    keys = [(f.get("detector"), tuple(f.get("components") or [])) for f in vd_findings]
    dupes = {k for k in keys if keys.count(k) > 1}
    assert not dupes, \
        f"KH-388 regression: duplicate VD-DET (detector, components) key(s): {dupes}"
