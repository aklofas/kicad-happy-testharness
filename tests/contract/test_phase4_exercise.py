"""Contract tests for Phase 4 4d-active end-to-end exercise outputs.

Skips when the gitignored fixture is absent (CI without harness corpus).
"""
from __future__ import annotations

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import json
import sys
from pathlib import Path

import pytest

FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "phase4-review"
ANALYSIS = FIXTURE / "analysis"
MERGED = ANALYSIS / "merged"
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"))


def _skip_if_fixture_missing():
    if not FIXTURE.exists() or not ANALYSIS.exists():
        pytest.skip("phase4-review fixture missing (gitignored)")


def _skip_if_merge_missing():
    _skip_if_fixture_missing()
    if not MERGED.exists():
        pytest.skip("merge step not yet executed")


# ---------- HI-3: strip_llm_overlays(merged) byte-identical to raw ----------

def test_hi3_strip_llm_byte_identical_on_real_fixture():
    _skip_if_merge_missing()
    from merge_annotations import strip_llm_overlays  # type: ignore[import-not-found]
    asserted = 0
    for fname in ["schematic.json", "pcb.json", "emc.json", "thermal.json", "cross_analysis.json"]:
        merged_path = MERGED / fname
        raw_path = ANALYSIS / fname
        if not merged_path.exists() or not raw_path.exists():
            continue
        merged = json.loads(merged_path.read_text())
        raw = json.loads(raw_path.read_text())
        assert strip_llm_overlays(merged) == raw, f"HI-3 violation on {fname}"
        asserted += 1
    assert asserted >= 1, "Exercise must have produced ≥1 merged envelope"


# ---------- HI-2: overlay-only — finding counts preserved ----------

def test_hi2_finding_counts_preserved_across_merge():
    _skip_if_merge_missing()
    for fname in ["schematic.json", "pcb.json", "emc.json", "thermal.json", "cross_analysis.json"]:
        merged_path = MERGED / fname
        raw_path = ANALYSIS / fname
        if not merged_path.exists() or not raw_path.exists():
            continue
        merged = json.loads(merged_path.read_text())
        raw = json.loads(raw_path.read_text())
        assert len(merged.get("findings", [])) == len(raw.get("findings", [])), (
            f"HI-2 violation: merged/{fname} finding count differs from raw")


# ---------- HI-8: 0 invariant violations on a passing exercise ----------

def test_hi8_invariant_violations_zero_on_real_fixture():
    _skip_if_merge_missing()
    report_path = MERGED / "_merge_report.json"
    if not report_path.exists():
        pytest.skip("merge report missing")
    report = json.loads(report_path.read_text())
    assert report.get("invariant_violations", []) == [], (
        f"HI-8 invariant violations: {report.get('invariant_violations')}")


# ---------- HI-7: capability_mode_ref present on every envelope ----------

def test_hi7_capability_mode_ref_consistent_across_envelopes():
    _skip_if_fixture_missing()
    cm_path = ANALYSIS / "capability_mode.json"
    if not cm_path.exists():
        pytest.skip("capability_mode.json missing")
    cm = json.loads(cm_path.read_text())
    canonical_run_id = cm["run_id"]
    asserted = 0
    for fname in ["schematic.json", "pcb.json", "emc.json", "thermal.json", "cross_analysis.json"]:
        path = ANALYSIS / fname
        if not path.exists():
            continue
        env = json.loads(path.read_text())
        ref = env.get("capability_mode_ref") or {}
        assert ref.get("run_id") == canonical_run_id, (
            f"{fname} capability_mode_ref.run_id mismatch")
        asserted += 1
    assert asserted >= 1


# ---------- 4b/4c sanity: ≥1 schema_era="v1.4" finding fired ----------

def test_phase4_finding_set_includes_v1_4_schema_era_tags():
    _skip_if_fixture_missing()
    sch_path = ANALYSIS / "schematic.json"
    if not sch_path.exists():
        pytest.skip("schematic.json missing")
    sch = json.loads(sch_path.read_text())
    v14 = [f for f in sch.get("findings", []) if f.get("schema_era") == "v1.4"]
    assert len(v14) >= 1, (
        "No schema_era='v1.4' findings — 4b/4c detectors didn't fire on fixture")


# ---------- design_context: schema-valid ----------

def test_design_context_validates_against_schema():
    _skip_if_fixture_missing()
    dc_path = ANALYSIS / "design_context.json"
    if not dc_path.exists():
        pytest.skip("design_context not yet produced")
    from jsonschema import Draft202012Validator
    schema = json.loads((MAIN_REPO_ROOT / "skills" / "kicad" / "review"
                          / "schemas" / "design_context.schema.json").read_text())
    dc = json.loads(dc_path.read_text())
    Draft202012Validator(schema).validate(dc)


# ---------- review_annotations: schema-valid ----------

def test_review_annotations_validates_against_schema():
    _skip_if_fixture_missing()
    review_path = ANALYSIS / "review_annotations.json"
    if not review_path.exists():
        pytest.skip("review_annotations not yet produced")
    from jsonschema import Draft202012Validator
    schema = json.loads((MAIN_REPO_ROOT / "skills" / "kicad" / "review"
                          / "schemas" / "review_annotations.schema.json").read_text())
    review = json.loads(review_path.read_text())
    Draft202012Validator(schema).validate(review)


# ---------- review_annotations: produced_for_run_id matches capability_mode ----------

def test_review_annotations_produced_for_canonical_run_id():
    _skip_if_fixture_missing()
    cm_path = ANALYSIS / "capability_mode.json"
    review_path = ANALYSIS / "review_annotations.json"
    if not cm_path.exists() or not review_path.exists():
        pytest.skip("capability_mode or review_annotations not yet produced")
    cm = json.loads(cm_path.read_text())
    review = json.loads(review_path.read_text())
    assert review["produced_for_run_id"] == cm["run_id"], (
        "review_annotations.produced_for_run_id must match capability_mode.run_id")
