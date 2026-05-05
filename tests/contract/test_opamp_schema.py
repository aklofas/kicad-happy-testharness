"""Contract tests for opamp.schema.json (Phase 3b Stage 3)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills/datasheets/schemas"
SCHEMA_PATH = SCHEMA_DIR / "opamp.schema.json"


def _registry() -> Registry:
    registry = Registry()
    for p in SCHEMA_DIR.glob("*.schema.json"):
        s = json.loads(p.read_text())
        if s.get("$id"):
            registry = registry.with_resource(s["$id"], Resource.from_contents(s))
    return registry


def _validator():
    schema = json.loads(SCHEMA_PATH.read_text())
    return Draft202012Validator(schema, registry=_registry())


def test_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(json.loads(SCHEMA_PATH.read_text()))


def test_schema_has_required_metadata():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["$id"].endswith("/opamp.schema.json")
    assert schema["title"] == "OpampExtension"
    assert schema["x-schema-version"] == "1.0"
    assert schema["additionalProperties"] is False


def test_minimal_validates():
    minimal = {"opamp_topology": "general_purpose", "channels": 1}
    assert list(_validator().iter_errors(minimal)) == []


def test_topology_enum_rejects_unknown():
    bad = {"opamp_topology": "not-a-topology", "channels": 1}
    assert list(_validator().iter_errors(bad))


def test_full_lm358_validates():
    """BJT general-purpose dual single-supply; values from Fairchild/ON Semi LM358 datasheet."""
    ev_hi = {"page": 3, "section": "Electrical Characteristics", "confidence": "high", "method": "table"}
    ev_curve = {"page": 7, "section": "Typical Performance Characteristics", "confidence": "medium", "method": "curve"}
    full = {
        "opamp_topology": "general_purpose",
        "channels": 2,
        "vsupply_range": [
            {"min": 3, "typ": None, "max": 32, "unit": "V",
             "condition": "Single supply (VCC to GND); split supply ±1.5V to ±16V also supported",
             "notes": "LM358/LM358A: 3V–32V single, ±1.5V–±16V split. From Absolute Maximum Ratings.",
             "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "high", "method": "table"}}
        ],
        "vsupply_split_capable": True,
        "iq_per_amp": [
            {"min": None, "typ": 2.5e-4, "max": 6e-4, "unit": "A",
             "condition": "RL=inf, VCC=5V; per-amp (ICC total / 2 channels)",
             "notes": "Datasheet ICC typ=0.5mA total for dual; per-amp = 0.25mA typ. Max ICC=1.2mA total → 0.6mA per-amp.",
             "evidence": {"page": 3, "section": "Electrical Characteristics", "confidence": "high", "method": "table"}}
        ],
        "gbw": [
            {"min": None, "typ": 1e6, "max": None, "unit": "Hz",
             "condition": "Unity-gain crossover from open-loop frequency response graph",
             "notes": "GBW not tabulated; read from Figure 3 Open Loop Frequency Response (~1MHz at 0dB crossover).",
             "evidence": {"page": 7, "section": "Typical Performance Characteristics", "confidence": "medium", "method": "curve"}}
        ],
        "slew_rate": None,
        "vos": [
            {"min": None, "typ": 2.9e-3, "max": 7e-3, "unit": "V",
             "condition": "VCM=0V to VCC-1.5V, VO(P)=1.4V, RS=0Ω, TA=25°C",
             "notes": None,
             "evidence": ev_hi}
        ],
        "ib": [
            {"min": None, "typ": 4.5e-8, "max": 2.5e-7, "unit": "A",
             "condition": "TA=25°C",
             "notes": "Datasheet IBIAS typ=45nA, max=250nA.",
             "evidence": ev_hi}
        ],
        "cmrr": [
            {"min": 65, "typ": 65, "max": None, "unit": "dB",
             "condition": "TA=25°C",
             "notes": None,
             "evidence": ev_hi}
        ],
        "psrr": [
            {"min": 65, "typ": 100, "max": None, "unit": "dB",
             "condition": "TA=25°C",
             "notes": None,
             "evidence": ev_hi}
        ],
        "vout_swing_high": [
            {"min": None, "typ": None, "max": 2.0, "unit": "V",
             "condition": "VCC=30V, RL=10kΩ; VOH=27-28V → headroom ~2-3V from V+",
             "notes": "Output swing high is not rail-to-rail. VOH=28V at VCC=30V → ~2V headroom.",
             "evidence": ev_hi}
        ],
        "vout_swing_low": [
            {"min": None, "typ": 5e-3, "max": 20e-3, "unit": "V",
             "condition": "VCC=5V, RL=10kΩ; VO(L) typ=5mV, max=20mV above GND",
             "notes": None,
             "evidence": ev_hi}
        ],
        "output_drive_current": [
            {"min": 20e-3, "typ": 30e-3, "max": None, "unit": "A",
             "condition": "VI(+)=1V, VI(-)=0V, VCC=15V, VO(P)=2V; source current",
             "notes": "ISOURCE min=20mA, typ=30mA. Sink current typ=15mA at same conditions.",
             "evidence": ev_hi}
        ],
        "unity_gain_stable": True,
        "shutdown_pin": None,
        "thermal_resistance": {
            "rtheta_ja": [
                {"min": None, "typ": None, "max": 150, "unit": "°C/W",
                 "condition": "SOIC-8 package, free air",
                 "notes": "Typical value for SOIC-8; not explicitly tabulated in this datasheet version.",
                 "evidence": {"page": 2, "section": "Absolute Maximum Ratings", "confidence": "medium", "method": "prose"}}
            ],
            "rtheta_jc": None,
            "rtheta_jl": None
        },
        "package": {
            "code": "SOIC-8",
            "pin_count": 8,
            "pitch_mm": 1.27,
            "body_mm": {"length": 4.9, "width": 3.9, "height": 1.5},
            "thermal_pad": False,
            "evidence": {"page": 8, "section": "Package Dimensions", "confidence": "medium", "method": "table"}
        }
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_full_mcp6004_validates():
    """CMOS rail-to-rail I/O quad; values from Microchip MCP6001/2/4 datasheet DS21733J."""
    ev_hi = {"page": 3, "section": "DC Electrical Specifications", "confidence": "high", "method": "table"}
    full = {
        "opamp_topology": "rail_to_rail_io",
        "channels": 4,
        "vsupply_range": [
            {"min": 1.8, "typ": None, "max": 6.0, "unit": "V",
             "condition": "VDD − VSS; single supply only",
             "notes": None,
             "evidence": ev_hi}
        ],
        "vsupply_split_capable": False,
        "iq_per_amp": [
            {"min": 50e-6, "typ": 100e-6, "max": 170e-6, "unit": "A",
             "condition": "IO=0, VDD=5.5V, VCM=5V; Quiescent Current per Amplifier",
             "notes": "Datasheet IQ per amplifier: typ=100µA, max=170µA at VDD=5.5V.",
             "evidence": ev_hi}
        ],
        "gbw": [
            {"min": None, "typ": 1e6, "max": None, "unit": "Hz",
             "condition": "Gain Bandwidth Product; features state 1MHz typical",
             "notes": None,
             "evidence": {"page": 1, "section": "Features", "confidence": "high", "method": "prose"}}
        ],
        "slew_rate": [
            {"min": None, "typ": 6e5, "max": None, "unit": "V/s",
             "condition": "0.6V/µs typical from features description; stored as 6e5 V/s",
             "notes": "Not tabulated in DC specs table of this datasheet; value from application section.",
             "evidence": {"page": 1, "section": "Features", "confidence": "medium", "method": "prose"}}
        ],
        "vos": [
            {"min": -4.5e-3, "typ": None, "max": 4.5e-3, "unit": "V",
             "condition": "VCM=VSS (Note 1), TA=25°C",
             "notes": "Datasheet VOS min=-4.5mV, max=+4.5mV.",
             "evidence": ev_hi}
        ],
        "ib": [
            {"min": None, "typ": 1e-12, "max": None, "unit": "A",
             "condition": "TA=25°C; Input Bias Current typ=±1.0pA",
             "notes": "CMOS input; IB typ=1pA (±1.0pA from table).",
             "evidence": ev_hi}
        ],
        "cmrr": [
            {"min": 60, "typ": 76, "max": None, "unit": "dB",
             "condition": "VCM=-0.3V to 5.3V, VDD=5V",
             "notes": None,
             "evidence": ev_hi}
        ],
        "psrr": [
            {"min": None, "typ": 86, "max": None, "unit": "dB",
             "condition": "VCM=VSS",
             "notes": None,
             "evidence": ev_hi}
        ],
        "vout_swing_high": [
            {"min": None, "typ": 25e-3, "max": None, "unit": "V",
             "condition": "VDD=5.5V, 0.5V input overdrive; headroom from V+ (VOH=VDD−25mV typ)",
             "notes": "Rail-to-rail output: VOH swings to within 25mV of VDD.",
             "evidence": ev_hi}
        ],
        "vout_swing_low": [
            {"min": None, "typ": 25e-3, "max": None, "unit": "V",
             "condition": "VDD=5.5V, 0.5V input overdrive; headroom from V− (VOL=VSS+25mV typ)",
             "notes": "Rail-to-rail output: VOL swings to within 25mV of VSS.",
             "evidence": ev_hi}
        ],
        "output_drive_current": [
            {"min": None, "typ": 6e-3, "max": None, "unit": "A",
             "condition": "VDD=1.8V; ISC=±6mA typ",
             "notes": "Output short circuit current ±6mA at VDD=1.8V, ±23mA at VDD=5.5V.",
             "evidence": ev_hi},
            {"min": None, "typ": 23e-3, "max": None, "unit": "A",
             "condition": "VDD=5.5V; ISC=±23mA typ",
             "notes": None,
             "evidence": ev_hi}
        ],
        "unity_gain_stable": True,
        "shutdown_pin": None,
        "thermal_resistance": {
            "rtheta_ja": [
                {"min": None, "typ": 80, "max": None, "unit": "°C/W",
                 "condition": "SOIC-14 package; estimated typical",
                 "notes": "Not explicitly tabulated for MCP6004 in this datasheet reading. Typical for SOIC-14 ~70-100°C/W.",
                 "evidence": {"page": 1, "section": "Features", "confidence": "low", "method": "derived"}}
            ],
            "rtheta_jc": None,
            "rtheta_jl": None
        },
        "package": {
            "code": "SOIC-14",
            "pin_count": 14,
            "pitch_mm": 1.27,
            "body_mm": {"length": 8.65, "width": 3.9, "height": 1.58},
            "thermal_pad": False,
            "evidence": {"page": 1, "section": "Package Types", "confidence": "high", "method": "prose"}
        }
    }
    errors = list(_validator().iter_errors(full))
    assert errors == [], "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


def test_additional_properties_rejected():
    bad = {"opamp_topology": "general_purpose", "channels": 1, "made_up_field": 42}
    assert list(_validator().iter_errors(bad))
