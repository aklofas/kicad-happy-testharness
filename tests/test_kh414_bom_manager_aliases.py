"""KH-414 / GitHub #46 — bom_manager shares the analyzers' MPN / DigiKey
alias set and matches property names normalized (case + whitespace), while
keeping its own ambiguous extras (MP, MFN) bom-local.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "bom", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import bom_manager


def test_canonical_for_new_names():
    assert bom_manager._canonical_for("Manufacturer P/N") == "mpn"
    assert bom_manager._canonical_for("manufacturer  p/n") == "mpn"
    assert bom_manager._canonical_for("Digikey P/N") == "digikey"
    assert bom_manager._canonical_for("Digi-Key P/N") == "digikey"


def test_canonical_for_keeps_bom_local_extras():
    assert bom_manager._canonical_for("MP") == "mpn"
    assert bom_manager._canonical_for("MFN") == "mpn"


def test_canonical_for_other_fields_unchanged():
    assert bom_manager._canonical_for("Mouser Part Number") == "mouser"
    assert bom_manager._canonical_for("LCSC") == "lcsc"
    assert bom_manager._canonical_for("Farnell PN") == "element14"
    assert bom_manager._canonical_for("Datasheet") is None


def test_canonical_names_unchanged():
    assert bom_manager.CANONICAL_NAMES["mpn"] == "MPN"


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
