# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

> **Reporting guidelines for Level 3 subagents**: Root cause descriptions must cite
> specific function names and line numbers, not just file names. When claiming code
> "doesn't check X", trace the actual code path for the repro input and show which line
> returns the wrong result — don't infer from the symptom what the code must be doing.
> Common pitfalls:
> - Code checks the right field but matches the wrong strings (KH-213: checked keywords
>   for `p-channel` but actual keywords contain `PMOS`)
> - Code has the right pattern but wrong format (KH-209: matched `Vnn` but not `nnVn`)
> - Fix exists but callers bypass it (KH-212: KH-153 fix requires `component_type` param
>   that callers don't pass)
> - Transforms are applied but decomposed wrong (KH-207: `compute_pin_positions` runs but
>   matrix→angle extraction is mathematically incorrect)
>
> Include in every report: (1) the function name and line number that produces the wrong
> result, (2) the actual input values from the repro file, (3) what the code returns vs
> what it should return.

Last updated: 2026-04-09

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-230**. Next TH number: **TH-013**.

> 1 open issue (1 KH-*).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-229 — USB compliance vbus_capacitance check crashes analyzer (HIGH)

**Symptom:** `analyze_schematic.py` crashes with `TypeError: unhashable type: 'dict'`
at line 7289 in `analyze_usb_compliance()` when a schematic has USB connectors with
VBUS capacitors. The analyzer aborts — no output produced. Affects any schematic with
USB connectors where VBUS cap detection fires.

**Root cause:** The `vbus_capacitance` check (lines 7251-7262) stores a **dict**
`{"status": "warning", "total_uf": ..., "detail": ...}` into `conn_checks["checks"]`,
while all other checks store plain strings (`"pass"`, `"fail"`, `"info"`). The summary
loop at line 7289 iterates `conn_c["checks"].values()` and uses each value as a dict
key (`all_checks[status]`), which fails when the value is a dict.

**Fix:** Either:
1. Store only the status string in `checks` and move the detail to a separate field:
   `conn_checks["checks"]["vbus_capacitance"] = "warning"` with
   `conn_checks["vbus_capacitance_detail"] = {...}`
2. Or extract `status` from dict values in the summary loop:
   `s = status["status"] if isinstance(status, dict) else status`

Option 1 is cleaner — keeps `checks` as a uniform `{name: status_string}` dict.

**Impact:** HIGH — crashes the analyzer entirely for any schematic with USB connectors
where VBUS capacitors are present. This blocks all output generation, not just USB
compliance. Introduced by commit d005983 (protocol electrical parameter checks).

**File:** `analyze_schematic.py:7251-7262` (dict assignment) and `:7289` (crash site).

**Repro:** `Dylanfg123/Zebra-X` — `ZeBra-X.kicad_sch` (has USB connectors with VBUS
caps). Any schematic with USB connectors + VBUS decoupling will trigger this.

**Discovered:** 2026-04-10 during --analysis-dir bug fix verification.

---

## Deferred

(none)

---

## Priority Queue (open issues, ordered by impact)

1. KH-229 — USB compliance vbus_capacitance crashes analyzer (HIGH)

