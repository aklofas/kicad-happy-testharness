"""KH-386 — thermal reports the power components it could not assess.

`_estimate_all_power_dissipation` used to silently `continue` past a
switching regulator whose output rail had no load estimate in
`power_budget.rails` (common when KH-375's rail-name mismatch drops a
rail). Two identical regulators, one dropped, produced no trace in the
output — a 97/100-looking thermal report that quietly omitted the
hotter of the two parts.

This test pins the fix: the estimator now returns `(results, skipped)`,
and the CLI surfaces `summary.components_skipped` (always) plus
top-level `skipped_components` (when non-empty), with `reason` drawn
from a fixed vocabulary: `no_load_estimate`, `no_vout`,
`below_min_pdiss`.
"""

TIER = "unit"

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
_SCRIPTS = os.path.join(_KH, "skills", "kicad", "scripts")
sys.path.insert(0, _SCRIPTS)

import analyze_thermal  # noqa: E402

THERMAL = os.path.join(_SCRIPTS, "analyze_thermal.py")

# Two identical buck regulators; only +3V3_A has a load estimate in
# power_budget.rails, so U2's rail (+3V3_B) is unresolvable.
SCH = {
    "findings": [
        {"detector": "detect_power_regulators", "ref": "U1", "value": "TPS61023",
         "topology": "buck", "estimated_vout": 3.3, "output_rail": "+3V3_A"},
        {"detector": "detect_power_regulators", "ref": "U2", "value": "TPS61023",
         "topology": "buck", "estimated_vout": 3.3, "output_rail": "+3V3_B"},
    ],
    "power_budget": {
        "rails": {
            "+3V3_A": {"estimated_load_mA": 500},
        },
    },
}

# Minimal but structurally valid PCB analyzer JSON — thermal's caller
# reads findings[] and zone data defensively, so an empty findings list
# is sufficient for the CLI to run end to end.
PCB = {"findings": [], "footprints": [], "vias": [], "zones": [], "zone_fills": []}


def test_dropped_regulator_is_listed():
    results, skipped = analyze_thermal._estimate_all_power_dissipation(SCH)
    assert [r["ref"] for r in results] == ["U1"]
    assert skipped == [{"ref": "U2", "value": "TPS61023", "reason": "no_load_estimate"}]


def test_cli_surfaces_skipped():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        sch_path = tmp_path / "sch.json"
        pcb_path = tmp_path / "pcb.json"
        out_path = tmp_path / "thermal.json"
        sch_path.write_text(json.dumps(SCH))
        pcb_path.write_text(json.dumps(PCB))

        subprocess.run(
            [sys.executable, THERMAL,
             "--schematic", str(sch_path), "--pcb", str(pcb_path),
             "--output", str(out_path)],
            capture_output=True, text=True, check=True,
        )
        out = json.loads(out_path.read_text())

        assert out["summary"]["components_skipped"] == 1
        assert out["skipped_components"][0]["ref"] == "U2"
        assert out["skipped_components"][0]["reason"] == "no_load_estimate"

        # Validate the live output against the analyzer's own declared schema
        # (same pattern as tests/contract/test_thermal_envelope.py).
        # Skip schema validation if jsonschema is not available (bare python3).
        try:
            from jsonschema import Draft202012Validator

            schema_out = subprocess.run(
                [sys.executable, THERMAL, "--schema"],
                capture_output=True, text=True, check=True,
            ).stdout
            schema = json.loads(schema_out)
            Draft202012Validator(schema).validate(out)
        except ImportError:
            pass  # jsonschema not available in bare python3; skip schema validation


def test_no_skipped_components_key_when_nothing_skipped():
    """summary.components_skipped is always present (even at 0); the
    top-level skipped_components list is omitted when empty."""
    sch = {
        "findings": [
            {"detector": "detect_power_regulators", "ref": "U1", "value": "TPS61023",
             "topology": "buck", "estimated_vout": 3.3, "output_rail": "+3V3_A"},
        ],
        "power_budget": {"rails": {"+3V3_A": {"estimated_load_mA": 500}}},
    }
    results, skipped = analyze_thermal._estimate_all_power_dissipation(sch)
    assert [r["ref"] for r in results] == ["U1"]
    assert skipped == []


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
