"""Contract tests for skills/datasheets/datasheet_types/ dataclasses.

Verifies that:
1. Dataclasses load from dict inputs matching the Track 2.1 JSON schemas.
2. to_dict() emits dicts that re-validate against the Track 2.1 schemas.
3. Round-trip (dict → dataclass → dict) preserves content.

Source of truth is the hand-written JSON schemas under
skills/datasheets/schemas/. The Python dataclasses are ergonomic
typed access on top; they do not re-derive the schemas.
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas"
FIXTURE_DIR = SCHEMA_DIR / "fixtures"  # Used by fixture round-trip tests in Tasks 3 and 5.

# Make skills/datasheets/datasheet_types/ importable as a top-level 'datasheet_types' package.
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _build_registry() -> Registry:
    registry = Registry()
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        schema = _load_json(schema_path)
        uri = schema.get("$id")
        if uri:
            registry = registry.with_resource(uri, Resource.from_contents(schema))
    return registry


# ---------------------------------------------------------------------------
# SpecValue + Evidence round-trip
# ---------------------------------------------------------------------------

def test_spec_value_from_dict_roundtrip() -> None:
    from datasheet_types.spec_value import SpecValue
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "min": 1.18, "typ": 1.23, "max": 1.28,
        "unit": "V",
        "condition": None, "notes": None,
        "evidence": {"page": 5, "section": "Electrical Characteristics",
                     "confidence": "high", "method": "table"},
    }
    obj = from_dict(SpecValue, raw)
    assert obj.min == 1.18
    assert obj.typ == 1.23
    assert obj.max == 1.28
    assert obj.unit == "V"
    assert obj.condition is None
    assert obj.evidence.page == 5
    assert obj.evidence.confidence == "high"
    # to_dict round-trips without drift.
    assert to_dict(obj) == raw


def test_spec_value_to_dict_validates_against_schema() -> None:
    from datasheet_types.spec_value import SpecValue
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "min": None, "typ": 50, "max": None,
        "unit": "°C/W",
        "condition": "TO-263, 1oz Cu, 2in² pour",
        "notes": "θJA",
        "evidence": {"page": 3, "section": "Thermal Information",
                     "confidence": "high", "method": "table"},
    }
    obj = from_dict(SpecValue, raw)
    emitted = to_dict(obj)

    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    errors = list(validator.iter_errors(emitted))
    assert errors == [], "\n".join(str(e.message) for e in errors)


def test_spec_value_required_fields_enforced() -> None:
    """Missing 'unit' or 'evidence' should raise, matching schema required[]."""
    from datasheet_types.spec_value import SpecValue
    from datasheet_types.codec import from_dict

    # Missing unit
    with pytest.raises((KeyError, TypeError)):
        from_dict(SpecValue, {"evidence": {"page": 1, "confidence": "high", "method": "table"}})
    # Missing evidence
    with pytest.raises((KeyError, TypeError)):
        from_dict(SpecValue, {"unit": "V"})


def test_evidence_from_dict_roundtrip() -> None:
    from datasheet_types.spec_value import Evidence
    from datasheet_types.codec import from_dict, to_dict

    raw = {"page": 14, "section": "External Components",
           "confidence": "medium", "method": "prose"}
    obj = from_dict(Evidence, raw)
    assert obj.page == 14
    assert obj.section == "External Components"
    assert obj.confidence == "medium"
    assert obj.method == "prose"
    assert to_dict(obj) == raw


def test_evidence_nullable_section_preserved() -> None:
    from datasheet_types.spec_value import Evidence
    from datasheet_types.codec import from_dict, to_dict

    raw = {"page": 1, "section": None, "confidence": "high", "method": "table"}
    obj = from_dict(Evidence, raw)
    assert obj.section is None
    assert to_dict(obj) == raw


def test_codec_list_field_rejects_non_list() -> None:
    """from_dict raises TypeError when a list-typed field gets a non-list value.

    Guards against silent string-iteration bugs that would confuse
    downstream dict[str, list[T]] consumers (Task 3's BaseBlock).
    """
    from datasheet_types.codec import _from_value

    with pytest.raises(TypeError, match="Expected list"):
        _from_value(list[str], "not-a-list")


def test_codec_dict_field_rejects_non_dict() -> None:
    """from_dict raises TypeError when a dict-typed field gets a non-dict value."""
    from datasheet_types.codec import _from_value

    with pytest.raises(TypeError, match="Expected dict"):
        _from_value(dict[str, int], [1, 2, 3])


def test_codec_omits_fields_marked_omit_if_none() -> None:
    """to_dict skips fields with metadata={'omit_if_none': True} when None.

    Used for DatasheetFacts category siblings (regulator, future mcu/...)
    so 'absent' signals 'no category' rather than emitting explicit nulls.
    """
    from dataclasses import dataclass, field
    from typing import Optional
    from datasheet_types.codec import to_dict

    @dataclass
    class Host:
        name: str = field(metadata={"description": "Required name."})
        sibling: Optional[str] = field(default=None, metadata={
            "description": "Absent when not needed.",
            "omit_if_none": True,
        })
        regular: Optional[str] = field(default=None, metadata={
            "description": "Emits null when not set."})

    # Both optional fields None.
    obj = Host(name="x")
    emitted = to_dict(obj)
    assert "sibling" not in emitted          # omitted entirely
    assert emitted["regular"] is None        # still emitted as null
    # When the omit-field has a value, it's present as normal.
    obj2 = Host(name="x", sibling="y")
    emitted2 = to_dict(obj2)
    assert emitted2["sibling"] == "y"


# ---------------------------------------------------------------------------
# Pin + AltFunction + Pinout wrapper
# ---------------------------------------------------------------------------

def test_alt_function_roundtrip() -> None:
    from datasheet_types.pinout import AltFunction
    from datasheet_types.codec import from_dict, to_dict

    raw = {"name": "USART1_TX", "peripheral": "USART1", "role": "TX", "af_code": "AF7"}
    obj = from_dict(AltFunction, raw)
    assert obj.name == "USART1_TX"
    assert obj.peripheral == "USART1"
    assert obj.role == "TX"
    assert obj.af_code == "AF7"
    assert to_dict(obj) == raw


def test_pin_roundtrip_minimal() -> None:
    """Pin with only required fields — numbers, name, type."""
    from datasheet_types.pinout import Pin
    from datasheet_types.codec import from_dict, to_dict

    raw = {"numbers": ["1"], "name": "VIN", "type": "power_in"}
    obj = from_dict(Pin, raw)
    assert obj.numbers == ["1"]
    assert obj.name == "VIN"
    assert obj.type == "power_in"
    # Optional fields default to None.
    assert obj.subtype is None
    assert obj.evidence is None
    assert obj.alt_functions == []  # default_factory list
    # to_dict emits every field (including Nones).
    emitted = to_dict(obj)
    assert emitted["numbers"] == ["1"]
    assert emitted["name"] == "VIN"
    assert emitted["type"] == "power_in"
    assert emitted["subtype"] is None
    assert emitted["evidence"] is None
    assert emitted["alt_functions"] == []


def test_pin_roundtrip_full() -> None:
    """Pin with all optional fields populated — BGA-style."""
    from datasheet_types.pinout import Pin
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "numbers": ["A1"],
        "name": "PA9",
        "type": "bidirectional",
        "subtype": "open_drain",
        "description": "GPIO Port A bit 9",
        "power_domain": "VDDIO_1",
        "alt_functions": [
            {"name": "USART1_TX", "peripheral": "USART1", "role": "TX", "af_code": "AF7"},
        ],
        "is_5v_tolerant": True,
        "absolute_max": None,
        "recommended": None,
        "drive_strength": None,
        "notes": None,
        "evidence": {"page": 10, "section": "Pinout", "confidence": "high", "method": "table"},
    }
    obj = from_dict(Pin, raw)
    assert obj.numbers == ["A1"]
    assert obj.alt_functions[0].peripheral == "USART1"
    assert obj.is_5v_tolerant is True
    assert obj.evidence.page == 10
    assert to_dict(obj) == raw


def test_pin_with_populated_spec_value_lists() -> None:
    """Optional[list[SpecValue]] fields round-trip when populated.

    The first exercise of the codec's Optional[list[nested_dataclass]]
    path — a regression in that path would silently break base block's
    dict[str, list[SpecValue]] shape in Task 3.
    """
    from datasheet_types.pinout import Pin
    from datasheet_types.codec import from_dict, to_dict

    ev = {"page": 5, "section": "Electrical Characteristics",
          "confidence": "high", "method": "table"}
    raw = {
        "numbers": ["PA9"], "name": "PA9", "type": "bidirectional",
        "subtype": None, "description": None, "power_domain": None,
        "alt_functions": [],
        "is_5v_tolerant": None,
        "absolute_max": [{
            "min": None, "typ": None, "max": 5.5,
            "unit": "V", "condition": None, "notes": None, "evidence": ev,
        }],
        "recommended": None,
        "drive_strength": None,
        "notes": None,
        "evidence": None,
    }
    obj = from_dict(Pin, raw)
    assert obj.absolute_max is not None
    assert len(obj.absolute_max) == 1
    assert obj.absolute_max[0].max == 5.5
    assert obj.absolute_max[0].unit == "V"
    assert obj.absolute_max[0].evidence.page == 5
    assert obj.recommended is None
    assert obj.drive_strength is None
    # Round-trip preserves the populated-list shape.
    assert to_dict(obj) == raw


def test_pinout_find_by_number_and_name() -> None:
    from datasheet_types.pinout import Pin, Pinout

    pins = [
        Pin(numbers=["1"], name="VIN", type="power_in"),
        Pin(numbers=["2"], name="OUT", type="output"),
        Pin(numbers=["3"], name="GND", type="power_in"),
    ]
    pinout = Pinout(pins=pins)
    # Find by pin number
    p = pinout.find(pin="2")
    assert p is not None
    assert p.name == "OUT"
    # Find by name
    p = pinout.find(name="VIN")
    assert p is not None
    assert p.numbers == ["1"]
    # Missing
    assert pinout.find(pin="99") is None
    assert pinout.find(name="DOESNOTEXIST") is None
    # Calling find() with no arguments returns None (documented behavior).
    assert pinout.find() is None


def test_pinout_in_domain() -> None:
    from datasheet_types.pinout import Pin, Pinout

    pins = [
        Pin(numbers=["1"], name="VDDIO1", type="power_in", power_domain="VDDIO_1"),
        Pin(numbers=["2"], name="VDDIO2", type="power_in", power_domain="VDDIO_1"),
        Pin(numbers=["3"], name="VDDCORE", type="power_in", power_domain="VDDCORE"),
        Pin(numbers=["4"], name="GND", type="power_in"),
    ]
    pinout = Pinout(pins=pins)
    matches = pinout.in_domain("VDDIO_1")
    assert len(matches) == 2
    assert {p.name for p in matches} == {"VDDIO1", "VDDIO2"}


def test_pinout_iter_and_len() -> None:
    from datasheet_types.pinout import Pin, Pinout

    pinout = Pinout(pins=[
        Pin(numbers=["1"], name="A", type="input"),
        Pin(numbers=["2"], name="B", type="output"),
    ])
    assert len(pinout) == 2
    names = [p.name for p in pinout]
    assert names == ["A", "B"]


def test_pinout_equality() -> None:
    """Pinout compares by content, not identity — behaves as a value type."""
    from datasheet_types.pinout import Pin, Pinout

    p1 = Pin(numbers=["1"], name="VIN", type="power_in")
    p2 = Pin(numbers=["2"], name="GND", type="power_in")
    a = Pinout(pins=[p1, p2])
    b = Pinout(pins=[Pin(numbers=["1"], name="VIN", type="power_in"),
                     Pin(numbers=["2"], name="GND", type="power_in")])
    c = Pinout(pins=[p2, p1])  # different order

    assert a == b                # same content → equal
    assert a != c                # different order → not equal
    assert a != "not-a-pinout"   # different type → not equal (NotImplemented falls back)


def test_pinout_roundtrip_through_codec() -> None:
    """Pinout serializes as a bare list (root-array shape)."""
    from datasheet_types.pinout import Pinout
    from datasheet_types.codec import from_dict, to_dict

    raw = [
        {"numbers": ["1"], "name": "VIN", "type": "power_in"},
        {"numbers": ["2"], "name": "GND", "type": "power_in"},
    ]
    pinout = from_dict(Pinout, raw)
    assert len(pinout) == 2
    # to_dict emits back to a bare list (NOT a dict with a 'pins' key).
    emitted = to_dict(pinout)
    assert isinstance(emitted, list)
    assert emitted[0]["name"] == "VIN"
    assert emitted[1]["name"] == "GND"


# ---------------------------------------------------------------------------
# BaseBlock + Package + ComplianceMark + PinRelationship + MoistureSensitivity
# ---------------------------------------------------------------------------

def test_package_roundtrip() -> None:
    from datasheet_types.base_block import Package
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "code": "TO-263-5",
        "pin_count": 5,
        "pitch_mm": None,
        "body_mm": None,
        "thermal_pad": True,
        "evidence": {"page": 1, "section": "Features", "confidence": "high", "method": "prose"},
    }
    obj = from_dict(Package, raw)
    assert obj.code == "TO-263-5"
    assert obj.pin_count == 5
    assert obj.thermal_pad is True
    assert obj.evidence.page == 1
    assert to_dict(obj) == raw


def test_body_mm_roundtrip() -> None:
    from datasheet_types.base_block import BodyMm
    from datasheet_types.codec import from_dict, to_dict

    raw = {"length": 9.9, "width": 5.1, "height": 4.57}
    obj = from_dict(BodyMm, raw)
    assert obj.length == 9.9
    assert obj.width == 5.1
    assert obj.height == 4.57
    assert to_dict(obj) == raw


def test_moisture_sensitivity_roundtrip() -> None:
    from datasheet_types.base_block import MoistureSensitivity
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "msl": 3,
        "peak_reflow_c": 260.0,
        "evidence": {"page": 8, "section": "Package Markings", "confidence": "high", "method": "table"},
    }
    obj = from_dict(MoistureSensitivity, raw)
    assert obj.msl == 3
    assert obj.peak_reflow_c == 260.0
    assert to_dict(obj) == raw


def test_compliance_mark_roundtrip() -> None:
    from datasheet_types.base_block import ComplianceMark
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "mark": "AEC-Q100",
        "rating": "Grade 1",
        "evidence": {"page": 1, "section": "Features", "confidence": "high", "method": "prose"},
    }
    obj = from_dict(ComplianceMark, raw)
    assert obj.mark == "AEC-Q100"
    assert obj.rating == "Grade 1"
    assert to_dict(obj) == raw


def test_pin_relationship_roundtrip() -> None:
    from datasheet_types.base_block import PinRelationship
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "type": "requires_pullup",
        "pins": ["5"],
        "notes": "Tie EN to VIN via 10k if unused",
        "evidence": None,
    }
    obj = from_dict(PinRelationship, raw)
    assert obj.type == "requires_pullup"
    assert obj.pins == ["5"]
    assert obj.notes == "Tie EN to VIN via 10k if unused"
    assert obj.evidence is None
    assert to_dict(obj) == raw


def test_base_block_from_fixture() -> None:
    """Full round-trip of the LM2596-ADJ fixture's base section.

    This test's `to_dict(obj) == base_raw` is Python dict equality
    (value/key equal, order-independent) — NOT JSON byte-equality.
    The assertion requires the fixture to include every optional
    field as explicit nulls/empty-lists because the codec's to_dict
    emits all declared fields; absent optional keys would compare
    unequal to an emitted `"key": null`. Track 2.1's original fixture
    was completed in Task 3 (package.pitch_mm, body_mm;
    base.moisture_sensitivity, compliance) to satisfy this invariant.

    Note for Track 2.3: json.dumps(to_dict(facts)) key ordering
    differs from lm2596-adj.example.json's ordering because Python
    dataclasses force required fields before optional fields (see
    module docstrings in base_block.py and extraction.py). Cache
    file rewrites via to_dict() are semantically idempotent but NOT
    JSON-text-idempotent — downstream staleness checks must hash
    the parsed dict, not the raw bytes.

    Alternative considered: loosen the assertion to subset-equality
    on keys present in base_raw. Rejected because value-level
    equality is a stronger contract and the fixture additions are
    schema-valid + semantically neutral (null for optional scalars,
    [] for optional arrays, both accepted by base.schema.json).
    """
    from datasheet_types.base_block import BaseBlock
    from datasheet_types.codec import from_dict, to_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    base_raw = fixture["base"]
    obj = from_dict(BaseBlock, base_raw)

    # Sanity-check typed access.
    assert obj.family == "step-down switching regulator"
    assert obj.package.code == "TO-263-5 (KTT)"
    assert obj.package.thermal_pad is True
    # Keyed-object shape: absolute_max["VIN_max"] is list[SpecValue].
    assert obj.absolute_max["VIN_max"][0].max == 45
    assert obj.absolute_max["VIN_max"][0].unit == "V"
    # Thermal uses compound units.
    assert obj.thermal["theta_ja"][0].unit == "°C/W"
    assert obj.thermal["theta_ja"][0].typ == 50
    # Pinout access via wrapper. Pipeline-extracted fixture uses verbose
    # datasheet pin names ("Feedback" not "FB", "Output" not "OUT").
    assert len(obj.pinout) == 5
    fb = obj.pinout.find(name="Feedback")
    assert fb is not None
    assert fb.numbers == ["4"]
    # pin_relationships empty list on this fixture.
    assert obj.pin_relationships == []
    # Round-trip matches the original shape (Python dict equality, order-independent).
    emitted = to_dict(obj)
    assert emitted == base_raw


def test_base_block_absolute_max_required() -> None:
    """absolute_max is required — raises if missing."""
    from datasheet_types.base_block import BaseBlock
    from datasheet_types.codec import from_dict

    # Start from a valid minimal base and strip the required key.
    fixture = _load_json(FIXTURE_DIR / "minimal.example.json")
    bad = dict(fixture["base"])
    del bad["absolute_max"]

    with pytest.raises(KeyError):
        from_dict(BaseBlock, bad)


# ---------------------------------------------------------------------------
# Regulator + StabilityConditions + Sequencing
# ---------------------------------------------------------------------------

def test_stability_conditions_roundtrip() -> None:
    from datasheet_types.regulator import StabilityConditions
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "cap_types_allowed": ["tantalum", "electrolytic", "polymer"],
        "esr_range": [
            {"min": 0.05, "typ": None, "max": 0.5, "unit": "Ω",
             "condition": None, "notes": None,
             "evidence": {"page": 15, "section": "Output Capacitor Selection",
                          "confidence": "medium", "method": "prose"}},
        ],
        "notes": "Pure ceramic caps may cause instability.",
        "evidence": {"page": 15, "section": "Output Capacitor Selection",
                     "confidence": "medium", "method": "prose"},
    }
    obj = from_dict(StabilityConditions, raw)
    assert obj.cap_types_allowed == ["tantalum", "electrolytic", "polymer"]
    assert obj.esr_range[0].min == 0.05
    assert obj.esr_range[0].max == 0.5
    assert obj.evidence.page == 15
    assert to_dict(obj) == raw


def test_sequencing_roundtrip() -> None:
    from datasheet_types.regulator import Sequencing
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "must_rise_after": ["VDD_IO"],
        "must_rise_before": [],
        "max_inter_rail_delay": None,
        "notes": None,
        "evidence": None,
    }
    obj = from_dict(Sequencing, raw)
    assert obj.must_rise_after == ["VDD_IO"]
    assert obj.must_rise_before == []
    assert obj.max_inter_rail_delay is None
    assert to_dict(obj) == raw


def test_regulator_from_fixture() -> None:
    """Full round-trip of the LM2596-ADJ fixture's regulator section."""
    from datasheet_types.regulator import Regulator
    from datasheet_types.codec import from_dict, to_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    reg_raw = fixture["regulator"]
    obj = from_dict(Regulator, reg_raw)

    assert obj.topology == "buck"
    assert obj.feedback_pin == "4"
    assert obj.enable_pin == "5"
    assert obj.compensation_pin is None
    assert obj.power_good_pin is None
    # Canonical SI checked.
    assert obj.switching_freq[0].typ == 150000  # Hz, not 150 kHz
    # cin_min lifted from page 27 ("470 µF typical") → typ slot, F units.
    assert obj.cin_min[0].typ == 4.7e-4         # F, not 470 µF
    # inductor_range lifted from Figure 9-8 nomograph (22 µH–150 µH for LM2596-ADJ).
    assert obj.inductor_range[0].min == 2.2e-5  # H, not 22 µH
    # Nested block access.
    assert obj.stability_conditions.cap_types_allowed == ["electrolytic", "tantalum"]
    # Sequencing absent on this part.
    assert obj.sequencing is None
    # Round-trip.
    emitted = to_dict(obj)
    assert emitted == reg_raw


def test_regulator_topology_required() -> None:
    """topology is the only required regulator field."""
    from datasheet_types.regulator import Regulator
    from datasheet_types.codec import from_dict

    with pytest.raises(KeyError):
        from_dict(Regulator, {})


# ---------------------------------------------------------------------------
# DatasheetFacts + Source + ExtractionMeta + SchemaVersion
# (plus full end-to-end round-trip of both fixtures)
# ---------------------------------------------------------------------------

def test_schema_version_roundtrip() -> None:
    from datasheet_types.extraction import SchemaVersion
    from datasheet_types.codec import from_dict, to_dict

    raw = {"base": "1.0", "categories": {"regulator": "0.3"}}
    obj = from_dict(SchemaVersion, raw)
    assert obj.base == "1.0"
    assert obj.categories == {"regulator": "0.3"}
    assert to_dict(obj) == raw


def test_source_roundtrip() -> None:
    from datasheet_types.extraction import Source
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "manufacturer": "Texas Instruments",
        "mpn": "LM2596-ADJ",
        "datasheet_revision": "Rev M",
        "datasheet_date": "2022-08",
        "source_url": "https://www.ti.com/lit/ds/symlink/lm2596.pdf",
        "local_path": "datasheets/LM2596-ADJ.pdf",
        "sha256": "sha256:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
        "page_count": 32,
        "family_ref": None,
    }
    obj = from_dict(Source, raw)
    assert obj.manufacturer == "Texas Instruments"
    assert obj.mpn == "LM2596-ADJ"
    assert obj.sha256.startswith("sha256:")
    assert obj.family_ref is None
    assert to_dict(obj) == raw


def test_extraction_meta_roundtrip() -> None:
    from datasheet_types.extraction import ExtractionMeta
    from datasheet_types.codec import from_dict, to_dict

    raw = {
        "extracted_at": "2026-04-19T12:00:00Z",
        "extractor_scout": "tier-B",
        "extractor_schema_version": "1.0",
        "quality_score": 87,
        "plan_ref": "LM2596-ADJ.plan.json",
    }
    obj = from_dict(ExtractionMeta, raw)
    assert obj.extracted_at == "2026-04-19T12:00:00Z"
    assert obj.quality_score == 87
    assert to_dict(obj) == raw


def test_datasheet_facts_from_lm2596_fixture() -> None:
    """End-to-end: load LM2596-ADJ fixture → DatasheetFacts → to_dict → re-validate."""
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict, to_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    facts = from_dict(DatasheetFacts, fixture)

    # Typed access across the full composition.
    assert facts.source.mpn == "LM2596-ADJ"
    assert facts.schema_version.base == "1.0"
    assert facts.schema_version.categories["regulator"] == "0.3"
    assert facts.base.family == "step-down switching regulator"
    assert facts.base.package.code == "TO-263-5 (KTT)"
    assert facts.categories == ["regulator"]
    assert facts.regulator is not None
    assert facts.regulator.topology == "buck"
    # Pinout access across the stack.
    en = facts.base.pinout.find(name="ON/OFF")
    assert en is not None
    assert en.numbers == ["5"]

    # Round-trip (Python dict equality, order-independent).
    emitted = to_dict(facts)
    assert emitted == fixture

    # And re-validate against the extraction.schema.json.
    schema = _load_json(SCHEMA_DIR / "extraction.schema.json")
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    errors = list(validator.iter_errors(emitted))
    assert errors == [], "\n".join(str(e.message) for e in errors)


def test_datasheet_facts_from_minimal_fixture() -> None:
    """Minimal fixture — only required fields — round-trips cleanly."""
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict, to_dict

    fixture = _load_json(FIXTURE_DIR / "minimal.example.json")
    facts = from_dict(DatasheetFacts, fixture)

    assert facts.source.mpn == "ACME-TEST-001"
    assert facts.regulator is None  # optional, absent in minimal
    assert facts.categories == []   # default_factory applies — absent field gets empty list

    emitted = to_dict(facts)

    schema = _load_json(SCHEMA_DIR / "extraction.schema.json")
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    errors = list(validator.iter_errors(emitted))
    assert errors == [], "\n".join(str(e.message) for e in errors)


def test_public_api_exports() -> None:
    """__init__.py must re-export every name consumers rely on.

    Exhaustively checks all 22 public names in __all__ so a regression
    that accidentally drops one of them from the re-export block or
    __all__ is caught immediately.
    """
    import datasheet_types as ds_types

    expected_names = {
        # Top-level facade
        "DatasheetFacts",
        # Envelope sub-types
        "SchemaVersion",
        "Source",
        "ExtractionMeta",
        # Base block + sub-types
        "BaseBlock",
        "Package",
        "BodyMm",
        "MoistureSensitivity",
        "ComplianceMark",
        "PinRelationship",
        # Pinout types
        "Pinout",
        "Pin",
        "AltFunction",
        # Primitives
        "SpecValue",
        "Evidence",
        # Regulator category
        "Regulator",
        "StabilityConditions",
        "Sequencing",
        # Consumer API entry point (lazy re-export from scripts/)
        "lookup",
        # Track 2.4 trust gating
        "best",
        "trusted",
        "has_data",
    }
    for name in expected_names:
        assert hasattr(ds_types, name), f"public API missing export: {name}"
    # __all__ agrees with what's importable.
    assert set(ds_types.__all__) == expected_names


# ---------------------------------------------------------------------------
# DatasheetFacts computed properties (quality, stale, cache_path)
# ---------------------------------------------------------------------------

def test_datasheet_facts_quality_property_passthrough() -> None:
    """quality returns extraction.quality_score without cache context."""
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    facts = from_dict(DatasheetFacts, fixture)
    # LM2596-ADJ fixture has extraction.quality_score = 98 (Phase 3a pipeline-produced).
    assert facts.quality == 98


def test_datasheet_facts_quality_none_when_not_scored() -> None:
    """quality returns None when extraction.quality_score is None."""
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict

    fixture = _load_json(FIXTURE_DIR / "minimal.example.json")
    facts = from_dict(DatasheetFacts, fixture)
    # Minimal fixture has no quality_score populated.
    assert facts.quality is None


def test_datasheet_facts_stale_defaults_false_without_cache_context() -> None:
    """stale returns False when constructed outside lookup() (no context).

    Regression guard: Track 2.2 tests construct DatasheetFacts via from_dict
    directly; they should continue to see stale=False.
    """
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    facts = from_dict(DatasheetFacts, fixture)
    assert facts.stale is False


def test_datasheet_facts_cache_path_defaults_none_without_cache_context() -> None:
    """cache_path returns None when constructed outside lookup()."""
    from datasheet_types.extraction import DatasheetFacts
    from datasheet_types.codec import from_dict

    fixture = _load_json(FIXTURE_DIR / "lm2596-adj.example.json")
    facts = from_dict(DatasheetFacts, fixture)
    assert facts.cache_path is None
