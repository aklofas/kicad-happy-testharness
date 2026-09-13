"""KH-377 — EMC PD-001: shunt-only output caps, configurable transient,
band-limited anti-resonance peaks, engineering-unit formatting, honest
count/list.

Five sub-defects verified in the PDN anti-resonance check (emc_rules.py
check_pdn_impedance, rule PD-001) and its cap source (signal_detectors.py
regulator output/input capacitor collection):

(a) The output/input capacitor collectors on a regulator's rail accept ANY
    capacitor whose net touches the rail, including one whose OTHER pin is
    not ground (e.g. a feedforward cap wired rail->FB). That non-decoupling
    cap gets modeled as a decoupler and can manufacture a bogus PD-001
    anti-resonance finding. Fix: the other pin must be ground.
(b) Capacitance values were printed as raw floats (`str(farads*1e6) +
    "uF"`). `_fmt_cap` gives clean engineering-notation strings instead.
(c) The transient-current fallback silently doubled a 0.5A default to 1.0A
    (`pdiss.get('estimated_iout_A', 0.5)` then `min(i_out*2, 5.0)`) even
    with zero power-budget data. Fix: configurable via
    project.pdn_transient_current_a > power_budget-derived > true 0.5A
    default, each labeled with `transient_source`.
(d) Anti-resonance peaks far above any frequency relevant to board-level
    decoupling (> PDN_RELEVANT_FMAX_HZ = 200 MHz) were treated the same as
    in-band peaks, driving a HIGH severity PD-001 finding. Fix: only
    in-band exceeding peaks drive the HIGH finding; out-of-band ones are
    reported separately (still rule_id PD-001, INFO) via
    `out_of_band_peaks`.
(e) The description text showed only the first 3 exceeding peaks with no
    indication of how many more existed. Fix: `peaks_total`/`peaks_shown`
    fields plus a "showing N of M" note in the description when truncated.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from kicad_types import AnalysisContext
from signal_detectors import detect_power_regulators

import emc_rules


# ---------------------------------------------------------------------------
# (a) Shunt-only output/input capacitor collection
# ---------------------------------------------------------------------------

def _comp(ref, value, ctype, lib_id="Device:R"):
    return {"reference": ref, "value": value, "type": ctype,
            "lib_id": lib_id, "footprint": "", "dnp": False, "in_bom": True}


def _reg_ctx(components, pins):
    """pins: {ref: {pin_number: (net_name, pin_name)}} -> real nets/pin_net shapes."""
    nets = {}
    for ref, pinmap in pins.items():
        for num, (net, pname) in pinmap.items():
            nets.setdefault(net, {"pins": []})["pins"].append(
                {"component": ref, "pin_number": num, "pin_name": pname,
                 "pin_type": "passive", "x": 0.0, "y": 0.0})
    pin_net = {}
    for net, info in nets.items():
        for p in info["pins"]:
            pin_net[(p["component"], p["pin_number"])] = (net, info)
    return AnalysisContext(components=components, nets=nets,
                           lib_symbols={}, pin_net=pin_net)


def _ldo_with_feedforward_cap():
    """AMS1117-style LDO: C1 (10uF) shunts +5V to GND (real decoupler);
    C2 (220pF) feedforward caps +5V to FB (not a decoupler -- other pin
    isn't ground)."""
    components = [
        _comp("U1", "AMS1117-3.3", "ic", lib_id="Regulator_Linear:AMS1117-3.3"),
        _comp("C1", "10uF", "capacitor", lib_id="Device:C"),
        _comp("C2", "220pF", "capacitor", lib_id="Device:C"),
    ]
    pins = {
        "U1": {"1": ("+12V", "VIN"), "2": ("GND", "GND"),
               "3": ("+5V", "VOUT"), "4": ("FB", "FB")},
        "C1": {"1": ("+5V", "~"), "2": ("GND", "~")},
        "C2": {"1": ("+5V", "~"), "2": ("FB", "~")},
    }
    return _reg_ctx(components, pins)


def _find_reg(ctx, ref="U1"):
    regs = detect_power_regulators(ctx, voltage_dividers=[])
    matches = [r for r in regs if r.get("ref") == ref]
    assert len(matches) == 1, f"expected exactly one regulator {ref!r}, got {matches}"
    return matches[0]


def test_feedforward_cap_excluded_from_output_capacitors():
    ctx = _ldo_with_feedforward_cap()
    reg = _find_reg(ctx)
    assert reg.get("output_rail") == "+5V"
    refs = [c["ref"] for c in reg.get("output_capacitors", [])]
    assert refs == ["C1"], f"expected only C1 (shunt to GND), got {refs}"


def test_shunt_cap_still_collected_when_alone():
    components = [
        _comp("U1", "AMS1117-3.3", "ic", lib_id="Regulator_Linear:AMS1117-3.3"),
        _comp("C1", "10uF", "capacitor", lib_id="Device:C"),
    ]
    pins = {
        "U1": {"1": ("+12V", "VIN"), "2": ("GND", "GND"),
               "3": ("+5V", "VOUT"), "4": ("FB", "FB")},
        "C1": {"1": ("+5V", "~"), "2": ("GND", "~")},
    }
    ctx = _reg_ctx(components, pins)
    reg = _find_reg(ctx)
    refs = [c["ref"] for c in reg.get("output_capacitors", [])]
    assert refs == ["C1"]


def test_feedforward_cap_excluded_from_input_capacitors():
    """Same guard applies to the input-rail collector."""
    components = [
        _comp("U1", "AMS1117-3.3", "ic", lib_id="Regulator_Linear:AMS1117-3.3"),
        _comp("C1", "10uF", "capacitor", lib_id="Device:C"),   # +12V -> GND: real
        _comp("C2", "220pF", "capacitor", lib_id="Device:C"),  # +12V -> FB: not a decoupler
    ]
    pins = {
        "U1": {"1": ("+12V", "VIN"), "2": ("GND", "GND"),
               "3": ("+5V", "VOUT"), "4": ("FB", "FB")},
        "C1": {"1": ("+12V", "~"), "2": ("GND", "~")},
        "C2": {"1": ("+12V", "~"), "2": ("FB", "~")},
    }
    ctx = _reg_ctx(components, pins)
    reg = _find_reg(ctx)
    assert reg.get("input_rail") == "+12V"
    refs = [c["ref"] for c in reg.get("input_capacitors", [])]
    assert refs == ["C1"], f"expected only C1 (shunt to GND), got {refs}"


# ---------------------------------------------------------------------------
# (b) _fmt_cap engineering-unit formatting
# ---------------------------------------------------------------------------

def test_fmt_cap_220pf():
    assert emc_rules._fmt_cap(220e-12) == "220pF"


def test_fmt_cap_100nf():
    assert emc_rules._fmt_cap(1e-7) == "100nF"


def test_fmt_cap_220nf():
    assert emc_rules._fmt_cap(2.2e-7) == "220nF"


def test_fmt_cap_10uf():
    assert emc_rules._fmt_cap(1e-5) == "10µF"


# ---------------------------------------------------------------------------
# (c)/(d)/(e) check_pdn_impedance: transient current, band limiting, counts
# ---------------------------------------------------------------------------

def _reg_finding(output_rail="+5V", vout=5.0, power_dissipation=None):
    reg = {
        "detector": "detect_power_regulators",
        "ref": "U1",
        "value": "TPS54331",
        "estimated_vout": vout,
        "output_rail": output_rail,
        "output_capacitors": [
            {"ref": "C1", "value": "10uF", "farads": 1e-5, "package": "0805"},
            {"ref": "C2", "value": "100nF", "farads": 1e-7, "package": "0402"},
        ],
    }
    if power_dissipation is not None:
        reg["power_dissipation"] = power_dissipation
    return reg


def _schematic_with_reg(**reg_kwargs):
    return {"findings": [_reg_finding(**reg_kwargs)]}


def _one_in_band_peak(freq_mhz=1.0, impedance_ohm=10.0):
    return [{"freq_hz": freq_mhz * 1e6, "freq_mhz": freq_mhz,
              "impedance_ohm": impedance_ohm, "exceeds_target": True}]


def _pd001_findings(findings):
    pd001 = [f for f in findings if f.get("rule_id") == "PD-001"]
    return pd001


def test_transient_current_from_config():
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: _one_in_band_peak()
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None,
                                           pdn_transient_a=0.2)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        assert pd001[0]["transient_a"] == 0.2
        assert pd001[0]["transient_source"] == "config"
    finally:
        er.find_anti_resonances = orig


def test_transient_current_from_power_budget():
    def fake_peaks(sweep, z_target=None):
        return _one_in_band_peak()
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = fake_peaks
    try:
        schematic = _schematic_with_reg(
            power_dissipation={"estimated_iout_A": 0.3})
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        assert pd001[0]["transient_a"] == 0.6
        assert pd001[0]["transient_source"] == "power_budget"
    finally:
        er.find_anti_resonances = orig


def test_transient_current_default_is_not_doubled():
    """Regression: with neither config nor power_budget data, the fallback
    must be the true 0.5A default, not the pre-fix doubled 1.0A."""
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: _one_in_band_peak()
    try:
        schematic = _schematic_with_reg()  # no power_dissipation key at all
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        assert pd001[0]["transient_a"] == 0.5
        assert pd001[0]["transient_source"] == "default"
    finally:
        er.find_anti_resonances = orig


def test_out_of_band_peak_does_not_trigger_high():
    """A single exceeding peak at 316 MHz (above the 200 MHz PDN-relevance
    ceiling) must not produce a HIGH PD-001; it shows up as an INFO finding
    with out_of_band_peaks."""
    out_of_band = [{"freq_hz": 316e6, "freq_mhz": 316.0,
                     "impedance_ohm": 3.5, "exceeds_target": True}]
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: out_of_band
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        finding = pd001[0]
        assert finding["severity"] != "error", "316 MHz peak must not be HIGH"
        assert finding["severity"] == "info"
        oob = finding.get("out_of_band_peaks")
        assert oob, "expected out_of_band_peaks to list the 316 MHz peak"
        assert oob[0]["freq_mhz"] == 316.0
        assert oob[0]["impedance_ohm"] == 3.5
    finally:
        er.find_anti_resonances = orig


def test_in_band_peak_still_triggers_high_and_carries_out_of_band():
    """An in-band exceeding peak drives the HIGH finding; an out-of-band
    exceeding peak alongside it is reported via out_of_band_peaks on the
    same finding, not silently dropped or conflated."""
    mixed = [
        {"freq_hz": 1e6, "freq_mhz": 1.0, "impedance_ohm": 5.0, "exceeds_target": True},
        {"freq_hz": 316e6, "freq_mhz": 316.0, "impedance_ohm": 3.5, "exceeds_target": True},
    ]
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: mixed
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        finding = pd001[0]
        assert finding["severity"] == "error", "in-band peak must still drive HIGH"
        assert finding["peaks_total"] == 1
        oob = finding.get("out_of_band_peaks")
        assert oob and oob[0]["freq_mhz"] == 316.0
    finally:
        er.find_anti_resonances = orig


def test_peaks_total_and_shown_with_truncation():
    five_peaks = [
        {"freq_hz": f * 1e6, "freq_mhz": float(f), "impedance_ohm": 2.0,
         "exceeds_target": True}
        for f in (1, 2, 3, 4, 5)
    ]
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: five_peaks
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        assert len(pd001) == 1
        finding = pd001[0]
        assert finding["peaks_total"] == 5
        assert finding["peaks_shown"] == 3
        assert "showing 3 of 5" in finding["description"]
    finally:
        er.find_anti_resonances = orig


def test_no_truncation_note_when_not_truncated():
    two_peaks = [
        {"freq_hz": 1e6, "freq_mhz": 1.0, "impedance_ohm": 2.0, "exceeds_target": True},
        {"freq_hz": 2e6, "freq_mhz": 2.0, "impedance_ohm": 2.0, "exceeds_target": True},
    ]
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: two_peaks
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        pd001 = _pd001_findings(findings)
        finding = pd001[0]
        assert finding["peaks_total"] == 2
        assert finding["peaks_shown"] == 2
        assert "showing" not in finding["description"]
    finally:
        er.find_anti_resonances = orig


def test_description_uses_fmt_cap_not_raw_float():
    import emc_rules as er
    orig = er.find_anti_resonances
    er.find_anti_resonances = lambda sweep, z_target=None: _one_in_band_peak()
    try:
        schematic = _schematic_with_reg()
        findings = er.check_pdn_impedance(None, schematic, spice_backend=None)
        finding = _pd001_findings(findings)[0]
        assert "10µF" in finding["description"]
        assert "100nF" in finding["description"]
        # Raw float artifact from the old `str(farads*1e6) + "uF"` formatting
        assert "1e-05" not in finding["description"]
        assert "9.999999999999999" not in finding["description"]
    finally:
        er.find_anti_resonances = orig


if __name__ == "__main__":
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
