"""Layer 2 (merge_annotations) failure-mode coverage beyond HI-2/HI-6/HI-7.

Audit LOG 11 / regression-testing-audit F11 (2026-05-15): the existing
``test_layer2_invariants.py`` covers the happy-path invariants HI-2 (merge
only writes ``llm_review`` siblings), HI-6 (``reviewer_observations`` stay
out of ``findings[]``), and HI-7 (``capability_mode_ref`` present after
analyzer run). This file covers the FAILURE modes — the contracts that
fire when something goes wrong:

  * Suppression cap policy (HI-8 30%) — exceeded vs at-cap vs under
  * Invalid annotations — HI-9a suppress-error, HI-9b suppress-datasheet,
    orphan (finding_id not present), mixed
  * Merged-path contract — per-analyzer files, ``_merge_report.json``,
    HI-3 strip-round-trip embedded in ``merge()``
  * Schema validation (jsonschema/mini-validator) — missing required,
    bad type, bad enum, additionalProperties violation, reason<20 chars,
    reviewer_observations cap of 5
  * ``validate_review.py`` CLI exit-code matrix (rc=0/1/2)
  * ``strip_llm_overlays`` correctness — top-level + nested + list cases,
    no false positives on names merely *containing* "llm"
  * Empty/minimal cases — zero annotations, zero envelopes

Synthetic envelopes only, no analyzer runs (the E2E side is covered by
``tests/contract/test_layer2_invariants.py::test_hi7_*`` and
``tests/contract/test_action_format_report_v14.py``). NO TIER.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

REVIEW_SCRIPTS_DIR = MAIN_REPO_ROOT / "skills" / "kicad" / "review" / "scripts"
if str(REVIEW_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(REVIEW_SCRIPTS_DIR))

VALIDATE_REVIEW_CLI = REVIEW_SCRIPTS_DIR / "validate_review.py"


# ---------------------------------------------------------------------------
# Envelope + review builders — keep test bodies focused on the failure
# mode under test, not on synthesizing 40 lines of envelope boilerplate.
# ---------------------------------------------------------------------------

def _make_finding(rule_id="VM-001", refs=("U1",), *,
                  severity="warning", confidence="heuristic",
                  finding_id=None):
    """Minimal Phase 4 finding shape. ``finding_id`` defaults to
    ``sch:<rule_id>:<lowercase first ref>``."""
    fid = finding_id or f"sch:{rule_id}:{refs[0].lower()}"
    return {
        "finding_id": fid,
        "rule_id": rule_id,
        "detector": "test_detector",
        "category": "test",
        "severity": severity,
        "confidence": confidence,
        "evidence_source": "topology",
        "summary": "test finding",
        "components": list(refs),
    }


def _make_envelope(findings=None, *, run_id="x"):
    """Minimal Phase 4 envelope wrapper conforming to merge_annotations'
    expectations (every field merge() reads or strip-checks)."""
    return {
        "schema_version": "1.4.0",
        "schematic": {"file_format_version": "20240108"},
        "findings": list(findings or []),
        "assessments": [],
        "trust_summary": {
            "by_severity": {"error": 0, "warning": len(findings or []), "info": 0},
            "by_confidence": {}, "by_evidence_source": {},
            "bom_coverage": {"covered_pct": 100, "missing": []},
            "total": len(findings or []),
        },
        "inputs": {"source_files": [], "source_hashes": {}, "run_id": run_id,
                   "config_hash": None, "upstream_artifacts": {}},
        "compat": {"minimum_consumer_version": "1.4.0",
                   "deprecated_fields": [], "experimental_fields": []},
        "capability_mode_ref": {"source": "analysis/capability_mode.json",
                                "run_id": run_id},
    }


def _make_annotation(finding_id, status="confirmed", *,
                     suggested_severity=None,
                     reason="default reviewer rationale exceeding twenty chars",
                     confidence="medium"):
    """Minimal annotation conforming to review_annotations.schema.json."""
    ann = {
        "finding_id": finding_id,
        "status": status,
        "reason": reason,
        "confidence": confidence,
        "reviewed_at": "2026-04-27T12:00:00Z",
    }
    if suggested_severity:
        ann["suggested_severity"] = suggested_severity
    return ann


def _make_review(annotations=None, *, run_id="x", observations=None):
    return {
        "schema_version": "1.0",
        "produced_for_run_id": run_id,
        "produced_at": "2026-04-27T12:00:00Z",
        "annotations": list(annotations or []),
        "reviewer_observations": list(observations or []),
    }


def _stage(tmp_path, envelope_by_stem, review):
    """Write envelopes (keyed by stem) and review.json into ``tmp_path``
    in the layout merge() expects. Returns ``(raw_dir, review_path,
    merged_dir)`` ready to pass to ``merge()``."""
    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir(exist_ok=True)
    for stem, env in envelope_by_stem.items():
        (raw_dir / f"{stem}.json").write_text(json.dumps(env, sort_keys=True))
    review_path = raw_dir / "review.json"
    review_path.write_text(json.dumps(review))
    return raw_dir, review_path, raw_dir / "merged"


# ===========================================================================
# 1. Suppression cap policy — REMOVED in v2.0 (spec §5)
# ===========================================================================
# test_hi8_suppression_rate_exceeded_is_logged_but_not_unapplied — DELETED (spec §5):
#   The 30% suppression rate cap is removed; suppression_rate_exceeded violations
#   are no longer produced. Replaced by test_v2_suppression_cap_removed below.
# test_hi8_suppression_at_cap_does_not_trip — DELETED (spec §5): cap removed.
# test_hi8_zero_findings_no_cap_calculation_crash — kept as test_zero_findings_no_crash
#   (the empty-review / empty-envelope path still matters without the cap).

def test_v2_suppression_cap_removed(tmp_path):
    """v2.0 (spec §5): the 30% suppression rate cap is removed. Suppressing
    more than 30% of findings (e.g. 4/10 = 40%) must NOT produce a
    suppression_rate_exceeded invariant violation."""
    from merge_annotations import merge

    findings = [_make_finding(rule_id=f"X-{i:03d}", refs=(f"R{i}",),
                              finding_id=f"sch:X-{i:03d}:r{i}")
                for i in range(10)]
    envelope = _make_envelope(findings)
    # Suppress 4/10 (40%) — was previously capped at 30%
    annotations = [
        _make_annotation(f"sch:X-{i:03d}:r{i}", status="suppressed")
        for i in range(4)
    ]
    review = _make_review(annotations)
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)

    cap_violations = [v for v in report["invariant_violations"]
                      if v["type"] == "suppression_rate_exceeded"]
    assert len(cap_violations) == 0, (
        "suppression_rate_exceeded must not fire in v2.0 (cap removed, spec §5)"
    )
    # All 4 suppressions applied cleanly
    assert report["suppressed_count"] == 4
    assert report["applied_count"] == 4
    assert report["invariant_violations"] == []
    merged = json.loads((merged_dir / "schematic.json").read_text())
    suppressed_findings = [
        f for f in merged["findings"]
        if f.get("llm_review", {}).get("status") == "suppressed"
    ]
    assert len(suppressed_findings) == 4


def test_zero_findings_no_crash(tmp_path):
    """Edge: empty envelopes and empty reviews must not crash merge().
    (Kept from former test_hi8_zero_findings_no_cap_calculation_crash —
    the empty-path correctness doesn't depend on cap presence.)"""
    from merge_annotations import merge

    envelope = _make_envelope([])
    review = _make_review([])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    assert report["applied_count"] == 0
    assert report["suppressed_count"] == 0
    assert report["invariant_violations"] == []


# ===========================================================================
# 2. Annotations — orphan + mixed; authority guards REMOVED in v2.0 (spec §5)
# ===========================================================================
# test_hi9a_suppress_error_skipped_and_logged — DELETED (spec §5):
#   suppress_error guard removed; suppressing error-severity findings now applies.
#   Replaced by test_v2_suppressing_error_severity_applies below.
# test_hi9b_suppress_datasheet_backed_skipped_and_logged — DELETED (spec §5):
#   suppress_datasheet guard removed; suppressing datasheet-backed findings applies.
#   Replaced by test_v2_suppressing_datasheet_backed_applies below.

def test_v2_suppressing_error_severity_applies(tmp_path):
    """v2.0 (spec §5): suppressing a severity=error finding now applies the
    overlay (no authority guard). No suppress_error invariant_violation produced."""
    from merge_annotations import merge

    err_finding = _make_finding(rule_id="E-001", refs=("U1",), severity="error")
    envelope = _make_envelope([err_finding])
    ann = _make_annotation(err_finding["finding_id"], status="suppressed")
    review = _make_review([ann])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    err_violations = [v for v in report["invariant_violations"]
                      if v["type"] == "suppress_error"]
    assert len(err_violations) == 0, (
        "suppress_error guard must not fire in v2.0 (cap removed, spec §5)"
    )
    merged = json.loads((merged_dir / "schematic.json").read_text())
    assert merged["findings"][0].get("llm_review", {}).get("status") == "suppressed", (
        "suppress annotation must be applied to error-severity finding in v2.0"
    )
    assert report["applied_count"] == 1
    assert report["suppressed_count"] == 1
    assert report["invariant_violations"] == []


def test_v2_suppressing_datasheet_backed_applies(tmp_path):
    """v2.0 (spec §5): suppressing a confidence=datasheet-backed finding now
    applies the overlay. No suppress_datasheet invariant_violation produced."""
    from merge_annotations import merge

    ds_finding = _make_finding(rule_id="EX-001", refs=("C1",),
                                confidence="datasheet-backed")
    envelope = _make_envelope([ds_finding])
    ann = _make_annotation(ds_finding["finding_id"], status="suppressed")
    review = _make_review([ann])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    ds_violations = [v for v in report["invariant_violations"]
                     if v["type"] == "suppress_datasheet"]
    assert len(ds_violations) == 0, (
        "suppress_datasheet guard must not fire in v2.0 (cap removed, spec §5)"
    )
    merged = json.loads((merged_dir / "schematic.json").read_text())
    assert merged["findings"][0].get("llm_review", {}).get("status") == "suppressed"
    assert report["suppressed_count"] == 1
    assert report["invariant_violations"] == []


def test_orphan_annotation_skipped_and_logged(tmp_path):
    """Annotation referring to a finding_id not present in ANY envelope
    is an orphan: logged in ``orphan_annotations``, merge proceeds, other
    annotations still applied. Critical for reviewer-tooling robustness —
    a stale finding_id in a review shouldn't crash the merge."""
    from merge_annotations import merge

    real_finding = _make_finding(rule_id="A-001", refs=("U1",))
    envelope = _make_envelope([real_finding])
    annotations = [
        _make_annotation(real_finding["finding_id"]),
        _make_annotation("sch:GHOST-999:ghost"),  # no matching finding
    ]
    review = _make_review(annotations)
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    assert len(report["orphan_annotations"]) == 1
    assert report["orphan_annotations"][0]["finding_id"] == "sch:GHOST-999:ghost"
    assert report["applied_count"] == 1, "real annotation must still apply"


def test_mixed_annotations_all_apply_except_orphan(tmp_path):
    """v2.0 (spec §5): confirmed, suppressed-error, suppressed-datasheet all
    apply. Only an orphan (unknown finding_id) is logged and skipped.
    Renamed from test_mixed_violations_routed_correctly — the v1.4 suppress_error
    and suppress_datasheet guard buckets are gone."""
    from merge_annotations import merge

    f_normal = _make_finding(rule_id="A-001", refs=("U1",))
    f_err = _make_finding(rule_id="E-001", refs=("U2",), severity="error")
    f_ds = _make_finding(rule_id="EX-001", refs=("C1",),
                          confidence="datasheet-backed")
    envelope = _make_envelope([f_normal, f_err, f_ds])

    annotations = [
        _make_annotation(f_normal["finding_id"], status="confirmed"),
        _make_annotation(f_err["finding_id"], status="suppressed"),
        _make_annotation(f_ds["finding_id"], status="suppressed"),
        _make_annotation("sch:GHOST-999:ghost", status="suppressed"),
    ]
    review = _make_review(annotations)
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    # All 3 real findings applied (confirmed + 2 suppressed); orphan skipped
    assert report["applied_count"] == 3
    assert report["suppressed_count"] == 2
    assert len(report["orphan_annotations"]) == 1
    # No authority violations in v2.0
    assert report["invariant_violations"] == []


# ===========================================================================
# 3. Merged-path contract + HI-3 round-trip
# ===========================================================================

def test_merged_dir_contains_one_file_per_input_envelope_stem(tmp_path):
    """For every analyzer envelope present in ``raw_dir``, a file with
    the same stem MUST appear under ``merged_dir/``. Missing input
    envelopes don't appear as merged outputs (no synthesis)."""
    from merge_annotations import merge

    schem = _make_envelope([_make_finding(rule_id="A")])
    pcb = _make_envelope([_make_finding(rule_id="P", refs=("FP1",),
                                         finding_id="pcb:P:fp1")])
    review = _make_review([])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": schem, "pcb": pcb}, review
    )

    merge(raw_dir, review_path, merged_dir)
    written = sorted(p.name for p in merged_dir.glob("*.json"))
    # _merge_report.json is also in merged_dir, so it should appear too
    assert "schematic.json" in written
    assert "pcb.json" in written
    assert "_merge_report.json" in written
    # emc.json etc. were not staged → not synthesized
    assert "emc.json" not in written


def test_merge_report_has_all_expected_top_level_fields(tmp_path):
    """``_merge_report.json`` is the consumer-facing contract for what
    Layer 2 did. Locks the top-level shape so a refactor can't silently
    drop a field that downstream Layer 3/3a-active consumers rely on."""
    from merge_annotations import merge

    envelope = _make_envelope([_make_finding()])
    review = _make_review(
        [_make_annotation("sch:VM-001:u1")],
        observations=[{
            "origin": "llm_novel",
            "observation": "test obs",
            "severity": "info",
            "confidence": "medium",
            "reasoning": "a sufficiently long reasoning string exceeding 20 chars",
            "reviewed_at": "2026-04-27T12:00:00Z",
        }],
    )
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    merge(raw_dir, review_path, merged_dir)
    report = json.loads((merged_dir / "_merge_report.json").read_text())
    expected_keys = {
        "merged_at", "produced_for_run_id", "annotation_count",
        "applied_count", "suppressed_count", "orphan_annotations",
        "invariant_violations", "reviewer_observations_count",
    }
    assert set(report.keys()) == expected_keys, (
        f"unexpected report shape: extras={set(report.keys()) - expected_keys}, "
        f"missing={expected_keys - set(report.keys())}"
    )
    assert report["produced_for_run_id"] == "x"
    assert report["annotation_count"] == 1
    assert report["applied_count"] == 1
    assert report["reviewer_observations_count"] == 1


def test_hi3_round_trip_enforced_on_clean_merge(tmp_path):
    """HI-3: ``strip_llm_overlays(merged) == raw`` is a hard-check INSIDE
    merge() that raises RuntimeError on violation. Test the positive path:
    after a normal merge, the strip operation recovers the original raw
    envelope byte-for-byte (modulo JSON formatting normalization)."""
    from merge_annotations import merge, strip_llm_overlays

    envelope = _make_envelope([_make_finding()])
    review = _make_review([_make_annotation("sch:VM-001:u1")])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    merge(raw_dir, review_path, merged_dir)  # would raise on HI-3 violation
    merged = json.loads((merged_dir / "schematic.json").read_text())
    raw = json.loads((raw_dir / "schematic.json").read_text())
    assert strip_llm_overlays(merged) == raw


def test_merge_uses_deterministic_json_formatting(tmp_path):
    """Merged outputs MUST be written with sort_keys=True so that two
    merges of the same input produce byte-equal outputs. Required for
    downstream byte-comparison gates (e.g., the v1.4 default contract
    gate's run_id_linkage contract)."""
    from merge_annotations import merge

    envelope = _make_envelope([_make_finding(rule_id="A"), _make_finding(rule_id="B", refs=("U2",))])
    review = _make_review([])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    merge(raw_dir, review_path, merged_dir)
    first = (merged_dir / "schematic.json").read_text()
    # Re-merge (forces a fresh write)
    merge(raw_dir, review_path, merged_dir)
    second = (merged_dir / "schematic.json").read_text()
    assert first == second


# ===========================================================================
# 4. Schema validation (mini-validator via merge() and validate_review CLI)
# ===========================================================================

def test_schema_validation_rejects_missing_required_field(tmp_path):
    """Review missing ``produced_for_run_id`` → schema validation fails
    (hard-raise inside _validate_review_schema)."""
    from merge_annotations import merge

    envelope = _make_envelope([])
    review = _make_review([])
    review.pop("produced_for_run_id")
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    with pytest.raises(Exception) as exc:
        merge(raw_dir, review_path, merged_dir)
    assert "produced_for_run_id" in str(exc.value) or "required" in str(exc.value).lower()


def test_schema_validation_rejects_bad_schema_version_const(tmp_path):
    """schema_version is a const ('1.0'). Any other value fails validation."""
    from merge_annotations import merge

    envelope = _make_envelope([])
    review = _make_review([])
    review["schema_version"] = "2.0"
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    with pytest.raises(Exception):
        merge(raw_dir, review_path, merged_dir)


def test_schema_validation_rejects_reason_under_20_chars(tmp_path):
    """annotation.reason has minLength=20. Catches lazy reviewer rationale
    (one-word 'wrong' style reasons)."""
    from merge_annotations import merge

    envelope = _make_envelope([_make_finding()])
    review = _make_review([_make_annotation(
        "sch:VM-001:u1", reason="too short"
    )])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    with pytest.raises(Exception):
        merge(raw_dir, review_path, merged_dir)


def test_schema_validation_rejects_bad_status_enum(tmp_path):
    """annotation.status must be in {confirmed, suppressed, escalated}."""
    from merge_annotations import merge

    envelope = _make_envelope([_make_finding()])
    bad_ann = _make_annotation("sch:VM-001:u1")
    bad_ann["status"] = "deferred"  # not in enum
    review = _make_review([bad_ann])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    with pytest.raises(Exception):
        merge(raw_dir, review_path, merged_dir)


def test_schema_validation_rejects_additional_property_at_root(tmp_path):
    """additionalProperties: false at root — unknown top-level keys fail.
    Catches reviewer tooling that accidentally adds a non-schema field."""
    from merge_annotations import merge

    envelope = _make_envelope([])
    review = _make_review([])
    review["__debug"] = "leaked-from-tooling"
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    with pytest.raises(Exception):
        merge(raw_dir, review_path, merged_dir)


def test_schema_validation_allows_reviewer_observations_over_5(tmp_path):
    """v2.0 (spec §5): reviewer_observations no longer has maxItems=5.
    More than 5 observations must be accepted by the schema validator.
    (Renamed from test_schema_validation_rejects_reviewer_observations_over_cap.)"""
    from merge_annotations import merge

    envelope = _make_envelope([])
    obs = {
        "origin": "llm_novel",
        "observation": "x",
        "severity": "info",
        "confidence": "medium",
        "reasoning": "twenty-character-min reasoning text here.",
        "reviewed_at": "2026-04-27T12:00:00Z",
    }
    review = _make_review([], observations=[obs] * 6)  # was rejected pre-v2.0; now ok
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    # Must not raise — 6 observations are valid under the v2.0 schema
    report = merge(raw_dir, review_path, merged_dir)
    assert report["reviewer_observations_count"] == 6


# ===========================================================================
# 5. validate_review.py CLI exit-code matrix
# ===========================================================================

def _run_validate_cli(review_path, *, emit_json=False):
    cmd = [sys.executable, str(VALIDATE_REVIEW_CLI), "--review", str(review_path)]
    if emit_json:
        cmd.append("--json")
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def test_validate_cli_rc_zero_on_valid_review(tmp_path):
    """validate_review.py exit code 0 on a schema-valid review."""
    review_path = tmp_path / "r.json"
    review_path.write_text(json.dumps(_make_review([])))
    r = _run_validate_cli(review_path)
    assert r.returncode == 0, r.stderr
    assert str(review_path) in r.stdout


def test_validate_cli_rc_one_on_schema_invalid_review(tmp_path):
    """validate_review.py exit code 1 on schema-invalid review."""
    review_path = tmp_path / "r.json"
    bad = _make_review([])
    bad["schema_version"] = "9.9"  # const mismatch
    review_path.write_text(json.dumps(bad))
    r = _run_validate_cli(review_path)
    assert r.returncode == 1, (r.stdout, r.stderr)


def test_validate_cli_rc_two_on_missing_file(tmp_path):
    """validate_review.py exit code 2 on file-not-found."""
    r = _run_validate_cli(tmp_path / "does_not_exist.json")
    assert r.returncode == 2


def test_validate_cli_rc_two_on_malformed_json(tmp_path):
    """validate_review.py exit code 2 on un-parseable JSON."""
    review_path = tmp_path / "r.json"
    review_path.write_text("{not valid json")
    r = _run_validate_cli(review_path)
    assert r.returncode == 2


def test_validate_cli_json_output_shape_on_invalid_review(tmp_path):
    """--json flag produces structured {valid, errors, review_path}.
    Important for tool-driven workflows that parse the result."""
    review_path = tmp_path / "r.json"
    bad = _make_review([])
    bad.pop("produced_for_run_id")
    review_path.write_text(json.dumps(bad))
    r = _run_validate_cli(review_path, emit_json=True)
    assert r.returncode == 1
    out = json.loads(r.stdout)
    assert out["valid"] is False
    assert isinstance(out["errors"], list) and len(out["errors"]) >= 1
    assert out["review_path"] == str(review_path)


# ===========================================================================
# 6. strip_llm_overlays correctness — no false positives, no false negatives
# ===========================================================================

def test_strip_removes_top_level_llm_keys():
    from merge_annotations import strip_llm_overlays
    inp = {"a": 1, "llm_x": 2, "b": 3}
    assert strip_llm_overlays(inp) == {"a": 1, "b": 3}


def test_strip_removes_nested_llm_keys():
    from merge_annotations import strip_llm_overlays
    inp = {"outer": {"inner": {"llm_secret": "x", "kept": 1}, "llm_skip": 2}}
    out = strip_llm_overlays(inp)
    assert out == {"outer": {"inner": {"kept": 1}}}


def test_strip_handles_lists_of_dicts():
    from merge_annotations import strip_llm_overlays
    inp = {"items": [{"k": 1, "llm_v": 2}, {"k": 3, "llm_v": 4}]}
    out = strip_llm_overlays(inp)
    assert out == {"items": [{"k": 1}, {"k": 3}]}


def test_strip_does_not_remove_keys_merely_containing_llm():
    """Only keys STARTING with 'llm_' are stripped. A field named
    'pull_models' or 'allow_llm' or 'llm' (no underscore) must survive.
    Guards against an overzealous substring match regression."""
    from merge_annotations import strip_llm_overlays
    inp = {
        "pull_models": ["llm-a", "llm-b"],
        "allow_llm": True,
        "llm": "no_underscore",  # bare 'llm' shouldn't match 'llm_*'
        "llm_review": "should be removed",
    }
    out = strip_llm_overlays(inp)
    assert "pull_models" in out
    assert "allow_llm" in out
    assert "llm" in out
    assert "llm_review" not in out


def test_strip_preserves_top_level_reason_field_when_llm_review_removed():
    """A top-level ``reason`` key on a finding must survive even though
    ``llm_review`` (which has a nested ``reason``) is removed. The strip
    is by KEY NAME, not by content."""
    from merge_annotations import strip_llm_overlays
    finding = {
        "rule_id": "X-001",
        "reason": "detector's own reason",
        "llm_review": {"reason": "reviewer's rationale", "status": "confirmed"},
    }
    out = strip_llm_overlays(finding)
    assert out == {"rule_id": "X-001", "reason": "detector's own reason"}


def test_strip_passthrough_on_primitives():
    from merge_annotations import strip_llm_overlays
    assert strip_llm_overlays(42) == 42
    assert strip_llm_overlays("hello") == "hello"
    assert strip_llm_overlays(None) is None
    assert strip_llm_overlays([1, 2, 3]) == [1, 2, 3]


# ===========================================================================
# 7. Empty / minimal cases
# ===========================================================================

def test_empty_annotations_produces_byte_equal_merged_envelope(tmp_path):
    """A review with annotations=[] still triggers a merge — but the merged
    output should match the raw envelope byte-for-byte after the strip
    round-trip. (Verbatim copy isn't promised due to JSON re-serialization
    with sort_keys; round-trip equivalence IS.)"""
    from merge_annotations import merge, strip_llm_overlays

    envelope = _make_envelope([_make_finding()])
    review = _make_review([])
    raw_dir, review_path, merged_dir = _stage(
        tmp_path, {"schematic": envelope}, review
    )

    report = merge(raw_dir, review_path, merged_dir)
    assert report["applied_count"] == 0
    merged = json.loads((merged_dir / "schematic.json").read_text())
    raw = json.loads((raw_dir / "schematic.json").read_text())
    assert strip_llm_overlays(merged) == raw


def test_no_envelopes_present_merge_still_succeeds(tmp_path):
    """If raw_dir contains no analyzer JSON files, merge() should run
    without crashing — produces an empty merged_dir (just the report)."""
    from merge_annotations import merge

    raw_dir = tmp_path / "analysis"
    raw_dir.mkdir()
    review_path = raw_dir / "review.json"
    review_path.write_text(json.dumps(_make_review([])))
    merged_dir = raw_dir / "merged"

    report = merge(raw_dir, review_path, merged_dir)
    assert report["applied_count"] == 0
    assert report["suppressed_count"] == 0
    # No analyzer envelopes → no merged files; just the report
    assert (merged_dir / "_merge_report.json").is_file()
    assert sorted(p.name for p in merged_dir.glob("*.json")) == ["_merge_report.json"]
