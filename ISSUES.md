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
maximum. Next KH number: **KH-317**. Next TH number: **TH-033**.

> 4 open issues.

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

### KH-314 — LOW — `analyze_thermal.py` has no `--schema` command

**Symptom:** All other analyzers expose `--schema` for machine-readable schema
introspection (`analyze_schematic.py --schema`, `analyze_pcb.py --schema`, etc.).
`analyze_thermal.py --schema` errors with "expected --schematic argument".

**Root cause:** `analyze_thermal.py` requires `--schematic` and `--pcb` as
mandatory args, and doesn't short-circuit when `--schema` is requested.

**Fix:** Add a `--schema` branch at the top of the analyzer that prints
the output envelope (analyzer_type, schema_version, summary, findings,
trust_summary, elapsed_s) and exits before input parsing.

**Repro:** `python3 skills/kicad/scripts/analyze_thermal.py --schema`

**Source:** Batch 20 Phase 5 ad-hoc confidence tests, `--schema` drift
audit (2026-04-16). Phase 6 sync covered the other 5 analyzers but skipped
thermal.

---

### KH-315 — LOW — `analyze_schematic.py --schema` has extra `hierarchy_context` key

**Symptom:** `analyze_schematic.py --schema` documents a `hierarchy_context`
top-level key that doesn't appear in real analyzer output.

**Root cause:** `hierarchy_context` was probably removed or moved from the
real output path but not synced in the `--schema` skeleton.

**Fix:** Either drop `hierarchy_context` from the `--schema` envelope, or
re-add it to real output if it was unintentionally removed.

**Repro:**
```
python3 skills/kicad/scripts/analyze_schematic.py --schema | jq 'keys | .[]' | grep hierarchy_context
# Returns: "hierarchy_context"
python3 skills/kicad/scripts/analyze_schematic.py OpenMowerMainboard.kicad_sch | jq 'has("hierarchy_context")'
# Returns: false
```

**Source:** Batch 20 Phase 5 ad-hoc confidence tests, `--schema` drift
audit (2026-04-16).

---

### KH-316 — LOW — `analyze_schematic.py` and `analyze_pcb.py` produce nondeterministic `findings[]` order

**Symptom:** Running `analyze_schematic.py` (or `analyze_pcb.py`) twice on
the same input produces outputs with the same set of findings but in
different array order. Same content, same count, different ordering.

**Root cause:** Likely set/dict iteration somewhere in the finding-emission
path. Probable suspects: `set()` of detector results flattened to a list,
or `dict().values()` where dict insertion order is incidental (dict order is
stable in Python 3.7+ but upstream set usage isn't).

**Repro:**
```
python3 analyze_schematic.py OpenMowerMainboard.kicad_sch -o /tmp/a.json
python3 analyze_schematic.py OpenMowerMainboard.kicad_sch -o /tmp/b.json
# Strip elapsed_s, diff — findings[] order differs across runs.
```

On OpenMower: 236 findings, same set, different order in `findings[]` and
`protocol_compliance` sections. `analyze_emc.py` is deterministic — only
schematic and PCB show this.

**Impact:**
- Byte-identical baseline snapshots aren't achievable without sorting.
- Git-friendly output diffs are noisier than necessary.
- Assertion matching is unaffected (assertions filter by detector/rule_id,
  not array position).

**Fix:** Sort `findings[]` (and similar list-of-dict sections) by a stable
key before serialization — e.g., `(rule_id, detector, summary)`. A single
`sort_findings(findings)` pass at the end of `main()` would cover both
analyzers.

**Source:** Batch 20 Phase 5 ad-hoc confidence tests, determinism check
(2026-04-16). Pre-existing behavior, not a Batch 20 regression.

---

## Test Harness Issues

## Priority Queue

4 open issues.

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | KH-312 | LOW | Small — add --mpn-list flag to sync scripts |
| 2 | KH-314 | LOW | Trivial — add --schema branch to analyze_thermal.py |
| 3 | KH-315 | LOW | Trivial — reconcile hierarchy_context key |
| 4 | KH-316 | LOW | Small — sort findings[] before serialization |
