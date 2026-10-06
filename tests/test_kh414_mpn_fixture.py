"""KH-414 / GitHub #46 — analyzer-level check that `Manufacturer P/N`,
`Manufacturer Part Number`, `Digikey P/N` and `Digi-Key P/N` populate the
schematic `components[].mpn` / `.digikey` fields and leave
`statistics.missing_mpn`, while the ambiguous bom-only alias `MP` does not.
Fixture: tests/fixtures/kh414/mpn_pn_fields.kicad_sch (R1/R2 annotated,
R3 carries only `MP`).
"""

TIER = "unit"

import json
import os
import subprocess
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy")))
SCH = _KH / "skills/kicad/scripts/analyze_schematic.py"
FIXTURE = _HARNESS / "tests/fixtures/kh414/mpn_pn_fields.kicad_sch"

_CACHE = {}


def _run():
    if "d" not in _CACHE:
        out = subprocess.run([sys.executable, str(SCH), str(FIXTURE), "--compact"],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["d"] = json.loads(out.stdout)
    return _CACHE["d"]


def _comp(ref):
    return next(c for c in _run()["components"] if c["reference"] == ref)


PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
PCB_FIXTURE = _HARNESS / "tests/fixtures/kh414/mpn_pn_fields.kicad_pcb"


def _run_pcb():
    if "p" not in _CACHE:
        out = subprocess.run([sys.executable, str(PCB), str(PCB_FIXTURE)],
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-2000:]
        _CACHE["p"] = json.loads(out.stdout)
    return _CACHE["p"]


def test_pcb_footprint_mpn_from_manufacturer_pn():
    fps = {f["reference"]: f for f in _run_pcb()["footprints"]}
    assert fps["R1"]["mpn"] == "RC0805FR-0710KL"


def test_pcb_footprint_mpn_case_insensitive():
    fps = {f["reference"]: f for f in _run_pcb()["footprints"]}
    assert fps["R2"]["mpn"] == "CRCW080510K0FKEA"


def test_manufacturer_pn_is_mpn():
    assert _comp("R1")["mpn"] == "RC0805FR-0710KL"


def test_manufacturer_part_number_is_mpn():
    assert _comp("R2")["mpn"] == "CRCW080510K0FKEA"


def test_digikey_pn_variants():
    assert _comp("R1")["digikey"] == "311-10.0KCRCT-ND"
    assert _comp("R2")["digikey"] == "541-10.0KCCT-ND"


def test_mp_is_not_an_mpn():
    assert _comp("R3")["mpn"] == ""


def test_missing_mpn_lists_only_r3():
    missing = _run()["statistics"]["missing_mpn"]
    assert "R1" not in missing and "R2" not in missing, missing
    assert "R3" in missing, missing


def test_no_ss001_or_ds001_for_annotated_parts():
    rule_ids = {f.get("rule_id") for f in _run().get("findings", [])}
    # Two of three unique parts carry an MPN; SS-001 ("0/N carry an MPN")
    # must not fire. (DS-001 is coverage-gated the same way.)
    assert "SS-001" not in rule_ids, rule_ids
    assert "DS-001" not in rule_ids, rule_ids


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
