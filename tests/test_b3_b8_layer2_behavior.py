"""B8 regression tests for Layer 2 annotation merge lifecycle.

Implements the B8 absorption ask from main-repo LOG entry #71: orphan
annotations and HI-8 violations are LOGGED in the merge report
(orphan_annotations vs invariant_violations top-level keys), not
propagated as merge failures. HI-3 round-trip strip yields dict-equal raw.
The B3 severity-tuning tests were retired with the design_context channel
(v3 round 1).

Tests subprocess to merge_annotations.py and import strip_llm_overlays
from kicad-happy. Graceful skip when KH unavailable.

Note: LOG #71 ask wording conflates orphan_annotations and
invariant_violations into one key. Code separates them. Tests assert
against actual code shape.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tests"))

KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_PYTHON = KH_DIR / ".venv" / "bin" / "python"

REVIEW_SCRIPTS_DIR = KH_DIR / "skills" / "kicad" / "review" / "scripts"
MERGE_ANNOTATIONS_SCRIPT = REVIEW_SCRIPTS_DIR / "merge_annotations.py"


def _python() -> str:
    """Pick kicad-happy venv python if present (provides jsonschema)."""
    return str(KH_PYTHON) if KH_PYTHON.exists() else sys.executable


def _import_strip_llm_overlays():
    """Import strip_llm_overlays from merge_annotations.py."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        return None
    if str(REVIEW_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(REVIEW_SCRIPTS_DIR))
    try:
        from merge_annotations import strip_llm_overlays
        return strip_llm_overlays
    except ImportError:
        return None


# ─── (B8) annotation merge lifecycle ──────────────────────────────────────

def _make_minimal_envelope(findings):
    """Build a minimal v1.4-shape schematic envelope with the given findings.

    Only the fields that merge_annotations.py touches are populated.
    Other consumers (jsonschema validators) may reject this minimal shape;
    merge_annotations.py is intentionally lenient because it just walks
    findings[] and writes overlays.
    """
    return {
        "analyzer_type": "schematic",
        "schema_version": "1.4.0",
        "findings": findings,
        "summary": {"total_findings": len(findings)},
    }


def _make_review(annotations, run_id="20260428T120000Z-aaaaaa",
                  reviewer_observations=None):
    """Build a minimal review_annotations.json payload."""
    return {
        "schema_version": "1.0",
        "produced_for_run_id": run_id,
        "produced_at": "2026-04-28T12:00:00Z",
        "annotations": annotations,
        "reviewer_observations": reviewer_observations or [],
    }


def _run_merge(tmp: Path, raw_envelopes, review):
    """Set up tmp/raw + tmp/review.json, run merge_annotations.py, return
    (returncode, report_dict_or_None, merged_dir_path)."""
    raw_dir = tmp / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for stem, env in raw_envelopes.items():
        (raw_dir / f"{stem}.json").write_text(
            json.dumps(env, indent=2, sort_keys=True))
    review_path = tmp / "review.json"
    review_path.write_text(json.dumps(review, indent=2, sort_keys=True))
    merged_dir = tmp / "merged"
    proc = subprocess.run(
        [_python(), str(MERGE_ANNOTATIONS_SCRIPT),
         "--raw-dir", str(raw_dir),
         "--review", str(review_path),
         "--merged-dir", str(merged_dir)],
        capture_output=True, text=True, timeout=20,
    )
    report_path = merged_dir / "_merge_report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else None
    return proc.returncode, report, merged_dir


def test_b8_valid_annotation_merges_with_llm_review_overlay():
    """Status=confirmed annotation gains llm_review overlay; applied_count==1."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    finding = {
        "finding_id": "sch:VM-001:u3",
        "detector": "validate_voltage_levels",
        "rule_id": "VM-001",
        "category": "voltage",
        "summary": "VCC exceeds U3 max",
        "description": "VCC at 5V exceeds U3 recommended max 3.6V",
        "severity": "error",
        "confidence": "heuristic",
        "components": ["U3"],
        "nets": [],
        "pins": [],
        "evidence_source": "heuristic_rule",
        "recommendation": "",
    }
    review = _make_review([{
        "finding_id": "sch:VM-001:u3",
        "status": "confirmed",
        "reason": "Confirmed: VCC at 5V exceeds U3 max — design issue.",
        "confidence": "high",
        "reviewed_at": "2026-04-28T12:00:00Z",
    }])
    with tempfile.TemporaryDirectory() as tmp:
        rc, report, merged_dir = _run_merge(
            Path(tmp), {"schematic": _make_minimal_envelope([finding])}, review)
        assert rc == 0, f"merge failed: rc={rc}"
        assert report is not None, "no _merge_report.json produced"
        assert report["applied_count"] == 1, \
            f"expected applied_count=1, got {report!r}"
        merged = json.loads((merged_dir / "schematic.json").read_text())
        merged_finding = merged["findings"][0]
        assert "llm_review" in merged_finding, \
            f"llm_review missing from merged finding: {list(merged_finding.keys())}"
        assert merged_finding["llm_review"]["status"] == "confirmed"
        assert merged_finding["llm_review"]["confidence"] == "high"


def test_b8_orphan_annotation_logged_in_orphan_annotations_key():
    """Annotation referencing non-existent finding_id is logged in
    report.orphan_annotations[] (a separate top-level key from
    invariant_violations[]) and merge exits 0."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    real_finding = {
        "finding_id": "sch:VM-001:u3",
        "rule_id": "VM-001",
        "severity": "warning",
        "confidence": "heuristic",
        "components": ["U3"], "nets": [], "pins": [],
    }
    review = _make_review([{
        "finding_id": "sch:DOES_NOT_EXIST:zzz",
        "status": "confirmed",
        "reason": "References a finding that doesn't exist in raw envelope.",
        "confidence": "medium",
        "reviewed_at": "2026-04-28T12:00:00Z",
    }])
    with tempfile.TemporaryDirectory() as tmp:
        rc, report, _ = _run_merge(
            Path(tmp),
            {"schematic": _make_minimal_envelope([real_finding])},
            review,
        )
        assert rc == 0, f"merge should exit 0 on orphan; got rc={rc}"
        orphans = report.get("orphan_annotations", [])
        assert len(orphans) == 1, \
            f"expected 1 orphan, got {orphans!r}"
        assert orphans[0]["finding_id"] == "sch:DOES_NOT_EXIST:zzz"
        # CRITICAL: orphans live in their own key, NOT in invariant_violations.
        # LOG #71 ask wording conflates them — flag in closure handoff.
        assert orphans[0] not in report.get("invariant_violations", []), \
            "orphans must NOT also appear in invariant_violations[]"


# test_b8_HI8_suppress_error_blocked_and_logged — FLIPPED for v2.0 (spec §5):
#   the suppress_error authority guard is removed; suppressing error-severity
#   findings now applies. See test_b8_v2_suppress_error_applies.
def test_b8_v2_suppress_error_applies():
    """v2.0 (spec §5): suppressing an error-severity finding applies the
    llm_review overlay; no suppress_error invariant violation; the finding's
    own severity field stays unchanged (suppression is an overlay)."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    error_finding = {
        "finding_id": "sch:VM-001:u3",
        "rule_id": "VM-001",
        "severity": "error",
        "confidence": "heuristic",
        "components": ["U3"], "nets": [], "pins": [],
    }
    review = _make_review([{
        "finding_id": "sch:VM-001:u3",
        "status": "suppressed",
        "reason": "Suppressing an error-severity finding (allowed in v2.0).",
        "confidence": "high",
        "reviewed_at": "2026-04-28T12:00:00Z",
    }])
    with tempfile.TemporaryDirectory() as tmp:
        rc, report, merged_dir = _run_merge(
            Path(tmp),
            {"schematic": _make_minimal_envelope([error_finding])},
            review,
        )
        assert rc == 0, f"merge should exit 0; got rc={rc}"
        violations = report.get("invariant_violations", [])
        assert violations == [], \
            f"no invariant violations expected in v2.0, got {violations!r}"
        merged = json.loads((merged_dir / "schematic.json").read_text())
        merged_finding = merged["findings"][0]
        assert merged_finding.get("llm_review", {}).get("status") == "suppressed", \
            "suppress annotation must be applied to error-severity finding in v2.0"
        assert merged_finding["severity"] == "error", \
            f"severity should be unchanged, got {merged_finding['severity']!r}"
        assert report["applied_count"] == 1
        assert report["suppressed_count"] == 1


# test_b8_HI8_suppress_datasheet_blocked_and_logged — FLIPPED for v2.0 (spec §5):
#   the suppress_datasheet authority guard is removed.
def test_b8_v2_suppress_datasheet_backed_applies():
    """v2.0 (spec §5): suppressing a confidence=datasheet-backed finding
    applies the llm_review overlay; no suppress_datasheet violation."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    ds_finding = {
        "finding_id": "sch:OV-001:u5",
        "rule_id": "OV-001",
        "severity": "warning",
        "confidence": "datasheet-backed",
        "components": ["U5"], "nets": [], "pins": [],
    }
    review = _make_review([{
        "finding_id": "sch:OV-001:u5",
        "status": "suppressed",
        "reason": "Suppressing a datasheet-backed finding (allowed in v2.0).",
        "confidence": "high",
        "reviewed_at": "2026-04-28T12:00:00Z",
    }])
    with tempfile.TemporaryDirectory() as tmp:
        rc, report, merged_dir = _run_merge(
            Path(tmp),
            {"schematic": _make_minimal_envelope([ds_finding])},
            review,
        )
        assert rc == 0, f"merge should exit 0; got rc={rc}"
        violations = report.get("invariant_violations", [])
        assert violations == [], \
            f"no invariant violations expected in v2.0, got {violations!r}"
        merged = json.loads((merged_dir / "schematic.json").read_text())
        assert merged["findings"][0].get("llm_review", {}).get("status") == "suppressed", \
            "suppress annotation must be applied to datasheet-backed finding in v2.0"
        assert report["suppressed_count"] == 1


# test_b8_HI8_30pct_suppression_cap_fires_suppression_rate_exceeded — FLIPPED
#   for v2.0 (spec §5): the 30% suppression rate cap is removed.
def test_b8_v2_no_suppression_rate_cap():
    """v2.0 (spec §5): 5 findings, 2 suppressions = 40% — previously over the
    30% cap — must NOT produce a suppression_rate_exceeded violation."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    findings = [
        {
            "finding_id": f"sch:PU-001:r{i}",
            "rule_id": "PU-001",
            "severity": "warning",
            "confidence": "heuristic",
            "components": [f"R{i}"], "nets": [], "pins": [],
        }
        for i in range(1, 6)
    ]
    review = _make_review([
        {
            "finding_id": f"sch:PU-001:r{i}",
            "status": "suppressed",
            "reason": f"Suppressing R{i} (40% — cap removed in v2.0).",
            "confidence": "medium",
            "reviewed_at": "2026-04-28T12:00:00Z",
        }
        for i in (1, 2)
    ])
    with tempfile.TemporaryDirectory() as tmp:
        rc, report, _ = _run_merge(
            Path(tmp),
            {"schematic": _make_minimal_envelope(findings)},
            review,
        )
        assert rc == 0, f"merge should exit 0; got rc={rc}"
        violations = report.get("invariant_violations", [])
        assert violations == [], \
            f"suppression_rate_exceeded must not fire in v2.0, got {violations!r}"
        assert report["suppressed_count"] == 2
        assert report["applied_count"] == 2


def test_b8_HI3_strip_llm_overlays_yields_dict_equal_raw():
    """Round-trip: after a valid merge, strip_llm_overlays(merged) ==
    raw envelope. Confirms merge_annotations.py:158 raise does NOT
    fire on valid input — i.e., HI-3 is honored end-to-end."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        pytest.skip('merge_annotations.py not available')
    strip = _import_strip_llm_overlays()
    if strip is None:
        pytest.skip('strip_llm_overlays not importable')
    finding = {
        "finding_id": "sch:VM-001:u3",
        "rule_id": "VM-001",
        "severity": "warning",
        "confidence": "heuristic",
        "components": ["U3"], "nets": [], "pins": [],
    }
    raw_envelope = _make_minimal_envelope([finding])
    review = _make_review([{
        "finding_id": "sch:VM-001:u3",
        "status": "confirmed",
        "reason": "Round-trip test: confirmed finding for HI-3 verification.",
        "confidence": "high",
        "reviewed_at": "2026-04-28T12:00:00Z",
    }])
    with tempfile.TemporaryDirectory() as tmp:
        rc, _report, merged_dir = _run_merge(
            Path(tmp), {"schematic": raw_envelope}, review)
        assert rc == 0, f"merge failed: rc={rc}"
        merged = json.loads((merged_dir / "schematic.json").read_text())
        # Confirm overlay was applied (so the round-trip is meaningful)
        assert "llm_review" in merged["findings"][0]
        # The HI-3 contract: stripping recovers raw byte-for-byte (modulo
        # JSON formatting — assert dict equality, not byte equality).
        stripped = strip(merged)
        assert stripped == raw_envelope, (
            "HI-3 violation: strip_llm_overlays(merged) != raw\n"
            f"diff keys: merged={set(stripped.get('findings', [{}])[0].keys())}, "
            f"raw={set(raw_envelope['findings'][0].keys())}"
        )


def test_b8_HI3_strip_handles_nested_llm_keys():
    """strip_llm_overlays recursively removes ALL keys starting with
    'llm_' at any nesting depth. Synthesize a hand-crafted dict with
    nested llm_review.suggested_severity + a sibling llm_observations
    list and assert all llm_* keys are gone after strip."""
    strip = _import_strip_llm_overlays()
    if strip is None:
        pytest.skip('strip_llm_overlays not importable')
    payload = {
        "analyzer_type": "schematic",
        "findings": [
            {
                "finding_id": "sch:VM-001:u3",
                "severity": "warning",
                "llm_review": {
                    "status": "confirmed",
                    "suggested_severity": "error",
                    "reviewed_at": "2026-04-28T12:00:00Z",
                },
                "llm_observations": [{"text": "noise"}],
            },
        ],
        "llm_top_level_overlay": {"some": "data"},
    }
    stripped = strip(payload)
    # All llm_* keys gone, recursively
    assert "llm_top_level_overlay" not in stripped
    assert "llm_review" not in stripped["findings"][0]
    assert "llm_observations" not in stripped["findings"][0]
    # Non-llm content preserved
    assert stripped["findings"][0]["finding_id"] == "sch:VM-001:u3"
    assert stripped["findings"][0]["severity"] == "warning"
    assert stripped["analyzer_type"] == "schematic"


# Custom-runner __main__ block (harness convention)
if __name__ == "__main__":
    import traceback
    fn_names = sorted(n for n, v in globals().items()
                      if n.startswith("test_") and callable(v))
    failed = 0
    passed = 0
    for n in fn_names:
        try:
            globals()[n]()
            print(f"PASS {n}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {n}: {e}")
            failed += 1
        except Exception as e:
            print(f"FAIL {n}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"{passed} passed, {failed} failed ({len(fn_names)} total)")
    sys.exit(0 if failed == 0 else 1)
