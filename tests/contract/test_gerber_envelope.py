"""Contract test: gerber analyzer output validates against its declared schema."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

GERBER = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_gerbers.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "gerbers"


def _run(argv):
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, check=True,
    ).stdout


def test_gerber_schema_is_draft_2020_12():
    schema = json.loads(_run([str(GERBER), "--schema"]))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_gerber_output_validates():
    result = json.loads(_run([str(GERBER), str(FIXTURE)]))
    schema = json.loads(_run([str(GERBER), "--schema"]))
    Draft202012Validator(schema).validate(result)


def test_gerber_schema_version_and_analyzer_type_are_const():
    schema = json.loads(_run([str(GERBER), "--schema"]))
    assert schema["properties"]["schema_version"]["const"] == "1.4.0"
    # Check whatever the analyzer_type literal is — likely 'gerber' or 'gerbers'
    analyzer_type_const = schema["properties"]["analyzer_type"].get("const")
    assert analyzer_type_const in ("gerber", "gerbers"), (
        f"Unexpected analyzer_type const: {analyzer_type_const}")


def test_gerber_runtime_schema_version_is_1_4_0():
    result = json.loads(_run([str(GERBER), str(FIXTURE)]))
    assert result["schema_version"] == "1.4.0"


def test_gerber_inputs_block_populated():
    out = _run([str(GERBER), str(FIXTURE)])
    result = json.loads(out)
    inputs = result["inputs"]
    # Gerber hashes every file in the directory — expect at least the 6
    # standard layers + drill file.
    assert len(inputs["source_files"]) >= 6
    for p in inputs["source_files"]:
        assert len(inputs["source_hashes"][p]) == 64
    assert inputs["upstream_artifacts"] == {}


def test_gerber_compat_block_v1_4_defaults():
    """Track 1.4: every envelope emits a CompatBlock with v1.4 defaults."""
    out = _run([str(GERBER), str(FIXTURE)])
    result = json.loads(out)
    compat = result["compat"]
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []
