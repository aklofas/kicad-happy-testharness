"""Contract tests for Phase 4 Layer 2 hard invariants HI-2, HI-6, HI-7."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))


def test_hi2_merge_only_writes_llm_review_field(tmp_path):
    """HI-2: merge_annotations only adds llm_review siblings; no detector field mutated."""
    from merge_annotations import merge

    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    finding = {
        "finding_id": "sch:VM-001:u1",
        "rule_id": "VM-001", "detector": "test", "category": "test",
        "severity": "warning", "confidence": "heuristic",
        "evidence_source": "topology", "summary": "test",
        "components": ["U1"],
    }
    env = {
        "schema_version": "1.4.0",
        "schematic": {"file_format_version": "20240108"},
        "findings": [finding],
        "assessments": [],
        "trust_summary": {"by_severity": {"error": 0, "warning": 1, "info": 0},
                           "by_confidence": {}, "by_evidence_source": {},
                           "bom_coverage": {"covered_pct": 100, "missing": []}, "total": 1},
        "inputs": {"source_files": [], "source_hashes": {}, "run_id": "x",
                    "config_hash": None, "upstream_artifacts": {}},
        "compat": {"minimum_consumer_version": "1.4.0", "deprecated_fields": [], "experimental_fields": []},
        "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": "x"},
    }
    (raw_dir / "schematic.json").write_text(json.dumps(env, sort_keys=True))

    review = {"schema_version": "1.0", "produced_for_run_id": "x",
               "produced_at": "2026-04-27T12:00:00Z",
               "annotations": [{
                   "finding_id": "sch:VM-001:u1",
                   "status": "escalated",
                   "reason": "Reviewer escalates to error severity (>20 char rationale).",
                   "confidence": "high",
                   "suggested_severity": "error",
                   "reviewed_at": "2026-04-27T12:00:00Z",
               }],
               "reviewer_observations": []}
    (raw_dir / "review.json").write_text(json.dumps(review))

    merge(raw_dir, raw_dir / "review.json", merged_dir)
    merged = json.loads((merged_dir / "schematic.json").read_text())
    f = merged["findings"][0]
    # All detector-owned fields unchanged (HI-2)
    assert f["rule_id"] == "VM-001"
    assert f["severity"] == "warning"  # NOT mutated to error despite escalation
    assert f["confidence"] == "heuristic"
    assert f["evidence_source"] == "topology"
    assert f["summary"] == "test"
    # Only the sibling llm_review field is added
    assert f["llm_review"]["status"] == "escalated"
    assert f["llm_review"]["suggested_severity"] == "error"


def test_hi6_reviewer_observations_never_in_findings_array(tmp_path):
    """HI-6: reviewer_observations live in review_annotations.json, never merged into findings[]."""
    from merge_annotations import merge

    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = {
        "schema_version": "1.4.0",
        "schematic": {"file_format_version": "20240108"},
        "findings": [],
        "assessments": [],
        "trust_summary": {"by_severity": {"error": 0, "warning": 0, "info": 0},
                           "by_confidence": {}, "by_evidence_source": {},
                           "bom_coverage": {"covered_pct": 100, "missing": []}, "total": 0},
        "inputs": {"source_files": [], "source_hashes": {}, "run_id": "x",
                    "config_hash": None, "upstream_artifacts": {}},
        "compat": {"minimum_consumer_version": "1.4.0", "deprecated_fields": [], "experimental_fields": []},
        "capability_mode_ref": {"source": "analysis/capability_mode.json", "run_id": "x"},
    }
    (raw_dir / "schematic.json").write_text(json.dumps(env, sort_keys=True))

    review = {"schema_version": "1.0", "produced_for_run_id": "x",
               "produced_at": "2026-04-27T12:00:00Z",
               "annotations": [],
               "reviewer_observations": [{
                   "origin": "llm_novel",
                   "observation": "Switching freq harmonic may overlap BLE band",
                   "severity": "warning",
                   "confidence": "medium",
                   "reasoning": "Regulator at 400kHz; 6000th harmonic in 2.4 GHz band (>20 chars).",
                   "reviewed_at": "2026-04-27T12:00:00Z",
               }]}
    (raw_dir / "review.json").write_text(json.dumps(review))

    merge(raw_dir, raw_dir / "review.json", merged_dir)
    merged = json.loads((merged_dir / "schematic.json").read_text())
    # Findings array stays empty; observations NOT promoted into findings[]
    assert merged["findings"] == []


def test_hi7_capability_mode_ref_present_after_analyzer_run(tmp_path):
    """HI-7: every analyzer envelope has capability_mode_ref top-level field."""
    import subprocess
    fx = HARNESS_ROOT / "tests" / "fixtures" / "simple-project"
    sch_files = list(fx.glob("*.kicad_sch"))
    if not sch_files:
        pytest.skip("simple-project fixture missing")
    output = tmp_path / "analysis" / "schematic.json"
    subprocess.run(
        ["python3", "skills/kicad/scripts/analyze_schematic.py",
         str(sch_files[0]), "--output", str(output)],
        check=True, cwd=MAIN_REPO_ROOT,
    )
    data = json.loads(output.read_text())
    assert "capability_mode_ref" in data
    assert data["capability_mode_ref"]["source"] == "analysis/capability_mode.json"
    assert data["capability_mode_ref"]["run_id"]
    cm_path = tmp_path / "analysis" / "capability_mode.json"
    assert cm_path.exists()
    cm = json.loads(cm_path.read_text())
    assert cm["run_id"] == data["capability_mode_ref"]["run_id"]
