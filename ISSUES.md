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

> 5 open issues.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-240: Battery-negative rails (BATT-/BAT-/VBAT-) not classified as ground

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during KH-238 spot-check
**Where:** `kicad-happy/skills/kicad/scripts/kicad_utils.py:937-955` in `is_ground_name()`

**Root cause:** `is_ground_name()` only recognizes GND/VSS/COM/0V variants. Battery-negative rails (`BATT-`, `BAT-`, `VBAT-`) used as circuit ground in single-supply designs are classified as ordinary signal nets. Cascades into missed feedback dividers, decoupling, sleep_current. Blast radius pending — harness KH-238 tail showed 0 BATT- stragglers, so may be narrow.

**Suggested fix:** Narrow keyword set for battery-ground (option a from original filing). Deliberately excludes V-/VEE which are legitimate bipolar supplies.

---

### KH-237: Switching frequency prefix-collision + duplicated table

**Severity:** HIGH
**Discovered:** 2026-04-11 during main-repo inspection brief (#5)
**Where:**
- `kicad-happy/skills/kicad/scripts/signal_detectors.py:29` (`_KNOWN_FREQS`, 21 entries, uses `str.startswith`)
- `kicad-happy/skills/emc/scripts/emc_rules.py:866` (`known_freqs` local copy, identical content, uses `prefix in val` — substring match, even looser)
- `signal_detectors.py:78` `_get_known_switching_freq()` — also uses `prefix in val` (substring)

**Blast radius:** 302 variants verified via DigiKey API on 2026-04-12. **175 confirmed mismatches** across 8 of 10 collision prefixes. Only LM259/LM257 (same-family, same freq) are clean. Worst offenders:

| Prefix | Table freq | Verified distinct freqs | Mismatches | Example |
|--------|-----------|------------------------|-----------|---------|
| TPS54 | 570 kHz | **11** (50–700 kHz) | 43/49 | TPS54302=400k, TPS54218=200k, TPS5430=500k |
| TPS62 | 2500 kHz | **10** (1000–4000 kHz) | 42/56 | TPS62203=1000k, TPS62840=1800k, TPS62088=4000k |
| TPS61 | 1000 kHz | **12** (50–3500 kHz) | 37/43 | TPS61041=50k, TPS61088=200k, TPS61253=3500k |
| TPS56 | 500 kHz | **9** (500–1400 kHz) | 30/38 | TPS560430=1100k, TPS563240=1400k, TPS561243=1280k |
| TPS63 | 2400 kHz | 5 (1250–2500 kHz) | 10/24 | TPS63001=1250k, TPS631000=2000k |
| TPS629 | 2200 kHz | 4 (200–2500 kHz) | 8/9 | TPS62933=200k, TPS62913=1000k |
| ADP2 | 700 kHz | 5 (200–2500 kHz) | 4/7 | ADP2503=2500k, ADP2301=1400k |
| LTC36 | 1000 kHz | 2 (1000–2000 kHz) | 1/1 | LTC3601=2000k |

Full verification data: `inspections/2026-04-11_prefix_collisions/freq_verified.json` (302 variants, 278 verified, 16 not found, 8 no param).

**Root cause:** The `_KNOWN_FREQS` design assumes one frequency per MPN prefix family. This is false for TI's TPS54/61/62/56/63 families where 3-4 character prefixes span dozens of distinct product families with different switching frequencies.

**Fix plan (main repo, 3 phases):**

**Phase 1: Extract + deduplicate (structural, no value changes)**
1. Move `_KNOWN_FREQS` from `signal_detectors.py:29` to `kicad_utils.py` as the single source of truth.
2. Delete the local `known_freqs` copy from `emc_rules.py:866`.
3. Add `from kicad_utils import _KNOWN_FREQS, lookup_switching_freq` in both consumers.
4. Standardize both call sites on `str.startswith` (drop the `prefix in val` substring match at `signal_detectors.py:78` and `emc_rules.py:890`).
5. Unit test: verify `_KNOWN_FREQS` is imported from one location and both callers produce the same results.

**Phase 2: Replace broad prefixes with exact-MPN entries**
Replace the 8 collision-prone prefixes with longer/exact entries from DigiKey data. Strategy per prefix:
- **TPS54**: Replace `'TPS54': 570e3` with 11 entries: `'TPS54331': 570e3, 'TPS5430': 500e3, 'TPS54302': 400e3, 'TPS54308': 350e3, 'TPS54218': 200e3, 'TPS546D2': 225e3, 'TPS5410': 500e3, 'TPS54202': 500e3, 'TPS54561': 100e3, 'TPS5405': 50e3, 'TPS5450': 500e3` (plus remaining sub-families grouped by frequency from the verified JSON).
- Same pattern for TPS62, TPS61, TPS56, TPS63, TPS629, ADP2, LTC36.
- Keep LM259 (150 kHz) and LM257 (52 kHz) as-is — verified no collisions.
- Keep the 10 non-colliding single-family entries (MP2307, MP1584, MP2359, AP3012, RT8059, SY820, MCP1640, MCP1603, XL6009, XL4015, MT3608) as-is.
- Source all replacement values from `freq_verified.json` (already populated).

**Phase 3: Add confidence + fallback**
- When `lookup_switching_freq()` finds a match, annotate with `"freq_source": "lookup_table"`.
- When no match, use the existing behavior (no frequency) but consider adding a `"freq_source": "unknown"` annotation.
- For adjustable-frequency regulators (e.g., TPS54335: 50 kHz–1.6 MHz), store the typical/default and annotate `"freq_range": [50e3, 1.6e6]`.

**Estimated effort:** Phase 1: ~30 min (structural refactor). Phase 2: ~1–2 hours (table rebuild from verified JSON, ~80 entries replacing 8). Phase 3: ~30 min (optional, deferred OK).

**Test plan:** Synthetic schematic fixtures with TPS54302 (→ 400 kHz), TPS62203 (→ 1000 kHz), TPS61088 (→ 200 kHz). Assert correct `switching_frequency_hz` in output. Assert EMC SW-001 harmonics shift to match. Run `quick_200` cross-section before/after for regression.

---

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

### KH-233: SCHEMAS dict missing 22 detector entries

**Severity:** MEDIUM
**Discovered:** 2026-04-10 by re-enabling `tests/test_detection_schema.py`
**Where:** `kicad-happy/skills/kicad/scripts/detection_schema.py`

22 `signal_analysis` keys present in real output but absent from SCHEMAS. Downstream code that walks SCHEMAS silently skips these detector classes.

---

### KH-230: Empty placed Value silently substituted with lib_symbol default

**Severity:** LOW
**Discovered:** 2026-04-10 by `validate/verify_parser.py`
**Where:** `kicad-happy/skills/kicad/scripts/analyze_schematic.py`

1 corpus file affected. Requires both duplicate-annotation AND empty Value.

---

## Priority Queue

1. **KH-237** — HIGH — Switching-freq prefix-collision. DigiKey verified, fix plan ready. Phase 1 (extract+dedup) first, then Phase 2 (table rebuild).
2. **KH-236** — MED — Vref prefix-collision. DigiKey verified, fix plan ready. Coordinate with KH-237 (shared `kicad_utils.py` refactor).
3. **KH-240** — MED — Battery-negative rails. Self-contained fix.
4. **KH-233** — MED — SCHEMAS backfill.
5. **KH-230** — LOW — Empty Value substitution.
