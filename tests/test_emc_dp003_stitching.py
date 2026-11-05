"""DP-003 grades a differential pair's layer changes by ground stitching.

Fixtures tests/fixtures/emc_dp003/: two-layer boards where USB_D+ and USB_D- each run on F.Cu,
drop through one via, and continue on B.Cu. stitched.kicad_pcb has a GND via 0.94 mm from both
signal vias; unstitched.kicad_pcb has its GND via 7 mm away. usb_pair_schematic.json is the
minimal schematic analysis naming the pair. The rule: DP-003 is info when every signal via has
a ground via within RP-001's stitching radius (here 1 mm: twice the 0.2 mm default dielectric),
warning otherwise. The via list exists only under `analyze_pcb --full`; without it stitching
cannot be shown, so every DP-003 is a warning that says so.
"""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(str(PRODUCT_ROOT))
PCB = _KH / "skills/kicad/scripts/analyze_pcb.py"
EMC = _KH / "skills/emc/scripts/analyze_emc.py"
FIXTURES = _HARNESS / "tests/fixtures/emc_dp003"
SCHEMATIC = FIXTURES / "usb_pair_schematic.json"


def _dp003(tmp_path, board, full):
    args = [sys.executable, str(PCB), str(FIXTURES / board)] + (["--full"] if full else [])
    pcb = tmp_path / "pcb.json"
    pcb.write_text(subprocess.run(args, capture_output=True, text=True, check=True).stdout,
                   encoding="utf-8")
    out = subprocess.run([sys.executable, str(EMC), "--schematic", str(SCHEMATIC), "--pcb", str(pcb)],
                         capture_output=True, text=True, check=True).stdout
    return sorted(((f["nets"][0], f["severity"], f["description"])
                   for f in json.loads(out)["findings"] if f.get("rule_id") == "DP-003"))


def test_stitched_layer_changes_are_info(tmp_path):
    found = _dp003(tmp_path, "stitched.kicad_pcb", full=True)
    assert [(net, sev) for net, sev, _ in found] == [("USB_D+", "info"), ("USB_D-", "info")]
    assert all("each with a ground via within 1mm" in d for _, _, d in found)


def test_unstitched_layer_changes_are_warnings(tmp_path):
    found = _dp003(tmp_path, "unstitched.kicad_pcb", full=True)
    assert [(net, sev) for net, sev, _ in found] == [("USB_D+", "warning"), ("USB_D-", "warning")]
    assert all("not all with a ground via within 1mm" in d for _, _, d in found)


def test_without_the_via_list_stitching_is_not_checked(tmp_path):
    found = _dp003(tmp_path, "stitched.kicad_pcb", full=False)
    assert [(net, sev) for net, sev, _ in found] == [("USB_D+", "warning"), ("USB_D-", "warning")]
    assert all("ground stitching was not checked; run analyze_pcb --full" in d for _, _, d in found)
