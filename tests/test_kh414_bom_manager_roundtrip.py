"""KH-414 final wave — bom_manager's `get_canonical()` (used inside
`generate_bom`) returned the convention-majority field's value even when
that value was EMPTY on a given symbol, so the normalized-alias fallback
scan (added for KH-414) was never reached for any symbol that didn't
populate the one field the project's convention happened to pick. Fixed
by falling through to the alias scan whenever the majority field is
empty on the symbol at hand.

Fixture: tests/fixtures/kh414/mpn_pn_fields.kicad_sch (R1 "Manufacturer
P/N", R2 "Manufacturer Part Number", R3 "MP" only).

Verified behavior note (deviation from the task brief's literal
"3 parts, 2 with MPN" expectation): bom_manager's own `FIELD_ALIASES["mpn"]`
deliberately ADDS back `MP`/`MFN` as bom-local extras on top of the shared
`MPN_FIELD_ALIASES` (see kicad_utils.py — those two names are excluded from
the shared set specifically so the schematic/PCB analyzers don't treat them
as MPN, but bom_manager keeps them as its own ambiguous-but-accepted aliases).
So once the empty-value fallthrough is fixed, R3's `MP` field IS picked up
by bom_manager's own alias scan -- verified by running
`bom_manager.py analyze --json` on this fixture both pre-fix (reports 1/3)
and post-fix (reports 3/3, not 2/3). This test asserts the actually-observed
post-fix behavior (R1, R2 AND R3 all count as having an MPN) rather than the
schematic-analyzer-shaped 2/3 figure, since R3's `MP` acceptance is bom_manager
by-design, not a bug this fix introduces.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
BOM_MANAGER = _KH / "skills/bom/scripts/bom_manager.py"
FIXTURE = _HARNESS / "tests/fixtures/kh414/mpn_pn_fields.kicad_sch"
_CACHE = {}


def _run():
    if "d" not in _CACHE:
        out = subprocess.run(
            [sys.executable, str(BOM_MANAGER), "analyze", str(FIXTURE), "--json"],
            capture_output=True, text=True, timeout=120,
        )
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["d"] = json.loads(out.stdout)
    return _CACHE["d"]


def _line(ref):
    return next(b for b in _run()["bom"] if ref in b["references"])


def test_three_parts_total():
    assert _run()["stats"]["total_components"] == 3


def test_r1_has_mpn_via_majority_field():
    assert _line("R1")["mpn"] == "RC0805FR-0710KL"


def test_r2_has_mpn_via_alias_fallback():
    # R2 doesn't populate the convention-majority field ("Manufacturer P/N");
    # pre-fix this returned "" instead of falling through to the alias scan.
    assert _line("R2")["mpn"] == "CRCW080510K0FKEA"


def test_r3_has_mpn_via_bom_local_mp_alias():
    # bom_manager (unlike the schematic/PCB analyzers) accepts "MP" as its
    # own ambiguous-but-recognized mpn alias -- by design (kicad_utils.py
    # MPN_FIELD_ALIASES excludes "mp"/"mfn"; bom_manager adds them back).
    assert _line("R3")["mpn"] == "SHOULD-NOT-BE-AN-MPN"


def test_with_mpn_count_is_three_of_three():
    assert _run()["stats"]["with_mpn"] == 3
    assert _run()["stats"]["without_mpn"] == 0


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
