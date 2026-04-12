# Issue Tracker (Harness)

Tracker for harness-owned issues: DigiKey-dependent verification tasks,
harness code bugs, and corpus-specific items. For the full kicad-happy
issue tracker see `kicad-happy/ISSUES.md` (main repo, gitignored working doc).

> **2026-04-12 reorganization:** Main-repo issues moved to main-repo
> `ISSUES.md`. The old findings-triage numbers (KH-241 through KH-273) were
> reassigned contiguously in the main-repo tracker starting from KH-241.
> Pre-existing open bugs (KH-230, KH-233, KH-240) keep their original
> numbers in both trackers. This file retains only harness-owned items
> (KH-236, KH-237, TH-015).

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

Old KH-xxx numbers (KH-001 through KH-240) are globally unique and never
reused. The main-repo tracker continues from KH-241. New harness-side
issues use KH numbers continuing from **KH-276** (the next available after
the main-repo renumbering). Next TH number: **TH-016**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## Transferred to Main Repo

The old findings-triage issues (KH-241 through KH-273) have been
reassigned contiguously starting from KH-241 in the main-repo tracker.
The new numbers follow the same order but are grouped by category
(core bugs, then roadmap themes). Two previously unfiled issues also
got numbers: KH-259 (hierarchical-sheet divider miss), KH-260
(op-amp-as-regulator).

Pre-existing open bugs KH-230, KH-233, KH-240 keep their original
numbers in both trackers.

Full write-ups for all transferred issues are preserved in
`TODO-combined-findings.md` in the main repo.

---

## Harness-Owned Issues

### KH-237: Switching frequency prefix-collision + duplicated table

**Severity:** HIGH
**Discovered:** 2026-04-11 during main-repo inspection brief (#5)
**Where:**
- `kicad-happy/skills/kicad/scripts/signal_detectors.py:29` (`_KNOWN_FREQS`, uses `str.startswith`)
- `kicad-happy/skills/emc/scripts/emc_rules.py:866` (`known_freqs` local, uses `prefix in val` — substring!)

**Blast radius:** **10 real mixed-family prefix collisions**, 1,300+ regulator instances with likely-wrong switching frequencies. Affects `signal_analysis.power_regulators[].switching_frequency_hz` in schematic.json AND downstream EMC SW-001 harmonic-band calculations.

**Confirmed landmine:** prefix `"TPS54"` maps to 570 kHz (correct for TPS54331). But `"TPS54302".startswith("TPS54")` is True, and TPS54302's actual center frequency is ~400 kHz. At least 78 corpus instances wrong under the TPS54 prefix alone.

**All 10 real collision prefixes:** TPS54 (317 instances), TPS62 (292), TPS61 (210), TPS56 (145), TPS63 (142), LM259 (107), LM257 (101), TPS629 (47), LTC36 (16), ADP2 (13).

**Table drift between locations:** Identical content (21 prefixes) but matchers differ: `signal_detectors.py` uses `startswith` (anchored), `emc_rules.py` uses `prefix in val` (substring). Substring is looser on 8 prefixes.

**Suggested fix:**
1. Extract `_KNOWN_FREQS` into `kicad_utils.py`. One source of truth.
2. Standardize to `startswith` everywhere.
3. Replace broad prefix entries with exact-MPN or longer-prefix entries for collisions.
4. DigiKey-verify replacement values before shipping. Stub at `inspections/2026-04-11_prefix_collisions/freq_verified.json` (302 variants).

**Test plan:** Synthetic schematic with TPS54302. Assert `switching_frequency_hz == 400e3` (not 570e3). Assert EMC SW-001 harmonics shift accordingly.

**Deferred:** DigiKey parametric verification (~60-90 min API queries). Do NOT patch values from this report alone.

---

### KH-236: Regulator Vref prefix-collision in _REGULATOR_VREF table

**Severity:** MEDIUM
**Discovered:** 2026-04-11 during main-repo inspection brief (#4)
**Where:** `kicad-happy/skills/kicad/scripts/kicad_utils.py:31` (`_REGULATOR_VREF`, longest-prefix-match at line 172)
**Blast radius:** **27 real mixed-family prefix collisions**, 1,600+ regulator instances. Confirmed TPS5430 landmine: 29 instances get Vref=1.221V when TPS54302/TPS54308 family actual is 0.596V.

**Root cause:** Longest-prefix-match collision when newer part families share a prefix with older table entries. Example: `"TPS54302".startswith("TPS5430")` → True → wrong Vref.

**Top collision prefixes:** LM78 (480), SY8 (191), TPS7A (159), TPS56 (145), LM259 (107), TPS5430 (95, confirmed wrong), AP736 (79), MP2 (66), LM337 (51), AP73 (50).

Full data at `inspections/2026-04-11_prefix_collisions/vref_prefix_collisions.md` and `vref_verified.json` (337 variants pre-populated).

**Suggested fix:** DigiKey-verify ~337 variants. Replace broad prefixes with exact-MPN or longer-prefix entries. Consider restructuring from longest-prefix-match to exact-MPN-prefix map.

**Test plan:** Synthetic TPS54302 with feedback divider. Assert `estimated_vout ≈ 2.93V` (not 6.01V).

**Deferred:** DigiKey verification (60-90 min). Do NOT patch from this report alone.

---

## Test Harness Issues

(None currently open.)

---

## Priority Queue

1. **KH-237** — HIGH — Switching-freq prefix-collision. Needs DigiKey verification.
2. **KH-236** — MED — Vref prefix-collision. Same DigiKey session.

> 2 open issues.
