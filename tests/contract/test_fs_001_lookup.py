"""Contract tests for FS-001 lookup() upgrade (Phase 4b Task 22)."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "datasheets"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ctx(source="test"):
    """Minimal AnalysisContext with cache_dir and design_context attributes."""
    from kicad_types import AnalysisContext
    ctx = AnalysisContext(
        components=[],
        nets={},
        lib_symbols={},
        pin_net={},
        source=source,
    )
    setattr(ctx, "cache_dir", None)
    setattr(ctx, "design_context", None)
    return ctx


def _make_regulator(ref="U1", r_top_ohms=10000, r_bottom_ohms=3300, mpn=""):
    """Build a power_regulators entry with a feedback divider."""
    return {
        "ref": ref,
        "mpn": mpn,
        "feedback_divider": {
            "r_top": {"ref": "R1", "ohms": r_top_ohms},
            "r_bottom": {"ref": "R2", "ohms": r_bottom_ohms},
        },
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def test_fs_001_helper_smoke_missing_mpn(tmp_path):
    """get_facts returns None for an unknown regulator MPN (cache miss)."""
    from lookup_helpers import get_facts
    assert get_facts("UNKNOWN-REG", cache_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# Heuristic preservation — impedance too low
# ---------------------------------------------------------------------------

def test_fs_001_impedance_too_low_heuristic(tmp_path):
    """Feedback divider with very low parallel impedance emits FS-001 at info/heuristic.

    Parallel impedance of 10R || 10R = 5R < 1000R threshold → severity='info'.
    Confidence must remain 'heuristic' (no datasheet logic for this check).
    schema_era='v1.4' must be present on the finding.
    design_context=None threads through without error.
    """
    import validation_detectors

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    # 10R || 10R = 5R < 1000R (impedance too low)
    reg = _make_regulator(r_top_ohms=10, r_bottom_ohms=10, mpn="")

    with patch.object(validation_detectors, "get_facts", return_value=None):
        findings = validation_detectors.validate_feedback_stability(ctx, [reg])

    assert findings, "Expected at least one FS-001 finding for low impedance"
    fs = [f for f in findings if f.get("rule_id") == "FS-001"]
    assert fs, "Expected FS-001 rule_id on findings"

    f = fs[0]
    assert f["severity"] == "info", f"Expected severity='info', got {f['severity']}"
    assert f["confidence"] == "heuristic", f"Expected confidence='heuristic', got {f['confidence']}"
    assert f["evidence_source"] == "topology", f"Expected evidence_source='topology', got {f['evidence_source']}"
    assert f.get("schema_era") == "v1.4", f"Expected schema_era='v1.4', got {f.get('schema_era')}"


# ---------------------------------------------------------------------------
# Heuristic preservation — impedance too high
# ---------------------------------------------------------------------------

def test_fs_001_impedance_too_high_heuristic(tmp_path):
    """Feedback divider with very high parallel impedance emits FS-001 at warning/heuristic.

    Parallel impedance of 3MR || 3MR = 1.5MR > 1000kR threshold → severity='warning'.
    Confidence must remain 'heuristic' and schema_era='v1.4' must be present.
    """
    import validation_detectors

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    # 3MR || 3MR = 1.5MR > 1000kR (impedance too high)
    reg = _make_regulator(r_top_ohms=3_000_000, r_bottom_ohms=3_000_000, mpn="")

    with patch.object(validation_detectors, "get_facts", return_value=None):
        findings = validation_detectors.validate_feedback_stability(ctx, [reg])

    fs = [f for f in findings if f.get("rule_id") == "FS-001"]
    assert fs, "Expected FS-001 finding for high impedance"

    f = fs[0]
    assert f["severity"] == "warning", f"Expected severity='warning', got {f['severity']}"
    assert f["confidence"] == "heuristic", f"Expected confidence='heuristic', got {f['confidence']}"
    assert f["evidence_source"] == "topology", f"Expected evidence_source='topology', got {f['evidence_source']}"
    assert f.get("schema_era") == "v1.4", f"Expected schema_era='v1.4', got {f.get('schema_era')}"


# ---------------------------------------------------------------------------
# Probe wiring — facts present but confidence stays heuristic
# ---------------------------------------------------------------------------

def test_fs_001_probe_runs_but_confidence_stays_heuristic(tmp_path):
    """When get_facts() returns a mock with regulator.cout_min populated, detector
    runs the probe but does NOT change confidence/evidence_source — those stay
    heuristic because FS-001's validation logic (fb divider impedance) doesn't
    use cout_min today. This is the 4b wiring boundary: probe is informational only.
    """
    from datasheet_types import SpecValue, Evidence
    import validation_detectors

    ev = Evidence(page=4, confidence="medium", method="table")
    sv_cout = SpecValue(unit="F", evidence=ev, typ=10e-6)

    fake_regulator = MagicMock()
    fake_regulator.cout_min = [sv_cout]
    fake_stability = MagicMock()
    fake_stability.esr_range = None
    fake_regulator.stability_conditions = fake_stability
    fake_facts = MagicMock()
    fake_facts.regulator = fake_regulator

    ctx = _make_ctx()
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    # Low impedance (5R) so a finding fires.
    reg = _make_regulator(r_top_ohms=10, r_bottom_ohms=10, mpn="LM2596")

    with patch.object(validation_detectors, "get_facts", return_value=fake_facts):
        findings = validation_detectors.validate_feedback_stability(ctx, [reg])

    fs = [f for f in findings if f.get("rule_id") == "FS-001"]
    assert fs, "Expected FS-001 finding even when regulator facts are present"
    assert all(f["confidence"] == "heuristic" for f in fs), (
        f"Confidence must stay 'heuristic' (probe is informational): "
        f"{[f['confidence'] for f in fs]}"
    )
    assert all(f.get("schema_era") == "v1.4" for f in fs), (
        f"schema_era='v1.4' must be present on all FS-001 findings: "
        f"{[f.get('schema_era') for f in fs]}"
    )


# ---------------------------------------------------------------------------
# No finding for in-range impedance
# ---------------------------------------------------------------------------

def test_fs_001_no_finding_for_in_range_impedance():
    """Feedback divider with in-range parallel impedance produces no FS-001 finding."""
    import validation_detectors

    ctx = _make_ctx()
    # 10kR || 10kR = 5kR — well within [1k, 1M] range, no finding expected.
    reg = _make_regulator(r_top_ohms=10_000, r_bottom_ohms=10_000, mpn="")

    findings = validation_detectors.validate_feedback_stability(ctx, [reg])
    fs = [f for f in findings if f.get("rule_id") == "FS-001"]
    assert not fs, f"Expected no FS-001 for in-range impedance, got {fs}"


# ---------------------------------------------------------------------------
# Empty regulators list
# ---------------------------------------------------------------------------

def test_fs_001_empty_regulators():
    """Empty power_regulators list returns empty findings."""
    import validation_detectors

    ctx = _make_ctx()
    findings = validation_detectors.validate_feedback_stability(ctx, [])
    assert findings == []
