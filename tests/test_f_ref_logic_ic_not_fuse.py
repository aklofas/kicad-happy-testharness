"""F-prefixed logic/analog ICs must not classify as `fuse`.

`classify_component`'s single-char prefix fallback maps the "F" prefix to
"fuse" (fuses are commonly ref-designated F1, F2, ...). But a 74LS32 wired
with reference F1 (seen in the corpus) also falls through to that prefix
map, and PP-001 (IC power-pin DC-continuity audit) then walks through a
logic IC as if it were a fuse -- bridging power rails it shouldn't.

The existing `result == "fuse"` override block (fiducial / filter-or-emi /
ferrite-or-bead lib_id overrides) gains a check: an F-ref whose lib_id names
a logic/analog IC family, or whose value looks like a standard logic part
number (74xx/40xx/45xx with common vendor prefixes), classifies as "ic"
instead. Real fuses (Device:Fuse lib_id, or no lib_id at all with a generic
current/value like "500mA") are unaffected.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_utils import classify_component  # noqa: E402


def test_f_ref_logic_ic_classifies_as_ic():
    result = classify_component("F1", "74xx:74LS32", "74LS32", footprint="Package_DIP:DIP-14_W7.62mm")
    assert result == "ic", result


def test_f_ref_real_fuse_still_fuse():
    result = classify_component("F1", "Device:Fuse", "2A", footprint="Fuse:Fuse_0603")
    assert result == "fuse", result


def test_f_ref_generic_no_lib_still_fuse():
    result = classify_component("F2", "", "500mA", footprint="")
    assert result == "fuse", result


def test_f_ref_current_ratings_still_fuse():
    """KH: the 74/40/45-prefix regex used to match fuse current ratings
    like "4000mA" or "4500 mA" (the leading "40"/"45" digits plus trailing
    digits satisfied the pattern even with an amp-unit suffix), wrongly
    reclassifying them as ICs. A trailing (m)A unit must block the match."""
    for value in ("4000mA", "4500 mA", "4A", "500mA", "2A"):
        result = classify_component("F1", "Device:Fuse", value, footprint="Fuse:Fuse_0603")
        assert result == "fuse", (value, result)
        result_fallback = classify_component("F1", "", value, footprint="")
        assert result_fallback == "fuse", (value, result_fallback)


def test_f_ref_logic_ic_values_still_ic():
    """Real logic/analog part numbers (no trailing amp unit) must keep
    classifying as ic, both through the full-prefix lib_id path and the
    single-char fallback path."""
    for value in ("74ls32", "cd4001be", "7432"):
        result = classify_component("F1", "74xx:" + value, value, footprint="Package_DIP:DIP-14_W7.62mm")
        assert result == "ic", (value, result)
        result_fallback = classify_component("F1", "", value, footprint="")
        assert result_fallback == "ic", (value, result_fallback)


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
