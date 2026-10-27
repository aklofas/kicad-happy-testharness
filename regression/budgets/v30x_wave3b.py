"""Budget predicates for product 3.0.x Wave 3b Part A (KiCad conformance, schematic reading),
range d2b9e72 -> 6c488c2.

Classes (handoff-wave3b-A.md "Budget classes"; file ``v30x-wave3b.json``). As in Wave 3 every delta is
claimed per UNIT: ``classify_unit`` gives a unit a label (the ``+``-joined triggers it carries, in
commit order) and every delta of that unit is explained, or the unit is a residual (label ``None``).

Schematic triggers, read off the two outputs (both legacy ``.sch`` and ``.kicad_sch``):

  N1a  a local label shares its name with a global label or power net on its own sheet (A3-F1)
  N1b  a power symbol's net name or a ``#PWR`` value changed (named from its hidden pin, A2-F2/X1)
  N1c  a net renamed with its membership unchanged, not an escape rename (driver priority, A3-F7)
  N1d  a ``#FLG`` / power_out symbol's value names a net on either side (KH-403/404)
  N6   a bus label, a bus wire or a ``bus_topology`` change (A3-F2/N2/F3/F6, netid N1/C6);
       ``N6e`` when an ``ambiguous_bus_width`` note went away
  S1   a net key renamed to its escaped form (``{slash}`` etc., A1-F1)
  S3   a net named ``0`` (R13)
  S4   a component's pin count changed (lib_symbols children, pinless units, body >= 3)
  S5   only pin names / types moved on a component (pin alternates, stacked pins, jumpers)
  S6   ``dnp`` true -> false on a component whose source carries ``(dnp no)``-style state
  S7   a legacy component's value / description / datasheet / reference text changed
  H1   a component reference / unit changed, or a value / footprint changed without a
       ``${`` / ``~`` / power explanation (instance identity, A4-F1)
  H2   a ``~`` datasheet or value became empty (hb-N2)
  H3   a field holding ``${`` changed (text variables, A4-F3)
  H4   ``bom[]`` package fields moved with components unchanged (A4-F2)
  H5   ``in_bom`` / ``on_board`` / ``dnp`` moved without S6 (sheet flags, A4-F4)
  H6   ``bom[]`` regrouped by DNP (hb-N1)
  H7   ``hierarchy_warning`` moved (declared top-level sheets)
  V1   legacy library records / lib_id ``~`` / ``_pin_source`` (A5-F1..F5, KH-662)
  V2   ``parsed_value`` moved with the value text unchanged (A15-F1..F3; V3 lists are inside)
  V4   an ``AmbiguousValueSeparator`` diagnostic appeared

N1a / N1b / N1c / N1d / N6 / S3 / S4 / S5 / H1 / V1-pins change connectivity or names that every
consumer reads: any block outside ``FIXED_TOP`` may follow, as M1/M2/M4 in Wave 3. The other
triggers open only their own blocks (``NARROW_BLOCKS``) and the findings they explain.

PCB triggers: S2 board net names kept as written (every renamed key decodes to its old form),
T1 tokenizer (footprint count / value / reference text, segment count, silkscreen).

Chained analyzers (emc / thermal / cross_analysis): ``D`` when an upstream schematic or pcb snap
differs and that upstream unit is itself explained.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

from regression.budgets.v30x_wave2 import _canon, _findings, _moved
from regression.budgets.v30x_wave3 import (
    DERIVED_TOP, FIXED_TOP, VOLATILE_TOP, _block_diffs, _deep_strings, _derived_ok, _diags, _is_legacy,
    _policy, _slot_root,
)
from regression.field_compare import compare_strict

ORDER = ("T1", "N1a", "N1b", "N1c", "N6", "N6e", "H1", "H2", "N1d", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
         "V1", "V2", "V4", "H3", "H4", "H5", "H6", "H7")
CONNECTIVITY = frozenset({"N1a", "N1b", "N1c", "N1d", "N6", "N6e", "S3", "S4", "S5", "H1", "V1p", "T1"})

# blocks a narrow trigger may move (findings are judged separately)
NARROW_BLOCKS = {
    # `~` on mpn / distributor fields feeds the sourcing blocks as well as the datasheet consumers
    "H2": {"components", "bom", "ic_pin_analysis", "transistor_pin_analysis", "missing_info", "sourcing_audit",
           "bom_lock", "statistics", "property_issues"},
    "H3": {"components", "bom", "missing_info", "annotation_issues", "statistics", "bom_optimization", "sourcing_audit",
           "bom_lock", "ic_pin_analysis", "transistor_pin_analysis"},
    "H4": {"bom", "statistics", "missing_info", "bom_coverage", "bom_optimization", "sourcing_audit", "bom_lock"},
    "H5": {"components", "bom", "statistics", "sourcing_audit", "bom_lock", "missing_info", "bom_optimization",
           "bom_coverage", "assembly_complexity", "property_issues"},
    "H6": {"bom", "statistics", "bom_coverage", "bom_optimization", "sourcing_audit", "bom_lock"},
    "H7": {"hierarchy_warning"},
    "S1": {"nets", "labels", "components", "net_classifications", "ic_pin_analysis", "bus_analysis",
           "protocol_compliance", "test_coverage", "erc_warnings", "label_shape_warnings", "cross_domain_signals",
           "design_analysis", "connectivity_issues", "hierarchical_labels", "transistor_pin_analysis"},
    "S6": {"components", "bom", "statistics", "bom_lock", "sourcing_audit", "missing_info", "bom_optimization",
           "assembly_complexity", "bom_coverage", "property_issues"},
    "S7": {"components", "bom", "statistics", "ic_pin_analysis", "transistor_pin_analysis", "missing_info",
           "bom_optimization", "sourcing_audit", "bom_lock"},
    "V1": {"components", "power_symbols", "subcircuits", "legacy_analysis_quality", "pin_source_coverage"},
    "V2": {"components", "bom_optimization", "pdn_impedance", "design_analysis", "subcircuits", "statistics",
           "power_budget", "inrush_analysis", "test_coverage", "sleep_current_audit", "power_sequencing",
           "power_sequencing_validation", "rail_voltages"},
    "V4": set(),
}
# rules a narrow trigger may move as a whole (findings tied to a changed ref / value are always allowed
# for H3 / V2 / S6 / H5, as M5 in Wave 3)
NARROW_RULES = {
    "S6": {"SS-001", "SS-002", "SS-003", "SP-001"},
    "H5": {"DS-001", "DS-002", "SS-001", "SS-002", "SS-003"},
    "H2": {"RS-001", "SS-001", "SS-002", "SS-003", "DS-001", "DS-002"},
    # value notation feeds the passive detectors and everything built on them (handoff V2 row)
    "V2": {"RC-DET", "DC-DET", "VD-DET", "LC-DET", "DO-DET", "UC-003", "XT-001", "FS-001", "PR-DET", "OA-DET"},
}
# the netlist itself: a narrow (non-connectivity) trigger never moves these, except S1's escape renames
NETLIST_BLOCKS = frozenset({"nets", "labels", "power_symbols", "hierarchical_labels", "bus_topology", "sheets",
                            "sheet_files", "sheets_parsed", "no_connects", "wires", "junctions"})
S1_NETLIST = frozenset({"nets", "labels"})

# value notation the candidate reads (A15-F1..F4): micro / ohm signs, Meg, decimal comma, grouped digits,
# field lists, femto
_NOTATION = re.compile(r"\d,\d|[\u00b5\u03bc\u03a9\u2126]|[0-9 ][Mm][Ee][Gg]|\d \d{3}|\S, \S|\d ?f(?![a-zA-Z])")
_BUS_NAME = re.compile(r"\[\d+\.\.\d+\]|\{")
_ESC = re.compile(r"\{(slash|backslash|space|tab|lt|gt|colon|dblquote|quote|comma|dollar|tilde|caret|"
                  r"brace|lbrace|rbrace|amp|newline|return)\}")


def _decode(s: str) -> str:
    table = {"slash": "/", "backslash": "\\", "space": " ", "tab": "\t", "lt": "<", "gt": ">", "colon": ":",
             "dblquote": '"', "quote": "'", "comma": ",", "dollar": "$", "tilde": "~", "caret": "^",
             "lbrace": "{", "rbrace": "}", "amp": "&", "newline": "\n", "return": "\r"}
    return _ESC.sub(lambda m: table.get(m.group(1), m.group(0)), s)


# ---- schematic helpers ----------------------------------------------------------------------

def _comps(doc: dict) -> list[dict]:
    return [c for c in doc.get("components") or [] if isinstance(c, dict)]


def _pair_components(a: dict, b: dict):
    """Pair components by (uuid, sheet, occurrence); unpaired ones are returned separately."""
    def keyed(doc):
        seen, out = Counter(), {}
        for c in _comps(doc):
            k = (c.get("uuid"), c.get("_sheet"))
            out[k + (seen[k],)] = c
            seen[k] += 1
        return out
    ka, kb = keyed(a), keyed(b)
    pairs = [(ka[k], kb[k]) for k in ka.keys() & kb.keys()]
    return pairs, [ka[k] for k in ka.keys() - kb.keys()], [kb[k] for k in kb.keys() - ka.keys()]


def _membership(doc: dict) -> dict[str, frozenset]:
    out = {}
    for name, net in (doc.get("nets") or {}).items():
        if isinstance(net, dict):
            out[name] = frozenset((p.get("component"), p.get("pin_number")) for p in net.get("pins") or []
                                  if isinstance(p, dict))
    return out


def _pin_labels(doc: dict) -> dict:
    out = {}
    for net in (doc.get("nets") or {}).values():
        for p in (net.get("pins") or []) if isinstance(net, dict) else []:
            if isinstance(p, dict):
                out[(p.get("component"), p.get("pin_number"))] = (p.get("pin_name"), p.get("pin_type"))
    return out


def _bus_present(doc: dict) -> bool:
    if (doc.get("bus_topology") or {}).get("bus_wires") or (doc.get("bus_topology") or {}).get("buses"):
        return True
    return any(isinstance(lbl, dict) and _BUS_NAME.search(str(lbl.get("name", ""))) for lbl in doc.get("labels") or [])


def _same_sheet_join(doc: dict) -> bool:
    local, glob = set(), set()
    for lbl in doc.get("labels") or []:
        if not isinstance(lbl, dict):
            continue
        key = (lbl.get("_sheet"), lbl.get("name"))
        if lbl.get("type") == "label":
            local.add(key)
        elif lbl.get("type") == "global_label":
            glob.add(key)
    for p in doc.get("power_symbols") or []:
        if isinstance(p, dict):
            glob.add((p.get("_sheet"), p.get("net_name")))
    return bool(local & glob)


def _flag_values(doc: dict) -> set[str]:
    return {str(c.get("value")) for c in _comps(doc) if str(c.get("reference", "")).startswith("#FLG")}


def _unresolved_reasons(doc: dict) -> Counter:
    return Counter(str(u.get("reason")) for u in (doc.get("bus_topology") or {}).get("unresolved") or []
                   if isinstance(u, dict))


def _schematic_triggers(a: dict, b: dict, stats: Counter) -> set[str]:
    trig: set[str] = set()
    legacy = _is_legacy(a) or _is_legacy(b)
    pairs, only_a, only_b = _pair_components(a, b)
    for x, y in pairs:
        if x == y:
            continue
        keys = {k for k in set(x) | set(y) if x.get(k) != y.get(k)}
        ref = str(y.get("reference"))
        power = ref.startswith("#")
        if keys & {"reference", "unit"}:
            trig.add("H1")
            stats["H1_refs"] += 1
        for f in ("value", "footprint", "datasheet", "description", "mpn", "manufacturer", "digikey", "mouser",
                  "lcsc", "element14"):
            if f not in keys:
                continue
            va, vb = str(x.get(f) or ""), str(y.get(f) or "")
            if "${" in va:
                trig.add("H3")
                stats["H3_" + f] += 1
            elif va.strip() == "~" and vb == "":
                trig.add("H2")
                stats["H2_" + f] += 1
                if f in ("value", "footprint"):
                    trig.add("VAL")
            elif legacy and f in ("value", "description", "datasheet"):
                trig.add("S7")
                stats["S7_" + f] += 1
            elif power and f == "value":
                trig.add("N1b")
                stats["N1b_power_value"] += 1
            elif f in ("value", "footprint"):
                trig.add("H1")
                stats["H1_" + f] += 1
            else:
                trig.add("H1x")
                stats["H1x_" + f] += 1
        if "dnp" in keys and x.get("dnp") is True and y.get("dnp") is False:
            trig.add("S6")
            stats["S6_dnp_cleared"] += 1
        elif keys & {"dnp", "in_bom", "on_board"}:
            trig.add("H5")
            stats["H5_flags"] += 1
        if "pins" in keys:
            pa, pb = x.get("pins") or [], y.get("pins") or []
            if legacy and x.get("_pin_source") != y.get("_pin_source"):
                trig.add("V1p")
                stats["V1_pin_source"] += 1
            elif len(pa) != len(pb):
                trig.add("S4")
                stats["S4_pin_count"] += 1
            else:
                trig.add("S5")
                stats["S5_pins"] += 1
        if "lib_id" in keys:
            trig.add("V1" if legacy else "S4")
            stats["lib_id"] += 1
        if "_pin_source" in keys and "pins" not in keys:
            trig.add("V1")
        if "parsed_value" in keys and "value" not in keys:
            trig.add("V2")
            stats["V2_parsed_value"] += 1
    if only_a or only_b:
        trig.add("H1" if not legacy else "S7")
        stats["components_unpaired"] += len(only_a) + len(only_b)

    ma, mb = _membership(a), _membership(b)
    ra = {c for mem in ma.values() for c, _ in mem}
    rb = {c for mem in mb.values() for c, _ in mem}
    if ra != rb:
        trig.add("H1")
        stats["H1_net_refs"] += len(ra ^ rb)
    la, lb = _pin_labels(a), _pin_labels(b)
    moved_pins = [k for k in la.keys() & lb.keys() if la[k] != lb[k]]
    if moved_pins:
        trig.add("S5")
        stats["S5_net_pins"] += len(moved_pins)
    # a hidden power_in pin names its net (as N1b's hidden-pin rule, on a non-power symbol)
    for name, mem in mb.items():
        bare = name.rsplit("/", 1)[-1]
        if mem != ma.get(name) and any(lb.get(k, (None, None)) == (bare, "power_in") for k in mem - ma.get(name, frozenset())):
            trig.add("N1b")
            stats["N1b_power_in_pin_joins"] += 1
            break
    # legacy: a pinless net named after a non-power part's value goes (only DEF ... P symbols name nets)
    if legacy:
        values = {str(c.get("value")) for c in _comps(a) if not str(c.get("reference", "")).startswith("#")}
        gone = [n for n in set(ma) - set(mb) if not ma[n] and n in values]
        if gone:
            trig.add("V1p")
            stats["V1_def_power_nets_removed"] += len(gone)
    ua = set((a.get("hierarchical_labels") or {}).get("unconnected_hierarchical") or [])
    ub = set((b.get("hierarchical_labels") or {}).get("unconnected_hierarchical") or [])
    if ub < ua:
        trig.add("N1c")
        stats["N1c_unconnected_hier_removed"] += len(ua - ub)
    part_a, part_b = Counter(ma.values()), Counter(mb.values())
    if part_a != part_b:
        stats["membership_changed"] += 1
    names_a = {v: k for k, v in ma.items()}
    for mem, name_b in ((v, k) for k, v in mb.items()):
        name_a = names_a.get(mem)
        if name_a is None or name_a == name_b:
            continue
        if _decode(name_b) == name_a or _ESC.search(name_b):
            trig.add("S1")
            stats["S1_renames"] += 1
        else:
            trig.add("N1c")
            stats["N1c_renames"] += 1
    if a.get("nets") != b.get("nets") and set(ma) == set(mb) and part_a == part_b:
        if any(_ESC.search(n) for n in mb):
            trig.add("S1")  # display_name added on an escaped key
    pwr_a = Counter((p.get("_sheet"), p.get("net_name")) for p in a.get("power_symbols") or [] if isinstance(p, dict))
    pwr_b = Counter((p.get("_sheet"), p.get("net_name")) for p in b.get("power_symbols") or [] if isinstance(p, dict))
    if pwr_a != pwr_b:
        trig.add("N1b")
        stats["N1b_power_symbols"] += 1
    if _same_sheet_join(a) or _same_sheet_join(b):
        trig.add("N1a")
    flags = _flag_values(a) | _flag_values(b)
    if flags & (set(ma) | set(mb) | {n.rsplit("/", 1)[-1] for n in set(ma) | set(mb)}):
        trig.add("N1d")
    if _bus_present(a) or _bus_present(b) or a.get("bus_topology") != b.get("bus_topology"):
        trig.add("N6")
        if _unresolved_reasons(a)["ambiguous_bus_width"] > _unresolved_reasons(b)["ambiguous_bus_width"]:
            trig.add("N6e")
    if "0" in ma or "0" in mb or any(n.endswith("/0") for n in set(ma) | set(mb)):
        trig.add("S3")
    if a.get("hierarchy_warning") != b.get("hierarchy_warning"):
        trig.add("H7")
    da = Counter(_canon(d) for d in _diags(a))
    db = Counter(_canon(d) for d in _diags(b))
    for d in (db - da).elements():
        exc = json.loads(d).get("exception")
        if exc == "AmbiguousValueSeparator":
            trig.add("V4")
        elif legacy:
            trig.add("V1")
        stats["diag+" + str(exc)] += 1
    for d in (da - db).elements():
        stats["diag-" + str(json.loads(d).get("exception"))] += 1
    if any(_NOTATION.search(str(c.get("value") or "")) for c in _comps(b)):
        trig.add("V2")
        stats["V2_notation_present"] += 1
    filled = _tilde_filled(a, b)
    if filled:
        stats["H4_tilde_filled"] += filled
    if _bom_norm(a) != _bom_norm(b) and not only_a and not only_b \
            and all(x.get(k) == y.get(k) for x, y in pairs
                    for k in ("dnp", "in_bom", "on_board", "reference", "value", "footprint")):
        sa, sb = a.get("statistics") or {}, b.get("statistics") or {}
        if len(a.get("bom") or []) != len(b.get("bom") or []) or sa.get("dnp_parts") != sb.get("dnp_parts"):
            trig.add("H6")
            stats["H6_bom_lines"] += len(b.get("bom") or []) - len(a.get("bom") or [])
        else:
            trig.add("H4")
    return trig


def _tilde_filled(a: dict, b: dict) -> int:
    """bom package fields that went from empty to ``~`` (an empty field reported as set)."""
    rows_a = {tuple(r.get("references") or []): r for r in a.get("bom") or [] if isinstance(r, dict)}
    n = 0
    for r in b.get("bom") or []:
        x = rows_a.get(tuple(r.get("references") or [])) if isinstance(r, dict) else None
        if x is not None:
            n += sum(1 for k in ("footprint", "datasheet") if str(r.get(k)).strip() == "~" and not str(x.get(k) or "").strip())
    return n


def _bom_norm(doc: dict) -> list:
    """bom rows with H2's ``~`` -> ``""`` applied, so H4 / H6 see only package / grouping changes."""
    out = []
    for r in doc.get("bom") or []:
        if isinstance(r, dict):
            r = {k: ("" if k in ("datasheet", "value", "footprint") and str(v).strip() == "~" else v) for k, v in r.items()}
        out.append(r)
    return out


def _changed_values(a: dict, b: dict) -> set[str]:
    out = set()
    pairs, only_a, only_b = _pair_components(a, b)
    for x, y in pairs:
        if x != y:
            out |= {str(x.get("reference")), str(y.get("reference"))}
            for f in ("value", "parsed_value"):
                if x.get(f) != y.get(f):
                    out |= {str(x.get(f)), str(y.get(f))}
    out |= {str(c.get("reference")) for c in only_a + only_b}
    return out - {"None", ""}


def _schematic(a, b):
    stats: Counter = Counter()
    trig = _schematic_triggers(a, b, stats)
    blocks = _block_diffs(a, b)
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    bad = [f"block {k}" for k in blocks & FIXED_TOP]
    if stats.get("H4_tilde_filled"):
        bad.append("bom field empty -> '~' (H4 filled an empty field from '~')")
    if trig - {"H1x", "VAL"}:
        trig.discard("H1x")  # a field moved alongside an explained change
    if not trig:
        return None, bad + ["schematic movement without a trigger"], stats
    blocks -= {"diagnostics"}
    if trig & CONNECTIVITY:
        return _label(trig, bad), bad, stats
    value_moved = bool(trig & {"VAL", "H3", "V2", "S7", "H1x"})
    netlist_ok = S1_NETLIST if "S1" in trig else frozenset()
    if value_moved:
        bad += [f"block {k}" for k in sorted(blocks & NETLIST_BLOCKS - netlist_ok)]
    else:
        allowed = set().union(*(NARROW_BLOCKS.get(t, set()) for t in trig))
        bad += [f"block {k}" for k in sorted(blocks - allowed)]
    if rem or add:
        tied = _changed_values(a, b)
        rules = set().union(*(NARROW_RULES.get(t, set()) for t in trig))
        net = Counter(f.get("rule_id") for f in add)
        net.subtract(Counter(f.get("rule_id") for f in rem))
        for f in rem + add:
            rule = f.get("rule_id")
            if net[rule] == 0 or rule in rules:
                continue  # rewritten at an unchanged count (echoed text), or a declared rule
            if (value_moved or trig & {"S6", "H5"}) and _deep_strings(f) & tied:
                continue
            bad.append(f"finding {rule} {str(f.get('summary', ''))[:60]}")
    return _label(trig, bad), bad, stats


def _label(trig: set[str], bad: list) -> str | None:
    if bad:
        return None
    t = {"V1" if x == "V1p" else x for x in trig} - {"H1x", "VAL"}
    return "+".join(x for x in ORDER if x in t)


# ---- pcb ------------------------------------------------------------------------------------

def _pcb_net_names(doc: dict) -> set[str]:
    nets = doc.get("nets")
    if isinstance(nets, dict):  # {net number: name}
        return {str(v) for v in nets.values()}
    if isinstance(nets, list):
        return {str(n.get("name")) for n in nets if isinstance(n, dict)}
    return set()


def _pcb(a, b):
    stats: Counter = Counter()
    trig: set[str] = set()
    na, nb = _pcb_net_names(a), _pcb_net_names(b)
    renamed_b = nb - na
    if renamed_b and all(_decode(n) in na for n in renamed_b):
        trig.add("S2")
        stats["S2_names"] += len(renamed_b)
    fa, fb = a.get("footprints") or [], b.get("footprints") or []
    if len(fa) != len(fb):
        trig.add("T1")
        stats["T1_footprints"] += len(fb) - len(fa)
    elif any(isinstance(x, dict) and isinstance(y, dict) and (x.get("value"), x.get("reference")) != (y.get("value"), y.get("reference"))
             for x, y in zip(fa, fb)):
        trig.add("T1")
        stats["T1_fp_text"] += 1
    sa, sb = a.get("statistics") or {}, b.get("statistics") or {}
    if any(sa.get(k) != sb.get(k) for k in ("track_segments", "segment_count", "footprint_count", "via_count")):
        trig.add("T1")
    if a.get("silkscreen") != b.get("silkscreen"):
        trig.add("T1")
        stats["T1_silkscreen"] += 1
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    bad = [f"block {k}" for k in _block_diffs(a, b) & FIXED_TOP]
    if not trig:
        return None, bad + ["pcb movement without a trigger"], stats
    if "T1" not in trig and Counter(f.get("rule_id") for f in rem) != Counter(f.get("rule_id") for f in add):
        bad.append("S2 rule counts moved")
    return _label(trig, bad), bad, stats


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


# ---- upstream (chained analyzers) ----------------------------------------------------------

_UP: OrderedDict = OrderedDict()


def _upstream(a_doc: dict, b_doc: dict) -> list[tuple[str, dict | None, dict | None]]:
    out = []
    ua = ((a_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    ub = ((b_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    for kind in ("schematic", "pcb"):
        pa, pb = (ua.get(kind) or {}).get("path"), (ub.get(kind) or {}).get("path")
        if not pa or not pb:
            continue
        key = (pa, pb)
        hit = _UP.get(key)
        if hit is None:
            try:
                da = json.loads(Path(pa).read_text(encoding="utf-8"))
                db = json.loads(Path(pb).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                hit = (True, None, None)
            else:
                ds_, _ = compare_strict(da, db, _policy(), unit=kind, analyzer=kind,
                                        root_prefixes=(_slot_root(pa), _slot_root(pb)))
                hit = (bool(ds_), da, db)
            _UP[key] = hit
            while len(_UP) > 16:
                _UP.popitem(last=False)
        if hit[0]:
            out.append((kind, hit[1], hit[2]))
    return out


# ---- unit classification --------------------------------------------------------------------

def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    if analyzer in ("emc", "thermal", "cross_analysis"):
        up = _upstream(a_doc, b_doc)
        if not up:
            return {"label": None, "reasons": [f"{analyzer} movement with identical upstream"], "stats": Counter()}
        reasons: list[str] = []
        labels = []
        for kind, da, db in up:
            if da is None:
                reasons.append(f"upstream {kind} unreadable")
                continue
            r = classify_unit(kind, da, db)
            if r["label"] is None:
                reasons.append(f"upstream {kind} unexplained")
            else:
                labels.append(r["label"])
        return {"label": "D" if not reasons else None, "reasons": reasons,
                "stats": Counter({"upstream_" + k: 1 for k, _, _ in up}) + Counter({"D<" + x: 1 for x in labels})}
    clf = _CLASSIFIERS.get(analyzer)
    if clf is None:
        return {"label": None, "reasons": [f"no class for analyzer {analyzer}"], "stats": Counter()}
    label, reasons, stats = clf(a_doc, b_doc)
    full = analyzer in _FULL_DERIVED
    if not _derived_ok(a_doc, full=full):
        reasons = reasons + ["a: derived blocks not from findings"]
    if not _derived_ok(b_doc, full=full):
        reasons = reasons + ["b: derived blocks not from findings"]
    return {"label": label if not reasons else None, "reasons": reasons, "stats": stats}


_CACHE: OrderedDict = OrderedDict()


def _cached(delta, a_doc, b_doc) -> dict | None:
    if not isinstance(a_doc, dict) or not isinstance(b_doc, dict):
        return None
    key = (id(a_doc), id(b_doc))
    hit = _CACHE.get(key)
    if hit is None:
        hit = (classify_unit(delta.analyzer, a_doc, b_doc), a_doc, b_doc)
        _CACHE[key] = hit
        while len(_CACHE) > 8:
            _CACHE.popitem(last=False)
    return hit[0]


def _labelled(kinds: tuple[str, ...]):
    def pred(delta, a_doc, b_doc) -> bool:
        if delta.analyzer not in kinds:
            return False
        r = _cached(delta, a_doc, b_doc)
        return bool(r and r["label"])
    pred.__name__ = "labelled_" + "_".join(kinds)
    return pred


schematic = _labelled(("schematic",))
pcb = _labelled(("pcb",))
downstream = _labelled(("emc", "thermal", "cross_analysis"))


# ---- adjudication summary over a streamed units.jsonl ---------------------------------------

def summarize_units(units_jsonl: Path) -> dict:
    """Per-trigger magnitudes from ``stream_budgeted.py``'s units.jsonl (label + stats per unit)."""
    carry: dict[str, dict] = {}
    first: Counter = Counter()
    unexplained = []
    for line in units_jsonl.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if not r.get("deltas"):
            continue
        an, lab = r["analyzer"], r.get("label")
        if not lab:
            unexplained.append({k: r.get(k) for k in ("unit", "deltas", "reasons")})
            continue
        parts = lab.split("+")
        first[f"{an}:{parts[0]}"] += 1
        repo = "/".join(r["unit"].split("/")[1:3])
        for t in parts:
            slot = carry.setdefault(f"{an}:{t}", {"units": 0, "repos": set(), "deltas": 0, "rules": Counter()})
            slot["units"] += 1
            slot["repos"].add(repo)
            slot["deltas"] += r["deltas"]
            slot["rules"].update({k: v for k, v in (r.get("stats") or {}).items() if k[-1:] in "+-" and "-" in k[:-1]})
    return {"carrying": {k: {"units": v["units"], "repos": len(v["repos"]), "deltas": v["deltas"],
                             "rules": dict(v["rules"].most_common(25))} for k, v in sorted(carry.items())},
            "first_in_commit_order": dict(sorted(first.items())),
            "unexplained_units": len(unexplained), "unexplained": unexplained[:500]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("units_jsonl", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args(argv)
    out = summarize_units(args.units_jsonl)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "unexplained"}, indent=1)[:6000])
    return 0 if out["unexplained_units"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
