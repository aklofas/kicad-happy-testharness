"""Budget predicates for product 3.0.x Wave 3 (parsing and connectivity), range 004bba5 -> d2b9e72.

Classes (handoff-wave3.md "Budget classes"; file ``v30x-wave3.json``). Every delta is claimed per
UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined set of the triggers it
carries, e.g. ``M3+M7``) and every delta of that unit is explained, or the unit is a residual
(label ``None``).

Schematic, legacy ``.sch`` units (L1-L4: KH-511 pin transform + snap, KH-512/515 hidden power pins
and body style, KH-513 hierarchy, KH-662 sym-lib-table) move everywhere: label ``L``; the header
blocks in ``FIXED_TOP`` must not move and the derived blocks must follow from ``findings[]``.

Schematic, modern ``.kicad_sch`` units, triggers read off the two outputs:

  M1  KH-510 tokenizer: the source holds a lone quoted ``"("`` / ``")"`` (read from the source file);
  M2  KH-515 De Morgan: a (component, pin) appears on more than one net slot in the baseline;
  M3  KH-668 LB-001: LB-001 findings changed and their count did not grow;
  M4  KH-514/670 buses: ``bus_topology`` changed, or nets changed on a design with a global bus label;
  M5  KH-516/517 values: a component ``parsed_value`` changed;
  M6  KH-518 rail+control suffix / configured rail under a sheet path: a net or rail name that
      the two products' ``is_power_net_name`` classify differently (both functions evaluated);
  M7  KH-519 negative rails: a rail voltage changed sign only, or a negative rail voltage is
      present (its consumers now take the magnitude or skip); findings must name such a rail;
  M8  KH-560 exact coordinates: a ``CoordinateNearMiss`` diagnostic appeared, or only
      ``point_count`` moved on nets.

M1 / M2 / M4 and an M8 near-miss change connectivity, so any block outside ``FIXED_TOP`` may
move. M6 reclassifies nets, so findings may move and the blocks in ``M6_BLOCKS`` may. M3 moves
LB-001 only; M5 moves ``components[].parsed_value`` and the value consumers; M7 moves only
``M7_BLOCKS``; an M8 ``point_count``-only unit moves only ``nets/*/point_count``.

PCB units: P1 KiCad-5 outline arcs (``board_outline`` changed), P2 courtyards
(``footprints[].courtyard*`` / malformed-courtyard diagnostic), P3 silkscreen, P4 BV-001,
P5 ``connectivity_graph`` / pad ``roundrect_rratio``, M1 tokenizer, M6 power-net blocks; each
trigger opens the blocks and rules in ``PCB_ALLOW``. Under M6 the signal-net lists in
``PCB_SIGNAL_NET_LISTS`` may gain or lose only entries for reclassified net names.

Chained analyzers (emc / thermal / cross_analysis): ``D`` when the upstream schematic or pcb snap
differs under strict and that upstream unit is itself explained (same rule as Wave 2 ``DS``).

``python -m regression.budgets.v30x_wave3 GATE_DIR -o class_summary.json`` reports per-label
units / repos / deltas with sub-statistics and the unexplained units with their reasons.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

from regression.budgets.v232_backport import (
    expected_audience_summary,
    expected_summary,
    expected_trust_summary,
)
from regression.budgets.v30x_wave2 import _canon, _findings, _moved, _refs
from regression.field_compare import compare_strict, load_policy

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})
FIXED_TOP = frozenset({"analyzer_type", "schema_version", "kicad_version", "file_version", "title_block",
                       "compat"})
CONNECTIVITY = frozenset({"M1", "M2", "M4", "M8"})
M6_BLOCKS = frozenset({"statistics", "net_classifications", "rail_voltages", "design_analysis",
                       "power_budget", "power_sequencing", "power_sequencing_validation",
                       "sleep_current_audit", "test_coverage", "subcircuits", "ground_domains",
                       "pdn_impedance", "inrush_analysis", "connectivity_issues", "ic_pin_analysis",
                       "protocol_compliance", "transistor_pin_analysis", "usb_compliance", "missing_info"})
M5_BLOCKS = frozenset({"components", "bom", "bom_optimization", "pdn_impedance", "design_analysis", "subcircuits", "statistics",
                       "power_budget", "inrush_analysis", "test_coverage", "sleep_current_audit"})
# KH-519: the rail values themselves plus every consumer that now takes the magnitude or skips
M7_BLOCKS = frozenset({"rail_voltages", "statistics", "design_analysis", "sleep_current_audit", "power_budget",
                       "inrush_analysis", "protocol_compliance", "power_sequencing", "power_sequencing_validation"})
NEAR_MISS = "CoordinateNearMiss"
_QUOTED_PAREN = re.compile(r'"[()]"')

_POLICY = None


def _policy():
    global _POLICY
    if _POLICY is None:
        _POLICY = load_policy("volatile-leaves-v1")
    return _POLICY


def _block_diffs(a_doc: dict, b_doc: dict) -> set[str]:
    keys = (set(a_doc) | set(b_doc)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}
    return {k for k in keys if a_doc.get(k, None) != b_doc.get(k, None) or (k in a_doc) != (k in b_doc)}


def _derived_ok(doc: dict, *, full: bool) -> bool:
    fs = _findings(doc)
    if full and isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


def _source_files(doc: dict) -> list[str]:
    return [p for p in ((doc.get("inputs") or {}).get("source_files") or []) if isinstance(p, str)]


_SRC_CACHE: OrderedDict = OrderedDict()


def _has_quoted_paren(doc: dict) -> bool:
    """KH-510 trigger: a source file holds a string that is a lone bracket, ``"("`` or ``")"``."""
    for p in _source_files(doc):
        hit = _SRC_CACHE.get(p)
        if hit is None:
            try:
                hit = bool(_QUOTED_PAREN.search(Path(p).read_text(encoding="utf-8", errors="replace")))
            except OSError:
                hit = False
            _SRC_CACHE[p] = hit
            while len(_SRC_CACHE) > 256:
                _SRC_CACHE.popitem(last=False)
        if hit:
            return True
    return False


def _diags(doc: dict) -> list:
    d = doc.get("diagnostics")
    return d if isinstance(d, list) else []


def _new_diags(a: dict, b: dict, exc: str) -> list:
    old = Counter(_canon(x) for x in _diags(a) if isinstance(x, dict) and x.get("exception") == exc)
    new = Counter(_canon(x) for x in _diags(b) if isinstance(x, dict) and x.get("exception") == exc)
    return list((new - old).elements())


def _diag_movement_ok(a: dict, b: dict, allowed_exc: set[str]) -> bool:
    ca = Counter(_canon(x) for x in _diags(a))
    cb = Counter(_canon(x) for x in _diags(b))
    moved = list((ca - cb).elements()) + list((cb - ca).elements())
    return all(json.loads(m).get("exception") in allowed_exc for m in moved)


# ---- schematic ------------------------------------------------------------------------------

def _is_legacy(doc: dict) -> bool:
    lq = doc.get("legacy_analysis_quality")
    if isinstance(lq, dict) and lq.get("is_legacy_schematic"):
        return True
    return any(p.lower().endswith(".sch") for p in _source_files(doc)[:1])


def _pin_slots(doc: dict) -> Counter:
    c = Counter()
    for net in (doc.get("nets") or {}).values():
        for p in (net.get("pins") or []) if isinstance(net, dict) else []:
            if isinstance(p, dict):
                c[(p.get("component"), p.get("pin_number"))] += 1
    return c


def _rails(doc: dict) -> dict:
    out = {}
    for r in ((doc.get("statistics") or {}).get("power_rails") or []):
        if isinstance(r, dict) and r.get("name") is not None:
            out[r["name"]] = r.get("voltage")
    return out


def _negative_rails(doc: dict) -> set[str]:
    out = {k for k, v in (doc.get("rail_voltages") or {}).items() if isinstance(v, (int, float)) and v < 0}
    out |= {k for k, v in _rails(doc).items() if isinstance(v, (int, float)) and v < 0}
    return out


_BUS_NAME = re.compile(r"\[\d+\.\.\d+\]|\{")


def _has_global_bus_label(doc: dict) -> bool:
    return any(isinstance(lbl, dict) and lbl.get("type") == "global_label" and _BUS_NAME.search(str(lbl.get("name", "")))
               for lbl in doc.get("labels") or [])


def _only_point_count(a: dict, b: dict) -> bool:
    na, nb = a.get("nets") or {}, b.get("nets") or {}
    if set(na) != set(nb):
        return False
    for k in na:
        x, y = na[k], nb[k]
        if x == y:
            continue
        if not isinstance(x, dict) or not isinstance(y, dict):
            return False
        if {f for f in set(x) | set(y) if x.get(f) != y.get(f)} != {"point_count"}:
            return False
    return True


_NETNAMES: dict[str, Any] = {}
BASELINE_SHA7, CANDIDATE_SHA7 = "004bba5", "d2b9e72"


def _netnames(side: str):
    """``kicad_core.netnames`` of one product clone (``results/v3_baseline/product_<sha7>``)."""
    if side not in _NETNAMES:
        import importlib.util
        from utils import DATA_ROOT
        sha = BASELINE_SHA7 if side == "a" else CANDIDATE_SHA7
        path = Path(DATA_ROOT) / "results" / "v3_baseline" / f"product_{sha}" / "skills" / "kicad" / "scripts" / "kicad_core" / "netnames.py"
        spec = importlib.util.spec_from_file_location(f"_v30x_w3_netnames_{side}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _NETNAMES[side] = mod
    return _NETNAMES[side]


def _flagged_nets(doc: dict) -> set[str]:
    """``kicad_types.scan_power_rails``: nets carrying a ``#PWR`` / ``#FLG`` pin (the context's rail set)."""
    out = set()
    for name, net in (doc.get("nets") or {}).items():
        for p in (net.get("pins") or []) if isinstance(net, dict) else []:
            if isinstance(p, dict) and str(p.get("component", "")).startswith(("#PWR", "#FLG")):
                out.add(name)
                break
    return out


def _power_name_flips(a: dict, b: dict, rails: set[str]) -> set[str]:
    """Names the two products classify differently, with the stats rails, the context rails or none."""
    old, new = _netnames("a").is_power_net_name, _netnames("b").is_power_net_name
    ctx_rails = _flagged_nets(a) | _flagged_nets(b)
    names = set(a.get("nets") or {}) | set(b.get("nets") or {}) | rails
    return {n for n in names if isinstance(n, str)
            and any(old(n, r) != new(n, r) for r in (rails, ctx_rails, None))}


def _sign_only(x, y) -> bool:
    return isinstance(x, (int, float)) and isinstance(y, (int, float)) and x != y and abs(x) == abs(y)


def _deep_strings(v: Any) -> set[str]:
    """Every string anywhere in a finding (component refs sit in many differently named fields)."""
    if isinstance(v, str):
        return {v}
    if isinstance(v, dict):
        return set().union(*(_deep_strings(x) for x in v.values())) if v else set()
    if isinstance(v, list):
        return set().union(*(_deep_strings(x) for x in v)) if v else set()
    return set()


def _schematic_legacy(a, b):
    bad = [f"block {k}" for k in _block_diffs(a, b) & FIXED_TOP]
    stats = Counter()
    ca = {c.get("reference"): c for c in a.get("components") or [] if isinstance(c, dict)}
    cb = {c.get("reference"): c for c in b.get("components") or [] if isinstance(c, dict)}
    l1 = l2 = False
    for ref in set(ca) & set(cb):
        pa, pb = ca[ref].get("pins") or [], cb[ref].get("pins") or []
        if [(p.get("x"), p.get("y")) for p in pa] != [(p.get("x"), p.get("y")) for p in pb] \
                or ca[ref].get("_pin_source") != cb[ref].get("_pin_source"):
            l1 = True
        if any(p.get("hidden") for p in pb) or len(pb) < len(pa):
            l2 = True
    l3 = (a.get("sheets_parsed") != b.get("sheets_parsed") or len(ca) != len(cb)
          or a.get("sheet_files") != b.get("sheet_files"))
    lra = ((a.get("legacy_analysis_quality") or {}).get("library_resolution") or {})
    lrb = ((b.get("legacy_analysis_quality") or {}).get("library_resolution") or {})
    l4 = lra.get("parsed_lib_count") != lrb.get("parsed_lib_count") or lra.get("sym_lib_table_used") != lrb.get("sym_lib_table_used")
    stats.update({"L1_pins": int(l1), "L2_hidden_or_body": int(l2), "L3_hierarchy": int(l3), "L4_symlib": int(l4),
                  "grouping_changed": int(a.get("nets") != b.get("nets")),
                  "components_delta": len(cb) - len(ca)})
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    return ("L" if not bad else None), bad, stats


def _schematic_triggers(a, b) -> tuple[set[str], Counter]:
    trig, stats = set(), Counter()
    blocks = _block_diffs(a, b)
    if _has_quoted_paren(b):
        trig.add("M1")
    sa, sb = _pin_slots(a), _pin_slots(b)
    if any(n > 1 and sb.get(k, 0) < n for k, n in sa.items()):
        trig.add("M2")
        stats["M2_pin_slots_removed"] += sum(sa.values()) - sum(sb.values())
    lb_a = [f for f in _findings(a) if f.get("rule_id") == "LB-001"]
    lb_b = [f for f in _findings(b) if f.get("rule_id") == "LB-001"]
    if Counter(map(_canon, lb_a)) != Counter(map(_canon, lb_b)) and len(lb_b) <= len(lb_a):
        trig.add("M3")
        stats["LB-001_delta"] += len(lb_b) - len(lb_a)
    bt_a, bt_b = a.get("bus_topology") or {}, b.get("bus_topology") or {}
    if "bus_topology" in blocks or ("nets" in blocks and (_has_global_bus_label(a) or _has_global_bus_label(b))):
        trig.add("M4")
        stats["M4_unresolved_delta"] += len(bt_b.get("unresolved") or []) - len(bt_a.get("unresolved") or [])
    pa = {c.get("reference"): c.get("parsed_value") for c in a.get("components") or [] if isinstance(c, dict)}
    pb = {c.get("reference"): c.get("parsed_value") for c in b.get("components") or [] if isinstance(c, dict)}
    vals = {r for r in set(pa) & set(pb) if pa[r] != pb[r]}
    if vals:
        trig.add("M5")
        stats["M5_values"] += len(vals)
    ra, rb = _rails(a), _rails(b)
    flipped = _power_name_flips(a, b, set(ra) | set(rb))
    if flipped:
        trig.add("M6")
        stats["M6_names_reclassified"] += len(flipped)
    flips = [k for k in set(ra) & set(rb) if _sign_only(ra[k], rb[k])]
    rva, rvb = a.get("rail_voltages") or {}, b.get("rail_voltages") or {}
    flips += [k for k in set(rva) & set(rvb) if _sign_only(rva[k], rvb[k])]
    if flips:
        trig.add("M7")
        stats["M7_sign_flips"] += len(flips)
    elif (_negative_rails(a) | _negative_rails(b)) and (blocks or _moved(a, b) != ([], [])):
        trig.add("M7")
        stats["M7_negative_rail_consumers"] += 1
    nm = _new_diags(a, b, NEAR_MISS)
    if nm:
        trig.add("M8")
        stats["M8_near_miss"] += len(nm)
    elif "nets" in blocks and _only_point_count(a, b):
        trig.add("M8pc")
        stats["M8_point_count_only"] += 1
    return trig, stats


def _schematic(a, b):
    if _is_legacy(a) or _is_legacy(b):
        return _schematic_legacy(a, b)
    trig, stats = _schematic_triggers(a, b)
    blocks = _block_diffs(a, b)
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    bad = [f"block {k}" for k in blocks & FIXED_TOP]
    if not trig:
        return None, bad + ["schematic movement without a trigger"], stats
    if not _diag_movement_ok(a, b, {NEAR_MISS}):
        bad.append("diagnostics beyond CoordinateNearMiss")
    blocks -= {"diagnostics"}
    if trig & CONNECTIVITY:
        allowed_blocks = None  # connectivity changed: everything outside FIXED_TOP may follow
        any_finding = True
    else:
        allowed_blocks = set()
        any_finding = False
        if "M6" in trig:
            allowed_blocks |= M6_BLOCKS
            any_finding = True
        if "M5" in trig:
            allowed_blocks |= M5_BLOCKS
        if "M7" in trig:
            allowed_blocks |= M7_BLOCKS
        if "M8pc" in trig:
            allowed_blocks |= {"nets"}
    if allowed_blocks is not None:
        bad += [f"block {k}" for k in blocks - allowed_blocks - FIXED_TOP]
        if "components" in blocks and "M5" in trig:
            ca = {c.get("reference"): c for c in a.get("components") or []}
            cb = {c.get("reference"): c for c in b.get("components") or []}
            for r in set(ca) | set(cb):
                x, y = ca.get(r), cb.get(r)
                if x != y and (x is None or y is None
                               or {k for k in set(x) | set(y) if x.get(k) != y.get(k)} - {"parsed_value"}):
                    bad.append(f"component {r} beyond parsed_value")
                    break
    if not any_finding:
        changed_vals = set()
        neg = {x.rsplit("/", 1)[-1] for x in _negative_rails(a) | _negative_rails(b)}
        if "M5" in trig:
            pa = {c.get("reference"): c.get("parsed_value") for c in a.get("components") or []}
            pb = {c.get("reference"): c.get("parsed_value") for c in b.get("components") or []}
            changed_vals = {r for r in set(pa) & set(pb) if pa[r] != pb[r]}
        for f in rem + add:
            rule = f.get("rule_id")
            if rule == "LB-001" and "M3" in trig:
                continue
            if "M5" in trig and (rule == "SC-001" or _deep_strings(f) & changed_vals):
                continue
            if "M7" in trig and {x.rsplit("/", 1)[-1] for x in _deep_strings(f)} & neg:
                continue
            bad.append(f"finding {rule} {str(f.get('summary', ''))[:60]}")
    return ("+".join(sorted(trig)) if not bad else None), bad, stats


# ---- pcb ------------------------------------------------------------------------------------

PCB_ALLOW = {
    # board size feeds statistics / DFM / density / design_intent signals; PM-002 is edge clearance
    "P1": ({"board_outline", "statistics", "dfm_summary", "placement_density", "placement_analysis",
            "board_edge_via_clearance", "edge_clearance", "component_edge_clearance", "dfm", "design_intent"},
           {"DFM-001", "DF-001", "BV-001", "EC-001", "PD-001", "PM-002"}),
    # courtyards: overlaps (PM-001), edge clearance (PM-002), via fanout patterns (vias.via_analysis)
    "P2": ({"footprints", "courtyard_overlaps", "placement_analysis", "placement_density", "via_fanout",
            "statistics", "assembly", "vias"}, {"PM-001", "PM-002"}),
    "P3": ({"silkscreen"}, set()),
    "P4": ({"board_edge_via_clearance"}, {"BV-001"}),
    "P5": ({"connectivity_graph", "footprints"}, set()),
    # a demoted rail joins the signal-net blocks (layer_transitions) and leaves the current-capacity ones
    "M6": ({"power_net_routing", "power_net_resolution", "statistics", "net_classifications",
            "current_capacity", "thermal_pad_vias"}, {"CC-DET", "CC-002"}),
}


COURTYARD_FIELDS = ("courtyard", "courtyard_poly")


def _fp_courtyards(doc: dict) -> list:
    # index-aligned: references repeat (REF**), so a dict by reference would collapse them
    return [tuple(f.get(k) for k in COURTYARD_FIELDS) for f in doc.get("footprints") or [] if isinstance(f, dict)]


def _fp_other_fields(a: dict, b: dict) -> set[str]:
    """Footprint fields that moved other than the courtyard (same footprint order on both sides)."""
    fa, fb = a.get("footprints") or [], b.get("footprints") or []
    if len(fa) != len(fb):
        return {"<count>"}
    out = set()
    for x, y in zip(fa, fb):
        if x != y and isinstance(x, dict) and isinstance(y, dict):
            out |= {k for k in set(x) | set(y) if x.get(k) != y.get(k)} - set(COURTYARD_FIELDS)
    return out


def _pcb_triggers(a, b) -> set[str]:
    blocks = _block_diffs(a, b)
    trig = set()
    if _has_quoted_paren(b):
        trig.add("M1")
    if "board_outline" in blocks:
        trig.add("P1")
    if _fp_courtyards(a) != _fp_courtyards(b) or _new_diags(a, b, "MalformedCourtyard"):
        trig.add("P2")
    if "silkscreen" in blocks:
        trig.add("P3")
    rem, add = _moved(a, b)
    if "board_edge_via_clearance" in blocks or any(f.get("rule_id") == "BV-001" for f in rem + add):
        trig.add("P4")
    if "connectivity_graph" in blocks:
        trig.add("P5")
    if blocks & {"power_net_routing", "power_net_resolution"}:
        trig.add("M6")
    return trig


# signal-net lists keyed by ``net``: a demoted / promoted rail joins or leaves them (KH-518)
PCB_SIGNAL_NET_LISTS = ("layer_transitions", "return_path_continuity")


def _signal_list_moves_are_reclassified(a: dict, b: dict, key: str) -> bool:
    """Entries only joined or left, each for a net name the two products classify differently."""
    la = {x.get("net"): x for x in a.get(key) or [] if isinstance(x, dict)}
    lb = {x.get("net"): x for x in b.get(key) or [] if isinstance(x, dict)}
    if any(la[n] != lb[n] for n in set(la) & set(lb)):
        return False
    old, new = _netnames("a").is_power_net_name, _netnames("b").is_power_net_name
    return all(isinstance(n, str) and old(n, None) != new(n, None) for n in set(la) ^ set(lb))


def _pcb(a, b):
    trig = _pcb_triggers(a, b)
    blocks = _block_diffs(a, b) - {"diagnostics"}
    for key in PCB_SIGNAL_NET_LISTS:
        if key in blocks and "M6" in trig and _signal_list_moves_are_reclassified(a, b, key):
            blocks.discard(key)
    rem, add = _moved(a, b)
    stats = Counter(f"{f.get('rule_id')}-" for f in rem)
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    bad = [f"block {k}" for k in blocks & FIXED_TOP]
    if not trig:
        return None, bad + ["pcb movement without a trigger"], stats
    if "M1" not in trig:
        ok_blocks, ok_rules = set(), set()
        for t in trig:
            ob, orl = PCB_ALLOW.get(t, (set(), set()))
            ok_blocks |= ob
            ok_rules |= orl
        bad += [f"block {k}" for k in blocks - ok_blocks]
        bad += [f"finding {f.get('rule_id')}" for f in rem + add if f.get("rule_id") not in ok_rules]
        if "footprints" in blocks and _fp_other_fields(a, b) and not ({"P5"} & trig):
            bad.append(f"footprint fields {sorted(_fp_other_fields(a, b))[:4]}")
    return ("+".join(sorted(trig)) if not bad else None), bad, stats


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


# ---- upstream (chained analyzers), as in v30x_wave2 -----------------------------------------

def _slot_root(p: str) -> str:
    m = re.match(r"(.*?/(?:baseline|candidate))/(?:schematic|pcb)/", p)
    return m.group(1) if m else ""


_UP: OrderedDict = OrderedDict()
_DELTA_UNITS: dict[str, frozenset | None] = {}


def _delta_units(slot_root: str) -> frozenset | None:
    gate = str(Path(slot_root).parent)
    if gate not in _DELTA_UNITS:
        rep = Path(gate) / "field_report_strict.json"
        try:
            doc = json.loads(rep.read_text(encoding="utf-8"))
            _DELTA_UNITS[gate] = frozenset(d["unit"] for d in doc.get("deltas") or [])
        except (OSError, json.JSONDecodeError):
            _DELTA_UNITS[gate] = None
    return _DELTA_UNITS[gate]


def _upstream(a_doc: dict, b_doc: dict) -> list[tuple[str, dict, dict]]:
    out = []
    ua = ((a_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    ub = ((b_doc.get("inputs") or {}).get("upstream_artifacts") or {})
    for kind in ("schematic", "pcb"):
        pa, pb = (ua.get(kind) or {}).get("path"), (ub.get(kind) or {}).get("path")
        if not pa or not pb:
            continue
        ra, rb = _slot_root(pa), _slot_root(pb)
        known = _delta_units(rb) if rb else None
        if known is not None:
            unit = pb[len(rb) + 1:]
            unit = unit[:-len("/snap.json")] if unit.endswith("/snap.json") else unit
            if unit not in known:
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
                ds_, _ = compare_strict(da, db, _policy(), unit=kind, analyzer=kind, root_prefixes=(ra, rb))
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
        for kind, da, db in up:
            if da is None:
                reasons.append(f"upstream {kind} unreadable")
            elif classify_unit(kind, da, db)["label"] is None:
                reasons.append(f"upstream {kind} unexplained")
        return {"label": "D" if not reasons else None, "reasons": reasons,
                "stats": Counter({"upstream_" + k: 1 for k, _, _ in up})}
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


def _label_in(prefixes: tuple[str, ...]):
    """A unit whose label is set and starts with one of ``prefixes`` (labels are trigger sets)."""
    def pred(delta, a_doc, b_doc) -> bool:
        r = _cached(delta, a_doc, b_doc)
        return bool(r and r["label"] and r["label"].startswith(prefixes))
    pred.__name__ = "label_" + "_".join(prefixes)
    return pred


legacy = _label_in(("L",))
modern_schematic = _label_in(("M",))
pcb = _label_in(("M", "P"))
downstream = _label_in(("D",))


# ---- adjudication summary -------------------------------------------------------------------

def summarize(gate_dir: Path, report_name: str = "field_report_strict.json") -> dict:
    rep = json.loads((gate_dir / report_name).read_text(encoding="utf-8"))
    units: dict[tuple[str, str], int] = OrderedDict()
    for d in rep.get("deltas") or []:
        units[(d["analyzer"], d["unit"])] = units.get((d["analyzer"], d["unit"]), 0) + 1
    per: dict[str, dict] = {}
    unexplained = []
    for (analyzer, unit), n in units.items():
        sub = unit.split("/", 1)[1]
        try:
            a = json.loads((gate_dir / "baseline" / unit / "snap.json").read_text(encoding="utf-8"))
            b = json.loads((gate_dir / "candidate" / unit / "snap.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            unexplained.append({"unit": unit, "reasons": [f"unreadable: {e}"]})
            continue
        r = classify_unit(analyzer, a, b)
        lab = r["label"] or "UNEXPLAINED"
        slot = per.setdefault(f"{lab}/{analyzer}", {"units": 0, "repos": set(), "deltas": 0, "stats": Counter()})
        slot["units"] += 1
        slot["repos"].add("/".join(sub.split("/")[:2]))
        slot["deltas"] += n
        slot["stats"].update(r["stats"])
        if r["label"] is None:
            unexplained.append({"unit": unit, "deltas": n, "reasons": r["reasons"][:10]})
    return {"report": str(gate_dir / report_name),
            "classes": {k: {"units": v["units"], "repos": len(v["repos"]), "deltas": v["deltas"],
                            "stats": dict(sorted(v["stats"].items()))} for k, v in sorted(per.items())},
            "unexplained_units": len(unexplained), "unexplained": unexplained}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate_dir", type=Path)
    ap.add_argument("--report", default="field_report_strict.json")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args(argv)
    out = summarize(args.gate_dir, args.report)
    args.output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "unexplained"}, indent=1)[:4000])
    return 0 if out["unexplained_units"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
