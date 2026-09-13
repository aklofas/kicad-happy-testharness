"""KH-397 — the GP-001 via-antipad credit (KH-392) must honour the via's
physical layer span. A blind/buried via that doesn't reach the probed
reference layer must not mask a real plane gap on that layer.

Reuses the KH-392/393 fixture board (tests/fixtures/kh392-antipad/) for its
real track + zone-fill geometry, but drives `analyze_return_path_continuity`
directly (not via the CLI) so the test can force a 4-layer `copper_order`
and a blind via without needing a real 4-layer stackup on the fixture file.
"""
TIER = "unit"

import os
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parent.parent
_KH = os.environ.get("KICAD_HAPPY_DIR", str(_HARNESS.parent / "kicad-happy"))
sys.path.insert(0, os.path.join(_KH, "skills", "kicad", "scripts"))

import analyze_pcb  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures/kh392-antipad/board.kicad_pcb"

ORDER = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]


def test_via_span():
    f = analyze_pcb._via_spans_layer
    assert f(["F.Cu", "In1.Cu"], "In2.Cu", ORDER) is False
    assert f(["F.Cu", "B.Cu"], "In2.Cu", ORDER) is True
    assert f(["In1.Cu", "B.Cu"], "In1.Cu", ORDER) is True
    assert f([], "In1.Cu", ORDER) is True
    assert f(["F.Cu", "In1.Cu"], "In1.Cu", []) is True
    assert f(["Weird.Cu", "B.Cu"], "In1.Cu", ORDER) is True  # unknown name -> through assumption


def test_copper_order():
    st = [{"type": "copper", "name": "F.Cu"}, {"type": "core"}, {"type": "copper", "name": "In1.Cu"},
          {"type": "prepreg"}, {"type": "copper", "name": "B.Cu"}]
    assert analyze_pcb._copper_order_from_stackup(st) == ["F.Cu", "In1.Cu", "B.Cu"]
    assert analyze_pcb._copper_order_from_stackup([]) == ["F.Cu", "B.Cu"]


def _load_fixture():
    root = analyze_pcb.parse_file(str(FIXTURE))
    net_names = analyze_pcb.extract_nets(root)
    footprints = analyze_pcb.extract_footprints(root)
    tracks = analyze_pcb.extract_tracks(root)
    vias_extracted = analyze_pcb.extract_vias(root)
    zones, zone_fills = analyze_pcb.extract_zones(root)
    return net_names, footprints, tracks, vias_extracted, zones, zone_fills


def test_kh397_blind_via_denied_layer_credit_through_via_still_credited():
    """SENSE1 keeps its real through via (F.Cu/B.Cu — spans In2.Cu).
    SENSE2's via is turned into a blind via (F.Cu/In1.Cu — does NOT span
    In2.Cu). Both stubs are probed with opp_layer forced to "In2.Cu" (no
    real copper there at all, so the via-end sample's credit comes ONLY
    from the antipad shortcut) and copper_order=ORDER supplied. Only the
    through via (SENSE1) may still claim the antipad credit.
    """
    net_names, footprints, tracks, vias_extracted, zones, zone_fills = _load_fixture()

    vias = {"vias": []}
    for v in vias_extracted["vias"]:
        v = dict(v)
        if net_names.get(v["net"]) == "SENSE2":
            v["layers"] = ["F.Cu", "In1.Cu"]  # now a blind via
        vias["vias"].append(v)

    debug_samples = []
    analyze_pcb.analyze_return_path_continuity(
        tracks, net_names, zones, zone_fills,
        signal_nets={"SENSE1", "SENSE2"},
        ref_layer_map={"F.Cu": "In2.Cu"},
        footprints=footprints,
        vias=vias,
        debug_samples=debug_samples,
        copper_order=ORDER,
    )

    def _sample(net, x, y):
        for s in debug_samples:
            if s["net"] == net and abs(s["x"] - x) < 0.01 and abs(s["y"] - y) < 0.01:
                return s
        raise AssertionError(f"no sample found for {net} at ({x}, {y}): {debug_samples}")

    sense1_via_end = _sample("SENSE1", 141.5, 100.0)
    assert sense1_via_end["hit"] is True
    assert sense1_via_end.get("antipad_credit") is True

    sense2_via_end = _sample("SENSE2", 141.5, 104.0)
    assert sense2_via_end["hit"] is False  # FAILS pre-fix: layer-blind antipad credit


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
