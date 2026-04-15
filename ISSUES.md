# Issue Tracker

Single source of truth for kicad-happy analyzer bugs (KH-*) and test harness
issues (TH-*). Contains enough detail to resume work with zero conversation
history. Enhancements and features are tracked in `TODO-v1.3-roadmap.md`
in each repo, not here.

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

Last updated: 2026-04-15

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-312**. Next TH number: **TH-032**.

> 2 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-311 — MEDIUM — EMC `trust_summary.total_findings` doesn't match `len(findings)`

**Symptom:** 161 EMC outputs on the smoke pack have `trust_summary.total_findings`
and `summary.total_findings` higher than actual `len(findings)`. The diff is
consistently 2 (e.g., reports 3 findings, actual 1).

**Root cause:** The EMC analyzer computes `summary` and `trust_summary` from the
full findings list, then filters some findings out before writing the output JSON.
The summary/trust_summary reflect the pre-filter count.

**Repro:** `results/outputs/emc/0101shift/Business_Card_AI/Business_card_AI.sch.json` —
`trust_summary.total_findings=3`, `summary.total_findings=3`, `len(findings)=1`.

**Fix:** In `analyze_emc.py`, either compute trust_summary after filtering, or
include all findings in the output.

**Verification:** `python3 validate/validate_invariants.py --type emc --cross-section smoke`
should show 0 trust_summary violations.

**Source:** Discovered by extending invariant checker to EMC outputs (P13, 2026-04-15).

---

## Test Harness Issues

### TH-031 — LOW — SPICE/EMC structural seeders use fragile stringified-list matching

**Symptom:** `seed_structural.py` generates `contains_match` assertions with
`field="components"` and `\b` word-boundary regex (e.g., `\bR5\b`). The
`contains_match` operator calls `str()` on the field value, so for a list
like `['R5', 'C3']` it matches against the string `"['R5', 'C3']"`. This
works today but breaks silently if the list repr changes (e.g., tuple,
different quoting, or if the operator is updated to handle lists natively).

**Affected code:**
- `generate_spice_structural_assertions()` line ~268: `field="components"`
- `generate_emc_structural_assertions()` line ~341: `field="components"`

**Root cause:** `components` is a list of strings, but `contains_match`
expects a scalar field to regex against. The thermal seeder was fixed to
use the scalar `ref` field instead. SPICE/EMC findings don't have a scalar
`ref` — they only have the `components` list.

**Options:**
1. Add a `reference` or `ref` field to SPICE/EMC findings (main repo change)
2. Teach `contains_match` to iterate list items when `field` points to a list
3. Use `count_matches` with `value >= 1` instead (already handles lists)
4. Leave as-is — fragile but functional

**Source:** Discovered during thermal structural seeder audit (2026-04-15).

---

## Priority Queue

2 open issues.

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | KH-311 | MEDIUM | Small — compute trust_summary after filtering in EMC |
| 2 | TH-031 | LOW | Small-medium — depends on chosen approach |
