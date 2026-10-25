"""GitHub #55 - PP-001 reported a buck's BST pin (typed power_in by many
vendor symbols) as "no DC path to a power rail" at error. A bootstrap pin
reaches SW through a capacitor and must not have a DC path to a rail. The
audit now skips power_in pins named like a bootstrap (BST / BOOT / CBST /
BOOTSTRAP, with digit or _A.._D channel suffixes), the names
detect_power_regulators already uses.
"""

TIER = "unit"

import os
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = str(PRODUCT_ROOT)
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_types import build_analysis_context  # noqa: E402
from signal_detectors import audit_power_pin_dc_paths  # noqa: E402


def _pin(ref, num, ptype="passive", name=""):
    return {"component": ref, "pin_number": num, "pin_type": ptype,
            "pin_name": name}


def _buck(bst_name="BST"):
    """U1 VIN on +5V (PWR_FLAG), C1 100n between BST and SW."""
    comps = [{"reference": "U1", "type": "ic", "value": "BUCK"},
             {"reference": "C1", "type": "capacitor", "value": "100n"}]
    nets = {
        "+5V": {"pins": [_pin("U1", "1", "power_in", "VIN")],
                "has_pwr_flag": True},
        "GND": {"pins": [_pin("U1", "2", "power_in", "GND")]},
        "SW": {"pins": [_pin("U1", "3", "output", "SW"), _pin("C1", "2")]},
        "BST": {"pins": [_pin("U1", "4", "power_in", bst_name),
                         _pin("C1", "1")]},
    }
    return build_analysis_context(comps, nets, {})


def _pp001(ctx):
    return [f for f in audit_power_pin_dc_paths(ctx) if f["rule_id"] == "PP-001"]


def test_bootstrap_pin_names_are_skipped():
    for name in ("BST", "BOOT", "CBST", "BOOTSTRAP", "BOOT1", "BST_A", "BST_D"):
        assert _pp001(_buck(name)) == [], name


def test_cap_only_supply_pin_still_fires():
    found = _pp001(_buck("VAUX"))
    assert len(found) == 1 and found[0]["severity"] == "error", found


if __name__ == "__main__":
    import traceback
    ok = fail = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                ok += 1
            except Exception:  # noqa: BLE001
                fail += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"{ok} passed, {fail} failed")
    sys.exit(1 if fail else 0)
