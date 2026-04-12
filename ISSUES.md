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

Last updated: 2026-04-12

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new
number, check both ISSUES.md (open) and FIXED.md (closed) for the current
maximum. Next KH number: **KH-276**. Next TH number: **TH-016**.

> 2 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-236: Regulator Vref prefix-collision in _REGULATOR_VREF table

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during main-repo inspection brief (#4)
**Where:** `kicad-happy/skills/kicad/scripts/kicad_utils.py:31` (`_REGULATOR_VREF`, 74 entries, longest-prefix-match at line 172)

**Blast radius:** 337 variants verified via DigiKey API on 2026-04-12. **185 confirmed mismatches** across 19 collision prefixes.

Critical findings:

| Prefix | Table Vref | Verified mismatches | Root cause |
|--------|-----------|-------------------|------------|
| LM78 | 1.25 V | 19/19 (100%!) | Fixed-output regulators (LM7805=5V, LM7812=12V). Vref concept doesn't apply — these have no FB pin. |
| TPS7A | 1.19 V | 33/35 | TPS7A family spans 0.8V–1.24V Vref across sub-families |
| AP73 | 0.6 V | 22/22 (100%!) | Fixed-output LDOs matched as adjustable (AP7333-33=3.3V, AP7384-50=5V) |
| AP736 | 0.8 V | 14/17 | Fixed-output variants (AP7361C-33=3.3V) mixed with adjustable (AP7365=0.8V) |
| TPS56 | 0.6 V | 25/38 | TPS560200=0.8V, TPS563200=0.76V, TPS563300=0.8V — multiple Vref values |
| LM259 | 1.23 V | 14/15 | Fixed-output variants (LM2596S-5=5V, LM2596S-3.3=3.3V) |
| MIC29 | 1.24 V | 9/9 (100%!) | Fixed-output (MIC2940A-5.0=5V, MIC29301-3.3=3.3V) |
| MP2 | 0.8 V | 12/16 | Mixed Vref (MP2338=0.5V, MP2359=0.81V, MP28167=1.0V) |
| TPS6102 | 0.595 V | 7/7 (100%!) | TPS61023=2.2V output, not Vref! DigiKey returns Vout not Vref for boost converters |
| LM2267 | 1.285 V | 2/4 | Fixed-output variants (LM22676MR-5=5V) |

Full verification data: `inspections/2026-04-11_prefix_collisions/vref_verified.json` (337 variants, 256 verified, 71 not found, 10 no param).

**Root causes (three distinct failure modes):**
1. **Fixed-output regulators stored with Vref**: LM78xx, LM259x-5, AP73xx-33, MIC29xxx-3.3 are fixed-output parts with no feedback pin. The table stores Vref for the adjustable variant, which is meaningless for fixed-output parts. The `lookup_regulator_vref()` function at `kicad_utils.py:135` already has a fixed-output suffix parser (lines 147–167) that runs BEFORE the prefix lookup — so these should be caught. **But** the prefix lookup at line 172 doesn't distinguish fixed vs adjustable, so if the suffix parser misses (e.g., `LM7805_TO220` — suffix is `_TO220` not a voltage), it falls through to the wrong Vref.
2. **Prefix too broad**: TPS7A, TPS56, MP2, AP736 span sub-families with different Vref values. Same problem as KH-237 — need longer/exact prefixes.
3. **DigiKey returns Vout not Vref for boost converters**: TPS6102x, TPS6103x, TPS6300x/6301x verification data shows output voltage (2.2V, 5V) rather than the internal reference voltage. The table's 0.595V for TPS6102 is likely correct (from the datasheet). These are false mismatches in the verification data — need manual review.

**Fix plan (main repo, 3 phases, coordinate with KH-237):**

**Phase 1: Fix the fixed-output suffix parser**
The suffix parser at `kicad_utils.py:147-167` already handles `-3.3`, `-33`, `-12` etc. but misses:
- `LM7805` (no separator, just digits at end)
- `LM7805_TO220` (package suffix after voltage)
- `AP7333-33SAG` (suffix after the voltage digits)
Fix: extend the regex to handle these patterns. This alone eliminates ~50% of the mismatches (all the LM78xx, LM259x-fixed, MIC29xxx-fixed, AP73xx-fixed cases) because the suffix parser runs first.

**Phase 2: Replace broad prefixes with longer entries**
Same strategy as KH-237 Phase 2:
- Replace `'TPS7A': 1.19` with specific sub-families: `'TPS7A49': 1.19, 'TPS7A25': 1.24, 'TPS7A92': 0.8, 'TPS7A03': (fixed-output, remove)` etc.
- Replace `'AP73': 0.6` with `'AP7362': 0.6, 'AP7363': 0.6` (actual adjustable parts). Remove AP7333/AP7381/AP7384 (all fixed-output — suffix parser should catch them).
- Similarly for TPS56, MP2, LT860.
- Source values from `vref_verified.json`, cross-referenced against datasheets for boost converter cases.

**Phase 3: Remove entries that duplicate the suffix parser**
Entries like `'LM78': 1.25` and `'LM317': 1.25` are redundant — LM317 is adjustable with Vref=1.25V, and LM7805 is fixed at 5V. The suffix parser already handles LM7805→5V correctly (when the suffix is detected). Keep only the adjustable-variant entries. Remove or reclassify entries for parts that are only sold as fixed-output (no adjustable variant exists).

**Estimated effort:** Phase 1: ~1 hour (regex + tests). Phase 2: ~2 hours (table rebuild from verified JSON + manual boost converter review). Phase 3: ~30 min (audit + cleanup).

**Test plan:** Fixture with LM7805 → assert Vref not used (fixed_suffix=5V takes precedence). Fixture with TPS7A4901 → assert Vref=1.19V. Fixture with TPS54302 feedback divider → assert estimated Vout based on correct Vref=0.596V (not 1.221V). Run `quick_200` before/after.

---

### KH-230: Empty placed Value silently substituted with lib_symbol default

**Severity:** LOW
**Discovered:** 2026-04-10 by `validate/verify_parser.py`
**Where:** `kicad-happy/skills/kicad/scripts/analyze_schematic.py`

1 corpus file affected. Requires both duplicate-annotation AND empty Value.

---

## Priority Queue

1. **KH-236** — MED — Vref prefix-collision. DigiKey verified, fix plan ready.
2. **KH-230** — LOW — Empty Value substitution.
