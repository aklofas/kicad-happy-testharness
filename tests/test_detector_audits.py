"""Unit tests for audit_* detectors in domain_detectors.py.

Audit functions scan for missing protective/supporting components on
external interfaces. These tests verify signature stability and catch
trivial regressions (crash, wrong return type).
"""

TIER = "unit"

import os
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_DIR / "tests"))

_KICAD_HAPPY = os.environ.get(
    "KICAD_HAPPY_DIR", str(HARNESS_DIR.parent / "kicad-happy"))
_SCRIPTS = Path(_KICAD_HAPPY) / "skills" / "kicad" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from fixtures._build_ctx import build_ctx, ic, resistor, connector  # noqa: E402


def _skip_if_no_kh():
    return not (_SCRIPTS / "domain_detectors.py").exists()


# ---------------------------------------------------------------------------
# audit_esd_protection
# Signature: audit_esd_protection(ctx, protection_devices: list[dict])
# ---------------------------------------------------------------------------

def test_audit_esd_protection_empty_ctx():
    if _skip_if_no_kh():
        return
    from domain_detectors import audit_esd_protection
    # Signature: audit_esd_protection(ctx, protection_devices) — pass [] for empty
    findings = audit_esd_protection(build_ctx([], {}, set()), [])
    assert isinstance(findings, list)


def test_audit_esd_protection_usb_connector_no_tvs():
    """USB connector with no TVS diode on D+/D-."""
    if _skip_if_no_kh():
        return
    from domain_detectors import audit_esd_protection

    ctx = build_ctx(
        components=[
            connector("J1", "USB_B_Micro",
                      [("1", "VBUS"), ("2", "D-"), ("3", "D+"),
                       ("4", "ID"), ("5", "GND")]),
        ],
        nets={
            "VBUS":   [("J1", "1")],
            "USB_DM": [("J1", "2")],
            "USB_DP": [("J1", "3")],
            "GND":    [("J1", "5")],
        },
        known_power_rails={"VBUS", "GND"},
    )
    # Signature: audit_esd_protection(ctx, protection_devices) — pass [] for empty
    findings = audit_esd_protection(ctx, [])
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# audit_led_circuits
# Signature: audit_led_circuits(ctx, transistor_circuits: list[dict])
# ---------------------------------------------------------------------------

def test_audit_led_circuits_empty_ctx():
    if _skip_if_no_kh():
        return
    from domain_detectors import audit_led_circuits
    # Signature: audit_led_circuits(ctx, transistor_circuits) — pass [] for empty
    findings = audit_led_circuits(build_ctx([], {}, set()), [])
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# audit_connector_ground_distribution
# Signature: audit_connector_ground_distribution(ctx) — ctx only
# ---------------------------------------------------------------------------

def test_audit_connector_ground_distribution_empty_ctx():
    if _skip_if_no_kh():
        return
    from domain_detectors import audit_connector_ground_distribution
    findings = audit_connector_ground_distribution(
        build_ctx([], {}, set()))
    assert isinstance(findings, list)


def test_audit_connector_ground_distribution_low_gnd_ratio():
    """40-pin connector with 1 GND pin."""
    if _skip_if_no_kh():
        return
    from domain_detectors import audit_connector_ground_distribution

    pins = [(str(i), f"P{i}") for i in range(1, 40)]
    pins.append(("40", "GND"))
    ctx = build_ctx(
        components=[connector("J1", "Conn_40P", pins)],
        nets={
            **{f"NET{i}": [("J1", str(i))] for i in range(1, 40)},
            "GND":  [("J1", "40")],
        },
        known_power_rails={"GND"},
    )
    findings = audit_connector_ground_distribution(ctx)
    assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# audit_datasheet_coverage / audit_sourcing_gate (analyze_schematic.py)
# DS-003 and SS-002 must agree on the coverage denominator: unique BOM
# lines (value + footprint), not component references (KH-390). These two
# audits take a plain components list (not an AnalysisContext), so they
# don't use build_ctx() like the domain_detectors audits above.
# ---------------------------------------------------------------------------

def _bom_component(ref, value, footprint, mpn=None):
    c = {
        "reference": ref, "value": value, "type": "resistor",
        "footprint": footprint, "in_bom": True, "dnp": False,
    }
    if mpn is not None:
        c["mpn"] = mpn
    return c


def test_ds003_ss002_share_unique_bom_line_denominator(tmp_path):
    """4 resistors share one value+footprint (2 with MPNs, 2 without) —
    that line is fully covered under BOM-line grouping since one MPN'd
    instance covers the whole line. A second line (2 capacitors, no MPN)
    creates a genuine gap: 1 of 2 unique BOM lines lacks an MPN. DS-003
    and SS-002 must report that same 1-of-2 basis, not DS-003's old
    per-reference 4-of-6.
    """
    if _skip_if_no_kh():
        return
    from analyze_schematic import audit_datasheet_coverage, audit_sourcing_gate

    components = [
        _bom_component("R1", "10k", "Resistor_SMD:R_0402_1005Metric",
                       mpn="RC0402FR-0710KL"),
        _bom_component("R2", "10k", "Resistor_SMD:R_0402_1005Metric",
                       mpn="RC0402FR-0710KL"),
        _bom_component("R3", "10k", "Resistor_SMD:R_0402_1005Metric"),
        _bom_component("R4", "10k", "Resistor_SMD:R_0402_1005Metric"),
        _bom_component("C1", "100nF", "Capacitor_SMD:C_0402_1005Metric"),
        _bom_component("C2", "100nF", "Capacitor_SMD:C_0402_1005Metric"),
    ]

    # DS-003 needs a datasheets/ dir with at least one file to take the
    # "datasheets present, partial coverage" branch.
    ds_dir = tmp_path / "datasheets"
    ds_dir.mkdir()
    (ds_dir / "dummy.pdf").write_text("x")

    ds_findings = audit_datasheet_coverage(components, str(tmp_path))
    ss_findings = audit_sourcing_gate(components)

    ds003 = [f for f in ds_findings if f["rule_id"] == "DS-003"]
    ss002 = [f for f in ss_findings if f["rule_id"] == "SS-002"]
    assert len(ds003) == 1, f"expected one DS-003 finding, got {ds_findings}"
    assert len(ss002) == 1, f"expected one SS-002 finding, got {ss_findings}"

    # Same denominator: 2 unique BOM lines, 1 missing an MPN.
    assert ds003[0]["bom_size"] == 2
    assert ss002[0]["total_bom_lines"] == 2
    assert ds003[0]["mpn_coverage_percent"] == 50.0
    assert ss002[0]["mpn_coverage_percent"] == 50.0

    # Both summaries must name the "unique BOM lines" basis.
    assert "unique BOM lines" in ds003[0]["summary"]
    assert "unique BOM lines" in ss002[0]["summary"]
    assert "1 of 2 unique BOM lines" in ds003[0]["summary"]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            # Inspect the function signature to determine if it needs tmp_path
            import inspect
            sig = inspect.signature(fn)
            if "tmp_path" in sig.parameters:
                # Create a TemporaryDirectory and pass it as Path for tests needing fixtures
                with tempfile.TemporaryDirectory() as tmpdir:
                    fn(Path(tmpdir))
            else:
                fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
