"""Contract test: EMC analyzer output validates against its declared schema."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMATIC = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
PCB = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_pcb.py"
EMC = MAIN_REPO_ROOT / "skills" / "emc" / "scripts" / "analyze_emc.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project"


def _run(argv):
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, check=True,
    ).stdout


def test_emc_schema_is_draft_2020_12():
    schema = json.loads(_run([str(EMC), "--schema"]))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_emc_output_validates(tmp_path):
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([str(EMC), "--schematic", str(sch_json), "--pcb", str(pcb_json)]))
    schema = json.loads(_run([str(EMC), "--schema"]))
    Draft202012Validator(schema).validate(result)


def test_emc_schema_version_and_analyzer_type_are_const():
    schema = json.loads(_run([str(EMC), "--schema"]))
    assert schema["properties"]["schema_version"]["const"] == "1.4.0"
    assert schema["properties"]["analyzer_type"]["const"] == "emc"


def test_emc_runtime_schema_version_is_1_4_0(tmp_path):
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([str(EMC), "--schematic", str(sch_json), "--pcb", str(pcb_json)]))
    assert result["schema_version"] == "1.4.0"


def test_emc_inputs_upstream_artifacts_populated(tmp_path):
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([
        str(EMC), "--schematic", str(sch_json), "--pcb", str(pcb_json)
    ]))
    inputs = result["inputs"]
    upstream = inputs["upstream_artifacts"]
    assert "schematic" in upstream
    assert "pcb" in upstream
    assert upstream["schematic"]["schema_version"] == "1.4.0"
    assert upstream["pcb"]["schema_version"] == "1.4.0"
    assert str(sch_json) in inputs["source_files"]
    assert str(pcb_json) in inputs["source_files"]


def test_emc_compat_block_v1_4_defaults(tmp_path):
    """Track 1.4: every envelope emits a CompatBlock with v1.4 defaults."""
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([
        str(EMC), "--schematic", str(sch_json), "--pcb", str(pcb_json)
    ]))
    compat = result["compat"]
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []
