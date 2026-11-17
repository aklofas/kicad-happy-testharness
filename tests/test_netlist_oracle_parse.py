"""kicad-cli netlist parsing: empty pin numbers are kept (keyed by pin function), and a netlist
that cannot see the design (no nodes, or symbols left off the board) is reported blind (TH-121)."""
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
from regression import netlist_oracle as o  # noqa: E402

pytestmark = pytest.mark.unit

# kicad-cli 10 layout: one token per line, tab-indented.
NETLIST = """(export
\t(version "E")
\t(components
\t\t(comp
\t\t\t(ref "E2")
\t\t\t(value "LS")
\t\t)
\t\t(comp
\t\t\t(ref "U1")
\t\t\t(value "74LS00")
\t\t)
\t)
\t(nets
\t\t(net
\t\t\t(code "1")
\t\t\t(name "/S1")
\t\t\t(class "Default")
\t\t\t(node
\t\t\t\t(ref "E2")
\t\t\t\t(pin "")
\t\t\t\t(pinfunction "S1_")
\t\t\t\t(pintype "output")
\t\t\t)
\t\t\t(node
\t\t\t\t(ref "U1")
\t\t\t\t(pin "9")
\t\t\t\t(pinfunction "E1V1_9")
\t\t\t\t(pintype "input")
\t\t\t)
\t\t)
\t\t(net
\t\t\t(code "2")
\t\t\t(name "/X")
\t\t\t(class "Default")
\t\t\t(node
\t\t\t\t(ref "E2")
\t\t\t\t(pin "")
\t\t\t\t(pinfunction "CI")
\t\t\t\t(pintype "input")
\t\t\t)
\t\t)
\t)
)
"""

EMPTY = """(export
\t(version "E")
\t(components
\t)
\t(nets
\t)
)
"""


def _write(tmp_path, text):
    p = tmp_path / "n.net"
    p.write_text(text)
    return str(p)


def test_empty_pin_nodes_are_kept_and_keyed_by_pin_function(tmp_path):
    nets = o.parse_netlist(_write(tmp_path, NETLIST))
    assert nets == {"/S1": {("E2", "S1_"), ("U1", "9")}, "/X": {("E2", "CI")}}


def test_analyzer_empty_pin_numbers_are_keyed_by_pin_name(tmp_path):
    p = tmp_path / "a.json"
    p.write_text('{"nets": {"VSS": {"pins": ['
                 '{"component": "E2", "pin_number": "", "pin_name": "CI"},'
                 '{"component": "U1", "pin_number": "7", "pin_name": "GND"}]}}}')
    assert o.analyzer_nets(str(p)) == {"VSS": {("E2", "CI"), ("U1", "7")}}


def test_netlist_refs_lists_the_components(tmp_path):
    assert o.netlist_refs(_write(tmp_path, NETLIST)) == {"E2", "U1"}


def test_a_netlist_without_nodes_is_blind(tmp_path):
    path = _write(tmp_path, EMPTY)
    assert o.oracle_blind(o.parse_netlist(path), o.netlist_refs(path), {"U1"})


def test_a_netlist_missing_a_symbol_the_analyzer_has_is_blind(tmp_path):
    path = _write(tmp_path, NETLIST)
    assert o.oracle_blind(o.parse_netlist(path), o.netlist_refs(path), {"E2", "U1", "U2"})


def test_power_pseudo_refs_do_not_make_a_netlist_blind(tmp_path):
    path = _write(tmp_path, NETLIST)
    assert not o.oracle_blind(o.parse_netlist(path), o.netlist_refs(path), {"E2", "U1", "#PWR01"})
