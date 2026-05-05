"""Contract test: PCB analyzer output validates against its declared schema."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

PCB = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_pcb.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project" / "simple.kicad_pcb"


def _run(argv):
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, check=True,
    ).stdout


def test_pcb_schema_is_draft_2020_12():
    schema = json.loads(_run([str(PCB), "--schema"]))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_pcb_output_validates():
    result = json.loads(_run([str(PCB), str(FIXTURE)]))
    schema = json.loads(_run([str(PCB), "--schema"]))
    Draft202012Validator(schema).validate(result)


def test_pcb_schema_version_and_analyzer_type_are_const():
    schema = json.loads(_run([str(PCB), "--schema"]))
    assert schema["properties"]["schema_version"]["const"] == "1.4.0"
    assert schema["properties"]["analyzer_type"]["const"] == "pcb"


def test_pcb_runtime_schema_version_is_1_4_0():
    result = json.loads(_run([str(PCB), str(FIXTURE)]))
    assert result["schema_version"] == "1.4.0"


def test_pcb_inputs_block_populated():
    out = _run([str(PCB), str(FIXTURE)])
    result = json.loads(out)
    inputs = result["inputs"]
    assert any(p.endswith("simple.kicad_pcb") for p in inputs["source_files"])
    for p in inputs["source_files"]:
        assert len(inputs["source_hashes"][p]) == 64
    import re
    assert re.match(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$", inputs["run_id"])
    assert inputs["upstream_artifacts"] == {}


def test_pcb_legacy_file_field_removed():
    schema = json.loads(_run([str(PCB), "--schema"]))
    assert "file" not in schema["properties"]


def test_pcb_compat_block_v1_4_defaults():
    """Track 1.4: every envelope emits a CompatBlock with v1.4 defaults."""
    out = _run([str(PCB), str(FIXTURE)])
    result = json.loads(out)
    compat = result["compat"]
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []
