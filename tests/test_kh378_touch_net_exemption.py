"""KH-378 — EMC GP-001 (and RP-001, if applicable) treat capacitive-touch-pad
nets as intentional plane voids.

`check_return_path_coverage` grades every net in `return_path_continuity` by
reference-plane coverage. A touch pad's deliberately cleared ground pour
scores as a severe gap and gets the generic "fill the void" recommendation,
which is actively wrong advice for a touch sensor.

Task 7 (already landed in this branch) made the PCB analyzer's CP-003
findings (`analyze_copper_presence` touch-pad GND-clearance measurements,
merged into the top-level `findings` list) carry a `nets` list of the pad's
non-ground nets. `_touch_nets(pcb)` unions those nets across all CP-003
findings, with a fallback for older pcb JSON where `nets` is empty (keyed
by the CP-003 finding's `components` refs).

The fallback reads footprint `connected_nets` (sorted list of that
footprint's pad net names), not a per-pad `pads` list: `analyze_pcb.py`'s
compact `footprint_summary` pass (analyze_pcb.py:6751) always strips the
per-pad `pads` key from the top-level `footprints` output and replaces it
with `pad_nets` (dict) / `connected_nets` (list) — verified against a real
cached PCB analyzer JSON (SacMap rev2, `analysis/2026-08-20_1500/pcb.json`)
where TP1/TP2 footprints carry no `pads` key at all.

`check_return_path_coverage` and `check_layer_transition_stitching` (RP-001)
are checked independently: RP-001 keys on `pcb['layer_transitions']` (via
positions at layer transitions), not on `return_path_continuity` rows, so
whether the touch-net demotion applies there is verified directly rather
than assumed.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))
sys.path.insert(0, os.path.join(_KH, "skills", "emc", "scripts"))

import emc_rules  # noqa: E402


PCB = {
    "return_path_continuity": [
        {"net": "TOUCH_1", "reference_plane_coverage_pct": 79, "total_trace_mm": 30},
        {"net": "SPI_CLK", "reference_plane_coverage_pct": 79, "total_trace_mm": 30},
    ],
    "findings": [
        {"rule_id": "CP-003", "components": ["TP1"], "nets": ["TOUCH_1"]},
    ],
}


# ---------------------------------------------------------------------------
# _touch_nets helper
# ---------------------------------------------------------------------------

def test_touch_nets_from_cp003_nets_field():
    assert emc_rules._touch_nets(PCB) == {"TOUCH_1"}


def test_legacy_cp003_without_nets_uses_footprint_connected_nets():
    pcb = dict(PCB, findings=[{"rule_id": "CP-003", "components": ["TP1"], "nets": []}],
               footprints=[{"reference": "TP1", "connected_nets": ["GND", "TOUCH_1"]}])
    assert emc_rules._touch_nets(pcb) == {"TOUCH_1"}


def test_touch_nets_empty_when_no_cp003_findings():
    pcb = {"findings": [{"rule_id": "GP-001", "components": [], "nets": ["FOO"]}]}
    assert emc_rules._touch_nets(pcb) == set()


def test_touch_nets_handles_missing_findings_key():
    assert emc_rules._touch_nets({}) == set()


def test_touch_nets_excludes_real_testpoint_library():
    """KH-373/KH-378: a CP-003 finding naming a real TestPoint:* library
    part must not contribute its net to the touch-net set -- a test point
    is not a capacitive touch pad, and letting it through would wrongly
    demote GP-001 on that net."""
    pcb = {
        "findings": [{"rule_id": "CP-003", "components": ["TP3"], "nets": ["TP3_NET"]}],
        "footprints": [{"reference": "TP3", "library": "TestPoint:TestPoint_Pad_D1.0mm",
                        "connected_nets": ["TP3_NET"]}],
    }
    assert emc_rules._touch_nets(pcb) == set()


# ---------------------------------------------------------------------------
# GP-001 (check_return_path_coverage)
# ---------------------------------------------------------------------------

def test_touch_net_gp001_is_info():
    # _make_finding runs severity through _normalize_severity: CRITICAL/HIGH -> 'error',
    # MEDIUM -> 'warning', LOW/INFO -> 'info'. Assert on the normalized (lowercase) values.
    out = {f["signal_net"]: f for f in emc_rules.check_return_path_coverage(PCB)}
    assert out["TOUCH_1"]["severity"] == "info"
    assert out["TOUCH_1"]["is_touch_net"] is True
    assert "fill the void" not in out["TOUCH_1"]["recommendation"]
    assert out["SPI_CLK"]["severity"] == "error"
    # Non-touch net is untouched: no is_touch_net key/flag leaking onto it.
    assert not out["SPI_CLK"].get("is_touch_net")


def test_legacy_cp003_without_nets_demotes_gp001_via_footprint_fallback():
    pcb = dict(
        PCB,
        findings=[{"rule_id": "CP-003", "components": ["TP1"], "nets": []}],
        footprints=[{"reference": "TP1", "connected_nets": ["GND", "TOUCH_1"]}],
    )
    out = {f["signal_net"]: f for f in emc_rules.check_return_path_coverage(pcb)}
    assert out["TOUCH_1"]["severity"] == "info"
    assert out["TOUCH_1"]["is_touch_net"] is True


def test_testpoint_does_not_demote_gp001():
    """A CP-003 finding naming a real TestPoint:* library part must not
    demote GP-001 severity on its net -- the net's reference-plane gap is
    real and stays CRITICAL/HIGH ('error' after normalization)."""
    pcb = {
        "return_path_continuity": [
            {"net": "TP3_NET", "reference_plane_coverage_pct": 30, "total_trace_mm": 30},
        ],
        "findings": [{"rule_id": "CP-003", "components": ["TP3"], "nets": ["TP3_NET"]}],
        "footprints": [{"reference": "TP3", "library": "TestPoint:TestPoint_Pad_D1.0mm",
                        "connected_nets": ["TP3_NET"]}],
    }
    out = {f["signal_net"]: f for f in emc_rules.check_return_path_coverage(pcb)}
    assert out["TP3_NET"]["severity"] == "error"
    assert not out["TP3_NET"].get("is_touch_net")


def test_no_touch_nets_unaffected():
    """With no CP-003 findings, existing GP-001 behavior is unchanged."""
    pcb = {
        "return_path_continuity": [
            {"net": "SPI_CLK", "reference_plane_coverage_pct": 79, "total_trace_mm": 30},
        ],
        "findings": [],
    }
    out = {f["signal_net"]: f for f in emc_rules.check_return_path_coverage(pcb)}
    assert out["SPI_CLK"]["severity"] == "error"
    assert "fill the void" in out["SPI_CLK"]["recommendation"]


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
