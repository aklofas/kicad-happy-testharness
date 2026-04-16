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
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in sorted(tests):
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL: {name}: {e}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    sys.exit(1 if failed else 0)
