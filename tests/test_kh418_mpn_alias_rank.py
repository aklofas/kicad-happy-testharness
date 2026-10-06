"""KH-418 — a generic part-number field (`Part#`, `Part Number`, `PartNo`)
must never outrank a manufacturer-specific one (`MPN`, `Manufacturer P/N`,
`Mfr Part Number`, ...). KH-414 made the pick file-order deterministic,
which turned an El-Luhb `Part#`=LCSC-code-before-`MPN` symbol into a
deterministic wrong answer. Two tiers: manufacturer-specific first, generic
only when no manufacturer-specific field is populated; file order breaks
ties within a tier. Fixtures: tests/fixtures/kh418/ (R4 carries Part#
before MPN; R5 carries Part# only).
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
sys.path.insert(0, str(_KH / "skills" / "kicad" / "scripts"))
sys.path.insert(0, str(_KH / "skills" / "bom" / "scripts"))

from kicad_utils import (MPN_FIELD_ALIASES, MPN_FIELD_ALIASES_PRIMARY,
                         MPN_FIELD_ALIASES_GENERIC, pick_mpn, get_mpn_property)

SCH = _KH / "skills/kicad/scripts/analyze_schematic.py"
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
BOM = _KH / "skills/bom/scripts/bom_manager.py"
FIX = _HARNESS / "tests/fixtures/kh418"
_CACHE = {}


def _run(script, path, *args):
    key = (str(script), str(path))
    if key not in _CACHE:
        out = subprocess.run([sys.executable, str(script), str(path), *args],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE[key] = json.loads(out.stdout)
    return _CACHE[key]


def test_tiers_partition_the_shared_set():
    assert MPN_FIELD_ALIASES_PRIMARY | MPN_FIELD_ALIASES_GENERIC == MPN_FIELD_ALIASES
    assert not (MPN_FIELD_ALIASES_PRIMARY & MPN_FIELD_ALIASES_GENERIC)
    for n in ("mpn", "manufacturer p/n", "manufacturer part number", "mfr_part_number", "mfg part"):
        assert n in MPN_FIELD_ALIASES_PRIMARY, n
    for n in ("part#", "part number", "partnumber", "partno", "partno."):
        assert n in MPN_FIELD_ALIASES_GENERIC, n


def test_pick_mpn_primary_beats_generic_regardless_of_order():
    assert pick_mpn({"Part#": "C86295", "MPN": "SN74"}) == "SN74"
    assert pick_mpn({"MPN": "SN74", "Part#": "C86295"}) == "SN74"
    assert pick_mpn({"Part Number": "C1", "Manufacturer P/N": "X1"}) == "X1"


def test_pick_mpn_generic_used_when_no_primary():
    assert pick_mpn({"Part#": "RC0603FR-071KL"}) == "RC0603FR-071KL"
    assert pick_mpn({"Part#": "", "MPN": ""}) == ""
    assert pick_mpn({"Value": "10k"}) == ""


def test_pick_mpn_file_order_within_tier():
    assert pick_mpn({"Manufacturer P/N": "A", "MPN": "B"}) == "A"
    assert pick_mpn({"MPN": "B", "Manufacturer P/N": "A"}) == "B"


def test_get_mpn_property_tiers():
    fp = ["footprint", "X", ["property", "Part#", "C86295"], ["property", "MPN", "SN74"]]
    assert get_mpn_property(fp) == "SN74"
    fp2 = ["footprint", "X", ["property", "Part#", "C86295"]]
    assert get_mpn_property(fp2) == "C86295"
    assert get_mpn_property(["footprint", "X"]) is None


def test_schematic_fixture_ranks():
    comps = {c["reference"]: c for c in _run(SCH, FIX / "mpn_rank.kicad_sch", "--compact")["components"]}
    assert comps["R4"]["mpn"] == "SN74LVC1G08DBVR"
    assert comps["R5"]["mpn"] == "RC0603FR-071KL"
    assert comps["R1"]["mpn"] == "RC0805FR-0710KL"   # kh414 behaviour unchanged


def test_pcb_fixture_ranks():
    fps = {f["reference"]: f for f in _run(PCB, FIX / "mpn_rank.kicad_pcb")["footprints"]}
    assert fps["R4"]["mpn"] == "SN74LVC1G08DBVR"
    assert fps["R1"]["mpn"] == "RC0805FR-0710KL"


def test_bom_manager_fallback_ranks():
    import bom_manager
    # The alias-scan fallback (used when the project's convention field is empty
    # on a symbol) must apply the same tiers.
    props = {"Part#": "C86295", "MPN": "SN74", "Reference": "R4"}
    assert bom_manager._pick_mpn_from_props(props) == "SN74"
    assert bom_manager._pick_mpn_from_props({"Part#": "C86295"}) == "C86295"


def test_bom_manager_majority_field_does_not_outrank_primary():
    # Reviewer-reported El-Luhb reproduction: `Part#` is the project's
    # convention-majority field for the "mpn" canonical (it's the most common
    # field name across R1-R3, R5), but R4 ALSO carries a populated `MPN`
    # field. The majority-field shortcut in get_canonical must not shadow a
    # populated primary-tier field on the symbol that has one.
    out = subprocess.run(
        [sys.executable, str(BOM), "analyze",
         str(FIX / "mpn_rank_majority.kicad_sch"), "--json"],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    data = json.loads(out.stdout)
    assert data["convention"]["field_mapping"]["mpn"] == "Part#"  # majority IS generic
    by_ref = {tuple(line["references"]): line["mpn"] for line in data["bom"]}
    assert by_ref[("R4",)] == "SN74LVC1G08DBVR"
    assert by_ref[("R1",)] == "RC0805FR-0710KL"
    assert by_ref[("R5",)] == "RC0603FR-071KL"


def test_bom_manager_convention_primary_beats_other_primary():
    # Round 2: when the project's convention-majority field for "mpn" is
    # ITSELF primary-tier (here `MPN`, populated on R1-R3), it is
    # authoritative over another, differently-named primary-tier field that
    # happens to come first in file order on one symbol. R4 carries
    # `Manufacturer P/N`=`WRONG-FIRST` BEFORE `MPN`=`SN74LVC1G08DBVR` — file
    # order must NOT win here; the project's declared MPN field does.
    out = subprocess.run(
        [sys.executable, str(BOM), "analyze",
         str(FIX / "mpn_rank_two_primaries.kicad_sch"), "--json"],
        capture_output=True, text=True, timeout=120,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    data = json.loads(out.stdout)
    assert data["convention"]["field_mapping"]["mpn"] == "MPN"  # majority IS primary-tier
    by_ref = {tuple(line["references"]): line["mpn"] for line in data["bom"]}
    assert by_ref[("R4",)] == "SN74LVC1G08DBVR"
    assert by_ref[("R1",)] == "RC0805FR-0710KL"


def test_blank_primary_does_not_mask_generic():
    # Final wave fix: a whitespace-only MPN must not win the primary tier
    # and shadow a populated generic field (BerkeleyLab Marble/Obsidian
    # mounting holes and fiducials carry MPN=" ").
    assert pick_mpn({"MPN": " ", "Part#": "X"}) == "X"
    assert pick_mpn({"MPN": "", "Part#": "X"}) == "X"
    fp = ["footprint", "X", ["property", "MPN", " "], ["property", "Part#", "Y"]]
    assert get_mpn_property(fp) == "Y"


def test_blank_only_symbol_keeps_old_behaviour():
    # No alias has a non-blank value anywhere: fall back to the pre-KH-418
    # pick (first truthy value in file order) so blank-only symbols are
    # unaffected by this fix and the corpus does not move on them.
    assert pick_mpn({"MPN": " "}) == " "


def test_bom_manager_strips_and_skips_blanks():
    import bom_manager
    assert bom_manager._pick_mpn_from_props({"Part#": "C1", "MPN": " "}) == "C1"
    assert bom_manager._pick_mpn_from_props({"MPN": " SN74 "}) == "SN74"
    assert bom_manager._first_nonblank_stripped({"MPN": "   "}, MPN_FIELD_ALIASES_PRIMARY) == ""


def test_legacy_sch_blank_primary_does_not_mask_generic():
    # Fix round 2: the legacy .sch custom-field loop's generic branch tested
    # `if not comp.get("mpn")`, and " " counts as set, so a blank primary
    # field appearing BEFORE a populated generic field still masked it.
    # R1 carries F4="MPN"=" " before F5="Part Number"="RC0603-10K" (blank
    # primary first); R2 carries the reverse order (populated generic
    # first, blank primary second) — both must resolve to the populated
    # generic value.
    comps = {c["reference"]: c for c in
             _run(SCH, FIX / "legacy_blank_primary.sch", "--compact")["components"]}
    assert comps["R1"]["mpn"] == "RC0603-10K"
    assert comps["R2"]["mpn"] == "RC0603-10K"


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
        except (AssertionError, ImportError, AttributeError) as e:
            failed += 1
            print(f"  FAIL: {name}: {e!r}")
    print(f"\n{passed} passed, {failed} failed ({passed + failed} total)")
    _sys.exit(1 if failed else 0)
