"""Contract tests for skills/kicad/review/scripts/merge_annotations.py."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))


def _make_envelope(findings):
    """Minimal valid v1.4 envelope shape."""
    return {
        "schema_version": "1.4.0",
        "schematic": {"file_format_version": "20240108"},
        "findings": findings,
        "assessments": [],
        "trust_summary": {
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "by_confidence": {"datasheet-backed": 0, "deterministic": 0, "heuristic": 0},
            "by_evidence_source": {},
            "bom_coverage": {"covered_pct": 100, "missing": []},
            "total": 0,
        },
        "inputs": {"source_files": [], "source_hashes": {}, "run_id": "20260427T120000Z-aaaaaa",
                    "config_hash": None, "upstream_artifacts": {}},
        "compat": {"minimum_consumer_version": "1.4.0", "deprecated_fields": [], "experimental_fields": []},
        "capability_mode_ref": {"source": "analysis/capability_mode.json",
                                  "run_id": "20260427T120000Z-aaaaaa"},
    }


def _make_finding(finding_id, severity="warning", confidence="heuristic"):
    return {
        "finding_id": finding_id,
        "rule_id": finding_id.split(":")[1],
        "detector": "test_detector",
        "category": "test",
        "severity": severity,
        "confidence": confidence,
        "evidence_source": "topology",
        "summary": "Test finding " + finding_id,
        "components": [finding_id.split(":")[-1].upper()],
    }


def test_merge_applies_overlay_to_matching_finding(tmp_path):
    from merge_annotations import merge

    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = _make_envelope([_make_finding("sch:VM-001:u1")])
    (raw_dir / "schematic.json").write_text(json.dumps(env))

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": "20260427T120000Z-aaaaaa",
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": [{
            "finding_id": "sch:VM-001:u1",
            "status": "confirmed",
            "reason": "Confirmed via design context analysis (>20 chars).",
            "confidence": "high",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
        "reviewer_observations": [],
    }
    review_path = raw_dir / "review_annotations.json"
    review_path.write_text(json.dumps(review))

    report = merge(raw_dir, review_path, merged_dir)

    merged_env = json.loads((merged_dir / "schematic.json").read_text())
    assert merged_env["findings"][0]["llm_review"]["status"] == "confirmed"
    assert report["annotation_count"] == 1
    assert report["suppressed_count"] == 0
    assert report["orphan_annotations"] == []
    assert report["invariant_violations"] == []


def test_merge_skips_orphan_annotation(tmp_path):
    from merge_annotations import merge
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = _make_envelope([_make_finding("sch:VM-001:u1")])
    (raw_dir / "schematic.json").write_text(json.dumps(env))

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": "x",
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": [{
            "finding_id": "sch:VM-001:nonexistent",
            "status": "confirmed",
            "reason": "Annotation references non-existent finding.",
            "confidence": "high",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
        "reviewer_observations": [],
    }
    review_path = raw_dir / "review_annotations.json"
    review_path.write_text(json.dumps(review))

    report = merge(raw_dir, review_path, merged_dir)
    assert len(report["orphan_annotations"]) == 1
    assert report["orphan_annotations"][0]["finding_id"] == "sch:VM-001:nonexistent"
    # Merge succeeded; existing finding unchanged
    merged_env = json.loads((merged_dir / "schematic.json").read_text())
    assert "llm_review" not in merged_env["findings"][0]


def test_merge_applies_suppress_on_error_severity(tmp_path):
    """v2.0 (spec §5): suppressing an error-severity finding applies the overlay.
    No suppress_error invariant_violation produced.
    (Renamed from test_merge_blocks_suppress_on_error_severity.)"""
    from merge_annotations import merge
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = _make_envelope([_make_finding("sch:AM-001:u1", severity="error")])
    (raw_dir / "schematic.json").write_text(json.dumps(env))

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": "x",
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": [{
            "finding_id": "sch:AM-001:u1",
            "status": "suppressed",
            "reason": "Reviewer suppresses error-severity finding (now allowed, spec §5).",
            "confidence": "high",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
        "reviewer_observations": [],
    }
    review_path = raw_dir / "review_annotations.json"
    review_path.write_text(json.dumps(review))

    report = merge(raw_dir, review_path, merged_dir)
    assert not any(v["type"] == "suppress_error" for v in report["invariant_violations"])
    merged_env = json.loads((merged_dir / "schematic.json").read_text())
    assert merged_env["findings"][0].get("llm_review", {}).get("status") == "suppressed"
    assert report["applied_count"] == 1
    assert report["suppressed_count"] == 1


def test_merge_applies_suppress_on_datasheet_backed(tmp_path):
    """v2.0 (spec §5): suppressing a datasheet-backed finding applies the overlay.
    No suppress_datasheet invariant_violation produced.
    (Renamed from test_merge_blocks_suppress_on_datasheet_backed.)"""
    from merge_annotations import merge
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = _make_envelope([_make_finding("sch:VM-001:u1", confidence="datasheet-backed")])
    (raw_dir / "schematic.json").write_text(json.dumps(env))

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": "x",
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": [{
            "finding_id": "sch:VM-001:u1",
            "status": "suppressed",
            "reason": "Reviewer suppresses datasheet-backed finding (now allowed, spec §5).",
            "confidence": "high",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
        "reviewer_observations": [],
    }
    review_path = raw_dir / "review_annotations.json"
    review_path.write_text(json.dumps(review))

    report = merge(raw_dir, review_path, merged_dir)
    assert not any(v["type"] == "suppress_datasheet" for v in report["invariant_violations"])
    merged_env = json.loads((merged_dir / "schematic.json").read_text())
    assert merged_env["findings"][0].get("llm_review", {}).get("status") == "suppressed"
    assert report["suppressed_count"] == 1


def test_merge_no_30pct_suppression_rate_limit(tmp_path):
    """v2.0 (spec §5): the 30% suppression rate cap is removed. Suppressing
    4/10 findings (40%) must not produce a suppression_rate_exceeded violation.
    (Renamed from test_merge_enforces_30pct_suppression_rate_limit.)"""
    from merge_annotations import merge
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    findings = [_make_finding(f"sch:R-1:u{i}", severity="warning") for i in range(10)]
    env = _make_envelope(findings)
    (raw_dir / "schematic.json").write_text(json.dumps(env))

    # 4 of 10 = 40% suppression — was previously capped at 30%
    annotations = [{
        "finding_id": f"sch:R-1:u{i}",
        "status": "suppressed",
        "reason": "Test suppression — cap removed in v2.0 (spec §5).",
        "confidence": "medium",
        "reviewed_at": "2026-04-27T12:00:00Z",
    } for i in range(4)]
    review = {"schema_version": "1.0", "produced_for_run_id": "x",
               "produced_at": "2026-04-27T12:00:00Z",
               "annotations": annotations, "reviewer_observations": []}
    (raw_dir / "review_annotations.json").write_text(json.dumps(review))
    report = merge(raw_dir, raw_dir / "review_annotations.json", merged_dir)

    rate_violations = [v for v in report["invariant_violations"]
                        if v["type"] == "suppression_rate_exceeded"]
    assert len(rate_violations) == 0
    assert report["suppressed_count"] == 4
    assert report["invariant_violations"] == []


def test_merge_strip_round_trip_byte_identical(tmp_path):
    """HI-3: stripping merged output yields byte-identical raw."""
    from merge_annotations import merge, strip_llm_overlays
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    merged_dir = raw_dir / "merged"

    env = _make_envelope([_make_finding("sch:VM-001:u1")])
    (raw_dir / "schematic.json").write_text(json.dumps(env, sort_keys=True))

    review = {
        "schema_version": "1.0",
        "produced_for_run_id": "x",
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": [{
            "finding_id": "sch:VM-001:u1",
            "status": "confirmed",
            "reason": "Confirmed via design context analysis (>20 chars).",
            "confidence": "high",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
        "reviewer_observations": [],
    }
    (raw_dir / "review_annotations.json").write_text(json.dumps(review))

    merge(raw_dir, raw_dir / "review_annotations.json", merged_dir)

    merged = json.loads((merged_dir / "schematic.json").read_text())
    raw = json.loads((raw_dir / "schematic.json").read_text())
    stripped = strip_llm_overlays(merged)
    assert stripped == raw
