"""kicad-cli netlist oracle: ground-truth connectivity for analyzer verification.

KiCad's own resolved netlist (via ``kicad-cli sch export netlist``) is ground
truth for schematic connectivity — full hierarchy resolution, positional bus
member mapping across sheet pins, per-instance sheet resolution. This module
exports and parses that netlist, extracts the equivalent view from
``analyze_schematic.py`` output, and compares the two by pin-grouping (not by
net name — KiCad and the analyzer name nets differently even when the
underlying connectivity agrees).

DEV/HARNESS-ONLY. The product (kicad-happy) never depends on kicad-cli; see
memory reference_kicad_cli_netlist_oracle.

Usage (library):
    from regression.netlist_oracle import export_netlist, parse_netlist, \\
        analyzer_nets, compare

    export_netlist("board.kicad_sch", "board.net")
    oracle = parse_netlist("board.net")
    analyzer = analyzer_nets("board_analysis.json")
    result = compare(analyzer, oracle)
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

# Verified against kicad-cli 10.0.4 output (2026-07-24). (net (code..) (name
# "..")...) blocks are newline/tab-separated, not single-line, but \s matches
# newlines so these still anchor correctly.
NET_RE = re.compile(
    r'\(net\s+\(code[^\)]*\)\s*\(name\s+"([^"]+)"\)(.*?)(?=\(net\s+\(code|\Z)',
    re.DOTALL,
)
NODE_RE = re.compile(
    r'\(node\s+\(ref\s+"?([^")\s]+)"?\)\s*\(pin\s+"?([^")\s]+)"?\)'
)


def export_netlist(sch_path: str, out_path: str, kicad_cli: str = "kicad-cli") -> None:
    """Export a fully-resolved netlist for sch_path via kicad-cli.

    Raises subprocess.CalledProcessError on failure (check=True).
    """
    subprocess.run(
        [kicad_cli, "sch", "export", "netlist", sch_path, "-o", out_path],
        check=True,
        capture_output=True,
    )


def parse_netlist(path: str) -> dict[str, set[tuple[str, str]]]:
    """Parse a kicad-cli netlist export into {net_name: {(ref, pin)}}."""
    text = Path(path).read_text(encoding="utf-8")
    nets: dict[str, set[tuple[str, str]]] = {}
    for name, body in NET_RE.findall(text):
        nets[name] = set(NODE_RE.findall(body))
    return nets


def analyzer_nets(analysis_json_path: str) -> dict[str, set[tuple[str, str]]]:
    """Load analyze_schematic.py JSON output into {net_key: {(component, pin_number)}}.

    Skips pin-less nets (e.g. phantom bus-name entries with no pins attached).
    """
    data = json.loads(Path(analysis_json_path).read_text(encoding="utf-8"))
    nets: dict[str, set[tuple[str, str]]] = {}
    for key, net in data.get("nets", {}).items():
        pins = net.get("pins") or []
        if not pins:
            continue
        nets[key] = {(p["component"], p["pin_number"]) for p in pins}
    return nets


def compare(
    analyzer: dict[str, set[tuple[str, str]]],
    oracle: dict[str, set[tuple[str, str]]],
) -> dict:
    """Compare analyzer nets to oracle nets by pin-grouping, not by name.

    Both sides are restricted to the shared pin universe — (ref, pin) tuples
    present in at least one net on BOTH sides. (KiCad's netlist export never
    includes power-symbol pseudo-refs like ``#PWR0102``, which the analyzer
    does emit, so this restriction is required just to align the two views —
    not merely a diagnostic nicety.) Every shared pin maps to exactly one
    restricted group on each side (its net's pins, intersected with the
    shared universe). Classification:

    - matched: an oracle group covered by exactly one analyzer group with an
      identical (restricted) pin set.
    - split: an oracle group whose shared pins are covered by >=2 distinct
      analyzer groups (the analyzer over-split a real net).
    - merged: an analyzer group whose shared pins cover >=2 distinct oracle
      groups (the analyzer wrongly co-grouped two real nets).
    - analyzer_only / oracle_only: nets on that side with zero pins in the
      shared universe (reported for diagnostics only, not pass/fail-gating).

    ``pass`` requires zero split, zero merged, and equal single-pin net
    counts on both sides (single-pin nets are the signature of the phantom
    bus-member defect this harness exists to catch).

    Stacked-pin divergence (reported, not gating): a connector symbol can
    define the same physical pin NUMBER twice with different functions — e.g.
    m68k's DIN41612 backplane pins Dc25 carry both an AD16 bidirectional
    signal and a GND power_in — so kicad-cli lists the identical (ref, pin)
    tuple in TWO nets. The analyzer's union-find assigns every pin to exactly
    one net and structurally cannot reproduce that, so such pins are dropped
    from the shared universe (and counted in ``stacked_pins``). This cannot
    mask a genuine bus merge: a real over-merge joins pins that each live in
    exactly ONE oracle net, so none of them are stacked.
    """
    oracle_pin_nets: dict[tuple[str, str], set[str]] = {}
    for name, pins in oracle.items():
        for pin in pins:
            oracle_pin_nets.setdefault(pin, set()).add(name)
    stacked = {pin for pin, nets in oracle_pin_nets.items() if len(nets) > 1}

    analyzer_pins: dict[tuple[str, str], str] = {}
    for name, pins in analyzer.items():
        for pin in pins:
            if pin in stacked:
                continue
            analyzer_pins[pin] = name
    oracle_pins: dict[tuple[str, str], str] = {}
    for name, pins in oracle.items():
        for pin in pins:
            if pin in stacked:
                continue
            oracle_pins[pin] = name

    shared = set(analyzer_pins) & set(oracle_pins)

    analyzer_restricted = {
        name: frozenset(p for p in pins if p in shared)
        for name, pins in analyzer.items()
    }
    oracle_restricted = {
        name: frozenset(p for p in pins if p in shared)
        for name, pins in oracle.items()
    }

    pin_to_analyzer_net = {
        p: name for name, pins in analyzer_restricted.items() for p in pins
    }
    pin_to_oracle_net = {
        p: name for name, pins in oracle_restricted.items() for p in pins
    }

    matched = 0
    split = []
    for oname, opins in oracle_restricted.items():
        if not opins:
            continue
        covering = sorted({pin_to_analyzer_net[p] for p in opins})
        if len(covering) > 1:
            split.append({"oracle_net": oname, "analyzer_nets": covering})
        elif analyzer_restricted[covering[0]] == opins:
            matched += 1

    merged = []
    for aname, apins in analyzer_restricted.items():
        if not apins:
            continue
        covering = sorted({pin_to_oracle_net[p] for p in apins})
        if len(covering) > 1:
            merged.append({"analyzer_net": aname, "oracle_nets": covering})

    analyzer_only = sorted(name for name, pins in analyzer_restricted.items() if not pins)
    oracle_only = sorted(name for name, pins in oracle_restricted.items() if not pins)

    # Count single-pin nets on real component pins only. The analyzer emits
    # power-symbol pseudo-refs (#PWR…, #+0131 for +12V, …) that kicad-cli never
    # includes; counting them would make a net the oracle sees as single-pin
    # (its lone connector pin) read as multi-pin on the analyzer side. This is
    # the same power-symbol-pseudo-ref divergence the shared-universe
    # restriction above already applies to split/merged — a real phantom
    # bus-member net has a real component pin, so this never hides one.
    def _real(pins):
        return {p for p in pins if not p[0].startswith("#")}
    analyzer_single_pin = sum(1 for pins in analyzer.values() if len(_real(pins)) == 1)
    oracle_single_pin = sum(1 for pins in oracle.values() if len(_real(pins)) == 1)

    split.sort(key=lambda d: d["oracle_net"])
    merged.sort(key=lambda d: d["analyzer_net"])

    return {
        "matched": matched,
        "split": split,
        "merged": merged,
        "analyzer_only": analyzer_only,
        "oracle_only": oracle_only,
        "analyzer_single_pin": analyzer_single_pin,
        "oracle_single_pin": oracle_single_pin,
        "stacked_pins": sorted(f"{ref}.{pin}" for ref, pin in stacked),
        "pass": not split and not merged and analyzer_single_pin == oracle_single_pin,
    }
