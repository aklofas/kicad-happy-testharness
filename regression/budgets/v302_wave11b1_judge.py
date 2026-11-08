"""Per-unit budget verdict for the v3.0.2 Wave 11b-1 gate (product 727d0ab3..f53d107e), over the v302_wave11b1_features.py census.

A moved unit is CLAIMED when every movement falls inside the merged budget's mechanisms
(budget-wave11b-1.json, 100 classes + restatements), checked per unit:

schematic
  - findings: every rule that gains or loses a finding (content pairing, finding_id ignored) is in
    SCH_RULES; rules the budget only rewrites in place (INPLACE) keep their count; rules the budget
    only removes or rewrites (SHRINK) never gain on net;
  - finding_id-only renumbering is allowed (PU-001 #N suffix, DO-DET uN#1, kh690 renamed nets);
  - components: only the fields in COMP_FIELDS change, refs unchanged (except the backslash-sheet unit);
  - nets: renamed with identical pin groups (KH-690 bus members, KH-671 naming), or re-grouped only
    with a KH-671 trigger (a root-sheet hierarchical label named like a global label / power net),
    the backslash-sheet unit, or a new diagnostic;
  - raw lists (power_symbols, no_connects, text_annotations) never move; labels only rename;
  - other blocks: only SCH_BLOCKS;
  - summary / trust_summary / audience_summary recompute from findings on both sides.
pcb       only diagnostics, and only growing (KH-482 malformed boards).
gerber    nothing.
emc / thermal / cross_analysis
          only when an upstream schematic or PCB artefact the unit read moved and is claimed.

Usage: python regression/budgets/v302_wave11b1_judge.py FEATURES_DIR OUT_PREFIX
FEATURES_DIR holds <analyzer>.jsonl from v302_wave11b1_features.py. Writes OUT_PREFIX.json + OUT_PREFIX.units.jsonl.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

BACKSLASH_UNITS = {"MSTRocketDesignTeam/Avionics-Pyro-Charge-Controller-PCB"}  # repo prefix (sch-backslash-sheet-unit)

SCH_RULES = frozenset({
    # G1 legacy dedupe / G2 classify / G3 MCU port H / G4 tables
    "VD-DET", "CS-DET", "RC-DET", "LC-DET", "TR-DET", "DC-DET", "DO-DET", "PR-DET", "RM-DET", "PP-001",
    "LA-AUD", "PS-001", "RS-001", "AD-DET", "LR-001", "LA-004",
    # G6 derating, G7 FS-001, G8 magjack, G9 current sense, G10 flyback (+LD-DET restated)
    "VD-001", "VD-004", "VD-003", "FS-001", "ET-DET", "LD-DET",
    # KH-683 / KH-694 / KH-671 / KH-690 (+ restated net-name followers) / KH-355 / KH-435 / KH-473 / KH-684
    "PU-001", "CG-AUD", "LB-001", "PD-DET", "KM-DET", "NT-001", "EP-AUD", "SJ-DET", "BR-DET", "LS-DET",
    "DI-DET", "MD-DET", "DS-001", "DS-002", "DS-003",
    # C1 G1 value parsing, G2 fields, G4 varistor, G8 classifiers; C2 G1 Vref, G3 VM-001
    "XL-DET", "CD-DET", "OA-DET", "SS-001", "IL-DET", "PP-DET", "SP-001", "WL-001", "RF-DET", "CERT-001",
    "SI-DET", "IB-DET", "VM-001",
    # gate restatements: AU-DET value text (G2, kicad-cli reads the last duplicate Value too),
    # UC-002 net-name text after a KH-690 bus-member rename
    "AU-DET", "UC-002",
})
# rewritten in place only: the count per unit never changes
INPLACE = frozenset({"ET-DET", "AD-DET", "XL-DET", "CD-DET", "LA-004", "KM-DET", "NT-001", "BR-DET",
                     "LS-DET", "DI-DET", "MD-DET", "SS-001", "IL-DET", "PP-DET", "SP-001", "LD-DET",
                     "AU-DET", "UC-002"})
# in-place rules whose finding may leave when its part's Value text goes empty (G2 last-duplicate rule)
VALUE_GATED = frozenset({"XL-DET", "CD-DET", "AU-DET"})
# removed or rewritten only: never a net gain in a unit
SHRINK = frozenset({"PU-001", "VM-001", "LR-001", "LA-AUD", "IB-DET", "RF-DET", "SI-DET", "PR-DET", "PS-001",
                    "TR-DET"})
# hand-adjudicated units (see operations.log): budget-rate VM-001 adds that are false on inspection
ADJUDICATED = {
    "schematic/ice458/VFD-Clock/PCB_controler_controler.kicad_sch":
        "VM-001 +1 FALSE: MC34063 own SwC/DC open-collector pins judged at the Ipk sense-resistor rail (KH-989 rule) vs a 1.0 V domain guess",
    "schematic/AbdulAjadi1/FPGA-Board/POWER_REGULATION2.kicad_sch":
        "VM-001 +1 FALSE: corrected +3V3 (KH-355, 1.35 -> 3.278 V) exposes SIP32510 load-switch EN not in LOAD_SWITCH_KEYWORDS",
}

COMP_FIELDS = frozenset({"connector_layout", "type", "category", "is_external_connector", "parsed_value",
                         "description", "datasheet", "value", "footprint", "functional_class", "function"})
# mandatory-field text (KH-711 / KH-723, C1 G2) and what reads it
FIELD_TEXT = frozenset({"description", "datasheet", "value", "footprint"})
FIELD_BLOCKS = frozenset({"annotation_issues", "bom_lock", "assembly_complexity"})
SCH_RAW = ("power_symbols", "no_connects", "text_annotations")
SCH_BLOCKS = frozenset({
    "components", "bom", "statistics", "placement_analysis", "ic_pin_analysis", "transistor_pin_analysis",
    "bom_optimization", "pdn_impedance", "subcircuits", "power_sequencing_validation", "net_classifications",
    "power_budget", "power_sequencing", "inrush_analysis", "rail_voltages", "sleep_current_audit",
    "missing_info", "design_analysis", "connectivity_issues", "pwr_flag_warnings", "ground_domains",
    "test_coverage", "label_shape_warnings", "labels", "bus_topology", "simulation_readiness", "diagnostics",
    "hierarchy_warning", "protocol_compliance", "nets", "findings", "summary", "trust_summary",
    "audience_summary",
}) | FIELD_BLOCKS
DERIVED = frozenset({"summary", "trust_summary", "audience_summary"})


def _bs(unit):
    rest = unit.split("/", 1)[1]
    return any(rest.startswith(p + "/") for p in BACKSLASH_UNITS)


def judge_schematic(r):
    bad, trig = [], set()
    unit = r["unit"]
    if _bs(unit):
        return "BACKSLASH", []
    tops = set(r["tops"])
    diag_grew = r["diag"][1] > r["diag"][0]
    if r["diag"][1] < r["diag"][0]:
        bad.append("diagnostics shrank")
    if diag_grew:
        trig.add("DIAG")
    for k in SCH_RAW:
        if k in tops:
            bad.append(f"raw {k}")
    lab = r.get("labels")
    if lab:
        if set(lab) - {"name"}:
            bad.append(f"labels fields {sorted(lab)}")
        else:
            trig.add("LABELNAME")
    for k in sorted(tops - SCH_BLOCKS):
        bad.append(f"block {k}")
    comp = r.get("comp") or {}
    if comp.get("__refs_differ__") and not diag_grew:
        bad.append("component refs differ")
    nets = r.get("nets")
    other = set(comp) - COMP_FIELDS - {"__refs_differ__", "__refs_added__", "__refs_removed__", "pin_nets"}
    if other:
        bad.append(f"component fields {sorted(other)}")
    if "pin_nets" in comp and not (nets or diag_grew):
        bad.append("component pin_nets moved without a net change")
    if comp:
        trig.add("COMP")
    if tops & FIELD_BLOCKS and not (set(comp) & FIELD_TEXT or comp.get("__refs_differ__")):
        bad.append(f"field blocks {sorted(tops & FIELD_BLOCKS)} without a field-text change")
    if nets:
        if nets["groups_equal"]:
            trig.add("NETNAME")
        elif r.get("root_hier"):
            trig.add("KH671")
        elif diag_grew:
            trig.add("DIAG")
        else:
            bad.append("net pin groups changed without a KH-671 trigger")
        if not nets["fields_ok"]:
            # has_pwr_flag / labels on a renamed or re-grouped net follow the same rename
            trig.add("NETFIELDS")
    rules = r.get("rules") or {}
    for rid, (rem, add) in rules.items():
        if rid not in SCH_RULES:
            bad.append(f"rule {rid} -{rem}+{add}")
        elif rid in INPLACE and rem != add and not (rid in VALUE_GATED and "value" in comp and add < rem):
            bad.append(f"in-place rule {rid} -{rem}+{add}")
        elif rid in SHRINK and add > rem:
            bad.append(f"shrink-only rule {rid} -{rem}+{add}")
    if rules:
        trig.add("F")
    for rid in (r.get("id_only") or {}):
        if rid not in SCH_RULES:
            bad.append(f"finding_id change on {rid}")
    if r.get("id_only"):
        trig.add("ID")
    if not all(r["derived_ok"]):
        bad.append(f"derived blocks not from findings {r['derived_ok']}")
    if tops & DERIVED and not (rules or r.get("id_only") or "findings" in tops):
        # trust_summary.bom_coverage counts datasheet / MPN fields (C1 G2 rollups)
        moved = {f"{k}.{x}" for k in tops & DERIVED for x in (r["sub"].get(k) or ["*"])}
        if not (moved <= {"trust_summary.bom_coverage"} and set(comp) & FIELD_TEXT):
            bad.append(f"rollups moved without findings {sorted(moved)}")
    if tops - DERIVED - {"findings"}:
        trig.add("B")
    if not trig and not bad:
        bad.append("movement without a trigger")
    if bad and unit in ADJUDICATED:
        return "ADJ", []
    return ("+".join(sorted(trig)) if not bad else None), bad


def judge_pcb(r):
    tops = set(r["tops"])
    if tops - {"diagnostics"}:
        return None, [f"pcb blocks {sorted(tops - {'diagnostics'})}"]
    if r["diag"][1] <= r["diag"][0]:
        return None, ["pcb diagnostics did not grow"]
    return "DIAG", []


def judge_gerber(r):
    return None, [f"gerber moved {r['tops']}"]


def judge_downstream(r, claimed):
    up = r.get("upstream") or {}
    moved, unclaimed = [], []
    for kind in ("schematic", "pcb"):
        ua, ub = (up.get(kind) or [None, None])
        if not ua:
            continue
        if ua in claimed:
            if claimed[ua] is None:
                unclaimed.append(f"upstream {kind} unclaimed")
            else:
                moved.append(kind)
    if unclaimed:
        return None, unclaimed
    if not moved:
        # KH-476: EMC reads the switching-frequency table itself (TPS6216x / TPS6300x)
        if r["an"] == "emc" and set(r.get("rules") or {}) <= {"SW-001", "EE-002"} and "board_info" in r["tops"]:
            return "KH476-EMC", []
        return None, [f"{r['an']} moved without an upstream move"]
    return "D:" + "+".join(moved), []


def _load(p):
    if not p.exists():
        return []
    return [json.loads(l) for l in p.open(encoding="utf-8")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("features_dir", type=Path)
    ap.add_argument("out")
    args = ap.parse_args()
    fd = args.features_dir
    out_units = []
    claimed = {}
    tally = {"rules": defaultdict(lambda: [0, 0, 0]), "comp": Counter(), "comp_types": Counter(),
             "blocks": Counter(), "id_only": Counter(), "labels": Counter(), "units": Counter()}
    for an, fn in (("schematic", judge_schematic), ("pcb", judge_pcb), ("gerber", judge_gerber)):
        for r in _load(fd / f"{an}.jsonl"):
            label, bad = fn(r) if "error" not in r else (None, [r["error"]])
            claimed[r["unit"]] = label
            out_units.append({"unit": r["unit"], "an": an, "label": label, "bad": bad[:8]})
    for an in ("emc", "thermal", "cross_analysis"):
        for r in _load(fd / f"{an}.jsonl"):
            label, bad = judge_downstream(r, claimed) if "error" not in r else (None, [r["error"]])
            claimed[r["unit"]] = label
            out_units.append({"unit": r["unit"], "an": an, "label": label, "bad": bad[:8]})
    # magnitudes, all analyzers
    for an in ("schematic", "pcb", "gerber", "emc", "thermal", "cross_analysis"):
        for r in _load(fd / f"{an}.jsonl"):
            tally["units"][an] += 1
            for rid, (rem, add) in (r.get("rules") or {}).items():
                t = tally["rules"][f"{an}:{rid}"]
                t[0] += rem; t[1] += add; t[2] += 1
            for k in r["tops"]:
                tally["blocks"][f"{an}:{k}"] += 1
            for k, v in (r.get("id_only") or {}).items():
                tally["id_only"][f"{an}:{k}"] += v
            for k, v in (r.get("comp") or {}).items():
                tally["comp"][k] += v
            for k, v in (r.get("comp_types") or {}).items():
                tally["comp_types"][k] += v
            for k, v in (r.get("labels") or {}).items():
                tally["labels"][k] += v if isinstance(v, int) else 1
    resid = [u for u in out_units if u["label"] is None]
    reasons = Counter(b.split(" -")[0] if b.startswith(("rule ", "shrink", "in-place")) else b
                      for u in resid for b in u["bad"])
    summary = {
        "moved_units": dict(tally["units"]),
        "claimed": sum(1 for u in out_units if u["label"]),
        "residual_units": len(resid),
        "residual_by_analyzer": dict(Counter(u["an"] for u in resid)),
        "residual_reasons": dict(reasons.most_common(60)),
        "labels": dict(Counter(u["label"] for u in out_units if u["label"]).most_common(40)),
        "rules": {k: {"removed": v[0], "added": v[1], "units": v[2]} for k, v in sorted(tally["rules"].items())},
        "blocks": dict(tally["blocks"].most_common()),
        "id_only": dict(tally["id_only"].most_common()),
        "comp_fields": dict(tally["comp"].most_common()),
        "comp_types": dict(tally["comp_types"].most_common(60)),
        "labels_fields": dict(tally["labels"]),
        "verdict": "clean" if not resid else "residuals",
    }
    Path(args.out + ".json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    with open(args.out + ".units.jsonl", "w", encoding="utf-8") as fo:
        for u in out_units:
            fo.write(json.dumps(u) + "\n")
    print(json.dumps({k: summary[k] for k in ("moved_units", "claimed", "residual_units", "residual_by_analyzer",
                                               "residual_reasons", "labels", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
