"""Budget predicates for product 3.0.x Wave 4 Part A (schematic detectors and SPICE), range 5161f19 -> b31d4ff.

Classes (Wave 4 Part A handoff "Budget classes"; file ``v30x-wave4a.json``). Every delta is claimed
per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined set of the classes whose
trigger it carries) and every delta of that unit is explained, or the unit is a residual (label
``None``).

Schematic units (modern and legacy alike). A class opens the blocks, ``design_analysis`` /
``statistics`` / ``protocol_compliance`` / ``connectivity_issues`` sub-blocks and finding rules in
``CLASSES``; it is triggered when one of its own blocks or rules moved, except the classes below,
whose triggers are read off constructs:

  A1   KH-708 field trim: a component text field (value / footprint / datasheet / description)
       differs only by surrounding whitespace or ``" ~"`` -> ``~``. Findings that differ only by
       such trimmed strings are A1 too (finding values echo component values).
  PWR  A3-A9 / S3b / C4 rails: a net changed power classification (``statistics.power_rails``,
       ``net_classifications``, ``design_analysis.net_classification``), or a rail voltage or a
       regulator estimate (PR-DET) moved. Any finding that names such a net or rail is PWR.
  K1   V4 LED typing: a component ``type`` moved led -> diode (and back for rescue libraries).

Component records may move only in the A1 text fields and the K1 ``type``; ``nets``, ``labels``,
``sheets`` and the header blocks never move in this round.

PCB units (``A4d``): the power-net blocks (``PCB_A4D_BLOCKS``) and CC-DET / CC-002 may move when
a net name in them is re-read as power by the candidate's ``is_power_net_name`` (the pcb analyzer
classifies by name, so ruling 62 reaches the standard profile) or, in full-chain, when the
unit's upstream schematic moved under PWR. Nothing else on a board moves.

Chained analyzers (emc / thermal / cross_analysis): ``D`` when the upstream schematic or pcb snap
differs under strict and that upstream unit is itself explained (same rule as Wave 3 ``D``).
Cross ``XV-001..003`` on trimmed values ride the A1 upstream move.

``python -m regression.budgets.v30x_wave4a GATE_DIR -o class_summary.json`` reports per-label
units / repos / deltas with per-class sub-statistics and the unexplained units with their reasons.
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
from regression.budgets.v30x_wave2 import _findings
from regression.field_compare import compare_strict, load_policy

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})
FIXED_TOP = frozenset({"analyzer_type", "schema_version", "kicad_version", "file_version", "title_block",
                       "compat", "nets", "labels", "sheets", "no_connects", "wire_geometry",
                       "hierarchical_labels", "power_symbols", "bus_topology", "text_annotations"})
# blocks compared per sub-key
COMPOSITE = frozenset({"design_analysis", "statistics", "protocol_compliance", "connectivity_issues"})
A1_FIELDS = ("value", "footprint", "datasheet", "description")
# consumers of a net's power status or a rail voltage (A4 list, A5, A8, A9)
RAIL_BLOCKS = frozenset({
    "statistics.power_rails", "net_classifications", "rail_voltages",
    "design_analysis.net_classification", "design_analysis.power_domains", "design_analysis.cross_domain_signals",
    "power_budget", "sleep_current_audit", "pdn_impedance", "test_coverage", "inrush_analysis",
    "power_sequencing", "power_sequencing_validation", "subcircuits", "pwr_flag_warnings",
    "ic_pin_analysis", "transistor_pin_analysis", "protocol_compliance.findings", "protocol_compliance.total_issues",
    "design_analysis.bus_analysis", "usb_compliance", "simulation_readiness", "missing_info",
})
RAIL_RULES = frozenset({"DO-DET", "DC-DET", "PP-001", "PU-001", "PR-001", "PR-002", "LB-001", "RS-001", "RS-002",
                        "VM-001", "EP-AUD", "CG-AUD", "CERT-001", "VD-004", "VD-001", "VD-DET", "PR-DET",
                        "PS-001", "FS-001",
                        # detectors that read a net's power status (has_snubber / *_is_power / power_nets /
                        # power_supply / shared signal counts follow a reclassified net)
                        "MI-DET", "TR-DET", "LD-DET", "SJ-DET", "MD-DET", "IL-DET", "LS-DET", "RS-003"})

# id -> (blocks, rules). Blocks are top-level keys or "<composite>.<sub-key>".
CLASSES: dict[str, tuple[frozenset, frozenset]] = {
    "A1": (frozenset({"components", "bom", "bom_lock", "bom_optimization", "statistics.unique_parts",
                      "statistics.missing_footprint", "statistics.missing_mpn", "statistics.dnp_parts", "annotation_issues",
                      "sourcing_audit", "property_issues", "missing_info", "assembly_complexity"}),
           # BOM lines merge once their texts are trimmed: the BOM-level sourcing / datasheet counts follow
           frozenset({"SS-001", "DS-001", "DS-002", "DS-003"})),
    "PWR": (RAIL_BLOCKS, RAIL_RULES),
    "K1": (frozenset({"components", "bom", "statistics.component_types", "assembly_complexity",
                      "bom_optimization"}), frozenset({"LR-001", "LA-AUD", "PD-DET", "PL-001", "LD-DET"})),
    "B1": (frozenset({"design_analysis.differential_pairs"}), frozenset()),
    "B2": (frozenset({"design_analysis.bus_analysis", "protocol_compliance", "protocol_compliance.findings",
                      "protocol_compliance.total_issues", "protocol_compliance.protocols_checked"}),
           frozenset({"PR-003"})),
    "B4": (frozenset({"net_classifications", "power_sequencing", "power_sequencing_validation"}),
           frozenset({"SI-DET", "RF-DET", "WL-001", "RS-DET", "LV-DET", "CERT-001"})),
    "B5": (frozenset(), frozenset({"IA-001"})),
    "B6": (frozenset({"design_analysis.erc_warnings", "connectivity_issues.multi_driver_nets"}), frozenset()),
    "B7": (frozenset({"instance_consistency_warnings", "footprint_filter_warnings"}), frozenset()),
    "V1": (frozenset({"rail_voltages", "power_budget", "subcircuits", "pdn_impedance", "inrush_analysis",
                      "power_sequencing_validation"}),
           frozenset({"VD-DET", "PR-DET", "DO-DET", "FS-001", "DC-DET", "CS-DET", "XL-DET"})),
    # RM-DET takes the parts an LC filter no longer claims
    "V2": (frozenset({"subcircuits"}), frozenset({"RC-DET", "LC-DET", "DO-DET", "AD-DET", "CD-DET", "RM-DET"})),
    "V3": (frozenset({"subcircuits"}), frozenset({"OA-DET"})),
    "V4": (frozenset(), frozenset({"LR-001", "LA-AUD", "PD-DET", "PL-001", "LD-DET"})),
    "V5": (frozenset(), frozenset({"FS-001", "VM-001", "PS-001"})),
    "V6": (frozenset(), frozenset({"PP-DET", "ET-DET"})),
}
# classes whose trigger is their own rules / blocks moving (A1, PWR and K1 are read off constructs)
SELF_TRIGGERED = ("B1", "B2", "B4", "B5", "B6", "B7", "V1", "V2", "V3", "V4", "V5", "V6")

_POLICY = None


def _policy():
    global _POLICY
    if _POLICY is None:
        _POLICY = load_policy("volatile-leaves-v1")
    return _POLICY


def _canon(f: Any) -> str:
    g = dict(f) if isinstance(f, dict) else {"_": f}
    g.pop("finding_id", None)
    return json.dumps(g, sort_keys=True, default=str)


def _trim(v: Any) -> Any:
    """KH-708 normalization: strings stripped of surrounding whitespace, ``" ~"`` read as ``~``."""
    if isinstance(v, str):
        return v.strip(" \t\n\r\v\f")
    if isinstance(v, dict):
        return {k: _trim(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_trim(x) for x in v]
    return v


def _trim_map(a: dict, b: dict) -> dict[str, str]:
    """Raw baseline text -> trimmed candidate text for every A1 field that only lost padding."""
    out = {}
    for x, y in zip(_comps(a), _comps(b)):
        for k in A1_FIELDS:
            u, v = x.get(k), y.get(k)
            # exact strings are already handled by the strip; a short text (``" ~"``) embedded in
            # unrelated strings would be rewritten where it is not an echo
            if isinstance(u, str) and isinstance(v, str) and u != v and _trim(u) == _trim(v) and len(_trim(u)) >= 3:
                out[u] = v
    return out


def _a1n(v: Any, repl: dict[str, str]) -> Any:
    """``_trim`` plus the trimmed component texts substituted where a string embeds the raw one
    (``repl`` is for the baseline side only: the candidate already carries the trimmed texts)."""
    if isinstance(v, str):
        for old, new in repl.items():
            if old in v:
                v = v.replace(old, new)
        return v.strip(" \t\n\r\v\f")
    if isinstance(v, dict):
        return {k: _a1n(x, repl) for k, x in v.items()}
    if isinstance(v, list):
        return [_a1n(x, repl) for x in v]
    return v


def _get(doc: dict, key: str) -> Any:
    top, _, sub = key.partition(".")
    v = doc.get(top)
    return v.get(sub) if sub and isinstance(v, dict) else v


def _sub_diffs(a: dict, b: dict) -> set[str]:
    out = set()
    for k in (set(a) | set(b)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}:
        x, y = a.get(k), b.get(k)
        if x == y and (k in a) == (k in b):
            continue
        if k in COMPOSITE and isinstance(x, dict) and isinstance(y, dict):
            out |= {f"{k}.{s}" for s in set(x) | set(y) if x.get(s) != y.get(s) or (s in x) != (s in y)}
        else:
            out.add(k)
    return out


def _moved(a: dict, b: dict) -> tuple[list, list]:
    ca = Counter(_canon(f) for f in _findings(a))
    cb = Counter(_canon(f) for f in _findings(b))
    return [json.loads(k) for k in (ca - cb).elements()], [json.loads(k) for k in (cb - ca).elements()]


def _deep_strings(v: Any) -> set[str]:
    if isinstance(v, str):
        return {v}
    if isinstance(v, dict):
        return set().union(*(_deep_strings(x) for x in v.values())) if v else set()
    if isinstance(v, list):
        return set().union(*(_deep_strings(x) for x in v)) if v else set()
    return set()


def _ident(f: dict) -> tuple:
    return (f.get("rule_id"), f.get("detection_id") or "", tuple(sorted(str(c) for c in f.get("components") or [])))


def _leaf(n: str) -> str:
    return n.rsplit("/", 1)[-1]


# ---- triggers ---------------------------------------------------------------------------------

def _comps(doc: dict) -> list:
    return [c for c in doc.get("components") or [] if isinstance(c, dict)]


DNP_VALUES = ("DNP", "DO NOT POPULATE", "DO NOT PLACE", "NP")


def _component_moves(a: dict, b: dict) -> tuple[Counter, list[str], set[str]]:
    """A1 / K1 counts, the component moves no class explains (index-aligned: refs repeat) and the
    refs whose trimmed value is blank or now reads as DNP (their findings change beyond an echo)."""
    stats, bad, a1_refs = Counter(), [], set()
    ca, cb = _comps(a), _comps(b)
    if len(ca) != len(cb):
        return stats, [f"component count {len(ca)} -> {len(cb)}"], a1_refs
    for x, y in zip(ca, cb):
        if x == y:
            continue
        trimmed_value = x.get("value") != y.get("value") and _trim(x.get("value")) == _trim(y.get("value"))
        if trimmed_value and not _trim(y.get("value")):
            a1_refs.add(y.get("reference"))
            stats["A1_value_blank"] += 1
        for k in set(x) | set(y):
            u, v = x.get(k), y.get(k)
            if u == v:
                continue
            if k in A1_FIELDS and _trim(u) == _trim(v):
                stats[f"A1_{k}"] += 1
            elif k == "dnp" and trimmed_value and str(y.get("value")).upper() in DNP_VALUES:
                stats["A1_dnp_by_value"] += 1
                a1_refs.add(y.get("reference"))
            elif k == "type" and {u, v} == {"led", "diode"}:
                stats[f"K1_{u}->{v}"] += 1
            elif k == "parsed_value" and _trim(x.get("value")) == _trim(y.get("value")) and x.get("value") != y.get("value"):
                stats["A1_parsed_value"] += 1
            else:
                bad.append(f"component {x.get('reference')} {k}: {str(u)[:40]!r} -> {str(v)[:40]!r}")
    return stats, bad, a1_refs


def _power_rail_names(doc: dict) -> dict:
    out = {}
    for r in ((doc.get("statistics") or {}).get("power_rails") or []):
        if isinstance(r, dict) and r.get("name") is not None:
            out[r["name"]] = r.get("voltage")
        elif isinstance(r, str):
            out[r] = None
    return out


def _classification(doc: dict) -> dict:
    out = {}
    nc = doc.get("net_classifications")
    if isinstance(nc, dict):
        out.update({k: json.dumps(v, sort_keys=True, default=str) for k, v in nc.items()})
    dnc = (doc.get("design_analysis") or {}).get("net_classification")
    if isinstance(dnc, dict):
        out.update({"da:" + k: json.dumps(v, sort_keys=True, default=str) for k, v in dnc.items()})
    return out


def _rail_nets(a: dict, b: dict) -> tuple[set[str], Counter]:
    """Nets / rails whose power status, class or voltage moved (the PWR trigger set)."""
    stats = Counter()
    ra, rb = _power_rail_names(a), _power_rail_names(b)
    flips = set(ra) ^ set(rb)
    stats["power_rails_added"] += len(set(rb) - set(ra))
    stats["power_rails_removed"] += len(set(ra) - set(rb))
    volt = {k for k in set(ra) & set(rb) if ra[k] != rb[k]}
    stats["power_rail_voltage_changed"] += len(volt)
    va, vb = a.get("rail_voltages") or {}, b.get("rail_voltages") or {}
    if isinstance(va, dict) and isinstance(vb, dict):
        stats["rail_voltages_keys_removed"] += len(set(va) - set(vb))
        stats["rail_voltages_keys_added"] += len(set(vb) - set(va))
        rv = {k for k in set(va) | set(vb) if va.get(k) != vb.get(k)}
        stats["rail_voltages_values_changed"] += len({k for k in rv if k in va and k in vb})
        volt |= rv
    ca, cb = _classification(a), _classification(b)
    cls = {k.removeprefix("da:") for k in set(ca) | set(cb) if ca.get(k) != cb.get(k)}
    stats["net_class_changed"] += len(cls)
    return flips | volt | cls, stats


_NETNAMES: dict[str, Any] = {}
BASELINE_SHA7, CANDIDATE_SHA7 = "0683d01", "b31d4ff"


def _netnames(side: str):
    """``kicad_core.netnames`` of one product clone (``results/v3_baseline/product_<sha7>``).

    Both clones name their package ``kicad_core``: each is imported alone with its scripts dir
    first on ``sys.path`` and then dropped from ``sys.modules``, so the two never mix."""
    if side not in _NETNAMES:
        import importlib
        from utils import DATA_ROOT
        sha = BASELINE_SHA7 if side == "a" else CANDIDATE_SHA7
        scripts = str(Path(DATA_ROOT) / "results" / "v3_baseline" / f"product_{sha}" / "skills" / "kicad" / "scripts")
        saved = {k: sys.modules.pop(k) for k in list(sys.modules) if k == "kicad_core" or k.startswith("kicad_core.")}
        sys.path.insert(0, scripts)
        try:
            _NETNAMES[side] = importlib.import_module("kicad_core.netnames")
        finally:
            sys.path.remove(scripts)
            for k in [k for k in sys.modules if k == "kicad_core" or k.startswith("kicad_core.")]:
                del sys.modules[k]
            sys.modules.update(saved)
    return _NETNAMES[side]


def _name_flips(a: dict, b: dict) -> set[str]:
    """Net names the two products' ``is_power_net_name`` / ``parse_voltage_from_net_name`` read differently."""
    old, new = _netnames("a"), _netnames("b")
    rails = set(_power_rail_names(a)) | set(_power_rail_names(b))
    out = set()
    for n in set(a.get("nets") or {}) | set(b.get("nets") or {}) | rails:
        if not isinstance(n, str):
            continue
        if any(old.is_power_net_name(n, r) != new.is_power_net_name(n, r) for r in (rails, None)) \
                or old.parse_voltage_from_net_name(n) != new.parse_voltage_from_net_name(n):
            out.add(n)
    return out


def _regulators_moved(rem: list, add: list) -> bool:
    return any(f.get("rule_id") == "PR-DET" for f in rem + add)


# ---- schematic --------------------------------------------------------------------------------

def _unmatched(findings: list, left: Counter, repl: dict[str, str]) -> list:
    """The findings whose A1-normalized form is still counted in ``left``."""
    left, out = Counter(left), []
    for f in findings:
        k = _canon(_a1n(f, repl))
        if left[k] > 0:
            left[k] -= 1
            out.append(f)
    return out


def _schematic(a: dict, b: dict):
    stats = Counter()
    subs = _sub_diffs(a, b)
    bad = [f"block {k}" for k in subs if k.split(".")[0] in FIXED_TOP]
    cstats, cbad, a1_refs = _component_moves(a, b)
    stats.update(cstats)
    bad += cbad
    trig: set[str] = set()
    if any(k.startswith("A1_") for k in cstats):
        trig.add("A1")
    if any(k.startswith("K1_") for k in cstats):
        trig.add("K1")

    repl = _trim_map(a, b)
    for k in sorted(subs):
        if k != "components" and k.split(".")[0] not in FIXED_TOP and _a1n(_get(a, k), repl) == _a1n(_get(b, k), {}):
            subs.discard(k)
            trig.add("A1")
            stats["A1_block_echo"] += 1
    rem, add = _moved(a, b)
    # findings that differ only by trimmed strings: A1 echoes, paired off before the class checks
    ta = Counter(_canon(_a1n(f, repl)) for f in rem)
    tb = Counter(_canon(_a1n(f, {})) for f in add)
    echo = ta & tb
    if echo:
        trig.add("A1")
        stats["A1_finding_echo"] += sum(echo.values())
        rem = _unmatched(rem, ta - echo, repl)
        add = _unmatched(add, tb - echo, {})
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))

    rail_set, rstats = _rail_nets(a, b)
    flipped = _name_flips(a, b) if (subs or rem or add) else set()
    rstats["net_names_reread"] += len(flipped)
    rstats["net_names_reread_sheet_path"] += sum(1 for n in flipped if "/" in n)
    rail_set |= flipped
    if rail_set or _regulators_moved(rem, add):
        trig.add("PWR")
        stats.update({k: v for k, v in rstats.items() if v})
    moved_rules = {f.get("rule_id") for f in rem + add}
    for cid in SELF_TRIGGERED:
        blocks, rules = CLASSES[cid]
        if (subs & blocks) or (moved_rules & rules):
            trig.add(cid)

    open_blocks, open_rules = set(), set()
    for t in trig:
        bl, rl = CLASSES[t]
        open_blocks |= bl
        open_rules |= rl
    if "components" in subs and not cbad:
        subs.discard("components")
    bad += [f"block {k}" for k in sorted(subs - open_blocks) if k.split(".")[0] not in FIXED_TOP]
    rail_leaves = {_leaf(n) for n in rail_set} | rail_set
    # a finding and its counterpart on the other side (same rule and detection / components)
    pair: dict[tuple, set[str]] = {}
    for f in rem + add:
        pair.setdefault(_ident(f), set()).update(_deep_strings(f))
    for f in rem + add:
        rule = f.get("rule_id")
        if rule in open_rules:
            continue
        names = pair.get(_ident(f), set())
        if a1_refs and names & a1_refs:
            stats["A1_finding_on_blank_or_dnp_value"] += 1
            continue
        if "PWR" in trig and ({_leaf(s) for s in names} | names) & rail_leaves:
            stats["PWR_finding_names_rail"] += 1
            continue
        bad.append(f"finding {rule} {str(f.get('summary', ''))[:60]}")
    if not trig and (subs or rem or add):
        bad.append("schematic movement without a trigger")
    return ("+".join(sorted(trig)) if not bad else None), bad, stats


# A4d (full-chain): pcb blocks and rules that follow the schematic's power nets
PCB_A4D_BLOCKS = frozenset({"power_net_resolution", "power_net_routing", "layer_transitions",
                            "return_path_continuity", "current_capacity", "thermal_pad_vias",
                            "statistics.power_nets", "net_classifications",
                            # copied out of current_capacity, present once the board has a power net
                            "board_thickness_mm"})
PCB_A4D_RULES = frozenset({"CC-DET", "CC-002"})


def _pcb_name_flips(a: dict, b: dict, subs: set[str], moved: list) -> set[str]:
    """Strings in the moved pcb blocks / findings that the two products' ``is_power_net_name`` read
    differently (the pcb analyzer classifies power nets by name)."""
    old, new = _netnames("a"), _netnames("b")
    names = set()
    for k in subs:
        names |= _deep_strings(_get(a, k)) | _deep_strings(_get(b, k))
    names |= _deep_strings(moved)
    return {n for n in names if len(n) < 64 and old.is_power_net_name(n, None) != new.is_power_net_name(n, None)}


def _pcb(a: dict, b: dict):
    """A4d: the power-net blocks and rules may move when a net name in them is re-read as power
    (ruling 62: both profiles) or, in full-chain, when the upstream schematic moved under PWR."""
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = Counter(f"{f.get('rule_id')}-" for f in rem)
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    flips = _pcb_name_flips(a, b, subs, rem + add)
    stats["pcb_net_names_reread"] += len(flips)
    pwr = bool(flips)
    for kind, da, db in _upstream(a, b) if not pwr else ():
        if kind == "schematic" and da is not None:
            lab = classify_unit("schematic", da, db)["label"]
            pwr = pwr or bool(lab and "PWR" in lab.split("+"))
    if pwr and not flips:
        stats["pcb_upstream_pwr"] += 1
    if not pwr:
        return None, ([f"pcb block {k}" for k in sorted(subs)][:10]
                      + [f"pcb finding {f.get('rule_id')}" for f in rem + add][:10]
                      + ["pcb movement without a re-read net name or an upstream PWR schematic move"]), stats
    bad = [f"pcb block {k}" for k in sorted(subs - PCB_A4D_BLOCKS)]
    bad += [f"pcb finding {f.get('rule_id')}" for f in rem + add if f.get("rule_id") not in PCB_A4D_RULES]
    return ("A4d" if not bad else None), bad, stats


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


def _derived_ok(doc: dict, *, full: bool) -> bool:
    fs = _findings(doc)
    if full and isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


# ---- upstream (chained analyzers), as in v30x_wave3 -------------------------------------------

def _slot_root(p: str) -> str:
    m = re.match(r"(.*?/(?:baseline|candidate))/(?:schematic|pcb)/", p)
    return m.group(1) if m else ""


_UP: OrderedDict = OrderedDict()
_DELTA_UNITS: dict[str, frozenset | None] = {}


def _delta_units(slot_root: str) -> frozenset | None:
    """Units with strict deltas, from ``strict_delta_units.txt`` beside the gate (one unit per line).

    The strict report itself is too large to load in every worker (1.5 GB for this round); without
    the list the upstream pair is compared directly, which gives the same answer."""
    gate = str(Path(slot_root).parent)
    if gate not in _DELTA_UNITS:
        try:
            lines = (Path(gate) / "strict_delta_units.txt").read_text(encoding="utf-8").splitlines()
            _DELTA_UNITS[gate] = frozenset(x for x in lines if x)
        except OSError:
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


# ---- unit classification ----------------------------------------------------------------------

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


def _labelled(kind: str):
    def pred(delta, a_doc, b_doc) -> bool:
        r = _cached(delta, a_doc, b_doc)
        if not (r and r["label"]):
            return False
        return (r["label"] == "D") == (kind == "D")
    pred.__name__ = f"labelled_{kind}"
    return pred


schematic = _labelled("S")
pcb_power_nets = _labelled("S")
downstream = _labelled("D")


# ---- adjudication summary ---------------------------------------------------------------------

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
