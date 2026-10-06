"""KH-414 / GitHub #46 — `Manufacturer P/N` and `Digikey P/N` property names
were not recognised as MPN / DigiKey fields.

Three alias lists had drifted apart: analyze_schematic's `_MPN_KEYS` /
`_DIGIKEY_KEYS`, analyze_pcb's exact-case `get_property(fp, "MPN") or
get_property(fp, "Mfg Part")`, and bom_manager's `FIELD_ALIASES`. The fix
is one shared, normalized alias set in kicad_utils consumed by all three
(spec docs/superpowers/specs/2026-10-04-v2.3.1-maintenance-batch-design.md §1).

This file covers the kicad_utils primitives; the analyzer-level fixture
tests live in test_kh414_mpn_fixture.py.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

from kicad_utils import (normalize_field_name, MPN_FIELD_ALIASES,
                         DIGIKEY_FIELD_ALIASES, pick_field, get_property_ci)


def test_normalize_collapses_whitespace_and_case():
    assert normalize_field_name("Manufacturer  P/N") == "manufacturer p/n"
    assert normalize_field_name("  MPN ") == "mpn"
    assert normalize_field_name("Digi-Key\tP/N") == "digi-key p/n"


def test_new_aliases_present():
    for name in ("manufacturer p/n", "mfr p/n", "mfg p/n",
                 "manufacturer part number", "manf#", "mpn", "mfg part"):
        assert name in MPN_FIELD_ALIASES, name
    for name in ("digikey p/n", "digi-key p/n", "digikey", "dk"):
        assert name in DIGIKEY_FIELD_ALIASES, name


def test_ambiguous_bom_extras_excluded():
    # bom_manager keeps MP / MFN as bom-local extras; they must not leak
    # into the analyzers (would create new false MPN hits corpus-wide).
    assert "mp" not in MPN_FIELD_ALIASES
    assert "mfn" not in MPN_FIELD_ALIASES


def test_pick_field_case_insensitive():
    props = {"Reference": "R1", "Manufacturer P/N": "RC0805FR-0710KL"}
    assert pick_field(props, MPN_FIELD_ALIASES) == "RC0805FR-0710KL"
    assert pick_field({"MANUFACTURER P/N": "X"}, MPN_FIELD_ALIASES) == "X"
    assert pick_field({"Value": "10k"}, MPN_FIELD_ALIASES) == ""


def test_pick_field_is_file_order_not_hash_order():
    # Two aliases present: the FIRST one in property (file) order wins,
    # independent of PYTHONHASHSEED (the old _pick iterated a frozenset).
    props = {"Manufacturer P/N": "FIRST", "MPN": "SECOND"}
    assert pick_field(props, MPN_FIELD_ALIASES) == "FIRST"
    props2 = {"MPN": "FIRST", "Manufacturer P/N": "SECOND"}
    assert pick_field(props2, MPN_FIELD_ALIASES) == "FIRST"


def test_pick_field_skips_empty_values():
    props = {"MPN": "", "Manufacturer P/N": "X"}
    assert pick_field(props, MPN_FIELD_ALIASES) == "X"


def test_get_property_ci_matches_footprint_properties():
    fp = ["footprint", "Resistor_SMD:R_0805",
          ["property", "Reference", "R1"],
          ["property", "Manufacturer P/N", "RC0805FR-0710KL"],
          ["property", "private", "Digikey P/N", "311-10.0KCRCT-ND"]]
    assert get_property_ci(fp, MPN_FIELD_ALIASES) == "RC0805FR-0710KL"
    assert get_property_ci(fp, DIGIKEY_FIELD_ALIASES) == "311-10.0KCRCT-ND"
    assert get_property_ci(fp, frozenset({"nothing"})) is None


if __name__ == "__main__":
    import sys as _sys
    tests = [(name, fn) for name, fn in globals().items()
             if name.startswith("test_") and callable(fn)]
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
    _sys.exit(1 if failed else 0)
