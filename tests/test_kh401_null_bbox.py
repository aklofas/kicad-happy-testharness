"""KH-401 — cross_analysis VS-002 crashed on `"bounding_box": null`.

`outline.get('bounding_box', {})` only defaults a MISSING key; an explicit
JSON null reaches `bbox.get(...)` and raises AttributeError, killing the whole
cross-analysis run. Pre-existing at v2.2.0 (--full pcb JSON on
sparkfun/SparkFun_IoT_RedBoard-RP2350). Fix = `or {}` at every
`.get(key, {})` site in cross_analysis.py that reads producer JSON.
"""

TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import cross_analysis  # noqa: E402


def _pcb_with_null_bbox():
    return {
        "vias": {"vias": [{"x": 1.0, "y": 1.0, "net": 1, "size": 0.8, "drill": 0.4, "layers": ["F.Cu", "B.Cu"]}]},
        "board_outline": {"bounding_box": None, "edges": [{"type": "line", "start": [0, 0], "end": [10, 0]}]},
        "nets": {"1": "GND"},
        "tracks": {"segments": []},
        "connectivity_graph": None,
        "footprints": [],
    }


def test_vs002_skips_cleanly_on_null_bbox():
    findings = cross_analysis.check_via_stitching_density({}, _pcb_with_null_bbox())
    assert findings == []  # skipped, not crashed


def test_null_top_level_blocks_do_not_crash_the_run():
    sch = {"components": [], "nets": {}, "net_classifications": None, "pin_net": None, "findings": []}
    pcb = _pcb_with_null_bbox()
    pcb["tracks"] = None
    findings, checks_run = cross_analysis.run_all_checks(sch, pcb)
    assert isinstance(findings, list)
    assert isinstance(checks_run, list)


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
