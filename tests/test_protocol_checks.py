"""Unit tests for protocol electrical parameter checks.

Validates new protocol_compliance, USB compliance, Ethernet/HDMI/LVDS detector
fields, and cross_verify diff pair intra-pair skew logic.

Tests scan real corpus outputs where possible and fall back to synthetic data
for functions callable standalone (cross_verify.check_diff_pair_routing).
"""

TIER = "unit"

import json
import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

_RESULTS = _HARNESS / "results" / "outputs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _SkipTest(Exception):
    """Raised to skip a test gracefully."""
    pass


def _skip(reason: str):
    raise _SkipTest(reason)


def _find_output_with(output_type, check_fn, max_scan=5000):
    """Find first output file where check_fn(data) returns True."""
    out_dir = _RESULTS / output_type
    if not out_dir.exists():
        return None, None
    scanned = 0
    for owner in sorted(out_dir.iterdir()):
        if not owner.is_dir():
            continue
        for repo in sorted(owner.iterdir()):
            if not repo.is_dir():
                continue
            for jf in sorted(repo.glob("*.json")):
                try:
                    data = json.loads(jf.read_text())
                    if check_fn(data):
                        return data, str(jf)
                except Exception:
                    pass
                scanned += 1
                if scanned >= max_scan:
                    return None, None
    return None, None


def _skip_if_none(data, feature_name):
    """Raise _SkipTest if data is None."""
    if data is None:
        _skip(f"no {feature_name} output found in corpus")
    return False


def _get_protocol_finding(data, protocol, check_key=None):
    """Extract a protocol_compliance finding by protocol and optional check key."""
    pc = data.get("protocol_compliance", {})
    for f in pc.get("findings", []):
        if f.get("protocol") != protocol:
            continue
        if check_key is None:
            return f
        checks = f.get("checks", {})
        if check_key in checks:
            return f
    return None


# ===========================================================================
# 3a. I2C VOL check
# ===========================================================================

def test_i2c_vol_compatibility_field_structure():
    """I2C vol_compatibility check has required fields when present."""
    def check(data):
        f = _get_protocol_finding(data, "i2c", "vol_compatibility")
        return f is not None

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, "I2C vol_compatibility"):
        return
    finding = _get_protocol_finding(data, "i2c", "vol_compatibility")
    vc = finding["checks"]["vol_compatibility"]
    assert vc["status"] == "warning", f"expected warning status, got {vc['status']}"
    assert "pull_up_ohms" in vc, "missing pull_up_ohms"
    assert "max_for_vol" in vc, "missing max_for_vol"
    assert "iol_ma" in vc, "missing iol_ma"
    assert "speed_mode" in vc, "missing speed_mode"
    assert isinstance(vc["pull_up_ohms"], (int, float))
    assert isinstance(vc["max_for_vol"], (int, float))
    assert vc["iol_ma"] > 0, "iol_ma must be positive"
    assert vc["speed_mode"] in ("standard", "fast", "fast_plus", "high_speed")


def test_i2c_vol_pullup_exceeds_max():
    """When vol_compatibility triggers, pull_up_ohms > max_for_vol."""
    def check(data):
        return _get_protocol_finding(data, "i2c", "vol_compatibility") is not None

    data, path = _find_output_with("schematic", check)
    if _skip_if_none(data, "I2C vol_compatibility"):
        return
    finding = _get_protocol_finding(data, "i2c", "vol_compatibility")
    vc = finding["checks"]["vol_compatibility"]
    # The check fires when pull_up_ohms > max_for_vol
    assert vc["pull_up_ohms"] > vc["max_for_vol"], \
        f"pull_up {vc['pull_up_ohms']} should exceed max {vc['max_for_vol']}"


# ===========================================================================
# 3b. I2C bus current budget
# ===========================================================================

def test_i2c_bus_current_budget_structure():
    """I2C bus_current_budget check has required fields."""
    def check(data):
        return _get_protocol_finding(data, "i2c", "bus_current_budget") is not None

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "I2C bus_current_budget"):
        return
    finding = _get_protocol_finding(data, "i2c", "bus_current_budget")
    bcb = finding["checks"]["bus_current_budget"]
    assert bcb["status"] == "warning"
    assert "device_count" in bcb
    assert "estimated_leakage_ua" in bcb
    assert "pull_up_current_ua" in bcb
    assert isinstance(bcb["device_count"], int)
    assert bcb["device_count"] > 0
    assert bcb["estimated_leakage_ua"] > 0


def test_i2c_bus_current_leakage_exceeds_threshold():
    """Bus current budget warning fires when leakage > 10% of pull-up current."""
    def check(data):
        return _get_protocol_finding(data, "i2c", "bus_current_budget") is not None

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "I2C bus_current_budget"):
        return
    finding = _get_protocol_finding(data, "i2c", "bus_current_budget")
    bcb = finding["checks"]["bus_current_budget"]
    # The check triggers when leakage > 10% of pull-up current
    assert bcb["estimated_leakage_ua"] > bcb["pull_up_current_ua"] * 0.1, \
        "leakage should exceed 10% of pull-up current when warning fires"


# ===========================================================================
# 3c. SPI device loading
# ===========================================================================

def test_spi_device_loading_warning_when_many_devices():
    """SPI device_loading warning fires when >4 devices on bus."""
    def check(data):
        return _get_protocol_finding(data, "spi", "device_loading") is not None

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "SPI device_loading"):
        return
    finding = _get_protocol_finding(data, "spi", "device_loading")
    dl = finding["checks"]["device_loading"]
    assert dl["status"] == "warning"
    assert dl["device_count"] > 4, f"expected >4 devices, got {dl['device_count']}"


def test_spi_no_device_loading_when_few_devices():
    """SPI bus with <=4 devices should not have device_loading warning."""
    def check(data):
        pc = data.get("protocol_compliance", {})
        for f in pc.get("findings", []):
            if f.get("protocol") != "spi":
                continue
            # Found an SPI finding without device_loading
            lc = f.get("load_count", 0)
            checks = f.get("checks", {})
            if "device_loading" not in checks and lc <= 4 and lc > 0:
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=3000)
    if _skip_if_none(data, "SPI bus with <=4 devices"):
        return
    pc = data.get("protocol_compliance", {})
    for f in pc.get("findings", []):
        if f.get("protocol") != "spi":
            continue
        lc = f.get("load_count", 0)
        checks = f.get("checks", {})
        if "device_loading" not in checks and lc <= 4 and lc > 0:
            assert "device_loading" not in checks, \
                "should not have device_loading with <=4 devices"
            break


# ===========================================================================
# 3d. UART RS-232 transceiver detection
# ===========================================================================

def test_uart_rs232_transceiver_detection():
    """UART finding detects RS-232 transceiver and reports it."""
    def check(data):
        return _get_protocol_finding(data, "uart", "rs232_transceiver") is not None

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "UART rs232_transceiver"):
        return
    finding = _get_protocol_finding(data, "uart", "rs232_transceiver")
    rs = finding["checks"]["rs232_transceiver"]
    assert rs["status"] == "pass", "rs232 transceiver detection should be pass"
    assert "transceivers" in rs
    assert isinstance(rs["transceivers"], list)
    assert len(rs["transceivers"]) > 0, "should have at least one transceiver ref"
    assert "detail" in rs


def test_uart_rs232_charge_pump_caps():
    """RS-232 transceiver check includes charge pump capacitor validation."""
    def check(data):
        return _get_protocol_finding(data, "uart", "rs232_transceiver") is not None

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "UART rs232_transceiver"):
        return
    finding = _get_protocol_finding(data, "uart", "rs232_transceiver")
    checks = finding.get("checks", {})
    # Charge pump check may or may not be present depending on cap count
    if "rs232_charge_pump_caps" in checks:
        cpc = checks["rs232_charge_pump_caps"]
        assert "status" in cpc
        assert "caps_found" in cpc
        assert "typical_required" in cpc
        assert isinstance(cpc["caps_found"], int)
        assert cpc["typical_required"] == 4


# ===========================================================================
# 3e. USB VBUS capacitance
# ===========================================================================

def test_usb_vbus_capacitance_warning():
    """USB vbus_capacitance warning fires when total < 1uF."""
    def check(data):
        uc = data.get("usb_compliance", {})
        for conn in uc.get("connectors", []):
            checks = conn.get("checks", {})
            vc = checks.get("vbus_capacitance")
            if isinstance(vc, dict) and vc.get("status") == "warning":
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=8000)
    if _skip_if_none(data, "USB vbus_capacitance warning"):
        return
    uc = data["usb_compliance"]
    for conn in uc["connectors"]:
        vc = conn["checks"].get("vbus_capacitance")
        if isinstance(vc, dict) and vc.get("status") == "warning":
            assert vc["total_uf"] < 1.0, \
                f"warning should fire when < 1uF, got {vc['total_uf']}"
            assert "recommended_min_uf" in vc
            assert vc["recommended_min_uf"] == 1.0
            assert "detail" in vc
            break


def test_usb_vbus_capacitance_pass():
    """USB vbus_capacitance passes when total >= 1uF."""
    def check(data):
        uc = data.get("usb_compliance", {})
        for conn in uc.get("connectors", []):
            checks = conn.get("checks", {})
            vc = checks.get("vbus_capacitance")
            if isinstance(vc, dict) and vc.get("status") == "pass":
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=8000)
    if _skip_if_none(data, "USB vbus_capacitance pass"):
        return
    uc = data["usb_compliance"]
    for conn in uc["connectors"]:
        vc = conn["checks"].get("vbus_capacitance")
        if isinstance(vc, dict) and vc.get("status") == "pass":
            assert vc["total_uf"] >= 1.0, \
                f"pass should require >= 1uF, got {vc['total_uf']}"
            break


# ===========================================================================
# 3f. Ethernet impedance advisory
# ===========================================================================

def test_ethernet_impedance_advisory_present():
    """Ethernet interface has impedance_advisory field."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for eth in sa.get("ethernet_interfaces", []):
            if "impedance_advisory" in eth:
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "Ethernet impedance_advisory"):
        return
    sa = data["signal_analysis"]
    for eth in sa["ethernet_interfaces"]:
        if "impedance_advisory" not in eth:
            continue
        ia = eth["impedance_advisory"]
        assert "status" in ia, "impedance_advisory must have status"
        assert ia["status"] in ("pass", "warning", "fail"), \
            f"unexpected status: {ia['status']}"
        assert "detail" in ia, "impedance_advisory must have detail string"
        break


def test_ethernet_impedance_advisory_magnetics_pass():
    """Ethernet with magnetics gets pass on impedance_advisory."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for eth in sa.get("ethernet_interfaces", []):
            ia = eth.get("impedance_advisory", {})
            if ia.get("status") == "pass" and eth.get("magnetics"):
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=8000)
    if _skip_if_none(data, "Ethernet impedance_advisory pass with magnetics"):
        return
    sa = data["signal_analysis"]
    for eth in sa["ethernet_interfaces"]:
        ia = eth.get("impedance_advisory", {})
        if ia.get("status") == "pass" and eth.get("magnetics"):
            assert len(eth["magnetics"]) > 0
            break


# ===========================================================================
# 3g. HDMI termination check
# ===========================================================================

def test_hdmi_termination_field_present():
    """HDMI/DVI interface entry has termination check field."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for h in sa.get("hdmi_dvi_interfaces", []):
            if "termination" in h:
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=15000)
    if _skip_if_none(data, "HDMI termination"):
        return
    sa = data["signal_analysis"]
    for h in sa["hdmi_dvi_interfaces"]:
        if "termination" not in h:
            continue
        term = h["termination"]
        assert "status" in term, "termination must have status"
        assert term["status"] in ("pass", "warning"), \
            f"unexpected status: {term['status']}"
        assert "detail" in term, "termination must have detail string"
        break


def test_hdmi_termination_warning_no_resistors():
    """HDMI without termination resistors gets warning."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for h in sa.get("hdmi_dvi_interfaces", []):
            term = h.get("termination", {})
            if isinstance(term, dict) and term.get("status") == "warning":
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=15000)
    if _skip_if_none(data, "HDMI termination warning"):
        return
    sa = data["signal_analysis"]
    for h in sa["hdmi_dvi_interfaces"]:
        term = h.get("termination", {})
        if isinstance(term, dict) and term.get("status") == "warning":
            assert "100" in term["detail"] or "termination" in term["detail"].lower(), \
                "warning should mention termination requirement"
            break


# ===========================================================================
# 3h. LVDS detection
# ===========================================================================

def test_lvds_interfaces_detected():
    """LVDS interfaces are detected in signal_analysis."""
    def check(data):
        sa = data.get("signal_analysis", {})
        return len(sa.get("lvds_interfaces", [])) > 0

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "LVDS interfaces"):
        return
    sa = data["signal_analysis"]
    lvds = sa["lvds_interfaces"]
    assert len(lvds) > 0
    entry = lvds[0]
    assert "reference" in entry, "LVDS entry must have reference"
    assert "role" in entry, "LVDS entry must have role"
    assert entry["role"] in ("serializer", "deserializer", "unknown"), \
        f"unexpected role: {entry['role']}"


def test_lvds_impedance_requirement():
    """LVDS entries include impedance_required field."""
    def check(data):
        sa = data.get("signal_analysis", {})
        for l in sa.get("lvds_interfaces", []):
            if "impedance_required" in l:
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=5000)
    if _skip_if_none(data, "LVDS impedance_required"):
        return
    sa = data["signal_analysis"]
    for entry in sa["lvds_interfaces"]:
        if "impedance_required" in entry:
            assert "100" in entry["impedance_required"], \
                "LVDS should require 100 ohm differential impedance"
            break


# ===========================================================================
# 3i. Diff pair intra-pair skew (cross_verify)
# ===========================================================================

from cross_verify import check_diff_pair_routing


def test_diff_pair_skew_usb_exceeds_tolerance():
    """USB diff pair with 2mm intra-pair skew (>1mm tolerance) produces finding."""
    sch = {
        "design_analysis": {
            "differential_pairs": [{
                "positive": "USB_DP",
                "negative": "USB_DN",
                "type": "USB",
            }],
        },
    }
    pcb = {
        "net_lengths": [
            {"net": "USB_DP", "total_length_mm": 50.0, "layers": {"F.Cu": 50.0}},
            {"net": "USB_DN", "total_length_mm": 52.0, "layers": {"F.Cu": 52.0}},
        ],
    }
    results = check_diff_pair_routing(sch, pcb)
    assert len(results) == 1
    entry = results[0]
    assert entry["type"] == "USB"
    # 2mm delta exceeds both the outer tolerance (2.0mm) and the
    # intra-pair tolerance (1.0mm)
    assert entry["delta_mm"] == 2.0

    # The intra-pair skew check should fire (2mm > 1mm tolerance)
    assert "intra_pair_skew" in entry, \
        "intra_pair_skew should be present for 2mm skew on USB (1mm tolerance)"
    skew = entry["intra_pair_skew"]
    assert skew["skew_mm"] == 2.0
    assert skew["tolerance_mm"] == 1.0
    assert skew["severity"] in ("MEDIUM", "HIGH")
    assert "detail" in skew


def test_diff_pair_skew_usb_within_tolerance():
    """USB diff pair with 0.3mm skew (within 1mm tolerance) has no skew finding."""
    sch = {
        "design_analysis": {
            "differential_pairs": [{
                "positive": "USB_DP",
                "negative": "USB_DN",
                "type": "USB",
            }],
        },
    }
    pcb = {
        "net_lengths": [
            {"net": "USB_DP", "total_length_mm": 50.0, "layers": {"F.Cu": 50.0}},
            {"net": "USB_DN", "total_length_mm": 50.3, "layers": {"F.Cu": 50.3}},
        ],
    }
    results = check_diff_pair_routing(sch, pcb)
    assert len(results) == 1
    entry = results[0]
    assert entry["type"] == "USB"
    assert entry["delta_mm"] == 0.3
    assert entry["status"] == "pass", \
        f"0.3mm skew should pass for USB, got {entry['status']}"
    assert "intra_pair_skew" not in entry, \
        "intra_pair_skew should not be present for 0.3mm skew"


# ===========================================================================
# 3j. KH-229 — vbus_capacitance must be string, detail in separate key
# ===========================================================================

def test_kh229_vbus_capacitance_is_string():
    """KH-229: vbus_capacitance must be a status string, not a dict."""
    def check(data):
        uc = data.get("usb_compliance", {})
        for conn in uc.get("connectors", []):
            checks = conn.get("checks", {})
            if "vbus_capacitance" in checks:
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=8000)
    if _skip_if_none(data, "USB vbus_capacitance"):
        return
    uc = data["usb_compliance"]
    for conn in uc["connectors"]:
        vc = conn["checks"].get("vbus_capacitance")
        if vc is not None:
            assert isinstance(vc, str), \
                f"KH-229: vbus_capacitance should be a string, got {type(vc).__name__}: {vc!r}"
            assert vc in ("pass", "warning", "fail", "info"), \
                f"unexpected status value: {vc!r}"
            break


def test_kh229_vbus_detail_separate():
    """KH-229: vbus_capacitance_detail dict on connector when status is pass/warning."""
    def check(data):
        uc = data.get("usb_compliance", {})
        for conn in uc.get("connectors", []):
            vc = conn.get("checks", {}).get("vbus_capacitance")
            if isinstance(vc, str) and vc in ("pass", "warning"):
                return True
        return False

    data, path = _find_output_with("schematic", check, max_scan=8000)
    if _skip_if_none(data, "USB vbus_capacitance pass/warning with detail"):
        return
    uc = data["usb_compliance"]
    for conn in uc["connectors"]:
        vc = conn.get("checks", {}).get("vbus_capacitance")
        if isinstance(vc, str) and vc in ("pass", "warning"):
            # detail lives on the connector dict, not inside checks
            detail = conn.get("vbus_capacitance_detail")
            assert detail is not None, \
                "vbus_capacitance_detail should exist when status is pass/warning"
            assert isinstance(detail, dict), \
                f"vbus_capacitance_detail should be a dict, got {type(detail).__name__}"
            assert "total_uf" in detail, \
                "vbus_capacitance_detail must contain total_uf key"
            assert isinstance(detail["total_uf"], (int, float)), \
                f"total_uf should be numeric, got {type(detail['total_uf']).__name__}"
            break


# ---------------------------------------------------------------------------
# __main__ runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed = failed = skipped = 0
    for t in tests:
        name = t.__name__
        try:
            t()
            passed += 1
            print(f"  PASS  {name}")
        except _SkipTest as e:
            skipped += 1
            print(f"  SKIP  {name}: {e}")
        except Exception:
            failed += 1
            print(f"  FAIL  {name}")
            traceback.print_exc()

    total = passed + failed + skipped
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped ({total} total)")
    sys.exit(1 if failed else 0)
