"""Contract test: thermal analyzer output validates against its declared schema."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

THERMAL = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_thermal.py"
SCHEMATIC = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
PCB = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_pcb.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "simple-project"


def _run(argv):
    return subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, check=True,
    ).stdout


def test_thermal_schema_is_draft_2020_12():
    out = _run([str(THERMAL), "--schema"])
    schema = json.loads(out)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_thermal_output_matches_schema(tmp_path):
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    th_output = _run([str(THERMAL), "--schematic", str(sch_json), "--pcb", str(pcb_json)])
    result = json.loads(th_output)
    schema = json.loads(_run([str(THERMAL), "--schema"]))
    Draft202012Validator(schema).validate(result)


def test_thermal_schema_version_is_1_4():
    # Now that schema_codec supports const metadata, check the discriminator
    # fields strictly — analyzer_type must be const "thermal" and
    # schema_version must be const "1.4.0".
    schema = json.loads(_run([str(THERMAL), "--schema"]))
    assert schema["properties"]["schema_version"]["const"] == "1.4.0"
    assert schema["properties"]["analyzer_type"]["const"] == "thermal"


def test_thermal_assessments_are_separated_from_findings(tmp_path):
    """Track 1.2: TH-DET entries live in assessments[], NOT in findings[]."""
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([
        str(THERMAL), "--schematic", str(sch_json), "--pcb", str(pcb_json)
    ]))

    # findings[] may contain rule-derived items (TS-001..005, TP-001..002).
    # It MUST NOT contain any TH-DET rule_id items.
    findings_rule_ids = {f.get("rule_id") for f in result.get("findings", [])}
    assert "TH-DET" not in findings_rule_ids, (
        f"TH-DET items must be in assessments[], not findings[]. "
        f"Found rule_ids in findings: {findings_rule_ids}"
    )

    # assessments[] must be present and be a list.
    assert "assessments" in result, "thermal envelope must declare assessments[]"
    assert isinstance(result["assessments"], list), "assessments must be a list"

    # If the fixture produced any assessments at all, they should all be TH-DET.
    # (The simple fixture has no ICs so assessments is likely [] — that's fine.)
    assessment_rule_ids = {a.get("rule_id") for a in result["assessments"]}
    extra = assessment_rule_ids - {"TH-DET"}
    assert not extra, (
        f"Unexpected rule_ids in assessments[]: {extra}. Only TH-DET is "
        f"expected for thermal at v1.4."
    )


def test_thermal_inputs_upstream_artifacts_populated(tmp_path):
    """Track 1.3: thermal's inputs.upstream_artifacts carries schematic + pcb
    metadata keyed by stage name."""
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([
        str(THERMAL), "--schematic", str(sch_json), "--pcb", str(pcb_json)
    ]))

    inputs = result["inputs"]
    upstream = inputs["upstream_artifacts"]

    assert "schematic" in upstream, "thermal must name schematic upstream"
    assert "pcb" in upstream, "thermal must name pcb upstream"

    sch_art = upstream["schematic"]
    assert sch_art["path"] == str(sch_json)
    assert len(sch_art["sha256"]) == 64
    assert sch_art["schema_version"] == "1.4.0"
    import re
    assert re.match(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$", sch_art["run_id"])

    pcb_art = upstream["pcb"]
    assert pcb_art["path"] == str(pcb_json)
    assert len(pcb_art["sha256"]) == 64
    assert pcb_art["schema_version"] == "1.4.0"
    assert re.match(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$", pcb_art["run_id"])

    # source_files should list both JSON paths.
    assert str(sch_json) in inputs["source_files"]
    assert str(pcb_json) in inputs["source_files"]


def test_thermal_compat_block_v1_4_defaults(tmp_path):
    """Track 1.4: every envelope emits a CompatBlock with v1.4 defaults."""
    sch_json = tmp_path / "sch.json"
    pcb_json = tmp_path / "pcb.json"
    sch_json.write_text(_run([str(SCHEMATIC), str(FIXTURE / "simple.kicad_sch")]))
    pcb_json.write_text(_run([str(PCB), str(FIXTURE / "simple.kicad_pcb")]))
    result = json.loads(_run([
        str(THERMAL), "--schematic", str(sch_json), "--pcb", str(pcb_json)
    ]))
    compat = result["compat"]
    assert compat["minimum_consumer_version"] == "1.4.0"
    assert compat["deprecated_fields"] == []
    assert compat["experimental_fields"] == []
