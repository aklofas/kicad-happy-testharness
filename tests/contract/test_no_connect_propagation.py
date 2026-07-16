#!/usr/bin/env python3
"""Regression test: a stray no-connect marker on a connected multi-pin net must
not flip every IC/connector pin on that net to NO_CONNECT in ic_pin_analysis.

Bug: the net-level `no_connect` flag is set when *any* point in a net's
union-find group is an NC marker. ic_pin_analysis used that flag directly, so a
single stray NC marker absorbed into a rail (e.g. VBUS/GND) reported all of that
rail's pins as NO_CONNECT. Fixed by only honoring the net-level flag for
single-pin nets (analyze_schematic.py, has_no_connect).

Fixture `nc_marker_on_multipin_net.kicad_sch`: a 2-pin connector J1 with both
pins on net VBUS, plus a stray no_connect marker joined to VBUS via a same-name
label — so VBUS is a 2-pin net carrying the no_connect flag.

Adopted from anyasabo/kicad-happy @ 23c5c31 (ported 2026-07-15).

Run directly (`python3 test_no_connect_propagation.py`) or via pytest.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

ANALYZER = MAIN_REPO_ROOT / "skills" / "kicad" / "scripts" / "analyze_schematic.py"
FIXTURE = HARNESS_ROOT / "tests" / "fixtures" / "nc_marker_on_multipin_net.kicad_sch"


def _analyze():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        out_path = tf.name
    subprocess.run(
        [sys.executable, str(ANALYZER), str(FIXTURE), "--output", out_path],
        capture_output=True, text=True, check=True,
    )
    return json.loads(Path(out_path).read_text())


def test_nc_marker_does_not_propagate_to_connected_pins():
    data = _analyze()

    # Precondition: the fixture really is the bug scenario — a multi-pin net that
    # carries the net-level no_connect flag.
    vbus = data["nets"]["VBUS"]
    assert len(vbus["pins"]) == 2, f"expected 2 pins on VBUS, got {len(vbus['pins'])}"
    assert vbus.get("no_connect") is True, "fixture should set the net-level no_connect flag"

    # The fix: both connector pins on VBUS report the net, not NO_CONNECT.
    j1 = next(ic for ic in data["ic_pin_analysis"] if ic["reference"] == "J1")
    pin_nets = {p["pin_number"]: p["net"] for p in j1["pins"]}
    assert pin_nets == {"1": "VBUS", "2": "VBUS"}, f"pins flipped to NO_CONNECT: {pin_nets}"


if __name__ == "__main__":
    test_nc_marker_does_not_propagate_to_connected_pins()
    print("PASS: no-connect marker does not propagate to connected multi-pin net")
