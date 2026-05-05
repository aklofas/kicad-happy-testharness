"""Tests for shared envelope primitives."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from schema_codec import dataclass_to_json_schema  # noqa: E402
from analyzer_envelope import (  # noqa: E402
    TrustSummary,
    ByConfidence,
    ByEvidenceSource,
    BySeverity,
    BomCoverage,
    TitleBlock,
    Finding,
    Assessment,
    UpstreamArtifact,
    InputsBlock,
    CompatBlock,
)
from jsonschema import Draft202012Validator  # noqa: E402


def _assert_valid(cls):
    schema = dataclass_to_json_schema(cls)
    Draft202012Validator.check_schema(schema)
    return schema


def test_by_confidence_shape():
    schema = _assert_valid(ByConfidence)
    props = schema["properties"]
    assert props["deterministic"]["type"] == "integer"
    assert props["heuristic"]["type"] == "integer"
    assert props["datasheet_backed"]["type"] == "integer"


def test_by_severity_matches_v1_3_vocab():
    schema = _assert_valid(BySeverity)
    assert set(schema["properties"].keys()) == {"error", "warning", "info"}


def test_trust_summary_fields():
    schema = _assert_valid(TrustSummary)
    props = schema["properties"]
    assert props["total_findings"]["type"] == "integer"
    assert props["trust_level"]["type"] == "string"
    assert props["by_confidence"]["type"] == "object"
    assert props["by_evidence_source"]["type"] == "object"
    # provenance_coverage_pct is Optional[float] — None when total_findings==0
    assert props["provenance_coverage_pct"]["anyOf"] == [
        {"type": "number"}, {"type": "null"}]
    assert "provenance_coverage_pct" not in schema["required"]
    # bom_coverage is schematic-only -> optional
    assert "bom_coverage" not in schema["required"]


def test_finding_required_fields():
    schema = _assert_valid(Finding)
    required = set(schema["required"])
    # Per v1.3 rich finding contract — these must always be present.
    assert "detector" in required
    assert "rule_id" in required
    assert "severity" in required
    assert "confidence" in required
    assert "evidence_source" in required
    assert "summary" in required


def test_title_block_all_optional():
    schema = _assert_valid(TitleBlock)
    # Title block fields are all optional (may be blank in a given .kicad_sch)
    assert schema["required"] == []


def test_assessment_required_fields():
    schema = _assert_valid(Assessment)
    required = set(schema["required"])
    # Assessments are informational measurements — they carry detector/rule_id
    # context, confidence, evidence source, and a summary. They do NOT carry
    # severity or recommendation (those are Finding-only).
    assert required == {"detector", "rule_id", "confidence", "evidence_source", "summary"}


def test_assessment_has_no_severity_or_recommendation():
    schema = _assert_valid(Assessment)
    props = schema["properties"]
    assert "severity" not in props, "Assessment must not declare severity"
    assert "recommendation" not in props, "Assessment must not declare recommendation"


def test_assessment_has_extra_for_domain_specific_measurements():
    schema = _assert_valid(Assessment)
    props = schema["properties"]
    assert "extra" in props, "Assessment must declare extra field for domain measurements"
    # extra is Optional[dict] -> anyOf[object, null]
    assert "extra" not in schema["required"]


def test_upstream_artifact_required_fields():
    schema = _assert_valid(UpstreamArtifact)
    required = set(schema["required"])
    # Every upstream artifact reference must name a file (path) and a
    # sha256 so consumers can verify the upstream hasn't drifted since
    # this run consumed it. schema_version and run_id are required too
    # so cross-run provenance can be walked.
    assert required == {"path", "sha256", "schema_version", "run_id"}


def test_inputs_block_required_fields():
    schema = _assert_valid(InputsBlock)
    required = set(schema["required"])
    assert required == {
        "source_files",
        "source_hashes",
        "run_id",
        "upstream_artifacts",
    }
    # config_hash is optional: not every project uses .kicad-happy.json.
    assert "config_hash" in schema["properties"]
    assert "config_hash" not in required


def test_inputs_block_upstream_artifacts_is_dict_of_upstream_artifact():
    schema = _assert_valid(InputsBlock)
    # upstream_artifacts is dict[str, UpstreamArtifact] — keyed by stage name
    # (e.g. "schematic", "pcb"). dict[str, T] serializes as
    # {"type": "object", "additionalProperties": <T>}.
    prop = schema["properties"]["upstream_artifacts"]
    assert prop["type"] == "object"
    assert prop["additionalProperties"]["type"] == "object"
    ua_required = set(prop["additionalProperties"]["required"])
    assert ua_required == {"path", "sha256", "schema_version", "run_id"}


def test_compat_block_required_fields():
    schema = _assert_valid(CompatBlock)
    required = set(schema["required"])
    # All three fields are required at v1.4 — consumers rely on their
    # presence even when the lists are empty.
    assert required == {
        "minimum_consumer_version",
        "deprecated_fields",
        "experimental_fields",
    }


def test_compat_block_list_fields_are_str_arrays():
    schema = _assert_valid(CompatBlock)
    props = schema["properties"]
    # deprecated_fields / experimental_fields are simple lists of
    # dotted-path strings identifying envelope keys.
    assert props["deprecated_fields"]["type"] == "array"
    assert props["deprecated_fields"]["items"] == {"type": "string"}
    assert props["experimental_fields"]["type"] == "array"
    assert props["experimental_fields"]["items"] == {"type": "string"}


@pytest.mark.parametrize("cls", [
    ByConfidence, ByEvidenceSource, BySeverity, BomCoverage,
    TrustSummary, TitleBlock, Finding, Assessment,
    UpstreamArtifact, InputsBlock, CompatBlock,
])
def test_all_primitives_round_trip_through_codec(cls):
    """Every shared primitive must produce a valid Draft 2020-12 schema."""
    schema = dataclass_to_json_schema(cls)
    Draft202012Validator.check_schema(schema)
    # Basic envelope invariants
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["title"] == cls.__name__
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema
