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

Last updated: 2026-04-16

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-323**. Next TH number: **TH-036**.

> 0 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-323: `pin_coverage_warnings` emitted by schematic analyzer but missing from `--schema`

**Severity:** LOW (documentation gap, not a functional bug)

**Repro:**
- `analyze_schematic.py` emits top-level key `pin_coverage_warnings` at line 8921 when
  `verify_pin_coverage()` (line 5679) returns a truthy list.
- `python3 analyze_schematic.py --schema` does NOT list `pin_coverage_warnings` in the
  documented top-level envelope.
- Harness `tests/test_schema_drift.py::test_schematic_schema_drift` correctly flagged this
  as drift. Temporarily allow-listed in `_KNOWN_UNDOCUMENTED['schematic']` (2026-04-17) so
  harness commits can push; this issue tracks the real main-repo fix.

**Fix:** Add `pin_coverage_warnings` to the schematic `--schema` output with a description,
marked `OPTIONAL` (only emitted conditionally). Mirrors `instance_consistency_warnings`
and `generic_symbol_warnings` treatment.

**File:** `skills/kicad/scripts/analyze_schematic.py` — `--schema` handler (the function that
prints the documented envelope structure)

**Resolution:** Close by documenting the key in `--schema` AND removing the entry from
harness `_KNOWN_UNDOCUMENTED['schematic']` in the same pair of changes. The harness v1.4
Track 1 typed-envelope-SOT work will collapse the whole allow-list; this issue can be
subsumed by that work or fixed standalone.

---

## Test Harness Issues

_No open test-harness issues._

---

## Priority Queue

_1 open issue: KH-323 (LOW)._
