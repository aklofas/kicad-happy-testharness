"""Budget predicates for product 3.0.x Waves 9b + 9c (v3.0.1), range 238e0b4 -> 8c42799
(baseline clone 389fbd5 = 238e0b4 + docs/CI only; 9b = schematic / PCB / Gerber, 9c = EMC / SPICE).

Every delta is claimed per UNIT: ``classify_unit`` gives a unit one label (the sorted ``+``-joined
set of classes that moved it) and every delta of that unit is explained, or the unit is a residual
(label ``None``). Classes follow the handoff's commit map; the per-class magnitudes are tallied in
``stats`` and compared with the handoff by hand.

Gerber:
  G-ERR   a file that is not a Gerber stays listed as an error record (``error`` key, one
          "not a Gerber file" diagnostic); layer_count / completeness / alignment follow (9b T18).
  G-SKIP  dot files, ``.git*``, ``._*`` and ``:Zone.Identifier`` files leave ``gerbers[]``;
          ``statistics.gerber_files`` and zip ``age_delta_hours`` / ``vs_loose_files`` follow (9b T18).
  G-JOB   a job file that does not parse adds a JSON diagnostic (9b T18).
  G-EXT   D02 moves do not grow copper extents: ``alignment.layer_extents`` only shrink;
          ``aligned`` may turn True and GR-002 findings leave (9b T17).
  GR-001 findings are added only with G-ERR (a required layer turned into an error record).

PCB:
  DEC     ``decoupling_placement`` / ``decoupling_proximity``: caps on the IC's signal-pin nets leave;
          no IC or cap is added (9b T15).
  GND     ``ground_domains`` move under the shared ground-name rule (9b T14).
  KO      KO-001 findings are only removed, and every KO-001 drops ``keepout_allowed_net`` (9b T10).
  RT      RT-001 / BV-001 findings only removed (9b T11).
  TE      TE-001 replaced in place (touch pads are not test points, 9b T13).

Thermal and cross_analysis: D only, from a labelled upstream schematic or PCB move.

``python -m regression.budgets.v30x_wave9bc GATE_DIR UNIT`` classifies one unit.
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
from regression.budgets.v30x_wave5 import _upstream_paths

VOLATILE_TOP = frozenset({"inputs", "capability_mode_ref", "elapsed_s"})
DERIVED_TOP = frozenset({"summary", "trust_summary", "audience_summary"})


def _canon(f: Any) -> str:
    g = dict(f) if isinstance(f, dict) else {"_": f}
    g.pop("finding_id", None)
    return json.dumps(g, sort_keys=True, default=str)


def _moved(a: dict, b: dict, drop: tuple = ()) -> tuple[list, list]:
    def canon(f):
        if drop and isinstance(f, dict):
            f = {k: v for k, v in f.items() if k not in drop}
        return _canon(f)
    ca = Counter(canon(f) for f in _findings(a))
    cb = Counter(canon(f) for f in _findings(b))
    return [json.loads(k) for k in (ca - cb).elements()], [json.loads(k) for k in (cb - ca).elements()]


def _sub_diffs(a: dict, b: dict) -> set[str]:
    return {k for k in (set(a) | set(b)) - VOLATILE_TOP - DERIVED_TOP - {"findings"}
            if a.get(k) != b.get(k) or (k in a) != (k in b)}


def _same_body(a: dict, b: dict) -> bool:
    return ({k: v for k, v in a.items() if k not in VOLATILE_TOP}
            == {k: v for k, v in b.items() if k not in VOLATILE_TOP})


_UP: OrderedDict = OrderedDict()


def _upstream_label(a: dict, b: dict, kind: str) -> tuple[bool, str | None] | None:
    """(upstream moved, its label) for the *kind* artefact a chained unit read; None without one.

    Cached per path pair: a schematic feeds its EMC, thermal and cross units."""
    pa, pb = _upstream_paths(a, b, kind)
    if not pa or not pb:
        return None
    hit = _UP.get((pa, pb))
    if hit is None:
        try:
            da = json.loads(Path(pa).read_text(encoding="utf-8"))
            db = json.loads(Path(pb).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            hit = (True, None)
        else:
            hit = (False, None) if _same_body(da, db) else (True, classify_unit(kind, da, db)["label"])
        _UP[(pa, pb)] = hit
        while len(_UP) > 64:
            _UP.popitem(last=False)
    return hit


def _derived_ok(doc: dict, *, full: bool) -> bool:
    fs = _findings(doc)
    if full and isinstance(doc.get("summary"), dict) and doc["summary"] != expected_summary(fs, doc["summary"]):
        return False
    if isinstance(doc.get("trust_summary"), dict) and doc["trust_summary"] != expected_trust_summary(fs, doc["trust_summary"]):
        return False
    if "audience_summary" in doc and doc["audience_summary"] != expected_audience_summary(fs):
        return False
    return True


def _rule_stats(rem: list, add: list) -> Counter:
    s = Counter(f"{f.get('rule_id')}-" for f in rem)
    s.update(Counter(f"{f.get('rule_id')}+" for f in add))
    return s


def _verdict(trig: set, bad: list, stats: Counter, what: str):
    if bad:
        return None, bad, stats
    return ("+".join(sorted(trig)) if trig else None), ([] if trig else [f"{what} movement without a trigger"]), stats


# ---- schematic ------------------------------------------------------------------------------------

SCH_RAW = ("labels", "power_symbols", "no_connects", "text_annotations")
NC_PIN_TYPES = frozenset({"no_connect", "unconnected"})  # KiCad 6+ / legacy .sch
# Findings the 9b schematic fixes move: NC isolation (T4), regulator suffix voltages (T5), net ties
# (T6), supply rails recognised by their pins and bridge outputs (T8), load switches (T9), VM-001
# (T3), and the knock-ons of those rails (pull-ups to a recognised rail, RF / bridge detectors,
# isolation domains).
SCH_RULES = frozenset({
    "DO-DET", "DC-DET", "PP-001", "RC-DET", "LC-DET", "EP-AUD", "PU-001", "PR-DET", "RS-001", "RS-003",
    "CG-AUD", "PP-DET", "PD-DET", "IL-DET", "PR-001", "VM-001", "NT-001", "IB-DET", "PS-001", "VD-001",
    "VD-004", "RM-DET", "TR-DET", "BR-DET", "LS-DET", "MI-DET", "LA-AUD", "AD-DET",
})
SCH_BLOCKS = frozenset({
    "nets", "components", "statistics", "design_analysis", "subcircuits", "pdn_impedance", "test_coverage",
    "power_budget", "rail_voltages", "power_sequencing_validation", "power_sequencing", "sleep_current_audit",
    "ic_pin_analysis", "transistor_pin_analysis", "protocol_compliance", "net_classifications",
    "connectivity_issues", "inrush_analysis", "ground_domains", "pwr_flag_warnings", "simulation_readiness",
})


def _pin_groups(doc: dict, *, split_nc: bool) -> Counter:
    """Nets as pin multisets, names ignored (unannotated ``U?`` refs repeat, ``__unnamed_N`` renumber).

    With *split_nc* every NC-typed pin is taken out of its net into a net of its own."""
    def key(ps):
        return tuple(sorted(Counter((p.get("component"), p.get("pin_number"), p.get("pin_type"))
                                    for p in ps).items()))
    out = Counter()
    for n in (doc.get("nets") or {}).values():
        ps = [p for p in n.get("pins") or [] if isinstance(p, dict)] if isinstance(n, dict) else []
        if split_nc:
            keep = [p for p in ps if p.get("pin_type") not in NC_PIN_TYPES]
            if keep:
                out[key(keep)] += 1
            for p in ps:
                if p.get("pin_type") in NC_PIN_TYPES:
                    out[key([p])] += 1
        elif ps:
            out[key(ps)] += 1
    return out


def _named_nets_ok(a: dict, b: dict) -> bool:
    """A net on both sides keeps every field but its pins, no_connect flag and point count."""
    na, nb = a.get("nets") or {}, b.get("nets") or {}
    skip = ("pins", "no_connect", "point_count")
    return all({k: v for k, v in na[n].items() if k not in skip} == {k: v for k, v in nb[n].items() if k not in skip}
               for n in set(na) & set(nb) if not n.startswith("__unnamed") and isinstance(na[n], dict)
               and isinstance(nb[n], dict))


def _schematic(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    for k in SCH_RAW:
        if a.get(k) != b.get(k):
            bad.append(f"raw list {k} changed")
    strip = lambda cs: [json.dumps({k: v for k, v in c.items() if k != "pin_nets"}, sort_keys=True, default=str)  # noqa: E731
                        for c in cs or [] if isinstance(c, dict)]
    if strip(a.get("components")) != strip(b.get("components")):
        bad.append("components changed beyond pin_nets")
    if "nets" in subs:
        ga, gb = _pin_groups(a, split_nc=False), _pin_groups(b, split_nc=False)
        if _pin_groups(a, split_nc=True) == gb:
            if ga != gb or set(a.get("nets") or {}) != set(b.get("nets") or {}):
                # an NC pin alone on a labelled net also moves to a net of its own
                trig.add("NC")
                stats["nc pins isolated"] += sum((gb - ga).values())
        elif ga != gb:
            bad.append("connectivity changed beyond NC-typed pins leaving their nets")
        if not _named_nets_ok(a, b):
            bad.append("net fields beyond pins / no_connect / point_count")
    if "statistics" in subs:
        sa, sb = a.get("statistics") or {}, b.get("statistics") or {}
        if {k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)} - {"total_nets"} or "NC" not in trig:
            bad.append("statistics beyond total_nets under NC isolation")
    if "missing_info" in subs:
        ma, mb = a.get("missing_info") or {}, b.get("missing_info") or {}
        if {k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k)} - {"heuristic_vref"}:
            bad.append("missing_info beyond heuristic_vref")
    bad += [f"block {k}" for k in sorted(subs - SCH_BLOCKS - set(SCH_RAW) - {"missing_info"})]
    # Any detector may rewrite a finding in place (count unchanged) when a pin, rail or regulator
    # estimate it reads moved; only the rules above may gain or lose findings.
    counts = Counter(f.get("rule_id") for f in add)
    counts.subtract(Counter(f.get("rule_id") for f in rem))
    moved_rules = {r for r, n in counts.items() if n}
    if {f.get("rule_id") for f in rem + add} - moved_rules:
        trig.add("F")
    if moved_rules - SCH_RULES:
        bad.append(f"findings outside the 9b schematic rules: {sorted(map(str, moved_rules - SCH_RULES))}")
    elif moved_rules:
        trig.add("F")
    if subs - {"nets", "components", "statistics"} and not trig:
        trig.add("B")  # system analyses moved by a rail / regulator estimate without a finding change
    return _verdict(trig, bad, stats, "schematic")


# ---- gerber ---------------------------------------------------------------------------------------

NOT_GERBER = "not a Gerber file"


def _skipped_name(name: str) -> bool:
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    return base.startswith(".") or ":Zone.Identifier" in name


def _gerber(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    ga = {g.get("filename"): g for g in a.get("gerbers") or [] if isinstance(g, dict)}
    gb = {g.get("filename"): g for g in b.get("gerbers") or [] if isinstance(g, dict)}
    for name in set(ga) | set(gb):
        x, y = ga.get(name), gb.get(name)
        if x == y:
            continue
        if y is None and _skipped_name(str(name)):
            trig.add("G-SKIP")
            stats["file skipped"] += 1
        elif x is not None and y is not None and "error" in y:
            trig.add("G-ERR")
            stats["error record"] += 1
        else:
            bad.append(f"gerbers[{name}] beyond skipped files and error records")
    if "gerbers" in subs and not trig and not bad:
        bad.append("gerbers order changed")
    da, db = list(a.get("diagnostics") or []), list(b.get("diagnostics") or [])
    if da != db:
        new = [d for d in db if d not in da]
        if any(d not in db for d in da):
            bad.append("diagnostics removed")
        for d in new:
            msg = json.dumps(d)
            if NOT_GERBER in msg:
                stats["not-a-gerber diagnostic"] += 1
            elif "Expecting" in msg or "JSONDecodeError" in msg:
                trig.add("G-JOB")
                stats["job diagnostic"] += 1
            else:
                bad.append("diagnostic beyond not-a-gerber / job JSON")
    if "statistics" in subs:
        sa, sb = a.get("statistics") or {}, b.get("statistics") or {}
        moved = {k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k)}
        if moved - {"gerber_files"} or not trig & {"G-SKIP", "G-ERR"}:
            bad.append(f"statistics {sorted(moved)}")
    if "zip_archives" in subs:
        za = {z.get("filename"): z for z in a.get("zip_archives") or []}
        zb = {z.get("filename"): z for z in b.get("zip_archives") or []}
        keys = {k for f in set(za) | set(zb) for k in set(za.get(f, {})) | set(zb.get(f, {}))
                if za.get(f, {}).get(k) != zb.get(f, {}).get(k)}
        if set(za) != set(zb) or keys - {"age_delta_hours", "vs_loose_files"} or "G-SKIP" not in trig:
            bad.append(f"zip_archives {sorted(keys)}")
    if "alignment" in subs:
        ea = (a.get("alignment") or {}).get("layer_extents") or {}
        eb = (b.get("alignment") or {}).get("layer_extents") or {}
        # A layer whose only extent came from a skipped or error-record file read 0 x 0; it may grow
        # to the real file's extent once that file leaves.
        zero_ok = bool(trig & {"G-ERR", "G-SKIP"})
        grew = [l for l in set(ea) & set(eb) if isinstance(ea[l], dict) and isinstance(eb[l], dict)
                and any((eb[l].get(k) or 0) > (ea[l].get(k) or 0) + 1e-9 for k in ("width", "height"))
                and not (zero_ok and not (ea[l].get("width") or ea[l].get("height")))]
        if zero_ok:
            stats["zero extent restored"] += sum(1 for l in set(ea) & set(eb) if isinstance(ea[l], dict)
                                                 and not (ea[l].get("width") or ea[l].get("height"))
                                                 and eb[l] != ea[l])
        added_layers = set(eb) - set(ea)
        if grew or (added_layers and "G-ERR" not in trig):
            bad.append(f"alignment extents grew on {sorted(grew)[:3]} / layers added {sorted(added_layers)[:3]}")
        elif ea != eb:
            trig.add("G-EXT")
            stats["extents moved"] += 1
        elif not trig & {"G-ERR", "G-SKIP"}:
            bad.append("alignment moved without shrinking extents or an error record")
    for k in ("layer_count", "completeness"):
        if k in subs and not trig & {"G-ERR", "G-SKIP"}:
            bad.append(f"{k} without an error record or skipped file")
    bad += [f"block {k}" for k in sorted(subs - {"gerbers", "diagnostics", "statistics", "zip_archives",
                                                  "alignment", "layer_count", "completeness"})]
    for f in add:
        if f.get("rule_id") != "GR-001" or not trig & {"G-ERR", "G-SKIP"}:
            bad.append(f"finding {f.get('rule_id')} added")
    for f in rem:
        if f.get("rule_id") not in ("GR-002", "GR-001"):
            bad.append(f"finding {f.get('rule_id')} removed")
    if any(f.get("rule_id") == "GR-002" for f in rem):
        trig.add("G-EXT")
    return _verdict(trig, bad, stats, "gerber")


# ---- pcb ------------------------------------------------------------------------------------------

def _placement(entries: Any) -> tuple[Counter, dict] | None:
    """(entries per IC, union of nearby caps per IC); a panel file can repeat an IC reference."""
    if entries is None:
        return Counter(), {}
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        return None
    n, caps = Counter(), {}
    for e in entries:
        n[e.get("ic")] += 1
        caps.setdefault(e.get("ic"), set()).update(
            c.get("cap") if isinstance(c, dict) else c for c in e.get("nearby_caps") or [])
    return n, caps


def _decoupling_ok(a: dict, b: dict, stats: Counter) -> bool:
    """No IC or cap is added; caps only leave (and an IC whose caps all left may leave)."""
    if a.get("decoupling_placement") != b.get("decoupling_placement"):
        pa, pb = _placement(a.get("decoupling_placement")), _placement(b.get("decoupling_placement"))
        if pa is None or pb is None or pb[0] - pa[0]:
            return False
        if any(not caps <= pa[1].get(ic, set()) for ic, caps in pb[1].items()):
            return False
        stats["placement caps removed"] += sum(len(c - pb[1].get(ic, set())) for ic, c in pa[1].items())
        stats["placement ics removed"] += sum((pa[0] - pb[0]).values())
    if a.get("decoupling_proximity") != b.get("decoupling_proximity"):
        xa, xb = a.get("decoupling_proximity") or [], b.get("decoupling_proximity") or []
        if not isinstance(xa, list) or not isinstance(xb, list):
            return False
        # A row is an (IC, cap) pair; its shared_nets may only lose the IC's signal-pin nets.
        def rows(xs):
            out = {}
            for r in xs:
                if not isinstance(r, dict):
                    return None
                k = json.dumps({k: v for k, v in r.items() if k != "shared_nets"}, sort_keys=True, default=str)
                out.setdefault(k, []).append(set(r.get("shared_nets") or []))
            return out
        ra, rb = rows(xa), rows(xb)
        if ra is None or rb is None:
            return False
        for k, nets in rb.items():
            pool = list(ra.get(k, []))
            for s in nets:
                hit = next((i for i, p in enumerate(pool) if s <= p), None)
                if hit is None:
                    return False
                if s != pool[hit]:
                    stats["proximity shared_nets narrowed"] += 1
                pool.pop(hit)
        stats["proximity rows removed"] += sum(len(v) for v in ra.values()) - sum(len(v) for v in rb.values())
    return True


# KiCad names a net after a pad (``Net-(U1-GND)``, ``unconnected-(U1-GND-Pad3)``), optionally under a
# sheet path or a panel prefix (``Board_3-``).
PAD_NAMED = re.compile(r"^(?:.*[/-])?(?:unconnected-|Net-)\(")
ZERO_VOLT_OR_BAT_NEG = re.compile(r"(?:^|/)(?:0V\w*|\w*BAT\w*-|BATTERY-|Battery-)$", re.I)


def _ground_domains_ok(a: dict, b: dict, stats: Counter) -> bool:
    """Domains on both sides are unchanged; pad-named domains leave, 0V / battery-negative ones arrive."""
    ga, gb = a.get("ground_domains") or {}, b.get("ground_domains") or {}
    if not isinstance(ga, dict) or not isinstance(gb, dict):
        return False
    if (set(ga) | set(gb)) - {"domains", "domain_count", "multi_domain_components"}:
        return False
    da = {d.get("net"): d for d in ga.get("domains") or []}
    db = {d.get("net"): d for d in gb.get("domains") or []}
    if any(da[n] != db[n] for n in set(da) & set(db)):
        return False
    gone, new = set(da) - set(db), set(db) - set(da)
    if not all(PAD_NAMED.match(str(n)) for n in gone) or not all(ZERO_VOLT_OR_BAT_NEG.search(str(n)) for n in new):
        return False
    if gb.get("domain_count") != len(db):
        return False
    stats["ground domains removed"] += len(gone)
    stats["ground domains added"] += len(new)
    return True


def _pcb(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b, drop=("keepout_allowed_net",))
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    if subs & {"decoupling_placement", "decoupling_proximity"}:
        if _decoupling_ok(a, b, stats):
            trig.add("DEC")
        else:
            bad.append("decoupling beyond caps leaving")
    if "ground_domains" in subs:
        if _ground_domains_ok(a, b, stats):
            trig.add("GND")
        else:
            bad.append("ground_domains beyond pad-named domains leaving and 0V / battery-negative domains arriving")
    bad += [f"block {k}" for k in sorted(subs - {"decoupling_placement", "decoupling_proximity", "ground_domains"})]
    ko_b = [f for f in _findings(b) if f.get("rule_id") == "KO-001"]
    if any("keepout_allowed_net" in f for f in ko_b):
        bad.append("KO-001 still carries keepout_allowed_net")
    if any(f.get("rule_id") == "KO-001" for f in _findings(a)) and not ko_b == [f for f in _findings(a) if f.get("rule_id") == "KO-001"]:
        trig.add("KO")
    te_rem = sum(1 for f in rem if f.get("rule_id") == "TE-001")
    te_add = sum(1 for f in add if f.get("rule_id") == "TE-001")
    if te_rem or te_add:
        if te_rem == te_add:
            trig.add("TE")
        else:
            bad.append("TE-001 count changed")
    for f in rem:
        rid = f.get("rule_id")
        if rid == "KO-001":
            trig.add("KO")
        elif rid in ("RT-001", "BV-001"):
            trig.add("RT")
        elif rid != "TE-001":
            bad.append(f"finding {rid} removed")
    for f in add:
        if f.get("rule_id") != "TE-001":
            bad.append(f"finding {f.get('rule_id')} added")
    return _verdict(trig, bad, stats, "pcb")


# ---- emc ------------------------------------------------------------------------------------------

# 9c rules (T2 DC-002, T3 ES-001/002, T4 GP-001, T5 SW-002, T6 DP-003/RP-001, T7 SU-001/002, CK-001,
# DP-004, T8 IO-001/002, BE-001, RP-001, T9 SW-003) and the EMC readers of 9b PCB blocks (T14 GP-005,
# T15 DC-001/002/003).
EMC_RULES = frozenset({
    "DC-001", "DC-002", "DC-003", "ES-001", "ES-002", "GP-001", "GP-005", "SW-002", "SW-003", "DP-003",
    "SU-001", "SU-002", "CK-001", "DP-004", "IO-001", "IO-002", "BE-001", "RP-001",
})
EMC_FOLLOW = frozenset({"category_summary", "regulatory_coverage", "per_net_scores", "test_plan"})


def _upstream_moved(a: dict, b: dict) -> tuple[bool, list]:
    """(an upstream schematic or PCB moved and is labelled, reasons when one moved unexplained)."""
    moved, reasons = False, []
    for kind in ("schematic", "pcb"):
        up = _upstream_label(a, b, kind)
        if up is None or not up[0]:
            continue
        moved = True
        if up[1] is None:
            reasons.append(f"upstream {kind} unexplained")
    return moved, reasons


def _emc(a: dict, b: dict):
    subs = _sub_diffs(a, b)
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    bad, trig = [], set()
    rules = {f.get("rule_id") for f in rem + add}
    up = None
    if rules & EMC_RULES:
        trig.add("E")
    other = rules - EMC_RULES
    if other or "board_info" in subs:
        up = _upstream_moved(a, b)
        if not up[0]:
            bad.append(f"rules {sorted(map(str, other))} / board_info without an upstream move")
        bad += up[1]
        if up[0] and not up[1]:
            trig.add("D")
    if "board_info" in subs:
        ba, bb = a.get("board_info") or {}, b.get("board_info") or {}
        if {k for k in set(ba) | set(bb) if ba.get(k) != bb.get(k)} - {"total_nets"}:
            bad.append("board_info beyond total_nets")
    bad += [f"block {k}" for k in sorted(subs - EMC_FOLLOW - {"board_info"})]
    if subs & EMC_FOLLOW and not trig:
        bad.append("EMC roll-ups moved without a finding move")
    sa, sb = (a.get("summary") or {}).get("emc_risk_score"), (b.get("summary") or {}).get("emc_risk_score")
    if isinstance(sa, (int, float)) and isinstance(sb, (int, float)) and sa != sb:
        stats["score up" if sb > sa else "score down"] += 1
        stats["score |d|>10"] += abs(sb - sa) > 10
    return _verdict(trig, bad, stats, "emc")


# ---- unit classification --------------------------------------------------------------------------

_CLASSIFIERS = {"schematic": _schematic, "gerber": _gerber, "pcb": _pcb, "emc": _emc}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


def _downstream(analyzer: str, a: dict, b: dict) -> dict:
    rem, add = _moved(a, b)
    stats = _rule_stats(rem, add)
    for kind in ("schematic", "pcb"):
        up = _upstream_label(a, b, kind)
        if up is None or not up[0]:
            continue
        if up[1] is None:
            return {"label": None, "reasons": [f"upstream {kind} unexplained"], "stats": stats}
        return {"label": "D", "reasons": [], "stats": stats}
    return {"label": None, "reasons": [f"{analyzer} movement without an upstream move"], "stats": stats}


def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
    if analyzer in ("thermal", "cross_analysis"):
        r = _downstream(analyzer, a_doc, b_doc)
    else:
        clf = _CLASSIFIERS.get(analyzer)
        if clf is None:
            return {"label": None, "reasons": [f"no class for analyzer {analyzer}"], "stats": Counter()}
        label, reasons, stats = clf(a_doc, b_doc)
        r = {"label": label, "reasons": reasons, "stats": stats}
    full = analyzer in _FULL_DERIVED
    reasons = list(r["reasons"])
    if not _derived_ok(a_doc, full=full):
        reasons.append("a: derived blocks not from findings")
    if not _derived_ok(b_doc, full=full):
        reasons.append("b: derived blocks not from findings")
    return {"label": r["label"] if not reasons else None, "reasons": reasons, "stats": r["stats"]}


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


def _labelled(analyzers: tuple[str, ...]):
    def pred(delta, a_doc, b_doc) -> bool:
        if delta.analyzer not in analyzers:
            return False
        r = _cached(delta, a_doc, b_doc)
        return bool(r and r["label"])
    pred.__name__ = "labelled_" + "_".join(analyzers)
    return pred


schematic = _labelled(("schematic",))
pcb = _labelled(("pcb",))
gerber = _labelled(("gerber",))
emc = _labelled(("emc",))
downstream = _labelled(("thermal", "cross_analysis"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate_dir", type=Path)
    ap.add_argument("unit", help="one unit (<analyzer>/<owner>/<repo>/<file>) to classify")
    args = ap.parse_args(argv)
    a = json.loads((args.gate_dir / "baseline" / args.unit / "snap.json").read_text(encoding="utf-8"))
    b = json.loads((args.gate_dir / "candidate" / args.unit / "snap.json").read_text(encoding="utf-8"))
    r = classify_unit(args.unit.split("/", 1)[0], a, b)
    print(json.dumps({"label": r["label"], "reasons": r["reasons"], "stats": dict(r["stats"])}, indent=1))
    return 0 if r["label"] else 1


if __name__ == "__main__":
    sys.exit(main())
