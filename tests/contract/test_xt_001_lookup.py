"""Contract tests for XT-001 lookup() upgrade (Phase 4b Task 21)."""

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
    """Minimal AnalysisContext for validate_crystal_load_caps (needs only source + attrs)."""
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


def _make_xtal_entry(
    ref="Y1",
    status="out_of_spec",
    target_source="parsed_from_value",
    effective_pF=27.5,
    target_pF=18.0,
    error_pct=52.8,
    load_caps=None,
):
    """Build a crystal_circuits entry dict as produced by detect_crystal_circuits."""
    if load_caps is None:
        load_caps = [
            {"ref": "C1", "value": "22pF", "farads": 22e-12, "net": "XTAL1"},
            {"ref": "C2", "value": "22pF", "farads": 22e-12, "net": "XTAL2"},
        ]
    return {
        "reference": ref,
        "value": "16MHz/18pF",
        "frequency": 16e6,
        "load_caps": load_caps,
        "effective_load_pF": effective_pF,
        "target_load_pF": target_pF,
        "target_load_source": target_source,
        "load_cap_error_pct": error_pct,
        "load_cap_status": status,
        "detector": "detect_crystal_circuits",
        "rule_id": "XL-DET",
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def test_xt_001_helper_smoke_missing_mpn(tmp_path):
    """get_facts returns None for an unknown crystal MPN (cache miss)."""
    from lookup_helpers import get_facts
    assert get_facts("UNKNOWN-XTAL", cache_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# Heuristic path — out_of_spec fires at severity='warning'
# ---------------------------------------------------------------------------

def test_xt_001_fires_out_of_spec_heuristic():
    """out_of_spec status with parsed_from_value source → XT-001 warning, heuristic."""
    import validation_detectors
    ctx = _make_ctx()
    xtal_entry = _make_xtal_entry(status="out_of_spec", target_source="parsed_from_value")

    findings = validation_detectors.validate_crystal_load_caps(ctx, [xtal_entry])

    assert findings, "Expected at least one XT-001 finding"
    xt = [f for f in findings if f.get("rule_id") == "XT-001"]
    assert xt, "Expected XT-001 rule_id"
    assert xt[0]["severity"] == "warning", f"out_of_spec should be 'warning', got {xt[0]['severity']}"
    assert xt[0]["confidence"] == "heuristic", f"Expected confidence='heuristic', got {xt[0]['confidence']}"
    assert xt[0]["evidence_source"] == "topology", f"Expected evidence_source='topology', got {xt[0]['evidence_source']}"


# ---------------------------------------------------------------------------
# Heuristic path — marginal fires at severity='info'
# ---------------------------------------------------------------------------

def test_xt_001_fires_marginal_at_info():
    """marginal status → XT-001 at severity='info'."""
    import validation_detectors
    ctx = _make_ctx()
    xtal_entry = _make_xtal_entry(
        status="marginal",
        target_source="parsed_from_value",
        effective_pF=20.5,
        target_pF=18.0,
        error_pct=13.9,
    )

    findings = validation_detectors.validate_crystal_load_caps(ctx, [xtal_entry])

    xt = [f for f in findings if f.get("rule_id") == "XT-001"]
    assert xt, "Expected XT-001 finding for marginal status"
    assert xt[0]["severity"] == "info", f"marginal should be 'info', got {xt[0]['severity']}"
    assert xt[0]["confidence"] == "heuristic"


# ---------------------------------------------------------------------------
# Silent statuses — no XT-001 for 'ok' or 'unverified'
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status", ["ok", "unverified"])
def test_xt_001_silent_for_ok_and_unverified(status):
    """ok and unverified statuses do not emit XT-001."""
    import validation_detectors
    ctx = _make_ctx()
    xtal_entry = _make_xtal_entry(
        status=status,
        target_source="frequency_default",
        effective_pF=18.5,
        target_pF=18.0,
        error_pct=2.8,
    )
    findings = validation_detectors.validate_crystal_load_caps(ctx, [xtal_entry])
    xt = [f for f in findings if f.get("rule_id") == "XT-001"]
    assert not xt, f"Expected no XT-001 for status='{status}', got {xt}"


# ---------------------------------------------------------------------------
# Datasheet branch — confidence='datasheet-backed'
# ---------------------------------------------------------------------------

def test_xt_001_datasheet_branch_fires_with_datasheet_confidence():
    """target_load_source='datasheet' → XT-001 fires with confidence='datasheet-backed'."""
    import validation_detectors
    ctx = _make_ctx()
    xtal_entry = _make_xtal_entry(
        status="out_of_spec",
        target_source="datasheet",
        effective_pF=27.5,
        target_pF=18.0,
        error_pct=52.8,
    )

    findings = validation_detectors.validate_crystal_load_caps(ctx, [xtal_entry])

    xt = [f for f in findings if f.get("rule_id") == "XT-001"]
    assert xt, "Expected XT-001 finding with datasheet-backed confidence"
    assert xt[0]["confidence"] == "datasheet-backed", (
        f"Expected confidence='datasheet-backed', got {xt[0]['confidence']}"
    )
    assert xt[0]["evidence_source"] == "datasheet", (
        f"Expected evidence_source='datasheet', got {xt[0]['evidence_source']}"
    )
    assert xt[0]["severity"] == "warning"


# ---------------------------------------------------------------------------
# Empty list — no findings
# ---------------------------------------------------------------------------

def test_xt_001_empty_crystal_circuits():
    """Empty crystal_circuits list returns empty findings."""
    import validation_detectors
    ctx = _make_ctx()
    findings = validation_detectors.validate_crystal_load_caps(ctx, [])
    assert findings == []


# ---------------------------------------------------------------------------
# detect_crystal_circuits datasheet probe wiring
# ---------------------------------------------------------------------------

def test_detect_crystal_circuits_probes_datasheet_for_target_load(tmp_path):
    """detect_crystal_circuits probes get_facts for crystal.load_capacitance.

    When get_facts returns a mock with crystal.load_capacitance populated,
    target_load_source is set to 'datasheet' and target_load_pF uses the
    datasheet value (converted from Farads to pF).
    """
    from datasheet_types import SpecValue, Evidence
    import signal_detectors
    from kicad_types import AnalysisContext

    # Mock: facts.crystal.load_capacitance → [SpecValue(typ=1.8e-11)] = 18 pF
    ev = Evidence(page=1, confidence="medium", method="table")
    sv_cl = SpecValue(unit="F", evidence=ev, typ=1.8e-11)

    fake_crystal_block = MagicMock()
    fake_crystal_block.load_capacitance = [sv_cl]
    fake_facts = MagicMock()
    fake_facts.crystal = fake_crystal_block

    # Build minimal context: one crystal with 2 load caps that give effective CL ≈ 14pF
    # C1=22pF, C2=22pF → (22*22)/(22+22) + 3 stray ≈ 14pF (out_of_spec vs 18pF target)
    xtal_ref = "Y1"
    c1_ref = "C1"
    c2_ref = "C2"
    xtal = {
        "reference": xtal_ref, "value": "XTAL-16M", "type": "crystal",
        "lib_id": "Device:Crystal", "footprint": "", "properties": {},
        "pins": [
            {"number": "1", "name": "IN", "x": 0, "y": 0},
            {"number": "2", "name": "OUT", "x": 0, "y": 0},
        ],
    }
    c1 = {"reference": c1_ref, "value": "22p", "type": "capacitor",
          "lib_id": "Device:C", "footprint": "", "properties": {}}
    c2 = {"reference": c2_ref, "value": "22p", "type": "capacitor",
          "lib_id": "Device:C", "footprint": "", "properties": {}}
    ctx = AnalysisContext(
        components=[xtal, c1, c2],
        nets={
            "XTAL1": {"pins": [
                {"component": xtal_ref, "pin_number": "1", "pin_name": "IN", "x": 0, "y": 0},
                {"component": c1_ref, "pin_number": "1", "pin_name": "1", "x": 0, "y": 0},
            ]},
            "XTAL2": {"pins": [
                {"component": xtal_ref, "pin_number": "2", "pin_name": "OUT", "x": 0, "y": 0},
                {"component": c2_ref, "pin_number": "1", "pin_name": "1", "x": 0, "y": 0},
            ]},
            "GND": {"pins": [
                {"component": c1_ref, "pin_number": "2", "pin_name": "2", "x": 0, "y": 0},
                {"component": c2_ref, "pin_number": "2", "pin_name": "2", "x": 0, "y": 0},
            ]},
        },
        lib_symbols={},
        pin_net={
            (xtal_ref, "1"): ("XTAL1", None),
            (xtal_ref, "2"): ("XTAL2", None),
            (c1_ref, "1"): ("XTAL1", None),
            (c1_ref, "2"): ("GND", None),
            (c2_ref, "1"): ("XTAL2", None),
            (c2_ref, "2"): ("GND", None),
        },
        known_power_rails={"GND"},
        source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)

    with patch.object(signal_detectors, "get_facts", return_value=fake_facts):
        crystal_circuits = signal_detectors.detect_crystal_circuits(ctx)

    assert crystal_circuits, "Expected crystal circuit detection to produce results"
    xc = crystal_circuits[0]
    assert xc["target_load_source"] == "datasheet", (
        f"Expected target_load_source='datasheet', got {xc['target_load_source']}"
    )
    assert abs(xc["target_load_pF"] - 18.0) < 0.01, (
        f"Expected target_load_pF≈18.0, got {xc['target_load_pF']}"
    )
    # XL-DET assessment must be unchanged
    assert xc["rule_id"] == "XL-DET", "XL-DET rule_id must be preserved"
    assert xc["severity"] == "info", "XL-DET severity must remain 'info'"


# ---------------------------------------------------------------------------
# Cache-variant locks — stale + low-conf (LOG 13)
# ---------------------------------------------------------------------------

def _build_crystal_ctx(tmp_path, xtal_value="XTAL-16M"):
    """Minimal ctx with one crystal (16MHz, value not parseable for CL) and
    two 22pF load caps. Effective CL ≈ 14pF (with 3pF stray) → out-of-spec
    vs 18pF target. Mirrors the construction in
    test_detect_crystal_circuits_probes_datasheet_for_target_load."""
    from kicad_types import AnalysisContext

    xtal_ref = "Y1"
    c1_ref = "C1"
    c2_ref = "C2"
    xtal = {
        "reference": xtal_ref, "value": xtal_value, "type": "crystal",
        "lib_id": "Device:Crystal", "footprint": "", "properties": {},
        "pins": [
            {"number": "1", "name": "IN", "x": 0, "y": 0},
            {"number": "2", "name": "OUT", "x": 0, "y": 0},
        ],
    }
    c1 = {"reference": c1_ref, "value": "22p", "type": "capacitor",
          "lib_id": "Device:C", "footprint": "", "properties": {}}
    c2 = {"reference": c2_ref, "value": "22p", "type": "capacitor",
          "lib_id": "Device:C", "footprint": "", "properties": {}}
    ctx = AnalysisContext(
        components=[xtal, c1, c2],
        nets={
            "XTAL1": {"pins": [
                {"component": xtal_ref, "pin_number": "1", "pin_name": "IN", "x": 0, "y": 0},
                {"component": c1_ref, "pin_number": "1", "pin_name": "1", "x": 0, "y": 0},
            ]},
            "XTAL2": {"pins": [
                {"component": xtal_ref, "pin_number": "2", "pin_name": "OUT", "x": 0, "y": 0},
                {"component": c2_ref, "pin_number": "1", "pin_name": "1", "x": 0, "y": 0},
            ]},
            "GND": {"pins": [
                {"component": c1_ref, "pin_number": "2", "pin_name": "2", "x": 0, "y": 0},
                {"component": c2_ref, "pin_number": "2", "pin_name": "2", "x": 0, "y": 0},
            ]},
        },
        lib_symbols={},
        pin_net={
            (xtal_ref, "1"): ("XTAL1", None),
            (xtal_ref, "2"): ("XTAL2", None),
            (c1_ref, "1"): ("XTAL1", None),
            (c1_ref, "2"): ("GND", None),
            (c2_ref, "1"): ("XTAL2", None),
            (c2_ref, "2"): ("GND", None),
        },
        known_power_rails={"GND"},
        source="test",
    )
    setattr(ctx, "cache_dir", tmp_path)
    setattr(ctx, "design_context", None)
    return ctx


def test_xt_001_stale_cache_still_fires_datasheet_branch(tmp_path):
    """detect_crystal_circuits does NOT branch on facts.stale — datasheet
    branch still wins over parse/frequency fallback even when the cache
    is stale. Per-detector half of the A3.3 staleness/trust-gating
    orthogonality lock for XT-001's upstream lookup consumer."""
    from datasheet_types import SpecValue, Evidence
    import signal_detectors

    ev = Evidence(page=1, confidence="medium", method="table")
    sv_cl = SpecValue(unit="F", evidence=ev, typ=1.8e-11)  # 18 pF

    fake_crystal_block = MagicMock()
    fake_crystal_block.load_capacitance = [sv_cl]
    fake_facts = MagicMock()
    fake_facts.crystal = fake_crystal_block
    fake_facts.stale = True  # stale cache

    ctx = _build_crystal_ctx(tmp_path)
    with patch.object(signal_detectors, "get_facts", return_value=fake_facts):
        crystal_circuits = signal_detectors.detect_crystal_circuits(ctx)

    assert crystal_circuits, "Expected crystal detection to produce results"
    xc = crystal_circuits[0]
    assert xc["target_load_source"] == "datasheet", (
        f"stale cache must NOT bypass datasheet branch, "
        f"got target_load_source={xc['target_load_source']!r}"
    )
    assert abs(xc["target_load_pF"] - 18.0) < 0.01, (
        f"Expected datasheet-derived target_load_pF≈18.0, got {xc['target_load_pF']}"
    )


def test_xt_001_low_confidence_target_load_falls_back_to_frequency_default(tmp_path):
    """Low-confidence crystal.load_capacitance → best(min_confidence='medium')
    returns None → datasheet branch skips → falls through to value-parse
    (unparseable here) → frequency_default branch wins. Locks the implicit
    per-rule low-conf gate inside detect_crystal_circuits."""
    from datasheet_types import SpecValue, Evidence
    import signal_detectors

    ev_low = Evidence(page=1, confidence="low", method="prose")
    sv_cl = SpecValue(unit="F", evidence=ev_low, typ=1.8e-11)

    fake_crystal_block = MagicMock()
    fake_crystal_block.load_capacitance = [sv_cl]
    fake_facts = MagicMock()
    fake_facts.crystal = fake_crystal_block

    ctx = _build_crystal_ctx(tmp_path)
    with patch.object(signal_detectors, "get_facts", return_value=fake_facts):
        crystal_circuits = signal_detectors.detect_crystal_circuits(ctx)

    assert crystal_circuits, "Expected crystal detection to produce results"
    xc = crystal_circuits[0]
    assert xc["target_load_source"] != "datasheet", (
        f"low-conf load_capacitance must NOT promote to datasheet branch, "
        f"got target_load_source={xc['target_load_source']!r}"
    )
