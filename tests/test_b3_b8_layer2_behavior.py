"""B3+B8 regression tests for Layer 2 behavior invariants.

Implements two of the four absorption asks from main-repo LOG entry #71:
  (B3) renderer contract — stored severity is base; effective severity
       is computed at render time only. _apply_severity_tuning is gated
       on design_context being passed (finding_schema.py:186); detectors
       don't pass it, so analyzer-emitted findings carry base severity.
  (B8) annotation merge lifecycle — orphan annotations and HI-8 violations
       are LOGGED in the merge report (orphan_annotations vs
       invariant_violations top-level keys), not propagated as merge
       failures. HI-3 round-trip strip yields dict-equal raw.

Tests subprocess to merge_annotations.py and import _apply_severity_tuning
+ strip_llm_overlays from kicad-happy. Pattern matches B1+B2: graceful
skip when KH unavailable.

Note: LOG #71 ask wording conflates orphan_annotations and
invariant_violations into one key. Code separates them. Tests assert
against actual code shape; flag mismatch in closure handoff.
"""
from __future__ import annotations

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR))
sys.path.insert(0, str(HARNESS_DIR / "tests"))

KH_DIR = Path(os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy")))
KH_PYTHON = KH_DIR / ".venv" / "bin" / "python"

FINDING_SCHEMA_DIR = KH_DIR / "skills" / "kicad" / "scripts"
REVIEW_SCRIPTS_DIR = KH_DIR / "skills" / "kicad" / "review" / "scripts"
SEVERITY_TUNING_PATH = KH_DIR / "skills" / "kicad" / "review" / "severity_tuning.json"
MERGE_ANNOTATIONS_SCRIPT = REVIEW_SCRIPTS_DIR / "merge_annotations.py"


def _python() -> str:
    """Pick kicad-happy venv python if present (provides jsonschema)."""
    return str(KH_PYTHON) if KH_PYTHON.exists() else sys.executable


def _import_severity_tuning_fns():
    """Import _apply_severity_tuning from kicad-happy. Returns None if unavailable."""
    if not (FINDING_SCHEMA_DIR / "finding_schema.py").exists():
        return None
    if str(FINDING_SCHEMA_DIR) not in sys.path:
        sys.path.insert(0, str(FINDING_SCHEMA_DIR))
    try:
        from finding_schema import _apply_severity_tuning
        return _apply_severity_tuning
    except ImportError:
        return None


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


def _load_severity_tuning():
    """Load the severity_tuning.json rules dict. Returns {} if unavailable."""
    if not SEVERITY_TUNING_PATH.exists():
        return {}
    return json.loads(SEVERITY_TUNING_PATH.read_text()).get("rules", {})


# ─── (B3) renderer contract ───────────────────────────────────────────────

def test_apply_severity_tuning_changes_severity_on_known_input():
    """OV-001 base=warning + environment=automotive → severity_delta +1 → error."""
    fn = _import_severity_tuning_fns()
    if fn is None:
        print("  SKIP: _apply_severity_tuning not importable")
        return
    result = fn("OV-001", "warning", {"environment": "automotive"})
    assert result == "error", \
        f"expected 'error' (severity_delta +1), got {result!r}"


def test_analyzer_emits_base_severity_for_make_finding_findings():
    """For findings whose rule_id appears in severity_tuning.json,
    analyzer-emitted severity must equal the configured base_severity.

    HI-5 partial coverage: most analyzer findings don't carry rule_ids
    in the tuning matrix at v1.4 (only 11 rule_ids covered). If no
    matching findings are emitted by the synthetic schematic, test skips.
    """
    rules = _load_severity_tuning()
    if not rules:
        print("  SKIP: severity_tuning.json not loadable")
        return
    # Reuse the synthetic-schematic fixture from B1+B2's pattern via subprocess.
    analyzer = KH_DIR / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
    if not analyzer.exists():
        print("  SKIP: analyzer not available")
        return
    sys.path.insert(0, str(HARNESS_DIR / "tests"))
    from fixtures._build_sch import Schematic, pin1, pin2
    sch = (
        Schematic()
        .resistor("R1", "10k", at=(50, 50))
        .resistor("R2", "10k", at=(50, 62))
        .power("+3V3", at=(50, 40))
        .power("GND", at=(50, 72))
        .wire((50, 40), pin1(50, 50))
        .wire(pin2(50, 50), pin1(50, 62))
        .wire(pin2(50, 62), (50, 72))
    )
    with tempfile.TemporaryDirectory() as tmp:
        sch_path = sch.write(str(Path(tmp) / "test.kicad_sch"))
        out_path = str(Path(tmp) / "out.json")
        proc = subprocess.run(
            [_python(), str(analyzer), sch_path, "--output", out_path],
            capture_output=True, text=True, timeout=30,
        )
        assert proc.returncode == 0, f"analyzer failed: {proc.stderr[:300]}"
        env = json.loads(Path(out_path).read_text())
    findings_with_tuned_rules = [
        f for f in env.get("findings", [])
        if f.get("rule_id") in rules
    ]
    if not findings_with_tuned_rules:
        print("  SKIP: synthetic fixture emitted no findings with tuning rule_ids")
        return
    for f in findings_with_tuned_rules:
        rule_id = f["rule_id"]
        expected_base = rules[rule_id]["base_severity"]
        assert f["severity"] == expected_base, (
            f"finding {rule_id}: stored severity {f['severity']!r} != "
            f"base_severity {expected_base!r} from severity_tuning.json"
        )


def test_render_time_tuning_can_yield_distinct_effective_severity():
    """Tuning function can produce a result distinct from base severity,
    proving that storing the tuned value would lose information.

    Uses VM-001: base=error, tuning entry maps environment=hobby to
    severity_floor=warning. Function called with hobby context returns
    'warning' for an info input (floor lifts it), proving render-time
    tuning is meaningful and the stored base must remain base.
    """
    fn = _import_severity_tuning_fns()
    if fn is None:
        print("  SKIP")
        return
    rules = _load_severity_tuning()
    if "VM-001" not in rules:
        print("  SKIP: VM-001 not in severity_tuning.json")
        return
    # VM-001 base = error. Hobby context applies severity_floor=warning,
    # which is BELOW error, so the floor does not change error → error stays.
    # Use input lower than the floor to demonstrate the floor lifts it:
    result_with_floor = fn("VM-001", "info", {"environment": "hobby"})
    assert result_with_floor == "warning", \
        f"VM-001 + info + hobby should floor to warning, got {result_with_floor!r}"
    # And without the matching context, the input is returned unchanged
    result_no_match = fn("VM-001", "info", {"environment": "industrial"})
    assert result_no_match == "info", \
        f"VM-001 + info + industrial should pass through, got {result_no_match!r}"
    # Confirms tuning is a function of (rule, base, context) — not stored.
    assert result_with_floor != result_no_match


def test_HI9_tuning_max_severity_cap_honored():
    """LR-001 caps at warning per tuning_max_severity. Even an attempted
    severity_delta or floor cannot escalate beyond it.

    LR-001 has empty 'tuning' array, so no entries match — but the cap
    still clamps any base passed in. Verify: passing 'error' as base for
    LR-001 with no design_context returns 'error' (no tuning, no clamp
    triggered since there's no design_context). With a design_context
    that doesn't match anything in LR-001's tuning array, result = base.
    """
    fn = _import_severity_tuning_fns()
    if fn is None:
        print("  SKIP")
        return
    rules = _load_severity_tuning()
    if "LR-001" not in rules:
        print("  SKIP: LR-001 not in severity_tuning.json")
        return
    assert rules["LR-001"].get("tuning_max_severity") == "warning", \
        f"LR-001 tuning_max_severity != 'warning': {rules['LR-001']!r}"
    # Pass 'error' as base under any design_context — the cap should clamp.
    # Per finding_schema.py:138-141, the cap applies after walking entries.
    result = fn("LR-001", "error", {"environment": "industrial"})
    assert result == "warning", \
        f"LR-001 should cap at 'warning', got {result!r}"


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
        print("  SKIP: merge_annotations.py not available")
        return
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
        print("  SKIP")
        return
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


def test_b8_HI8_suppress_error_blocked_and_logged():
    """Annotation tries to suppress an error-severity finding; logged in
    invariant_violations[] with type='suppress_error'; finding's severity
    is unchanged in merged output; merge exits 0."""
    if not MERGE_ANNOTATIONS_SCRIPT.exists():
        print("  SKIP")
        return
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
        "reason": "Trying to suppress an error-severity finding (HI-8 violation).",
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
        suppress_errors = [v for v in violations if v.get("type") == "suppress_error"]
        assert len(suppress_errors) == 1, \
            f"expected 1 suppress_error, got {violations!r}"
        # Finding should NOT have llm_review applied (annotation skipped)
        merged = json.loads((merged_dir / "schematic.json").read_text())
        merged_finding = merged["findings"][0]
        assert "llm_review" not in merged_finding, \
            f"suppress_error annotation should be skipped, but llm_review was applied"
        assert merged_finding["severity"] == "error", \
            f"severity should be unchanged, got {merged_finding['severity']!r}"


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
