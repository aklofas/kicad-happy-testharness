"""RS-001 treats a net tie as one conductor (GitHub #50).

Fixture tests/fixtures/net_tie/net_tie.kicad_sch: charger U1's OUT pin (power_out) drives
CHG_OUT, and net tie NT1 (Device:NetTie_2) joins CHG_OUT to VDD, which feeds load U2's VIN
(power_in) and its cap C2. KiCad keeps CHG_OUT and VDD as two nets, but a rail tied to a
sourced net is sourced, so VDD gets no "no declared source" finding.
net_tie_unannotated.kicad_sch: the same charger with two net ties both referenced NT?, to VDD
and to VDDIO. Their pins pool under one reference, so which nets each joins is unknown and
neither joins any: both rails keep RS-001.
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
FIXTURES = _HARNESS / "tests/fixtures/net_tie"


def _rs001_nets(name):
    out = subprocess.run([sys.executable, str(SCH), str(FIXTURES / name)],
                         capture_output=True, text=True, check=True).stdout
    return sorted(f["nets"][0] for f in json.loads(out)["findings"] if f.get("rule_id") == "RS-001")


def test_rail_fed_through_a_net_tie_is_sourced():
    assert _rs001_nets("net_tie.kicad_sch") == []


def test_net_ties_sharing_a_reference_join_nothing():
    assert _rs001_nets("net_tie_unannotated.kicad_sch") == ["VDD", "VDDIO"]
