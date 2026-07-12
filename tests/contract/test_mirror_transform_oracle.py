"""Mirror-transform oracle: pin-net assignments vs kicad-cli ground truth.

Locks the mirrored+rotated symbol pin transform fix (main-repo f57277d,
PR #27 / issue #17). The fixture instantiates an asymmetric 4-pin symbol
across 4 rotations x 3 mirror states with net labels at every transformed
pin position; mir12.net is the kicad-cli 10.0.3 netlist export = ground
truth for all 48 (ref, pin) -> net assignments.

Pre-fix analyzers score 32/48 (U5/U6/U11/U12 — the mirror+90/270 combos —
have all 4 pins wrong); f57277d+ scores 48/48.
"""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from tests.contract._paths import HARNESS_ROOT, MAIN_REPO_ROOT

ANALYZER = (MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"
            / "analyze_schematic.py")
FIXTURE_DIR = HARNESS_ROOT / "tests" / "fixtures" / "mirror-oracle"
SCH = FIXTURE_DIR / "mir12.kicad_sch"
NETLIST = FIXTURE_DIR / "mir12.net"


def _oracle():
    """Parse mir12.net into {(ref, pin): net-suffix} (suffix after last '_')."""
    root = ET.parse(NETLIST).getroot()
    expected = {}
    for net in root.iter("net"):
        suffix = net.get("name").rsplit("_", 1)[-1]
        for node in net.iter("node"):
            expected[(node.get("ref"), node.get("pin"))] = suffix
    return expected


@pytest.fixture(scope="module")
def pin_nets(tmp_path_factory):
    """{(ref, pin): net} from a real analyzer run on the fixture."""
    out = tmp_path_factory.mktemp("mirror-oracle") / "schematic.json"
    subprocess.run(
        [sys.executable, str(ANALYZER), str(SCH), "--output", str(out)],
        check=True, capture_output=True)
    data = json.loads(out.read_text())
    actual = {}
    for comp in data["components"]:
        for pin, net in (comp.get("pin_nets") or {}).items():
            actual[(comp["reference"], pin)] = net
    return actual


def test_oracle_netlist_has_48_single_node_assignments():
    expected = _oracle()
    assert len(expected) == 48
    assert {ref for ref, _pin in expected} == {f"U{i}" for i in range(1, 13)}


def test_all_48_pin_net_assignments_match_kicad_netlist(pin_nets):
    expected = _oracle()
    mismatches = []
    for (ref, pin), suffix in sorted(expected.items()):
        actual_net = pin_nets.get((ref, pin))
        if actual_net is None or actual_net.rsplit("_", 1)[-1] != suffix:
            mismatches.append(f"{ref}.{pin}: expected *_{suffix}, got {actual_net!r}")
    assert mismatches == [], (
        f"{len(mismatches)}/48 pin-net assignments diverge from the "
        f"kicad-cli ground truth:\n  " + "\n  ".join(mismatches)
    )
