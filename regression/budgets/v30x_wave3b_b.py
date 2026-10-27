"""Budget predicates for product 3.0.x Wave 3b Part B (KiCad conformance: PCB reading, BOM tools,
writers, cross-checks), range 6c488c2 -> 0683d01.

Classes (handoff-wave3b-B.md "Budget classes"; files ``v30x-wave3b-b{,-full-chain}.json``). Every delta
is claimed per UNIT, as in Part A: ``classify_unit`` gives a unit a label (the ``+``-joined triggers in
commit order) or ``None`` (a residual).

Schematic: X1 only — ``components[].instance_path`` is added; with it removed, the two outputs are equal.

PCB triggers are read off the SOURCE board (``inputs.source_files[0]``), because the classes are keyed to
constructs, not to output shapes:

  P1   a copper layer in the layer table has a non-canonical name (KiCad 5 ``Top`` / ``Bottom`` /
       ``Inner1`` ...), or the output's copper layer names moved
  P1s  an SMD / connect pad sits on the other copper side from its footprint (``641096d``'s CP-001 side check
       reaches every board with one, not only KiCad 5 boards)
  P1h  the layer table carries the unquoted ``hide`` keyword (output ``layers[].alias`` "hide" -> null)
  P2   a polygon point list carries ``(arc ...)``;  P2d  a point list repeats a point back to back
  P3   a board graphic (``gr_*``) carries a non-zero net
  P4   a track carries a plural ``(layers ...)``
  P5   a pad is ``custom`` with primitives
  P6   board version < 20250210 with a zone fill, ``min_thickness`` > 0 and no ``(filled_areas_thickness no)``
  P7   the board has vias (tenting inherited from the setup; a pad's mask opening exposes a via)
  P8   a via without its own ``(drill ...)``, or with ``(drill 0)``
  P9   an arc track
  P10  an ``np_thru_hole`` pad on a copper layer with a net

Each trigger opens the blocks and rules its handoff row names (``P_BLOCKS`` / ``P_RULES``); a unit is
explained when every moved block and every moved finding's rule is opened by one of its triggers, or the
finding is rewritten at an unchanged per-rule count (echoed geometry, as in Part A).

Cross_analysis: X2 (``checks_run`` gains XV-004) on every unit; XV-001..004 / DA-001 findings move freely
(X3-X8); any other moved block or rule needs a moved, explained upstream pcb (``D``).
EMC / thermal: ``D`` only, keyed to a moved, explained upstream pcb (the schematic change is one additive
key no chained analyzer reads, so a schematic-only upstream move explains nothing).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

from regression.budgets.v30x_wave2 import _findings, _moved
from regression.budgets.v30x_wave3 import FIXED_TOP, _block_diffs, _derived_ok, _policy, _slot_root
from regression.field_compare import compare_strict

ORDER = ("X1", "P1", "P1s", "P1h", "P2", "P2d", "P4", "P3", "P5", "P6", "P8", "P7", "P9", "P10")

# every pcb block that reads layers, geometry or connectivity; P1 renames the copper layers everything is keyed by
_LAYERED = frozenset({
    "statistics", "layers", "setup", "tracks", "vias", "zones", "keepout_zones", "footprints", "ground_domains",
    "net_lengths", "power_net_routing", "placement_density", "layer_transitions", "decoupling_placement",
    "decoupling_proximity", "copper_presence_summary", "thermal_pad_scan", "thermal_pad_vias", "dfm_summary",
    "design_rule_compliance", "connectivity", "connectivity_graph", "return_path_continuity", "silkscreen",
    "board_outline", "component_groups", "design_intent", "assessments", "dimensions", "current_capacity",
    "trace_proximity", "via_analysis",
})
_ROUTING = frozenset({"connectivity", "statistics", "connectivity_graph", "net_lengths", "tracks",
                      "layer_transitions", "return_path_continuity", "power_net_routing", "assessments"})
P_BLOCKS = {
    "P1": _LAYERED,
    "P1s": frozenset({"copper_presence_summary"}),
    "P1h": frozenset({"layers"}),
    "P2": frozenset({"board_outline", "statistics", "dfm_summary", "placement_density", "design_intent", "zones",
                     "footprints", "keepout_zones", "copper_presence_summary", "assessments", "thermal_pad_scan",
                     "decoupling_placement", "connectivity_graph", "dimensions"}),
    "P3": _ROUTING,
    "P4": _ROUTING | {"copper_presence_summary"},
    "P5": frozenset({"connectivity_graph"}),
    "P6": frozenset({"zones", "copper_presence_summary", "connectivity_graph", "return_path_continuity",
                     "ground_domains", "assessments", "thermal_pad_scan"}),
    "P7": frozenset({"vias", "assessments"}),
    "P8": frozenset({"vias", "dfm_summary", "net_lengths", "statistics", "design_rule_compliance", "assessments",
                     "via_analysis"}),
    "P9": frozenset({"power_net_routing", "assessments"}),
    "P10": frozenset({"connectivity_graph"}),
}
_ANY = None  # P1: any pcb rule (side-aware rules follow the renamed layers)
P_RULES = {
    "P1": _ANY,
    "P1s": frozenset({"CP-001"}),
    "P1h": frozenset(),
    "P2": frozenset({"PM-002", "DFM-001", "DFM-002", "DFM-003", "DFM-004", "DFM-005", "CY-001", "CY-002",
                     "FD-001", "OR-001", "KO-001", "CP-001", "CP-002", "CP-003", "TV-001"}),
    "P3": frozenset({"RT-001"}),
    "P4": frozenset({"RT-001"}),
    "P5": frozenset(),
    "P6": frozenset({"CP-001", "CP-002", "CP-003", "TV-001"}),
    "P7": frozenset({"VP-001", "TV-001"}),
    "P8": frozenset({"DFM-001", "DFM-002", "TV-001"}),
    "P9": frozenset(),
    "P10": frozenset({"CP-003", "CP-001"}),
}

# the duplicate-point drop is P2's commit and opens P2's blocks and rules
P_BLOCKS["P2d"] = P_BLOCKS["P2"]
P_RULES["P2d"] = P_RULES["P2"]

XV_RULES = frozenset({"XV-001", "XV-002", "XV-003", "XV-004", "DA-001"})

_CANON_CU = re.compile(r"^(F\.Cu|B\.Cu|In\d+\.Cu)$")
_HEAD = re.compile(r"\(\s*([A-Za-z_][\w.]*)")
_LAYER_ROW = re.compile(r'\(\s*(\d+)\s+("(?:[^"\\]|\\.)*"|[^\s()"]+)\s+(signal|power|mixed|jumper|user)\b([^()]*)\)')
_PTS_ARC = re.compile(r"(?:\(pts|\(xy\s[^()]*\))\s*\(arc\s")
_DUP_XY = re.compile(r"\(xy\s+([-\d.e]+)\s+([-\d.e]+)\s*\)\s*\(xy\s+\1\s+\2\s*\)")
_NET_ID = re.compile(r'\(net\s+(?:(\d+)|"([^"]*)")')
_VERSION = re.compile(r"\(version\s+(\d+)")
_MIN_THICK = re.compile(r"\(min_thickness\s+([\d.]+)")
_FP_SIDE = re.compile(r'\(layer\s+"?([FB])\.Cu')
_PAD_CU = re.compile(r'\(layers\s([^()]*)\)')
_PAD_HEAD = re.compile(r'\(pad\s+(?:"(?:[^"\\]|\\.)*"|\S+)\s+(\w+)\s+(\w+)')


def _children(text: str, start: int, end: int):
    """(head, start, end) of every direct child list of the list spanning text[start:end]."""
    out, depth, i, in_str, cstart = [], 0, start, False, -1
    while i < end:
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 1
            elif ch == '"':
                in_str = False
        elif ch == '"' and (i == 0 or text[i - 1] in " \t\r\n("):
            in_str = True  # KiCad 5 writes unquoted tokens that contain a quote (0.96"_OLED)
        elif ch == "(":
            depth += 1
            if depth == 2:
                cstart = i
        elif ch == ")":
            if depth == 2 and cstart >= 0:
                m = _HEAD.match(text, cstart)
                out.append((m.group(1) if m else "", cstart, i + 1))
            depth -= 1
        i += 1
    return out


def _has_net(block: str) -> bool:
    for m in _NET_ID.finditer(block):
        if m.group(1) is not None and m.group(1) != "0":
            return True
        if m.group(2):
            return True
    return False


def scan_board(text: str) -> dict:
    """Construct counts per trigger for one board file (the classes' keys)."""
    c: Counter = Counter()
    top = _children(text, 0, len(text))
    ver = _VERSION.search(text[:2000])
    version = int(ver.group(1)) if ver else 0
    for head, s, e in top:
        blk = text[s:e]
        if head == "layers":
            for m in _LAYER_ROW.finditer(blk):
                name, kind, rest = m.group(2).strip('"'), m.group(3), m.group(4)
                if kind != "user" and not _CANON_CU.match(name):
                    c["P1"] += 1
                if re.search(r"\bhide\b", rest):
                    c["P1h"] += 1
        elif head.startswith("gr_") and _has_net(blk):
            c["P3"] += 1
        elif head in ("segment", "arc") and "(layers " in blk:
            c["P4"] += 1
        if head == "arc" and "(net " in blk:
            c["P9"] += 1
        if head == "via":
            c["P7"] += 1
            if "(drill " not in blk or re.search(r"\(drill\s+0(?:\.0*)?\)", blk):
                c["P8"] += 1
        if head == "zone" and 0 < version < 20250210 and "(filled_areas_thickness no)" not in blk:
            mt = _MIN_THICK.search(blk)
            if mt and float(mt.group(1)) > 0 and "(filled_polygon" in blk:
                c["P6"] += 1
        if head in ("footprint", "module"):
            side = _FP_SIDE.search(text, s, min(e, s + 600))
            for ph, ps, pe in _children(text, s, e):
                if ph != "pad":
                    continue
                pad = text[ps:pe]
                hm = _PAD_HEAD.match(pad)
                ptype, pshape = (hm.group(1), hm.group(2)) if hm else ("", "")
                lay = _PAD_CU.search(pad)
                if side and ptype in ("smd", "connect") and lay:
                    own, other = f"{side.group(1)}.Cu", ("B.Cu" if side.group(1) == "F" else "F.Cu")
                    if other in lay.group(1) and own not in lay.group(1):
                        c["P1s"] += 1
                if pshape == "custom" and "(primitives" in pad:
                    c["P5"] += 1
                if ptype == "np_thru_hole" and re.search(r'\(layers[^)]*(\*|[FB]|In\d+)\.Cu', pad) and _has_net(pad):
                    c["P10"] += 1
    c["P2"] = len(_PTS_ARC.findall(text))
    c["P2d"] = len(_DUP_XY.findall(text))
    return {k: v for k, v in c.items() if v}


_SCAN: OrderedDict = OrderedDict()


def _board_constructs(doc: dict) -> dict | None:
    src = ((doc.get("inputs") or {}).get("source_files") or [None])[0]
    if not isinstance(src, str):
        return None
    hit = _SCAN.get(src)
    if hit is None:
        try:
            hit = scan_board(Path(src).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            return None
        _SCAN[src] = hit
        while len(_SCAN) > 64:
            _SCAN.popitem(last=False)
    return hit


# ---- schematic ------------------------------------------------------------------------------

def _strip_instance_path(doc: dict) -> dict:
    out = dict(doc)
    out["components"] = [{k: v for k, v in c.items() if k != "instance_path"} if isinstance(c, dict) else c
                         for c in doc.get("components") or []]
    return out


def _schematic(a, b):
    stats: Counter = Counter()
    n = sum(1 for c in b.get("components") or [] if isinstance(c, dict) and "instance_path" in c)
    stats["X1_paths"] = n
    if any(isinstance(c, dict) and "instance_path" in c for c in a.get("components") or []):
        return None, ["instance_path already on the baseline"], stats
    bad = [f"block {k}" for k in sorted(_block_diffs(_strip_instance_path(a), _strip_instance_path(b)))]
    if _moved(a, b) != ([], []):
        bad.append("schematic findings moved")
    if not n:
        bad.append("schematic movement without instance_path")
    return (None if bad else "X1"), bad, stats


# ---- pcb ------------------------------------------------------------------------------------

def _copper_names(doc: dict) -> list:
    return [x.get("name") for x in doc.get("layers") or [] if isinstance(x, dict)
            and str(x.get("type")) in ("signal", "power", "mixed", "jumper")]


def _pcb(a, b):
    stats: Counter = Counter()
    cons = _board_constructs(b) or _board_constructs(a)
    if cons is None:
        return None, ["pcb source board unreadable"], stats
    trig = set(cons)
    if _copper_names(a) != _copper_names(b):
        trig.add("P1")
    if any(isinstance(x, dict) and x.get("alias") == "hide" for x in a.get("layers") or []):
        trig.add("P1h")
    for t in trig:
        stats[f"{t}_constructs"] += cons.get(t, 0)
    blocks = _block_diffs(a, b) - {"diagnostics"}
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    bad = [f"block {k}" for k in sorted(blocks & FIXED_TOP)]
    used = trig & set(P_BLOCKS)
    allowed = set().union(*(P_BLOCKS[t] for t in used)) if used else set()
    bad += [f"block {k}" for k in sorted(blocks - allowed - FIXED_TOP)]
    any_rule = any(P_RULES[t] is _ANY for t in used)
    rules = set().union(*(P_RULES[t] or set() for t in used)) if used else set()
    net = Counter(f.get("rule_id") for f in add)
    net.subtract(Counter(f.get("rule_id") for f in rem))
    for f in rem + add:
        r = f.get("rule_id")
        if any_rule or r in rules or net[r] == 0:
            continue
        bad.append(f"finding {r} {str(f.get('summary', ''))[:60]}")
    if not (blocks or rem or add):
        return _label(_explaining(trig, set(), []), bad), bad, stats
    return _label(_explaining(trig, blocks, rem + add), bad), bad, stats


def _explaining(trig: set[str], blocks: set[str], moved: list) -> set[str]:
    """The triggers that open at least one moved block or rule (the rest are present but idle)."""
    rules = {f.get("rule_id") for f in moved}
    out = set()
    for t in trig:
        if t not in P_BLOCKS:
            continue
        if blocks & P_BLOCKS[t] or (P_RULES[t] is _ANY and rules) or (P_RULES[t] and rules & P_RULES[t]):
            out.add(t)
    return out or set(trig)


def _label(trig: set[str], bad: list) -> str | None:
    if bad or not trig:
        return None
    return "+".join(x for x in ORDER if x in trig)


# ---- upstream (chained analyzers) ----------------------------------------------------------

_UP: OrderedDict = OrderedDict()


def _upstream(a_doc: dict, b_doc: dict) -> dict[str, tuple[bool, dict | None, dict | None]]:
    out = {}
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
        out[kind] = hit
    return out


def _pcb_upstream_label(up: dict, reasons: list) -> str | None:
    hit = up.get("pcb")
    if not hit or not hit[0]:
        return None
    if hit[1] is None:
        reasons.append("upstream pcb unreadable")
        return None
    r = classify_unit("pcb", hit[1], hit[2])
    if r["label"] is None:
        reasons.append("upstream pcb unexplained")
    return r["label"]


def _cross(a, b):
    stats: Counter = Counter()
    up = _upstream(a, b)
    reasons: list[str] = []
    trig = set()
    blocks = _block_diffs(a, b) - {"diagnostics"}
    if "checks_run" in blocks:
        ca, cb = a.get("checks_run") or [], b.get("checks_run") or []

        def _xv4(x):
            return (x.get("check") if isinstance(x, dict) else x) == "XV-004"

        def _mask(rows):
            # the XV / DA rows carry their own finding counts, which move with X3-X8
            return [{k: v for k, v in x.items() if k not in ("findings", "items_examined")}
                    if isinstance(x, dict) and str(x.get("check", "")).startswith(("XV-", "DA-")) else x
                    for x in rows if not _xv4(x)]

        if _mask(cb) == _mask(ca) and any(_xv4(x) for x in cb) and not any(_xv4(x) for x in ca):
            trig.add("X2")
            blocks.discard("checks_run")
    rem, add = _moved(a, b)
    stats.update(Counter(f"{f.get('rule_id')}-" for f in rem))
    stats.update(Counter(f"{f.get('rule_id')}+" for f in add))
    other = [f for f in rem + add if f.get("rule_id") not in XV_RULES]
    if any(f.get("rule_id") in XV_RULES for f in rem + add):
        trig.add("X")
    if blocks or other:
        lab = _pcb_upstream_label(up, reasons)
        if lab is None and not reasons:
            reasons.append("cross movement outside XV/DA with identical upstream pcb: "
                           + ", ".join(sorted(blocks)[:4] + sorted({str(f.get('rule_id')) for f in other})[:4]))
        else:
            trig.add("D")
            stats["D<" + str(lab)] += 1
    if not trig and not reasons:
        reasons.append("cross movement without a trigger")
    order = ("X2", "X", "D")
    return (None if reasons else "+".join(t for t in order if t in trig)), reasons, stats


def _chained(a, b):
    up = _upstream(a, b)
    reasons: list[str] = []
    lab = _pcb_upstream_label(up, reasons)
    if lab is None and not reasons:
        reasons.append("emc/thermal movement with identical upstream pcb")
    return (None if reasons else "D"), reasons, Counter({"D<" + str(lab): 1})


_CLASSIFIERS = {"schematic": _schematic, "pcb": _pcb, "cross_analysis": _cross, "emc": _chained,
                "thermal": _chained}
_FULL_DERIVED = {"schematic", "pcb", "gerber", "cross_analysis"}


# ---- unit classification --------------------------------------------------------------------

def classify_unit(analyzer: str, a_doc: dict, b_doc: dict) -> dict:
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
cross = _labelled(("cross_analysis",))
downstream = _labelled(("emc", "thermal"))


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
