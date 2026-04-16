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
maximum. Next KH number: **KH-320**. Next TH number: **TH-035**.

> 2 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-312 — LOW — `sync_datasheets_digikey.py` needs `--mpn-list` batch mode

**Symptom:** Harness batch extraction requires downloading datasheets for a
list of MPNs. The sync script only accepts `.kicad_sch` or analyzer JSON as
input, requiring a full project context.

**Root cause:** The sync script extracts MPNs from analyzer output, then
downloads. There's no mode to accept a plain text list of MPNs.

**Fix:** Add `--mpn-list mpns.txt` flag to `sync_datasheets_digikey.py` (and
optionally the other distributor sync scripts) that reads one MPN per line
and downloads datasheets for each.

**Workaround:** Use `fetch_datasheet_digikey.py --search <MPN>` per MPN in
a loop. Works but doesn't update the `datasheets/index.json` manifest.

**Source:** Datasheet v2 extraction spec (2026-04-15).

---

## Test Harness Issues

### TH-033 — MEDIUM — No KiCad 10.0.0 test fixtures in the corpus

**Symptom:** Surveyed `repos/**/*.kicad_pcb` — first sampled file has
`(kicad_pcb (version 20211014) ...)` (KiCad 6). No corpus file is in
10.0.0 format (version 20260206). Jump from 9.x to 10.0.0 introduced 22
PCB version increments + 14 schematic increments — a major format
frontier that is completely uncovered by regression tests.

**Root cause:** Corpus was seeded before KiCad 10.0 was released. No
workflow has added 10.0-era fixtures since.

**Impact:**
- Bugs like KH-318 (via type always None — bare-token vs nested list) would
  have been caught immediately by any 10.0.0 regression assertion.
- New 10.0-only features (variants, jumper pads, backdrill, PCB barcodes,
  complex padstacks) have zero harness coverage.
- When 10.1 or 11 ships, we'll have the same problem again — the corpus
  should grow forward with KiCad.

**Fix:**
1. Curate 3–5 representative corpus boards, re-save them through KiCad
   10.0.0 (File → Save), commit alongside originals in a new subdirectory
   like `repos/10.0.0-samples/{owner}/{repo}-v10/*.kicad_*`.
2. Add smoke-level fixtures exercising 10.0-only features:
   - A board with blind + buried + micro vias (covers KH-318 fix)
   - A schematic with hidden pins (covers KH-319 fix)
   - A board using variants (forward-looking)
   - A footprint using a complex padstack (forward-looking)
3. Add `tests/test_kicad10_format.py` smoke asserting both parsers can
   open each fixture and produce a non-empty `findings[]`.
4. Backfill regression assertions on the new fixtures as part of the
   normal seed flow.

**Priority:** MEDIUM. Not urgent (10.0 parses today without crashing) but
high value (turns an invisible class of bugs into visible ones).

**Workaround:** Manual verification of parser output on any 10.0 file
the user supplies.

**Source:** KiCad 10.0.1 format compatibility review, 2026-04-16. See
[TODO-kicad-10-format-compat.md](TODO-kicad-10-format-compat.md) §3.

---

## Priority Queue

2 open issues.

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | TH-033 | MEDIUM | Medium — curate 3–5 KiCad 10.0.0 fixtures, re-save through KiCad 10, commit + seed assertions. |
| 2 | KH-312 | LOW | Small — add --mpn-list flag to sync scripts |
