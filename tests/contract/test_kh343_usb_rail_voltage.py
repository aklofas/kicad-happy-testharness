#!/usr/bin/env python3
"""KH-343: rail-voltage inference must not map USB data lines to 5.0V."""

import sys

from tests.contract._paths import MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))
from analyze_schematic import _estimate_rail_voltage
from signal_detectors import _infer_rail_voltage


def test_usb_data_nets_get_no_voltage():
    for name in ("USB_DM", "USB_DP", "USBDP", "USBDM", "/usb/USB_D+",
                 "USB_D-", "USB_DPLUS", "USB_DMINUS"):
        assert _estimate_rail_voltage(name) is None, name
        assert _infer_rail_voltage(name) is None, name


def test_usb_power_nets_still_5v():
    for name in ("VBUS", "USB_VBUS", "VUSB", "USB_PWR", "USB"):
        assert _estimate_rail_voltage(name) == 5.0, name
        assert _infer_rail_voltage(name) == 5.0, name
