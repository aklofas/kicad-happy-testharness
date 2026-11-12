#!/usr/bin/env python3
"""Auto-generate VALIDATION.md for the kicad-happy repo.

Reads harness data (catalog, assertions, health, schema) and produces a
markdown validation summary with current stats.

Usage:
    python3 generate_validation_md.py                                          # stdout
    python3 generate_validation_md.py --output VALIDATION.md                   # local file
    python3 generate_validation_md.py @args.txt     # arguments from a file, one per line

A release page passes the measured run_checks output, the baseline ledger (it classifies
each non-passing assertion), the gate rollup with its units.jsonl and budgeted per-unit
report (every nonzero gate counter is attributed to the budget classes that claimed its
units) and the budget file. The generator refuses (exit 1) to write a page that
contradicts itself: a CLEAN verdict with an unattributed FAIL / Disappeared / Downgrades /
NewUnknown unit, or an assertion table that does not add up to the measured total.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent.parent
CATALOG_FILE = HARNESS_DIR / "reference" / "repo_catalog.json"
SCHEMA_FILE = HARNESS_DIR / "reference" / "schema_inventory.json"
BUGFIX_FILE = HARNESS_DIR / "regression" / "bugfix_registry.json"
HEALTH_LOG = HARNESS_DIR / "reference" / "health_log.jsonl"
CROSS_SECTIONS = HARNESS_DIR / "reference" / "cross_sections.json"
ISSUES_FILE = HARNESS_DIR / "ISSUES.md"
FIXED_FILE = HARNESS_DIR / "FIXED.md"
OUTPUTS_DIR = HARNESS_DIR / "results" / "outputs"


def _count_output_files(atype):
    """Count output JSON files for an analyzer type."""
    d = OUTPUTS_DIR / atype
    if not d.exists():
        return 0
    # capability_mode.json is the analyzer's per-repo run-metadata sidecar,
    # not an analysis output; _timing/_aggregate* are runner bookkeeping.
    return sum(1 for _ in d.rglob("*.json")
               if _.name not in ("capability_mode.json", "_timing.json")
               and not (_.parent == d and _.name == "manifest.json")
               and not _.name.startswith("_aggregate"))


def _heading_ids(path, prefix):
    """Ids a heading opens with: `### TH-012: ...`, `## 2026-11-03 — TH-012: ...` or
    `### KH-398 (MEDIUM) / KH-399 (LOW): ...`. Ids later in the title (rule ids such as
    `TH-001/PDN`, ranges in an `Earlier fixes` heading) are not the heading's own."""
    one = rf"{prefix}-\d{{3}}(?:\s*\([A-Z-]+\))?"
    lead = re.compile(rf"#+\s+(?:\d{{4}}-\d\d-\d\d\s+—\s+)?({one}(?:\s*(?:/|,|and|\+)\s*{one})*)")
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = lead.match(line)
        if m:
            ids.update(int(n) for n in re.findall(rf"{prefix}-(\d{{3}})", m.group(1)))
    return ids


def _count_issues(prefix):
    """Count <prefix>-* issues by distinct id from ISSUES.md (open) and FIXED.md (closed).

    An id still in ISSUES.md is open even when FIXED.md records a fixed half.
    Returns (open_count, closed_count, max_number).
    """
    open_ids = _heading_ids(ISSUES_FILE, prefix) if ISSUES_FILE.exists() else set()
    fixed_ids = _heading_ids(FIXED_FILE, prefix) if FIXED_FILE.exists() else set()
    closed_ids = fixed_ids - open_ids
    return len(open_ids), len(closed_ids), max(open_ids | fixed_ids, default=0)


def _count_kh_issues():
    return _count_issues("KH")


def _count_th_issues():
    return _count_issues("TH")


_SEVERITY_ORDER = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "unclassified")


def _severity_by_id(path, prefix):
    """{id number: severity} for the <prefix>-* ids headings in `path` open with: the
    severity in the heading (`### KH-398 (MEDIUM) / KH-399 (LOW): ...`), else the entry's
    first `**Severity:**` line. LOW-MEDIUM counts as MEDIUM; no recognised severity is
    "unclassified"."""
    if not Path(path).exists():
        return {}
    one = rf"{prefix}-\d{{3}}(?:\s*\([A-Z-]+\))?"
    lead = re.compile(rf"#+\s+(?:\d{{4}}-\d\d-\d\d\s+—\s+)?({one}(?:\s*(?:/|,|and|\+)\s*{one})*)")

    def norm(word):
        word = word.rstrip("-")
        word = "MEDIUM" if word == "LOW-MEDIUM" else word
        return word if word in _SEVERITY_ORDER else None

    sev, current = {}, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            m = lead.match(line)
            current = []
            if m:
                for n, word in re.findall(rf"{prefix}-(\d{{3}})(?:\s*\(([A-Z-]+)\))?", m.group(1)):
                    i = int(n)
                    sev.setdefault(i, "unclassified")
                    if word and norm(word) and sev[i] == "unclassified":
                        sev[i] = norm(word)
                    current.append(i)
            continue
        m = re.match(r"\*\*Severity:?\*\*:?\s*\**\s*([A-Z][A-Z-]*)", line)
        if m and current:
            word = norm(m.group(1))
            for i in current:
                if sev[i] == "unclassified" and word:
                    sev[i] = word
            current = []
    return sev


def _open_by_severity(prefix):
    """Open <prefix>-* ids in ISSUES.md by severity, in _SEVERITY_ORDER."""
    counts = Counter(_severity_by_id(ISSUES_FILE, prefix).values())
    return {k: counts[k] for k in _SEVERITY_ORDER if counts[k]}


def _severity_list(prefix):
    return ", ".join(f"{n} {k}" for k, n in _open_by_severity(prefix).items())


def _severity_text(prefix):
    if not _open_by_severity(prefix):
        return ""
    text = ": " + _severity_list(prefix)
    if prefix == "KH" and _has_low_medium():
        text += "; LOW-MEDIUM counts as MEDIUM"
    return text


def _has_low_medium():
    return ISSUES_FILE.exists() and "**Severity:** LOW-MEDIUM" in ISSUES_FILE.read_text(encoding="utf-8")


def _load_ledger(path):
    """A baseline-debt ledger (reference/baseline_debts/<sha7>.json); None when no path."""
    if not path:
        return None
    if not Path(path).exists():
        raise FileNotFoundError(f"ledger not found: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


# Gate counters and how a units.jsonl record contributes to each.
_COUNTER_FIELDS = {"FAIL": None, "WARN": None, "Disappeared": "disappeared_count",
                   "Downgrades": "severity_downgrades", "Upgrades": "severity_upgrades",
                   "NewKnown": "new_known_count", "NewUpgraded": "new_upgraded_count",
                   "NewUnknown": "new_unknown_count"}
# The counters a CLEAN verdict needs fully attributed.
_CLEAN_RULE = ("FAIL", "Disappeared", "Downgrades", "NewUnknown")


def _unit_claims(path):
    """{unit: (claimed classes, residual count)} from a budgeted comparison: a
    compare_snap_trees budgeted report (field_report_budgeted.json) or a per-unit JSONL
    with {"unit", "claimed": {class: n}, "residuals": n} rows."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"budget report not found: {path}")
    claims = defaultdict(lambda: [set(), 0])
    rows_path = path if path.suffix == ".jsonl" else None
    budget = {}
    if rows_path is None:
        budget = json.loads(path.read_text(encoding="utf-8")).get("budget") or {}
        if budget.get("claims_file"):        # a spilled report keeps per-unit rows in a sidecar
            rows_path = path.parent / budget["claims_file"]
    if rows_path is not None:
        for line in rows_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                claims[r["unit"]][0].update(k for k, n in (r.get("claimed") or {}).items() if n)
                claims[r["unit"]][1] += int(r.get("residuals") or 0)
    else:
        for cls, deltas in (budget.get("claimed") or {}).items():
            for d in deltas:
                claims[d["unit"]][0].add(cls)
        for d in budget.get("residuals") or []:
            claims[d["unit"]][1] += 1
    return {u: (frozenset(c), r) for u, (c, r) in claims.items()}


def _attribute_gate(units_path, budget_report_path):
    """Per gate counter: its total in units.jsonl, the units each budget class covers, and
    the units nothing covers (a residual delta, or no field delta recorded for the unit)."""
    if not Path(units_path).exists():
        raise FileNotFoundError(f"gate units not found: {units_path}")
    claims = _unit_claims(budget_report_path)
    out = {k: {"total": 0, "units": 0, "classes": Counter(), "unattributed": 0} for k in _COUNTER_FIELDS}
    for line in Path(units_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        u = json.loads(line)
        classes, residuals = claims.get(f"{u['analyzer']}/{u['unit_id']}", (frozenset(), 0))
        for key, field in _COUNTER_FIELDS.items():
            n = int(u.get("verdict") == key) if field is None else int(u.get(field) or 0)
            if not n:
                continue
            out[key]["total"] += n
            out[key]["units"] += 1
            if classes and not residuals:
                out[key]["classes"].update(classes)
            else:
                out[key]["unattributed"] += 1
    return out


def _attribution_text(key, attr, gate_pass):
    """One-line attribution for a gate counter. SKIP reads the rollup's skip breakdown;
    the others read `_attribute_gate` output."""
    if key == "SKIP":
        gp = gate_pass or {}
        parts = [f"{n:,} {k.replace('_', ' ')}" for k, n in (gp.get("skip_breakdown") or {}).items() if n]
        if gp.get("ledgered_skips"):
            parts.append(f"{gp['ledgered_skips']:,} in the baseline ledger")
        if gp.get("unledgered_skips"):
            parts.append(f"{len(gp['unledgered_skips']):,} NOT in the ledger")
        return ", ".join(parts)
    if key not in _COUNTER_FIELDS or attr is None:
        return ""
    a = attr[key]
    parts = []
    if _COUNTER_FIELDS[key] is not None:      # a finding count: say how many units hold them
        parts.append(f"{_plural(a['total'], 'finding')} in {_plural(a['units'], 'unit')}")
    if a["classes"]:
        if len(a["classes"]) == 1 and not a["unattributed"]:
            parts.append(f"attributed to `{next(iter(a['classes']))}`")
        else:
            parts.append("attributed to " + ", ".join(
                f"`{c}` ({_plural(n, 'unit')})" for c, n in sorted(a["classes"].items())))
    if a["unattributed"]:
        parts.append(f"{_plural(a['unattributed'], 'unit')} unattributed")
    return ", ".join(parts)


def _plural(n, word):
    return f"{n:,} {word}{'' if n == 1 else 's'}"


def _class_summary(evidence):
    """The budget class's evidence up to the first absolute path (record pointers stay in the
    budget file)."""
    return re.split(r"\s+/\S", evidence or "", maxsplit=1)[0].rstrip(" .;")


def _pct(passed, total):
    """Pass rate at four decimals; a non-passing assertion never displays as 100."""
    if not total:
        return "not measured"
    rate = round(passed / total * 100, 4)
    if rate >= 100 and passed < total:
        rate = 99.9999
    return f"{rate:.4f} %"


def _cell(text):
    return f" {text} " if text else " "


def _cause_columns(cause):
    if not cause or cause == "unreviewed":
        return "unclassified", ""
    m = re.match(r"((?:KH|TH)-\d+(?:\s*/\s*(?:KH|TH)-\d+)*)\s*:?\s*(.*)", cause)
    return (m.group(1), m.group(2)) if m else ("unclassified", cause)


def _load_check_results(path):
    """Load run_checks --json output. None when no path is given; a given path that does not
    exist is an error (a mistyped path must not publish an unmeasured document)."""
    if not path:
        return None
    if not Path(path).exists():
        raise FileNotFoundError(f"check results not found: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_gate_rollup(path):
    """Load a corpus gate rollup JSON. None when no path is given; a missing path is an error."""
    if not path:
        return None
    if not Path(path).exists():
        raise FileNotFoundError(f"gate rollup not found: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_catalog_stats():
    """Load and summarize repo catalog, including assertion totals."""
    if not CATALOG_FILE.exists():
        return {}
    catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))

    categories = Counter(r.get("category", "?") for r in catalog)
    versions = Counter()
    multi_version_repos = uncounted_repos = 0
    for r in catalog:
        counted = 0
        for v in r.get("kicad_versions", []):
            # Parse major version from strings like "9.0", "5 (legacy)", "10.99"
            m = re.match(r"(\d+)", v)
            if m:
                major = int(m.group(1))
                if major >= 5:
                    versions[f"KiCad {major}"] += 1
                    counted += 1
        if counted > 1:
            multi_version_repos += 1
        elif counted == 0:
            uncounted_repos += 1

    total_components = sum(r.get("complexity", {}).get("total_components", 0)
                           for r in catalog)
    total_nets = sum(r.get("complexity", {}).get("total_nets", 0) or 0
                     for r in catalog)

    # Detector coverage
    det_coverage = Counter()
    for r in catalog:
        for det in r.get("detectors_fired", {}):
            det_coverage[det] += 1

    # Assertion totals from catalog (avoids scanning 111K files)
    assertion_total = 0
    assertion_by_type = Counter()
    for r in catalog:
        a = r.get("assertions", {})
        assertion_total += a.get("total", 0)
        for prefix in ("SEED", "STRUCT", "FND", "BUGFIX"):
            assertion_by_type[prefix] += a.get(prefix, 0)

    return {
        "total_repos": len(catalog),
        "categories": categories,
        "versions": versions,
        "multi_version_repos": multi_version_repos,
        "uncounted_repos": uncounted_repos,
        "total_components": total_components,
        "total_nets": total_nets,
        "detector_coverage": det_coverage,
        "assertion_total": assertion_total,
        "assertion_by_type": assertion_by_type,
    }


def _measured_assertion_stats(check_results):
    """Assertion total + per-prefix breakdown from run_checks --json output.

    The measured total is authoritative; the catalog's per-repo sums are only
    the fallback when no check results are supplied.
    """
    by_type, passed = Counter(), Counter()
    for r in check_results.get("results", []):
        if r.get("aspirational"):   # outside the total, so outside the category rows too
            continue
        prefix = (r.get("id") or "?").split("-")[0]
        by_type[prefix] += 1
        passed[prefix] += bool(r.get("passed"))
    return {"total": check_results.get("total", 0), "by_type": dict(by_type),
            "passed_by_type": dict(passed)}


def generate_markdown(check_results=None, gate_rollup=None,
                      gate_label=None, gate_verdict=None, *, checks_label=None,
                      ledger=None, gate_attribution=None, gate_budget=None):
    """Generate VALIDATION.md content.

    check_results: dict from regression/run_checks.py --json (or None).
    gate_rollup:   dict from regression/run_v14_gate.py rollup (or None).
    gate_label:    how to name the gate run (e.g. "the v2.3.0 batch gate
                   (`788649f` → `b54b5c4`, harness `results/v23_gate/...`)").
    gate_verdict:  verdict text; required when the rollup is not strict-clean
                   (a budgeted gate's verdict lives in its adjudication record).
    checks_label:  where the check results were measured (e.g. "at the v3.0.1 regen").
    ledger:        baseline-debt ledger dict; its `checks[].cause` classifies failures.
    gate_attribution: `_attribute_gate(units.jsonl, budget report)`.
    gate_budget:   the budget file dict (class legend, acknowledged overruns).

    Raises ValueError when the page would contradict itself (see the module docstring).
    """
    cat_stats = _load_catalog_stats()
    if check_results:
        assertion_stats = _measured_assertion_stats(check_results)
    else:
        assertion_stats = {
            "total": cat_stats.get("assertion_total", 0),
            "by_type": dict(cat_stats.get("assertion_by_type", {})),
        }
    open_kh, closed_kh, max_kh = _count_kh_issues()
    open_th, closed_th, max_th = _count_th_issues()
    bugfix_count = 0
    if BUGFIX_FILE.exists():
        bugfix_count = len(json.loads(BUGFIX_FILE.read_text(encoding="utf-8")))

    # Count output files
    sch_files = _count_output_files("schematic")
    pcb_files = _count_output_files("pcb")
    gerber_files = _count_output_files("gerber")
    emc_files = _count_output_files("emc")
    spice_files = _count_output_files("spice")

    detector_coverage = cat_stats.get("detector_coverage", {})
    n_detectors = len(detector_coverage)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    md = f"""# Validation Summary

This document describes how kicad-happy is tested and validated. Every change to the analysis engine is verified against a corpus of real-world KiCad projects before release.

*Auto-generated on {now} by `generate_validation_md.py`.*

## Why this matters

Hardware design review tools must be trustworthy. A false negative (missed bug) can cost a board respin ($5K-$50K). A false positive (phantom warning) erodes trust until engineers ignore the tool entirely. kicad-happy addresses both through large-scale automated validation that no human reviewer could replicate.

## Test corpus

The [test harness](https://github.com/aklofas/kicad-happy-testharness) contains {cat_stats.get('total_repos', '?'):,} open-source KiCad projects — the kind of designs real engineers actually build.

**Corpus diversity:**

| Dimension | Coverage |
|-----------|----------|
| Project types | Hobby boards, production hardware, motor controllers, RF frontends, battery management systems, IoT devices, audio amplifiers, power supplies, sensor boards, dev kits |
| KiCad versions | {', '.join(sorted(cat_stats.get('versions', {}).keys(), key=lambda k: int(k.split()[-1])))} |
| File formats | `.kicad_sch` (S-expression), legacy `.sch` (EESchema), `.kicad_pcb` |
| Design complexity | Single-sheet through multi-sheet hierarchical, 2-layer through 6-layer |
| Component counts | 3 to 500+ components per project |
| Net complexity | Simple power supplies to multi-bus digital designs (I2C, SPI, UART, CAN, USB, Ethernet, HDMI) |

**KiCad version distribution:**

| Version | Repos |
|---------|------:|
"""
    for ver, count in sorted(cat_stats.get("versions", {}).items(),
                              key=lambda x: int(x[0].split()[-1])):
        md += f"| {ver} | {count:,} |\n"
    md += (f"\nA repo is counted once for each KiCad version string found in its files, so the "
           f"{cat_stats.get('multi_version_repos', 0):,} repos that hold files from more than "
           f"one version appear in more than one row (KiCad 8.0 and 8.99 both count under "
           f"KiCad 8); the {cat_stats.get('uncounted_repos', 0):,} repos whose version the "
           f"harness catalog records as unknown, empty or older than KiCad 5 are not counted.\n")

    md += f"""
**Category distribution:**

| Category | Repos |
|----------|------:|
"""
    for cat, count in cat_stats.get("categories", {}).most_common(15):
        md += f"| {cat} | {count:,} |\n"
    remaining = sum(c for _, c in cat_stats.get("categories", {}).most_common()
                    if _ not in dict(cat_stats.get("categories", {}).most_common(15)))
    if remaining:
        md += f"| *(other categories)* | {remaining:,} |\n"

    md += f"""
The corpus is sourced from public GitHub repositories. It is not curated for "easy" designs — it includes incomplete projects, unusual topologies, non-standard conventions, and designs with real bugs.

## What gets tested

Every analysis script runs against every applicable file in the corpus. Units that time out or crash on both the baseline and the candidate are carried as accepted baseline debt in the harness ledger (`reference/baseline_debts/`), never silently dropped.

### Crash testing

| Analyzer | Output files |
|----------|-------------|
| Schematic (`analyze_schematic.py`) | {sch_files:,} |
| PCB (`analyze_pcb.py`) | {pcb_files:,} |
| Gerber (`analyze_gerbers.py`) | {gerber_files:,} |
| EMC (`analyze_emc.py`) | {emc_files:,} |
| SPICE (`simulate_subcircuits.py`) | {spice_files:,} |

The counts are output files present in the corpus tree. A new unhandled exception on any file is a release blocker; the corpus gate's `candidate_failures` count is the measured value.

### Regression assertions

Hard assertions on known-good output values. If a previously correct result changes, the assertion fails and the change must be investigated.

"""
    rate_str = "not measured"
    if check_results:
        measured_total = check_results.get("total", 0)
        measured_passed = check_results.get("passed", 0)
        measured_failed = check_results.get("failed", 0)
        measured_errors = check_results.get("errors", 0)
        rate_str = _pct(measured_passed, measured_total)
        table_total = sum(assertion_stats["by_type"].values())
        if table_total != measured_total:
            raise ValueError(f"assertion table total {table_total:,} != measured total "
                             f"{measured_total:,} (check results do not list every assertion)")
        where = f" {checks_label}" if checks_label else ""
        md += f"*Measured via `regression/run_checks.py --json`{where}: " \
              f"{measured_passed:,} passed / {measured_failed:,} failed / " \
              f"{measured_errors:,} errors out of {measured_total:,} ({rate_str}).*\n\n"

    md += "| Category | Assertion count | Pass rate |\n"
    md += "|----------|----------------|-----------|\n"
    passed_by_type = assertion_stats.get("passed_by_type", {})
    for atype, count in sorted(assertion_stats.get("by_type", {}).items(),
                                key=lambda x: -x[1]):
        if count > 0:
            row_rate = (_pct(passed_by_type[atype], count) if atype in passed_by_type
                        else "not measured")
            md += f"| {atype} | {count:,} | {row_rate} |\n"
    md += f"| **Total** | **{assertion_stats.get('total', 0):,}** | **{rate_str}** |\n"

    failing = [r for r in (check_results or {}).get("results", [])
               if not r.get("passed") and not r.get("aspirational")]
    if failing:
        causes = {e.get("id"): e.get("cause") for e in (ledger or {}).get("checks", [])}
        md += (f"\nThe {len(failing):,} non-passing assertions, classified in the harness "
               "baseline ledger (`reference/baseline_debts/`):\n\n")
        md += "| Assertion | Where | Outcome | Issue | Cause |\n"
        md += "|-----------|-------|---------|-------|-------|\n"
        for r in failing:
            outcome = (f"error: {r['error']}" if r.get("error")
                       else f"failed (actual {r.get('actual')})")
            if r.get("id") in causes:
                issue, phrase = _cause_columns(causes[r.get("id")])
            else:
                issue, phrase = "unclassified", "not in the baseline ledger"
            md += (f"| `{r.get('id')}` | {r.get('repo', '')} `{r.get('file', '')}` | {outcome} "
                   f"| {issue} |{_cell(phrase)}|\n")

    md += f"""
Assertions are seeded from validated output and checked on every run. When analyzer logic changes intentionally (new fields, corrected calculations), affected assertions are re-seeded after manual verification.

"""

    if gate_rollup:
        totals = gate_rollup.get("totals", {})
        criteria = gate_rollup.get("pass_criteria", {})
        section = gate_rollup.get("section", "?")
        total_units = gate_rollup.get("total_units", 0)
        if gate_verdict is None:
            if not criteria.get("clean", False):
                raise ValueError("gate rollup is not strict-clean; pass "
                                 "--gate-verdict with the adjudicated verdict")
            gate_verdict = "CLEAN"
        if gate_attribution is not None:
            for key in _COUNTER_FIELDS:
                if gate_attribution[key]["total"] != totals.get(key, 0):
                    raise ValueError(f"gate units file gives {key} "
                                     f"{gate_attribution[key]['total']:,}, the rollup "
                                     f"{totals.get(key, 0):,}: they are not the same run")
        if gate_verdict.lstrip("*").upper().startswith("CLEAN"):
            open_counters = [k for k in _CLEAN_RULE if totals.get(k, 0) and (
                gate_attribution is None or gate_attribution[k]["unattributed"])]
            if open_counters:
                raise ValueError(f"verdict is CLEAN but {', '.join(open_counters)} has "
                                 "unattributed units (pass --gate-units and "
                                 "--gate-budget-report, or correct the verdict)")
        run_ref = f"The run below is {gate_label}." if gate_label else ""
        md += "### Layer 1 regression gate (pre-tag requirement)\n\n"
        md += ("Before any release is tagged, the harness runs the candidate over the full "
               "corpus and diffs every analyzer envelope unit by unit against a baseline: the "
               "previous release, or, for a release built in gated waves, the previous accepted "
               "candidate of each wave. Every unit that moves (FAIL, Disappeared, Downgrades, "
               "NewUnknown) must be attributed to a budget class pre-registered in the "
               "change's review record; unexplained movement, including a severity "
               f"downgrade no class covers, fails the gate. {run_ref}\n\n")
        md += f"Latest run: section `{section}`, {total_units:,} analyzer-runs. Verdict: **{gate_verdict}**.\n\n"
        md += "| Outcome | Count | Attribution |\n|---------|------:|-------------|\n"
        for key in ("PASS", "FAIL", "Disappeared", "Downgrades", "Upgrades",
                    "NewKnown", "NewUpgraded", "NewUnknown", "WARN", "SKIP"):
            n = totals.get(key, 0)
            note = (_attribution_text(key, gate_attribution, gate_rollup.get("gate_pass") or criteria)
                    if n else "")
            md += f"| {key} | {n:,} |{_cell(note)}|\n"
        md += ("\n*A gate is CLEAN when every unit counted under `FAIL`, `Disappeared`, "
               "`Downgrades` or `NewUnknown` is attributed to a budget class pre-registered in "
               "the adjudication record (a zero-delta gate has none to attribute); the "
               "Attribution column names the classes that claimed each counter's units. A "
               "unit can be counted under several outcomes. `NewKnown`/`NewUpgraded` are "
               "intentional new findings; `SKIP` units have no comparable baseline.*\n\n")
        if gate_budget:
            md += f"Budget classes (`{gate_budget.get('budget_id', '?')}`):\n\n"
            for c in gate_budget.get("classes", []):
                md += f"- `{c['id']}` ({c.get('analyzer', '?')}): {_class_summary(c.get('evidence'))}\n"
            overruns = gate_budget.get("acknowledged_overruns") or []
            if overruns:
                md += "\nAcknowledged overruns (measured beyond the declared size, ruled by the product):\n\n"
                for o in overruns:
                    md += (f"- {o.get('class')}: declared {o.get('declared')}, measured "
                           f"{o.get('measured')} — {o.get('ruling')}\n")
            md += "\n"

    md += f"""## Signal detector coverage

{n_detectors} active schematic detectors verified against the corpus:

| Detector | Repos with hits |
|----------|----------------|
"""
    for det, count in sorted(detector_coverage.items(), key=lambda x: -x[1]):
        md += f"| {det} | {count:,} |\n"

    md += f"""
## How to reproduce

Anyone can reproduce the validation:

```bash
# 1. Clone the harness
git clone https://github.com/aklofas/kicad-happy-testharness.git
cd kicad-happy-testharness

# 2. Clone test repos
python3 checkout.py

# 3. Run analyzers (auto-parallelizes across all CPU cores)
python3 run/run_schematic.py --resume
python3 run/run_pcb.py --resume
python3 run/run_emc.py --resume

# 4. Run regression assertions
python3 regression/run_checks.py
```

The harness requires Python 3.10+ and a checkout of the corpus repos. ngspice is optional but recommended for SPICE assertions. Use `--cross-section smoke` for a quick 20-repo validation.

## Issue tracking

All analyzer bugs found during validation are tracked with sequential IDs:

- `KH-001` through `KH-{max_kh}`: analyzer issues ({closed_kh + open_kh} filed, {closed_kh} closed, {open_kh} open{_severity_text("KH")})
- `TH-001` through `TH-{max_th:03d}`: harness infrastructure issues ({closed_th + open_th} filed, {closed_th} closed, {open_th} open{_severity_text("TH")})

Each closed analyzer issue has a corresponding bugfix regression guard assertion that prevents the bug from returning.

## Numbers at a glance

| Metric | Value |
|--------|-------|
| Repos in corpus | {cat_stats.get('total_repos', '?'):,} |
| Schematic files | {sch_files:,} |
| PCB files | {pcb_files:,} |
| Gerber directories | {gerber_files:,} |
| EMC analyses | {emc_files:,} |
| SPICE analyzer runs | {spice_files:,} |
| Components parsed | {cat_stats.get('total_components', 0):,} |
| Nets traced | {cat_stats.get('total_nets', 0):,} |
| Regression assertions | {assertion_stats.get('total', 0):,} at {rate_str} |
| Bugfix guards | {bugfix_count} |
| Closed issues | {closed_kh} analyzer + {closed_th} harness |
| Open issues | {open_kh} analyzer{f" ({_severity_list('KH')})" if open_kh else ""} + {open_th} harness{f" ({_severity_list('TH')})" if open_th else ""} |
| Schematic detectors | {n_detectors} |
"""
    return md


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate VALIDATION.md from harness data",
        fromfile_prefix_chars="@")
    parser.add_argument("--output", "-o", type=Path,
                        help="Output file (default: stdout)")
    parser.add_argument("--check-results", type=Path,
                        help="JSON output from regression/run_checks.py --json; "
                             "if provided, assertion pass rate is computed from it")
    parser.add_argument("--gate-rollup", type=Path,
                        help="JSON rollup from regression/run_v14_gate.py; "
                             "if provided, adds a Layer 1 gate section")
    parser.add_argument("--gate-label",
                        help="How to name the gate run in the narrative, e.g. "
                             "'the v2.3.0 batch gate (`788649f` → `b54b5c4`, "
                             "harness `results/v23_gate/adjudication_v23.md`)'")
    parser.add_argument("--gate-verdict",
                        help="Verdict text for the gate section; REQUIRED when the "
                             "rollup is not strict-clean (budgeted gate)")
    parser.add_argument("--checks-label",
                        help="Where the check results were measured, e.g. "
                             "'at the v3.0.1 corpus regen (`4c2a0d6`)'")
    parser.add_argument("--ledger", type=Path,
                        help="Baseline-debt ledger whose checks[].cause classifies each "
                             "non-passing assertion")
    parser.add_argument("--gate-units", type=Path,
                        help="The gate's units.jsonl (same run as --gate-rollup)")
    parser.add_argument("--gate-budget-report", type=Path,
                        help="Budgeted comparison of the same run: field_report_budgeted.json "
                             "or a per-unit JSONL ({unit, claimed, residuals})")
    parser.add_argument("--gate-budget", type=Path,
                        help="The budget file (class legend and acknowledged overruns)")
    args = parser.parse_args()
    if bool(args.gate_units) != bool(args.gate_budget_report):
        parser.error("--gate-units and --gate-budget-report go together")

    try:
        check_results = _load_check_results(args.check_results)
        gate_rollup = _load_gate_rollup(args.gate_rollup)
        ledger = _load_ledger(args.ledger)
        attribution = (_attribute_gate(args.gate_units, args.gate_budget_report)
                       if args.gate_units else None)
        budget = (json.loads(args.gate_budget.read_text(encoding="utf-8"))
                  if args.gate_budget else None)
        md = generate_markdown(check_results=check_results, gate_rollup=gate_rollup,
                               gate_label=args.gate_label, gate_verdict=args.gate_verdict,
                               checks_label=args.checks_label, ledger=ledger,
                               gate_attribution=attribution, gate_budget=budget)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"error: {e}")

    if args.output:
        args.output.write_text(md, encoding="utf-8")
        print(f"Wrote {args.output} ({len(md)} bytes)")
    else:
        print(md)


if __name__ == "__main__":
    main()
