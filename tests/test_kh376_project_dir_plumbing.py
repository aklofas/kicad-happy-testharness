"""KH-376 -- `project_dir` reaches every datasheet-feature lookup.

`get_regulator_features`/`get_mcu_features` (skills/datasheets/scripts/
datasheet_features.py) resolve the extraction cache via
`resolve_extract_dir(project_dir=...)`. Before this fix, every caller in
`validation_detectors.py` (4 sites) and the one in `emc_rules.py` called
them with the MPN only -- no `project_dir` and no `analysis_json` -- so
`resolve_extract_dir` always fell through to its temp-directory fallback
and datasheet-authority gates (PS-001 PG-status suppression, VM-001 EN
threshold skip, PR-004 USB series-R skip) never saw a real extraction,
even when one existed on disk for the project.

The fix threads `AnalysisContext.project_dir` (set at both `ctx =
AnalysisContext(...)` construction sites in analyze_schematic.py, derived
from the schematic path) through to each `..._features(mpn, ...)` call in
validation_detectors.py. The one call site in emc_rules.py has no
AnalysisContext; the schematic analyzer JSON carries no top-level `file`
key either (it's popped before serialization), so `_schematic_project_dir()`
derives the project directory from the schematic's own provenance block,
`inputs.source_files` (a list of path strings), and passes it as
`project_dir=`.

This test exercises the PS-001 (power sequencing) path end-to-end: a
regulator with a datasheet-confirmed `has_pg: False` must not be flagged
for "PG status unknown", but only when `project_dir` actually reaches the
lookup -- the control case (`project_dir=None`) reproduces the pre-fix
behavior and must still emit the info-level "no datasheet extraction"
PS-001.

Fixture format matches `_load`'s direct-file fallback in
datasheet_features.py: a bare `{mpn}.json` under `datasheets/extracted/`
needs no manifest index.
"""

TIER = "unit"

import os
import sys
import tempfile
import json
from pathlib import Path
from unittest import mock

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "datasheets", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

from kicad_types import AnalysisContext
from datasheet_features import get_regulator_features
from validation_detectors import validate_power_sequencing
import emc_rules
from emc_rules import _schematic_project_dir, check_diff_pair_cm_radiation


EXT = {"topology": "ldo",
       "pins": [{"number": "1", "name": "EN", "function": "EN"},
                {"number": "3", "name": "IN", "function": "VIN"},
                {"number": "5", "name": "OUT", "function": "VOUT"}],
       "features": {"has_pg": False},
       "extraction_metadata": {"extraction_version": 99, "extraction_score": 100}}


def _write_fixture(tmp: Path) -> None:
    extract_dir = tmp / "datasheets" / "extracted"
    extract_dir.mkdir(parents=True)
    with (extract_dir / "TPS7A0533.json").open("w") as f:
        json.dump(EXT, f)


def _comp(ref, value, ctype, pins, lib_id="Regulator_Linear:TPS7A0533"):
    return {"reference": ref, "value": value, "type": ctype,
            "lib_id": lib_id, "footprint": "", "dnp": False, "in_bom": True,
            "pins": pins}


def _ctx(project_dir):
    # U1: LDO regulator, OUT on +3V3, EN/IN pins present but unwired
    # (no PG pin at all -- matches the fixture's has_pg: False intent).
    u1 = _comp("U1", "TPS7A0533", "ic",
               pins=[{"number": "1", "name": "EN"},
                     {"number": "3", "name": "IN"},
                     {"number": "5", "name": "OUT"}])
    # U2: sequencing-sensitive load on +3V3 (matches _SEQUENCING_SENSITIVE_KEYWORDS "stm32").
    u2 = _comp("U2", "STM32F401RE", "ic",
               pins=[{"number": "1", "name": "VDD"}],
               lib_id="MCU_ST_STM32F4:STM32F401RE")

    net_info = {"pins": [
        {"component": "U1", "pin_number": "5", "pin_name": "OUT",
         "pin_type": "power_out", "x": 0.0, "y": 0.0},
        {"component": "U2", "pin_number": "1", "pin_name": "VDD",
         "pin_type": "power_in", "x": 0.0, "y": 0.0},
    ]}
    nets = {"+3V3": net_info}
    pin_net = {
        ("U1", "5"): ("+3V3", net_info),
        ("U2", "1"): ("+3V3", net_info),
    }
    return AnalysisContext(components=[u1, u2], nets=nets, lib_symbols={},
                           pin_net=pin_net, project_dir=project_dir)


def test_sanity_get_regulator_features_reads_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        _write_fixture(tmp)
        feat = get_regulator_features("TPS7A0533", project_dir=str(tmp))
        assert feat is not None
        assert feat["has_pg"] is False
        assert feat["quality"]["trusted"] is True


def test_ps001_suppressed_when_project_dir_reaches_lookup():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        _write_fixture(tmp)
        ctx = _ctx(project_dir=str(tmp))
        findings = validate_power_sequencing(
            ctx, [{"ref": "U1", "output_rail": "+3V3"}])
        ps001 = [f for f in findings if f.get("rule_id") == "PS-001" and "U1" in f.get("components", [])]
        assert ps001 == [], f"expected no PS-001 for U1 with datasheet-confirmed has_pg=False, got {ps001}"


def test_control_ps001_fires_without_project_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        _write_fixture(tmp)
        ctx = _ctx(project_dir=None)
        findings = validate_power_sequencing(
            ctx, [{"ref": "U1", "output_rail": "+3V3"}])
        ps001 = [f for f in findings if f.get("rule_id") == "PS-001" and "U1" in f.get("components", [])]
        assert len(ps001) == 1
        assert "no datasheet extraction" in ps001[0]["summary"]


def test_schematic_project_dir_reads_source_files():
    assert _schematic_project_dir(
        {"inputs": {"source_files": ["/tmp/proj/x.kicad_sch"]}}
    ) == "/tmp/proj"


def test_schematic_project_dir_none_when_missing():
    assert _schematic_project_dir({}) is None
    assert _schematic_project_dir(None) is None
    assert _schematic_project_dir({"inputs": {}}) is None
    assert _schematic_project_dir({"inputs": {"source_files": []}}) is None
    # Non-schematic source files (e.g. a .kicad_pcb from an upstream artifact)
    # don't match the .kicad_sch/.sch suffix check.
    assert _schematic_project_dir(
        {"inputs": {"source_files": ["/tmp/proj/board.kicad_pcb"]}}
    ) is None


def test_emc_diff_pair_cm_radiation_passes_project_dir_to_mcu_lookup():
    # Minimal USB diff pair with a shared MCU IC, wired through
    # check_diff_pair_cm_radiation (DP-002) -- the enclosing function
    # around the emc_rules.py ~2049 call site.
    schematic = {
        "components": [
            {"reference": "U1", "type": "ic", "value": "STM32F401RE",
             "lib_id": "MCU_ST_STM32F4:STM32F401RE"},
        ],
        "design_analysis": {
            "differential_pairs": [
                {"positive": "USB_DP", "negative": "USB_DM", "type": "USB",
                 "shared_ics": ["U1"]},
            ],
        },
        "inputs": {"source_files": ["/tmp/proj/x.kicad_sch"]},
    }
    pcb = {"net_lengths": []}

    with mock.patch.object(emc_rules, "_get_mcu_features",
                           return_value=None) as recorder:
        check_diff_pair_cm_radiation(pcb, schematic)

    recorder.assert_called_once_with("STM32F401RE", project_dir="/tmp/proj")


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
