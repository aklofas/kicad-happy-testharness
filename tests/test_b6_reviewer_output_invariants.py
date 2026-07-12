"""B6 reviewer-output regression coverage (Phase 4 Layer 2).

Per main-repo handoff (LOG #80 ask c). The reviewer.md prompt at
`skills/kicad/review/prompts/reviewer.md` is the spec source-of-truth.
review_annotations.schema.json captures the JSON shape; this file
asserts behavioral invariants that the schema doesn't formally enforce.

**Replay seed** — `tests/fixtures/phase4-review-trace/` carries the real
GNSSDO Phase 4d-active exercise output (run_id 20260504T070303Z-12b692,
10 annotations / 6 confirmed / 4 suppressed / 0 escalated, captured
2026-05-03 via Task 35 subagent dispatch). The trace is the seed for
behavioral assertions; mutation-style tests deepcopy it and twiddle one
field to exercise the negative case.

**Invariants tested** (LOG #80 ask c):

  1. produced_for_run_id format `YYYYMMDDTHHMMSSZ-<6hex>` matches
     run_id.py generator pattern.
  2. produced_for_run_id linkage: review_annotations.produced_for_run_id
     === capability_mode.run_id === _merge_report.produced_for_run_id.
  3. annotation reason minLength 20 chars (schema-enforced; test
     re-asserts behaviorally + checks that mutation to a short string
     would fail the same way schema validation does).
  4. suggested_severity ↔ status coupling per reviewer.md line 71:
       (a) status=='escalated' → suggested_severity MUST equal 'error'
       (b) status=='confirmed'|'suppressed' → suggested_severity MUST
           be omitted (not present in dict)
  5. reviewer_observations: [] empty array when capability_mode says
     reviewer_observations_enabled=false (v1.4 default).
  6. finding_id duplicate-allowed counter-example: real trace has two
     annotations targeting `sch:PR-001:u18` (SCL + SDA pull-up
     companions on the same I2C segment). The merge logic accepts
     duplicates; B6 must not assert per-finding uniqueness.

Plus structural sanity:

  7. _merge_report.annotation_count equals len(annotations) in the
     trace.
  8. _merge_report.suppressed_count equals the count of annotations
     with status=='suppressed'.
  9. JSON-Schema validation of the real trace against
     review_annotations.schema.json (skips cleanly when jsonschema
     library is absent).

v1.5 carry-overs flagged in main-repo notes (LOG #80, #82):
  - Schema-tighten suggested_severity ↔ status='escalated' coupling
    formally (today the rule lives in prose in reviewer.md only).
  - Raw-dict → make_finding migration: 4 of 6 analyzers (pcb / thermal
    / emc / gerber) emit findings with `finding_id: null`, so the
    addressable annotation set is hard-capped at the schematic +
    cross_analysis subset. v1.5 widening unlocks the rest.
"""
from __future__ import annotations

TIER = "unit"

import copy
import json
import os
import re
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
TRACE_DIR = HARNESS_DIR / "tests" / "fixtures" / "phase4-review-trace"
SCHEMA_PATH = (KH_DIR / "skills" / "kicad" / "review" / "schemas"
               / "review_annotations.schema.json")

ANNOTATIONS_PATH = TRACE_DIR / "review_annotations.json"
MERGE_REPORT_PATH = TRACE_DIR / "_merge_report.json"
CAPABILITY_MODE_PATH = TRACE_DIR / "capability_mode.json"

# run_id.py emits this exact pattern (LOG #65, schema_codec.py).
RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{6}$")


def _load_trace():
    """Load (annotations, merge_report, capability_mode). Returns 3-tuple
    of None when any fixture is missing — test should early-return."""
    if not (ANNOTATIONS_PATH.is_file() and MERGE_REPORT_PATH.is_file()
            and CAPABILITY_MODE_PATH.is_file()):
        return None, None, None
    return (
        json.loads(ANNOTATIONS_PATH.read_text()),
        json.loads(MERGE_REPORT_PATH.read_text()),
        json.loads(CAPABILITY_MODE_PATH.read_text()),
    )


def _try_jsonschema():
    """Return jsonschema module or None when unavailable."""
    try:
        import jsonschema
        return jsonschema
    except ImportError:
        return None


def _check_severity_coupling(annotation: dict) -> tuple[bool, str]:
    """Per reviewer.md line 71. Returns (ok, message).

    Rule:
      status=='escalated' → suggested_severity MUST be present and == 'error'
      status in {'confirmed', 'suppressed'} → suggested_severity MUST be absent
    """
    status = annotation.get("status")
    has_severity = "suggested_severity" in annotation
    severity = annotation.get("suggested_severity")
    if status == "escalated":
        if not has_severity:
            return False, "escalated annotation missing required suggested_severity"
        if severity != "error":
            return False, (
                f"escalated annotation has suggested_severity={severity!r}, "
                "must be 'error'"
            )
        return True, ""
    if status in ("confirmed", "suppressed"):
        if has_severity:
            return False, (
                f"{status} annotation has suggested_severity={severity!r}; "
                "field MUST be omitted for confirmed/suppressed per reviewer.md"
            )
        return True, ""
    return False, f"unknown status: {status!r}"


# ---------------------------------------------------------------------------
# Fixture sanity — make sure the real trace is loadable + well-shaped before
# running the more interesting invariants on top of it.
# ---------------------------------------------------------------------------

def test_trace_fixtures_present_and_loadable():
    """The three fixture files exist and parse as JSON."""
    annotations, merge, cap = _load_trace()
    assert annotations is not None, (
        f"phase4-review-trace fixtures missing under {TRACE_DIR}"
    )
    assert isinstance(annotations, dict)
    assert isinstance(merge, dict)
    assert isinstance(cap, dict)
    assert annotations["schema_version"] == "1.0"
    assert isinstance(annotations.get("annotations"), list)


def test_trace_annotations_count_matches_seed():
    """Real GNSSDO trace published 10 annotations (6 confirmed / 4 suppressed
    / 0 escalated) per main-repo handoff."""
    annotations, merge, _ = _load_trace()
    if annotations is None:
        return
    items = annotations["annotations"]
    assert len(items) == 10, f"expected 10 annotations, got {len(items)}"
    by_status: dict[str, int] = {}
    for a in items:
        by_status[a["status"]] = by_status.get(a["status"], 0) + 1
    assert by_status.get("confirmed") == 6
    assert by_status.get("suppressed") == 4
    assert by_status.get("escalated", 0) == 0


# ---------------------------------------------------------------------------
# Invariant 1: produced_for_run_id format matches run_id.py generator
# ---------------------------------------------------------------------------

def test_produced_for_run_id_format_matches_generator_pattern():
    """produced_for_run_id is a YYYYMMDDTHHMMSSZ-<6hex> string per
    skills/kicad/scripts/run_id.py."""
    annotations, _, _ = _load_trace()
    if annotations is None:
        return
    rid = annotations["produced_for_run_id"]
    assert RUN_ID_RE.match(rid), (
        f"produced_for_run_id={rid!r} does not match run_id pattern "
        f"{RUN_ID_RE.pattern}"
    )


# ---------------------------------------------------------------------------
# Invariant 2: produced_for_run_id linkage across all three files
# ---------------------------------------------------------------------------

def test_produced_for_run_id_linkage_to_capability_mode():
    """review_annotations.produced_for_run_id MUST match
    capability_mode.run_id (HI-7 capability_mode_ref consistency)."""
    annotations, _, cap = _load_trace()
    if annotations is None:
        return
    assert annotations["produced_for_run_id"] == cap["run_id"], (
        f"produced_for_run_id={annotations['produced_for_run_id']!r} "
        f"does not match capability_mode.run_id={cap['run_id']!r}"
    )


def test_produced_for_run_id_linkage_to_merge_report():
    """review_annotations.produced_for_run_id MUST match the merge
    report's produced_for_run_id (merge audit linkage)."""
    annotations, merge, _ = _load_trace()
    if annotations is None:
        return
    assert annotations["produced_for_run_id"] == merge["produced_for_run_id"]


# ---------------------------------------------------------------------------
# Invariant 3: reason minLength 20 chars — behavioral re-assert
# ---------------------------------------------------------------------------

def test_every_annotation_reason_meets_minlength_20():
    """reviewer.md + schema both require reason ≥20 chars on every
    annotation. Re-asserted behaviorally on the real trace."""
    annotations, _, _ = _load_trace()
    if annotations is None:
        return
    for i, a in enumerate(annotations["annotations"]):
        reason = a.get("reason", "")
        assert isinstance(reason, str) and len(reason) >= 20, (
            f"annotation[{i}] (finding_id={a.get('finding_id')!r}) reason "
            f"length is {len(reason)}, schema floor is 20"
        )


def test_short_reason_mutation_caught_by_minlength_check():
    """Mutation: shrink one annotation's reason to <20 chars and verify
    a behavioral length check would catch it. This proves the assertion
    above is meaningful, not vacuously true."""
    annotations, _, _ = _load_trace()
    if annotations is None:
        return
    mutated = copy.deepcopy(annotations)
    mutated["annotations"][0]["reason"] = "too short"
    # Re-run the same length predicate; should now flag at least one.
    failures = [a for a in mutated["annotations"]
                if not (isinstance(a.get("reason"), str)
                        and len(a["reason"]) >= 20)]
    assert len(failures) >= 1, (
        "deliberate short-reason mutation must be caught by minLength check"
    )


# ---------------------------------------------------------------------------
# Invariant 4: suggested_severity ↔ status coupling (reviewer.md line 71)
# ---------------------------------------------------------------------------

def test_real_trace_obeys_suggested_severity_coupling():
    """Every annotation in the real trace satisfies the status ↔
    suggested_severity coupling rule (none have suggested_severity since
    none are escalated; all are confirmed or suppressed)."""
    annotations, _, _ = _load_trace()
    if annotations is None:
        return
    for i, a in enumerate(annotations["annotations"]):
        ok, msg = _check_severity_coupling(a)
        assert ok, f"annotation[{i}] violates coupling rule: {msg}"


def test_synthetic_escalated_with_severity_passes_coupling():
    """Positive case: a synthesized escalated annotation with
    suggested_severity='error' passes the coupling rule."""
    a = {
        "finding_id": "sch:VM-001:u99",
        "status": "escalated",
        "reason": "Synthetic escalated annotation for B6 coupling positive test.",
        "confidence": "high",
        "suggested_severity": "error",
        "reviewed_at": "2026-05-04T00:00:00Z",
    }
    ok, msg = _check_severity_coupling(a)
    assert ok, f"escalated+error must pass: {msg}"


def test_synthetic_escalated_without_severity_fails_coupling():
    """Negative case: an escalated annotation MISSING suggested_severity
    fails the coupling rule (reviewer.md: 'where it MUST be \"error\"')."""
    a = {
        "finding_id": "sch:VM-001:u99",
        "status": "escalated",
        "reason": "Synthetic escalated annotation missing the required suggested_severity field.",
        "confidence": "high",
        "reviewed_at": "2026-05-04T00:00:00Z",
    }
    ok, msg = _check_severity_coupling(a)
    assert not ok, "escalated annotation without suggested_severity must fail"
    assert "missing" in msg.lower()


def test_synthetic_confirmed_with_severity_fails_coupling():
    """Negative case: a confirmed annotation WITH suggested_severity
    violates the coupling rule (reviewer.md: 'Omit it for confirmed and
    suppressed')."""
    a = {
        "finding_id": "sch:VM-001:u99",
        "status": "confirmed",
        "reason": "Synthetic confirmed annotation that wrongly carries suggested_severity.",
        "confidence": "high",
        "suggested_severity": "error",
        "reviewed_at": "2026-05-04T00:00:00Z",
    }
    ok, msg = _check_severity_coupling(a)
    assert not ok, "confirmed annotation with suggested_severity must fail"
    assert "MUST be omitted" in msg or "must be omitted" in msg.lower()


# ---------------------------------------------------------------------------
# Invariant 5: reviewer_observations gating
# ---------------------------------------------------------------------------

def test_reviewer_observations_empty_when_capability_mode_disables():
    """reviewer_observations in the annotations payload MUST be [] for this
    fixture (per review_annotations.schema.json and the v2.0 invariant that
    reviewer_observations live in review_annotations.json, never merged into
    findings[]). The v1.4-era capability_mode.reviewer_observations_enabled
    field is retired in v2.0 and no longer emitted."""
    annotations, _, cap = _load_trace()
    if annotations is None:
        return
    # reviewer_observations_enabled removed from capability_mode in v2.0 —
    # do not assert its presence. The invariant is checked on the annotations
    # payload directly.
    obs = annotations.get("reviewer_observations")
    assert obs == [], (
        f"reviewer_observations must be empty list in this fixture; got {obs!r}"
    )


# ---------------------------------------------------------------------------
# Invariant 6: finding_id duplicates are PERMITTED (real-world counter-example)
# ---------------------------------------------------------------------------

def test_duplicate_finding_id_allowed_real_world_counter_example():
    """Two annotations target the same finding_id (sch:PR-001:u18) for
    SCL + SDA pull-up companions on the same I2C segment. The merge
    logic accepts duplicates — B6 must NOT assert per-finding
    uniqueness."""
    annotations, merge, _ = _load_trace()
    if annotations is None:
        return
    seen: dict[str, int] = {}
    for a in annotations["annotations"]:
        fid = a["finding_id"]
        seen[fid] = seen.get(fid, 0) + 1
    duplicates = {fid: n for fid, n in seen.items() if n > 1}
    assert duplicates, (
        "real GNSSDO trace must contain at least one duplicate finding_id "
        "(sch:PR-001:u18) — proves the duplicate-allowed invariant on real data"
    )
    assert duplicates.get("sch:PR-001:u18") == 2, (
        f"expected 2 annotations on sch:PR-001:u18; got {duplicates}"
    )
    # The merge layer must have applied them all without complaint.
    assert merge["applied_count"] == merge["annotation_count"], (
        "merge must apply all annotations including duplicates "
        "(0 dropped, 0 invariant_violations)"
    )
    assert merge["invariant_violations"] == [], (
        "merge must report 0 invariant_violations on duplicate finding_ids"
    )


# ---------------------------------------------------------------------------
# Structural sanity: counts in _merge_report match the annotations payload
# ---------------------------------------------------------------------------

def test_merge_report_annotation_count_equals_annotations_length():
    annotations, merge, _ = _load_trace()
    if annotations is None:
        return
    assert merge["annotation_count"] == len(annotations["annotations"]), (
        f"merge_report.annotation_count={merge['annotation_count']} != "
        f"len(annotations)={len(annotations['annotations'])}"
    )


def test_merge_report_suppressed_count_matches_status_count():
    annotations, merge, _ = _load_trace()
    if annotations is None:
        return
    suppressed = [a for a in annotations["annotations"]
                  if a["status"] == "suppressed"]
    assert merge["suppressed_count"] == len(suppressed), (
        f"merge_report.suppressed_count={merge['suppressed_count']} != "
        f"actual suppressed count {len(suppressed)}"
    )


# ---------------------------------------------------------------------------
# Schema validation: the real trace must conform to review_annotations.schema.json
# ---------------------------------------------------------------------------

def test_real_trace_validates_against_schema():
    """Real GNSSDO output is a schema-conformant
    review_annotations.json. Skips cleanly when jsonschema is absent."""
    annotations, _, _ = _load_trace()
    if annotations is None:
        return
    if not SCHEMA_PATH.is_file():
        return  # older v1.3 KICAD_HAPPY_DIR, skip
    js = _try_jsonschema()
    if js is None:
        return  # jsonschema lib unavailable, skip
    schema = json.loads(SCHEMA_PATH.read_text())
    js.validate(instance=annotations, schema=schema)


# ---------------------------------------------------------------------------
# __main__ runner — harness convention (no pytest features)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import traceback

    tests = [
        test_trace_fixtures_present_and_loadable,
        test_trace_annotations_count_matches_seed,
        test_produced_for_run_id_format_matches_generator_pattern,
        test_produced_for_run_id_linkage_to_capability_mode,
        test_produced_for_run_id_linkage_to_merge_report,
        test_every_annotation_reason_meets_minlength_20,
        test_short_reason_mutation_caught_by_minlength_check,
        test_real_trace_obeys_suggested_severity_coupling,
        test_synthetic_escalated_with_severity_passes_coupling,
        test_synthetic_escalated_without_severity_fails_coupling,
        test_synthetic_confirmed_with_severity_fails_coupling,
        test_reviewer_observations_empty_when_capability_mode_disables,
        test_duplicate_finding_id_allowed_real_world_counter_example,
        test_merge_report_annotation_count_equals_annotations_length,
        test_merge_report_suppressed_count_matches_status_count,
        test_real_trace_validates_against_schema,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception:
            failed += 1
            print(f"FAIL: {t.__name__}")
            traceback.print_exc()
    total = passed + failed
    print(f"\n{passed} passed, {failed} failed ({total} total)")
    sys.exit(0 if failed == 0 else 1)
