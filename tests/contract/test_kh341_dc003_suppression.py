#!/usr/bin/env python3
"""KH-341 + KH-356: DC-003 must not demand vias on 2-layer boards or when
the cap ties into a same-layer pour of its own net. Fixtures use the REAL
pcb.json footprint shape — analyze_pcb strips `pads` from output (footprints
carry x/y/layer/pad_nets/connected_nets only), which is exactly what the
original KH-341 pour check got wrong (KH-356)."""

import json
import subprocess
import sys

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "emc" / "scripts"))
from emc_rules import check_decoupling_via_distance

ANALYZE_PCB = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_pcb.py"
SIMPLE_PCB = (HARNESS_ROOT / "tests" / "fixtures" / "simple-project"
              / "simple.kicad_pcb")


def _fp(ref="C1", nets_=("GND", "+3V3"), x=0.0, y=0.0):
    """Footprint entry in the real analyzer-output shape (no `pads` key)."""
    return {"reference": ref, "layer": "F.Cu", "x": x, "y": y,
            "pad_nets": {str(i + 1): {"net": n} for i, n in enumerate(nets_)},
            "connected_nets": sorted(nets_)}


def _pcb(layer_types, zones=None, cap_fp=None):
    return {
        "layers": [{"name": f"L{i}", "type": t}
                   for i, t in enumerate(layer_types)],
        "decoupling_placement": [{"ic": "U1", "nearby_caps": [{"cap": "C1"}]}],
        "vias": {"vias": [{"x": 50.0, "y": 50.0}]},
        "zones": zones or [],
        "footprints": [cap_fp or _fp()],
    }


def test_two_layer_board_suppressed():
    assert check_decoupling_via_distance(_pcb(["signal", "signal"])) == []


def test_four_layer_board_still_fires():
    findings = check_decoupling_via_distance(
        _pcb(["signal", "power", "power", "signal"]))
    assert len(findings) == 1
    assert findings[0].get("rule_id") == "DC-003"


def test_same_layer_same_net_pour_suppresses():
    """KH-356: must fire from real output fields (footprint center +
    connected_nets), not the stripped pads[] geometry."""
    zones = [{"net_name": "GND", "layers": ["F.Cu"],
              "filled_bbox": [-5.0, -5.0, 5.0, 5.0]}]
    pcb = _pcb(["signal", "power", "power", "signal"], zones, _fp())
    assert check_decoupling_via_distance(pcb) == []


def test_pour_of_foreign_net_does_not_suppress():
    zones = [{"net_name": "VUSB", "layers": ["F.Cu"],
              "filled_bbox": [-5.0, -5.0, 5.0, 5.0]}]
    pcb = _pcb(["signal", "power", "power", "signal"], zones, _fp())
    assert len(check_decoupling_via_distance(pcb)) == 1


def test_fixture_shape_matches_producer(tmp_path):
    """Guard against the KH-356 anti-pattern: assert the synthetic fixture
    uses exactly the fields the real producer emits."""
    out = tmp_path / "simple_pcb.json"
    r = subprocess.run([sys.executable, str(ANALYZE_PCB), str(SIMPLE_PCB),
                        "--output", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    fps = json.loads(out.read_text())["footprints"]
    assert fps, "producer emitted no footprints"
    real = fps[0]
    assert "pads" not in real, "producer now emits pads[] — update KH-341 check"
    for key in ("reference", "layer", "x", "y", "pad_nets", "connected_nets"):
        assert key in real, f"producer footprint lacks {key}"
