r"""KH-407 — the PR #44 voltage-name rule `^\d+V([A-Z][0-9A-Z]*)?$` excluded
only the literal `0V`; `0VA`, `0Vo`, `0VANA`, `0VCC` (European/analog ground
spellings) flipped to rails on 25 corpus units. Any `0V<letter/underscore>…`
name is ground — but `0V<digit>` (0V9, 0V85, 0V95, 0V5) is a sub-1V rail
under the industry `nnVn` naming convention (FPGA/SoC core supplies), not
ground. Fix round 1 (post-review): the first pass's `^\+?0+V` guard was too
broad and misclassified those sub-1V rails as ground."""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_utils import is_ground_name, is_power_net_name  # noqa: E402

ZERO = ("0V", "0VA", "0Vo", "0VANA", "0VCC", "0V_A", "+0V", "0VD", "/Power/0VA")
ZERO_DIGIT = ("0V9", "0V85", "0V95", "0V5")


def test_zero_volt_spellings_are_ground():
    for n in ZERO:
        assert is_ground_name(n), n


def test_zero_volt_spellings_are_not_power():
    for n in ZERO:
        assert not is_power_net_name(n), n


def test_zero_volt_digit_suffixed_are_power_not_ground():
    for n in ZERO_DIGIT:
        assert is_power_net_name(n), n
        assert not is_ground_name(n), n


def test_real_rails_unaffected():
    for n in ("5V", "10V", "1V0", "5VSB", "+3V3", "3V3"):
        assert is_power_net_name(n), n
    assert not is_ground_name("10V")


if __name__ == "__main__":
    import sys
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
