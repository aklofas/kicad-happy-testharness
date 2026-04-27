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

Last updated: 2026-04-19

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-325**. Next TH number: **TH-037**.

> 1 open issue.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-324 — `detection_schema.SCHEMAS` missing 7 detector keys (LOW)

**Symptom:** harness `tests/test_detection_schema.py::test_schema_completeness_zebra_x`
fails with 7 detector keys present in analyzer `findings[]` output but absent from
`SCHEMAS` (in `kicad-happy/skills/kicad/scripts/detection_schema.py`):

```
audit_rail_sources, validate_pullups, audit_datasheet_coverage,
integrated_ldos, validate_voltage_levels, decoupling, audit_sourcing_gate
```

**Repro:**
```
KICAD_HAPPY_DIR=/home/aklofas/Projects/kicad-happy \
  /home/aklofas/Projects/kicad-happy/.venv/bin/python -m pytest \
  tests/test_detection_schema.py::test_schema_completeness_zebra_x -v
```

**Triage:** either (a) `SCHEMAS` needs entries for these detectors, or (b) the
harness exemption list (`tests/test_detection_schema.py:323-328` for informational
sections like `design_observations`, `power_path`) needs extending. Test author
(harness) believes (a) is correct for detectors that emit identity/derived fields,
(b) for purely informational sections — main-repo to determine which apply.

**Severity LOW:** unit-test gap only; analyzer output unaffected, gate runner
unaffected, corpus assertions unaffected. Surfaced during v1.4-dev gate-runner
verification 2026-04-27.

---

## Test Harness Issues

_No open test-harness issues._

---

## Priority Queue

_0 open issues._
