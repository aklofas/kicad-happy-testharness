"""Contract tests for datasheet v2 JSON schemas.

Validates that every schema under skills/datasheets/schemas/ parses as
valid Draft 2020-12 and that the accompanying fixture files validate
against their declared schemas.

Uses jsonschema (Draft 2020-12 validator). Both are dev dependencies in
requirements-dev.txt.
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMA_DIR = MAIN_REPO_ROOT / "skills" / "datasheets" / "schemas"
FIXTURE_DIR = SCHEMA_DIR / "fixtures"


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _build_registry() -> Registry:
    """Build a referencing Registry so $ref between schemas resolves.

    Scaffolding for Tasks 2–6: consumed by the fixture-validation tests
    added in Task 5 once the extraction envelope + fixtures land. Kept
    here so each schema-add task only appends to the registry's input
    glob rather than refactoring test helpers.
    """
    registry = Registry()
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        schema = _load_json(schema_path)
        uri = schema.get("$id")
        if uri:
            registry = registry.with_resource(uri, Resource.from_contents(schema))
    return registry


# ---------------------------------------------------------------------------
# Per-schema Draft 2020-12 validity
# ---------------------------------------------------------------------------

SCHEMA_FILES = [
    "spec_value.schema.json",
    "pinout.schema.json",
    "base.schema.json",
    "regulator.schema.json",
    "extraction.schema.json",
    "manifest.schema.json",
    "scout.schema.json",
    "plan.schema.json",
]

FIXTURE_TARGETS = [
    # (fixture_filename, schema_filename)
    ("minimal.example.json", "extraction.schema.json"),
    ("lm2596-adj.example.json", "extraction.schema.json"),
    ("manifest.example.json", "manifest.schema.json"),
]


@pytest.mark.parametrize("schema_filename", SCHEMA_FILES)
def test_schema_is_valid_draft_2020_12(schema_filename: str) -> None:
    schema_path = SCHEMA_DIR / schema_filename
    assert schema_path.exists(), f"Missing schema file: {schema_path}"
    schema = _load_json(schema_path)
    # Raises SchemaError if the schema itself is malformed.
    Draft202012Validator.check_schema(schema)
    # Every schema must declare its $id and $schema dialect.
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert "$id" in schema, f"{schema_filename} is missing $id"


# ---------------------------------------------------------------------------
# SpecValue-specific shape assertions
# ---------------------------------------------------------------------------

def test_spec_value_requires_unit_and_evidence() -> None:
    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    required = set(schema.get("required", []))
    # unit is required so consumers never parse free-form strings.
    assert "unit" in required
    # evidence is required so no fact ships without provenance.
    assert "evidence" in required


def test_spec_value_evidence_has_required_confidence_and_method() -> None:
    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    evidence = schema["properties"]["evidence"]
    req = set(evidence.get("required", []))
    assert "page" in req
    assert "confidence" in req
    assert "method" in req
    # confidence is the trust-gating pivot — must be a closed enum.
    assert evidence["properties"]["confidence"]["enum"] == ["high", "medium", "low"]
    # method is the extraction-technique tag — closed enum.
    assert set(evidence["properties"]["method"]["enum"]) == {
        "table", "prose", "curve", "calculated", "derived",
    }


def test_spec_value_unit_is_closed_enum() -> None:
    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    unit = schema["properties"]["unit"]
    # Canonical SI set per spec §3, plus two compound units for thermal
    # resistance (θJA, θJC, ψJT) and thermal capacity. Extraction converts
    # (µA → A, mV → V, kΩ → Ω, kHz → Hz, °C/W → °C/W) so consumers never
    # see prefixes.
    expected = {
        "V", "A", "C", "s", "Hz", "Ω", "F", "H", "K", "W", "°C", "%", "ppm",
        "K/W", "°C/W",
        "V/s",  # slew rate (store 0.6V/µs as 6e5 V/s) — added for opamp v1.0
        "dB",   # CMRR, PSRR, open-loop gain — added for opamp v1.0
        None,   # null allowed for dimensionless quantities (e.g. hFE current gain)
    }
    assert set(unit["enum"]) == expected


def test_spec_value_numeric_fields_are_nullable_numbers() -> None:
    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    props = schema["properties"]
    for key in ("min", "typ", "max"):
        # Each may be a number or null (datasheet doesn't always publish
        # all three). Consumers check for None explicitly.
        assert props[key]["type"] == ["number", "null"]


# ---------------------------------------------------------------------------
# Pinout-specific shape assertions
# ---------------------------------------------------------------------------

def test_pinout_pin_object_shape() -> None:
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    pin = schema["$defs"]["Pin"]
    required = set(pin["required"])
    # numbers, name, type are the minimum any pin record must carry.
    # Everything else is null/optional until extraction populates it.
    assert required == {"numbers", "name", "type"}


def test_pinout_numbers_is_array_of_strings() -> None:
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    pin = schema["$defs"]["Pin"]
    numbers = pin["properties"]["numbers"]
    # Always an array even for single-pin records. Strings to handle BGA
    # grids ("A1"), LGA, stacked internal pins (["3","4","5"]), etc.
    assert numbers["type"] == "array"
    assert numbers["items"]["type"] == "string"
    assert numbers["minItems"] == 1


def test_pinout_type_uses_kicad_erc_vocabulary() -> None:
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    pin_type = schema["$defs"]["Pin"]["properties"]["type"]
    # Vocabulary mirrors KiCad's ERC pin-type matrix so detectors can
    # cross-reference against symbol pin types directly.
    assert set(pin_type["enum"]) == {
        "input", "output", "bidirectional", "tri_state", "passive",
        "open_collector", "open_emitter", "power_in", "power_out",
        "not_connected", "unspecified",
    }


def test_pinout_alt_function_shape() -> None:
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    alt = schema["$defs"]["AltFunction"]
    required = set(alt["required"])
    # Only name + peripheral are required; role and af_code are optional
    # because many fixed-peripheral alt functions don't publish a role.
    # Detectors filter on peripheral (e.g. PM-001 "does this pin support UART?").
    assert required == {"name", "peripheral"}


def test_pinout_top_level_is_array_of_pins() -> None:
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    # The schema exposes two top-level types: Pin (via $defs) and
    # Pinout (via the root type), letting base.schema.json use either.
    assert schema["type"] == "array"
    assert schema["items"]["$ref"] == "#/$defs/Pin"


def test_pinout_still_calibrating_marker() -> None:
    """Pin schema is additive-only-calibrating through v1.4 per spec §5."""
    schema = _load_json(SCHEMA_DIR / "pinout.schema.json")
    # Custom annotation — non-normative, but documents the stability
    # promise so downstream readers know the schema may shift before v1.5.
    assert schema.get("x-still-calibrating") is True


# ---------------------------------------------------------------------------
# Base-block-specific shape assertions
# ---------------------------------------------------------------------------

def test_base_absolute_max_is_keyed_object() -> None:
    """absolute_max, recommended_operating, esd are objects keyed by
    parameter name (e.g. 'VIN_max') → SpecValue[], NOT flat lists.

    This is the consumer-indexability shape from spec §4:
    ds.base.absolute_max["VIN_max"] should Just Work.
    """
    schema = _load_json(SCHEMA_DIR / "base.schema.json")
    amax = schema["properties"]["absolute_max"]
    assert amax["type"] == "object"
    # additionalProperties is the SpecValue array pattern — arbitrary
    # parameter names keyed, values are SpecValue[].
    add_props = amax["additionalProperties"]
    assert add_props["type"] == "array"
    assert "spec_value.schema.json" in add_props["items"]["$ref"]


def test_base_recommended_and_esd_same_shape_as_absolute_max() -> None:
    schema = _load_json(SCHEMA_DIR / "base.schema.json")
    for key in ("recommended_operating", "esd"):
        prop = schema["properties"][key]
        # Both use the keyed-object pattern (param-name → SpecValue[]).
        # recommended_operating is required/non-null; esd is nullable
        # (many parts don't publish ESD ratings), so we check the type
        # field contains "object" rather than requiring it to be exactly
        # the string "object".
        prop_type = prop["type"]
        if isinstance(prop_type, list):
            assert "object" in prop_type, f"{key} should include object in type"
        else:
            assert prop_type == "object", f"{key} should be keyed object"
        assert prop["additionalProperties"]["type"] == "array"


def test_base_pinout_refs_pinout_schema() -> None:
    schema = _load_json(SCHEMA_DIR / "base.schema.json")
    pinout = schema["properties"]["pinout"]
    # Base doesn't inline the pin shape — it defers to pinout.schema.json
    # so pinout can evolve independently.
    assert "pinout.schema.json" in pinout["$ref"]


def test_base_pin_relationships_vocabulary() -> None:
    schema = _load_json(SCHEMA_DIR / "base.schema.json")
    rels = schema["properties"]["pin_relationships"]
    assert rels["type"] == "array"
    rel_type = rels["items"]["properties"]["type"]
    # Starter vocabulary from spec §6. Extensible with real-corpus usage.
    expected = {
        "compensation_network", "matched_pair",
        "requires_pullup", "requires_pulldown",
        "current_programming", "stacked_internal",
        "exclusive_with", "timing_critical",
    }
    assert set(rel_type["enum"]) == expected


def test_base_compliance_is_array_of_marks() -> None:
    schema = _load_json(SCHEMA_DIR / "base.schema.json")
    comp = schema["properties"]["compliance"]
    assert comp["type"] == "array"
    # Each entry is an object with mark + rating so detectors can filter
    # (CM-001 reads compliance for AEC-Q100, IEC 62368, etc.).
    item = comp["items"]
    assert "mark" in item["properties"]


# ---------------------------------------------------------------------------
# Regulator-specific shape assertions
# ---------------------------------------------------------------------------

def test_regulator_topology_enum() -> None:
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    topo = schema["properties"]["topology"]
    # Flat vocabulary per spec §7. subtype lives inside the 'topology'
    # enum directly — no nested category/subtype split.
    expected = {
        "ldo", "buck", "boost", "buck_boost",
        "sepic", "flyback", "charge_pump", "isolated",
    }
    assert set(topo["enum"]) == expected


def test_regulator_required_fields() -> None:
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    required = set(schema["required"])
    # topology is the only hard-required field — every regulator knows its
    # own topology. Every other field is optional because datasheet
    # coverage varies (LDOs rarely publish inductor range; boost converters
    # don't have dropout specs, etc.).
    assert required == {"topology"}


def test_regulator_spec_value_array_fields() -> None:
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    props = schema["properties"]
    # All electrical parameters are optional SpecValue[].
    spec_value_fields = [
        "vin_range", "vout_range", "iout_max", "reference_voltage",
        "cin_min", "cout_min", "inductor_range", "switching_freq",
        "dropout", "psrr", "line_regulation", "load_regulation",
    ]
    for f in spec_value_fields:
        prop = props[f]
        # Nullable array of SpecValue.
        assert prop["type"] == ["array", "null"], f"{f} wrong type shape"
        assert "spec_value.schema.json" in prop["items"]["$ref"]


def test_regulator_pin_references_are_strings() -> None:
    """feedback_pin, compensation_pin, enable_pin, power_good_pin are
    pin number references — must resolve to base.pinout[*].numbers."""
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    props = schema["properties"]
    for f in ("feedback_pin", "compensation_pin", "enable_pin", "power_good_pin"):
        assert props[f]["type"] == ["string", "null"]


def test_regulator_stability_conditions_shape() -> None:
    """stability_conditions is a closed object consumed by SV-001.

    Verifies the nested block shape won't silently regress into a
    loose dict when Tasks 5+ exercise it via the LM2596-ADJ fixture.
    """
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    stab = schema["properties"]["stability_conditions"]
    # Nullable object — datasheet may not publish stability constraints.
    assert stab["type"] == ["object", "null"]
    assert stab["additionalProperties"] is False

    cap_types = stab["properties"]["cap_types_allowed"]
    # Closed vocabulary at the items level, array at the field level.
    assert cap_types["type"] == "array"
    assert cap_types["items"]["type"] == "string"
    # ceramic_c0g must be in the vocabulary — it's the Class 1
    # temperature-stable dielectric that appears in LDO stability notes.
    assert "ceramic_c0g" in cap_types["items"]["enum"]

    esr = stab["properties"]["esr_range"]
    assert esr["type"] == ["array", "null"]
    assert "spec_value.schema.json" in esr["items"]["$ref"]


def test_regulator_sequencing_shape() -> None:
    """sequencing is a closed object consumed by ST-001.

    must_rise_after / must_rise_before are arrays of rail-name strings;
    max_inter_rail_delay is a nullable SpecValue[] for time constraints.
    """
    schema = _load_json(SCHEMA_DIR / "regulator.schema.json")
    seq = schema["properties"]["sequencing"]
    assert seq["type"] == ["object", "null"]
    assert seq["additionalProperties"] is False

    for rail_list_field in ("must_rise_after", "must_rise_before"):
        prop = seq["properties"][rail_list_field]
        assert prop["type"] == "array"
        # Rail names, not integers.
        assert prop["items"]["type"] == "string"

    delay = seq["properties"]["max_inter_rail_delay"]
    assert delay["type"] == ["array", "null"]
    assert "spec_value.schema.json" in delay["items"]["$ref"]


# ---------------------------------------------------------------------------
# Extraction envelope — round-trip fixture validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture_filename,schema_filename", FIXTURE_TARGETS)
def test_fixture_validates_against_schema(fixture_filename: str, schema_filename: str) -> None:
    fixture_path = FIXTURE_DIR / fixture_filename
    schema_path = SCHEMA_DIR / schema_filename
    assert fixture_path.exists(), f"Missing fixture: {fixture_path}"
    fixture = _load_json(fixture_path)
    schema = _load_json(schema_path)
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(fixture), key=lambda e: list(e.absolute_path))
    assert errors == [], "\n".join(
        f"{list(e.absolute_path)}: {e.message}" for e in errors
    )


def test_extraction_top_level_required_fields() -> None:
    schema = _load_json(SCHEMA_DIR / "extraction.schema.json")
    required = set(schema["required"])
    # These four define a minimally-reconstructable cache entry.
    assert required == {"schema_version", "source", "extraction", "base"}


def test_extraction_schema_version_is_split_base_plus_categories() -> None:
    schema = _load_json(SCHEMA_DIR / "extraction.schema.json")
    sv = schema["properties"]["schema_version"]
    assert "base" in sv["properties"]
    assert "categories" in sv["properties"]
    # categories is a keyed object (regulator → "0.3", mcu → "1.0", …)
    assert sv["properties"]["categories"]["type"] == "object"


# ---------------------------------------------------------------------------
# Manifest (datasheets/manifest.json) shape assertions
# ---------------------------------------------------------------------------

def test_manifest_pdfs_section_keyed_by_sha256() -> None:
    schema = _load_json(SCHEMA_DIR / "manifest.schema.json")
    pdfs = schema["properties"]["pdfs"]
    # Tier 1 SHA dedup — outer key is sha256, value is {path, mpns[]}.
    assert pdfs["type"] == "object"
    # Key pattern enforces sha256: prefix so readers can dedup by hash
    # without parsing the value.
    pattern_key = list(pdfs["patternProperties"].keys())[0]
    assert "sha256:" in pattern_key
    entry = pdfs["patternProperties"][pattern_key]
    entry_req = set(entry["required"])
    assert {"path", "mpns"} <= entry_req


def test_manifest_pdfs_entry_mpns_is_non_empty_list() -> None:
    schema = _load_json(SCHEMA_DIR / "manifest.schema.json")
    pdfs = schema["properties"]["pdfs"]
    entry = next(iter(pdfs["patternProperties"].values()))
    mpns = entry["properties"]["mpns"]
    assert mpns["type"] == "array"
    # At least one MPN per PDF — a PDF without any MPN pointer would be
    # orphaned and subject to retention-policy sweep.
    assert mpns["minItems"] == 1
    assert mpns["items"]["type"] == "string"


def test_manifest_preserves_legacy_extractions_section() -> None:
    """v1.3 consumers read the 'extractions' section — v1.4 keeps it so
    the compat layer works without a data migration step."""
    schema = _load_json(SCHEMA_DIR / "manifest.schema.json")
    assert "extractions" in schema["properties"]


# ---------------------------------------------------------------------------
# SpecValue unit enum — negative (rejection) tests
# ---------------------------------------------------------------------------

def test_spec_value_rejects_prefixed_units() -> None:
    """Extraction must convert prefixed units (mV, kHz, µF, ...) to
    canonical SI before caching. Negative test: a fixture with any
    prefixed unit must fail validation.

    This locks the canonical-SI contract so a future enum expansion
    can't accidentally open it without a deliberate test change.
    """
    schema = _load_json(SCHEMA_DIR / "spec_value.schema.json")
    registry = _build_registry()
    validator = Draft202012Validator(schema, registry=registry)
    for bad_unit in ("mV", "kHz", "µF", "mA", "kΩ", "nF", "uF", "MΩ"):
        bad = {
            "unit": bad_unit,
            "evidence": {"page": 1, "confidence": "high", "method": "table"},
        }
        errors = list(validator.iter_errors(bad))
        assert errors, f"unit {bad_unit!r} should have been rejected"
