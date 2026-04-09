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
number: **KH-229**. Next TH number: **TH-013**.

> 1 open issue (1 TH-*).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

(none)

---

## Deferred

(none)

---

## Test Harness Issues

### TH-012 — seed_structural.py leaves stale assertions when output detections drop to zero (MEDIUM)

**Symptom:** When an analyzer change removes detections from an output (e.g., switching
loop area changes cause SW-001 findings to disappear), `seed_structural.py --all`
doesn't remove the old structural assertion files. The seed skips outputs with zero
detections in a section (nothing to seed), but the OLD assertion file persists and
expects the now-removed detections. This causes persistent failures that survive
multiple re-seed passes.

**Root cause:** `seed_structural.py` generates assertions from current output, writing
new files when detections exist. When an output has 0 detections for a section that
previously had detections, the seed has nothing to generate — so it doesn't touch the
existing assertion file. The `seed.py --prune-stale` flag exists for SEED assertions
but `seed_structural.py` has no equivalent.

**Scope:** 56 stale EMC structural assertion files found in this session, all referencing
`switching_emc`/`SW-001` findings that no longer exist after the KH-225 charge pump fix
and switching loop area enrichment.

**Fix:** Add `--prune-stale` to `seed_structural.py` that:
1. For each existing structural assertion file, check if the corresponding output still
   has detections in the referenced section
2. Delete assertion files whose output section is now empty
3. Alternatively, overwrite with an empty assertion set (0 assertions)

**Workaround:** Manual cleanup script (used this session):
```python
# Delete structural assertions that reference findings in outputs with 0 findings
for afile in Path('reference').rglob('assertions/emc/*_structural.json'):
    # check output, delete if 0 findings and assertion expects findings
```

**Discovered:** 2026-04-09 during switching loop area validation.

---

## Priority Queue (open issues, ordered by impact)

1. TH-012 — seed_structural.py leaves stale assertions when detections drop to zero (MEDIUM)

