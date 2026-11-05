"""A named net whose pins make it a supply is a power rail, whatever its name.

Fixture tests/fixtures/topology_rail/can_vcc_rail.kicad_sch: transceiver U1's VCC pin is typed
passive and sits on CAN_VCC_PROTECTED with a 100n cap C1 to GND and a 10k pull-up R1 to the
open-collector FAULT line. The rule: a net is a rail when every IC pin on it is a supply input
or a power output (a passive pin counts by its whole supply name, VCC/VDD/VIN), and a
capacitor goes to ground. So C1 is a decoupling cap and R1/C1 is no RC filter. The negative
control is MCU U2's crystal: OSC_IN is a passive pin with an 18p load cap to GND, and a pin
named OSC_IN is no supply, so that net stays a signal.
"""
TIER = "unit"

import json
import subprocess
import sys
from pathlib import Path
from tests.product_root import PRODUCT_ROOT  # noqa: E402

_HARNESS = Path(__file__).resolve().parent.parent
_KH = Path(str(PRODUCT_ROOT))
SCH = _KH / "skills/kicad/scripts/analyze_schematic.py"
FIXTURE = _HARNESS / "tests/fixtures/topology_rail/can_vcc_rail.kicad_sch"


def _analysis():
    out = subprocess.run([sys.executable, str(SCH), str(FIXTURE)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def _findings(analysis, rule_id):
    return [f for f in analysis["findings"] if f.get("rule_id") == rule_id]


def test_passive_vcc_net_gets_a_decoupling_record():
    rails = {f["rail"]: f["components"] for f in _findings(_analysis(), "DC-DET")}
    assert rails == {"+3V3": ["C2", "C5"], "CAN_VCC_PROTECTED": ["C1"]}


def test_pull_up_onto_the_rail_is_not_an_rc_filter():
    assert _findings(_analysis(), "RC-DET") == []


def test_crystal_net_stays_a_signal():
    analysis = _analysis()
    assert not {"OSC_IN", "OSC_OUT"} & {f["rail"] for f in _findings(analysis, "DC-DET")}
    assert analysis["net_classifications"]["OSC_IN"]["type"] == "clock_passive"
    [xtal] = _findings(analysis, "XL-DET")
    assert xtal["components"][0] == "Y1"
