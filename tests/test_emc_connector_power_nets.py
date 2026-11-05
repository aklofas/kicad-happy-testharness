"""IO-001 / IO-002 classify connector nets with the shared power and ground name rules.

Fixture tests/fixtures/emc_connector_nets/connectors.kicad_pcb: four pin headers, no filter
parts. J1 carries `5V PCIE`, `PWR`, GND and `VCC_EN`; J2 the same without `VCC_EN`; J3 SDA, SCL,
`VCC_EN` and GND; J4 `VDDIO`, `/USB/VBUS`, SDA, SCL and GND. The rule: the shared name rules
decide first, else EMC's prefix rule unless the name ends in a rail control or status suffix
(`_EN`, `_PG`, ...). So `VCC_EN` is a signal, `5V PCIE` and `PWR` stay power, and `VDDIO` and a
hierarchical `/USB/VBUS` are power. IO-001 calls a connector power-only when every pad is power
or ground; IO-002 wants at least two ground pins once a connector has three signal pins.
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
BOARD = _HARNESS / "tests/fixtures/emc_connector_nets/connectors.kicad_pcb"
POWER_ONLY = "appears to be a power-only connector"


def _findings(tmp_path, rule_id):
    pcb = tmp_path / "pcb.json"
    pcb.write_text(subprocess.run([sys.executable, str(PCB), str(BOARD)],
                                  capture_output=True, text=True, check=True).stdout,
                   encoding="utf-8")
    out = subprocess.run([sys.executable, str(EMC), "--pcb", str(pcb)],
                         capture_output=True, text=True, check=True).stdout
    return {f["components"][0]: f for f in json.loads(out)["findings"] if f.get("rule_id") == rule_id}


def test_rail_enable_makes_a_connector_carry_a_signal(tmp_path):
    io001 = _findings(tmp_path, "IO-001")
    assert POWER_ONLY not in io001["J1"]["recommendation"]
    assert POWER_ONLY in io001["J2"]["recommendation"]


def test_ground_pin_count_follows_the_shared_rules(tmp_path):
    io002 = _findings(tmp_path, "IO-002")
    assert sorted(io002) == ["J3"]
    assert "1 ground pin(s) for 3 signal pins" in io002["J3"]["description"]
