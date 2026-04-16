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

> 4 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-318 — HIGH — PCB via type detection always returns None (wrong s-expression shape)

**Symptom:** `via["type"]` field in `analyze_pcb.py` output JSON is `None`
for every via in every board we've ever analyzed. Microvias, blind vias,
and buried vias are indistinguishable from through vias in the analyzer
output.

**Root cause:** `kicad-happy/skills/kicad/scripts/analyze_pcb.py:916`
`extract_vias()` does:

```python
via_type = get_value(via, "type")  # blind, micro, etc.
```

`get_value(node, "type")` looks for a nested `(type X)` child. But KiCad
has never emitted that shape — the via type is a **bare token** between
`(via` and `(at ...)`:

- Through: `(via (at ...) (size ...) ...)` (no token, default)
- Blind: `(via blind (at ...) ...)`
- Buried: `(via buried (at ...) ...)` (new in 10.0, file version 20250926)
- Microvia: `(via micro (at ...) ...)`

Verified against KiCad source 10.0.0 writer at
`pcbnew/pcb_io/kicad_sexpr/pcb_io_kicad_sexpr.cpp:2609` and the parser at
`pcbnew/pcb_io/kicad_sexpr/pcb_io_kicad_sexpr_parser.cpp:7344` (expects
bare tokens `T_blind`, `T_buried`, `T_micro`). Verified against real corpus
files — every via in every corpus `.kicad_pcb` uses bare-token form.

**Impact:**
- Any detector that relies on `via.get("type") == "micro"` or similar is
  operating on always-None. Need to audit callers.
- In 10.0.0+ files, `BLIND_BURIED` is split into distinct `blind` and
  `buried` tokens — layer-stack sanity and blind-via-depth rules cannot
  distinguish the two.
- Silent false negatives: we never flag problematic microvia sizes because
  we never detect they're microvias.

**Fix:** In `extract_vias()` replace the `get_value(via, "type")` line with
bare-token scan:

```python
via_type = "through"
for child in via[1:]:
    if child in ("blind", "buried", "micro"):
        via_type = child
        break
```

Then emit `via_type` into the output dict unconditionally (not just when
non-None). Audit downstream consumers: search
`kicad-happy/skills/**/*.py` for `via.*["type"]` / `via.*\.get\("type"\)`
and verify the new string values are handled.

**Workaround:** None — there's no way for callers to distinguish via types
today.

**Source:** KiCad 10.0.1 format compatibility review, 2026-04-16. See
[TODO-kicad-10-format-compat.md](TODO-kicad-10-format-compat.md) §1.

---

### KH-319 — MEDIUM — Schematic `(hide yes)` boolean not detected by `has_flag()`

**Symptom:** Hidden pins (and potentially other objects with `(hide yes)`)
are reported as visible in analyzer output on any schematic saved by KiCad
9.0+ or 10.0+.

**Root cause:**
`kicad-happy/skills/kicad/scripts/analyze_schematic.py:212` uses:

```python
hidden = has_flag(pin, "hide")
```

`has_flag()` at `sexp_parser.py:209-211` is `return flag in node` —
membership test on the top-level list. This works for the legacy bare-token
form `(pin ... hide ...)` but fails for the post-20241004 form
`(pin ... (hide yes) ...)` where `hide` is inside a sub-list.

The inline comment at the caller acknowledges the new form
("KiCad uses `(hide yes)` inside pin node") but the `has_flag()`
implementation still uses bare-membership. Affects every `.kicad_sch` file
saved by KiCad ≥9.0 (9.0.8 ships schematic version 20250114; the boolean
format change landed at 20241004).

Verified against KiCad 10.0.0 parser at
`eeschema/sch_io/kicad_sexpr/sch_io_kicad_sexpr_parser.cpp` where
`T_hide → parseMaybeAbsentBool(true)` handles the new boolean form.

**Impact:**
- Hidden pins are not flagged as hidden. Affects power-pin detection on
  multi-unit symbols, ERC-style checks, pin-by-pin net attribution.
- Same `has_flag()` pattern is used for `in_bom`, `on_board`, `dnp`,
  `exclude_from_sim`, `fields_autoplaced`, `locked`, etc. — all of which
  have migrated to `(X yes/no)` form in 10.0.0. Each call site needs
  audit.

**Fix (narrow):** Replace `has_flag(pin, "hide")` with a helper:

```python
def is_hidden(node: list) -> bool:
    if "hide" in node:
        return True
    hide = find_first(node, "hide")
    if hide and len(hide) >= 2 and str(hide[1]).lower() in ("yes", "true"):
        return True
    return False
```

**Fix (broad):** Upgrade `has_flag()` in `sexp_parser.py` to also match
`(flag yes/true)` sub-lists. Backward compatible with old format; fixes all
callers at once:

```python
def has_flag(node: list, flag: str) -> bool:
    if flag in node:
        return True
    sub = find_first(node, flag)
    return bool(sub and len(sub) >= 2 and str(sub[1]).lower() in ("yes", "true"))
```

Broad fix is safer (single choke point, no missed call sites). Narrow fix
is more explicit. Recommend **broad** — the change is semantically
equivalent for old files and correctly handles new ones.

**Workaround:** None — hidden-pin signals are lost.

**Source:** KiCad 10.0.1 format compatibility review, 2026-04-16. See
[TODO-kicad-10-format-compat.md](TODO-kicad-10-format-compat.md) §2.

---

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

4 open issues.

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | KH-318 | HIGH | Small — replace `get_value(via, "type")` with bare-token scan in `analyze_pcb.py:916`. Audit downstream consumers of `via["type"]`. |
| 2 | KH-319 | MEDIUM | Small — upgrade `has_flag()` in `sexp_parser.py:209` to also match `(flag yes/true)` sub-lists. Covers all callers at once. |
| 3 | TH-033 | MEDIUM | Medium — curate 3–5 KiCad 10.0.0 fixtures, re-save through KiCad 10, commit + seed assertions. |
| 4 | KH-312 | LOW | Small — add --mpn-list flag to sync scripts |
