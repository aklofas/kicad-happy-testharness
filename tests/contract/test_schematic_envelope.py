"""Contract test: schematic analyzer output validates against its declared schema."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMATIC = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_sch"


def _run(argv):
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, check=True,
    ).stdout


def test_schematic_schema_is_draft_2020_12():
    schema = json.loads(_run([str(SCHEMATIC), "--schema"]))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_schematic_output_validates():
    out = _run([str(SCHEMATIC), str(FIXTURE)])
    result = json.loads(out)
    schema = json.loads(_run([str(SCHEMATIC), "--schema"]))
    Draft202012Validator(schema).validate(result)


def test_schematic_declares_pin_coverage_warnings_as_optional():
    """KH-323: pin_coverage_warnings must be an OPTIONAL documented field."""
    schema = json.loads(_run([str(SCHEMATIC), "--schema"]))
    assert "pin_coverage_warnings" in schema["properties"]
    assert "pin_coverage_warnings" not in schema["required"]


def test_schematic_schema_version_and_analyzer_type_are_const():
    schema = json.loads(_run([str(SCHEMATIC), "--schema"]))
    assert schema["properties"]["schema_version"]["const"] == "1.4.0"
    assert schema["properties"]["analyzer_type"]["const"] == "schematic"


def test_schematic_runtime_schema_version_is_1_4_0():
    out = _run([str(SCHEMATIC), str(FIXTURE)])
    result = json.loads(out)
    assert result["schema_version"] == "1.4.0"


def test_schematic_inputs_block_populated():
    """Track 1.3: inputs block records fixture path + sha256 + run_id."""
    out = _run([str(SCHEMATIC), str(FIXTURE)])
    result = json.loads(out)
    inputs = result["inputs"]

    # Path normalization — Python emits the same absolute/relative form the
    # analyzer received. We just check the fixture path appears in source_files.
    assert any(p.endswith("simple.kicad_sch") for p in inputs["source_files"])

    # Every source_files entry has a corresponding source_hashes entry.
    for p in inputs["source_files"]:
        assert p in inputs["source_hashes"]
        # SHA-256 hex = 64 chars.
        assert len(inputs["source_hashes"][p]) == 64

    # run_id has the expected format.
    import re
    assert re.match(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$", inputs["run_id"])

    # Raw-input analyzer — empty upstream.
    assert inputs["upstream_artifacts"] == {}


def test_schematic_legacy_file_field_removed():
    """Track 1.3: the legacy 'file' top-level field is gone (replaced by
    inputs.source_files[0])."""
    schema = json.loads(_run([str(SCHEMATIC), "--schema"]))
    assert "file" not in schema["properties"], (
        "Legacy 'file' field must be removed from schematic envelope. "
        "Consumers must read inputs.source_files[0]."
    )


def test_schematic_compat_block_v1_4_defaults():
    """Track 1.4: every envelope emits a CompatBlock with v1.4 defaults."""
    out = _run([str(SCHEMATIC), str(FIXTURE)])
    result = json.loads(out)
    compat = result["compat"]
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []
