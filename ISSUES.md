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
number: **KH-228**. Next TH number: **TH-011**.

> 13 open issues (10 KH-*, 3 TH-*) from Layer 3 batch reviews (2026-04-09).

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-218 — Vref heuristic wrong for TPS62912, TPS73601, LM22676 (HIGH)

**Symptom:** Regulator output voltage estimates are wildly wrong, generating false
`vout_net_mismatch` warnings. TPS62912 estimated 2.68V instead of 3.58V (+3V6_RF),
TPS73601 estimated 2.09V instead of 4.20V (+4V2_RF), LM22676-ADJ estimated 1.55V
instead of 3.31V (+3V3).

**Root cause:** The Vref lookup table does not include these parts. Falls back to generic
0.6V heuristic. Actual Vref values: TPS62912=0.8V, TPS73601/TPS736xx=1.204V,
LM22676=1.285V.

**Impact:** Every regulator using these parts gets wrong Vout estimate. Cascades into
false warnings in inrush_analysis and power_sequencing_validation. At least 6 instances
across 3 repos in this batch.

**File:** `analyze_schematic.py`, Vref lookup table.

**Repro:** `dpmj/masters-thesis-lora-gateway...` (3x TPS62912, 1x TPS73601),
`biomimetics/MRIRobot_PCB` (1x LM22676-ADJ), `jaromir-sukuba/nvm` (1x MCP1700-33
correctly looked up -- shows the mechanism works when part is in table).

**Discovered:** 2026-04-09 via Layer 3 batch review (3 repos).

---

### KH-219 — Load switches (TPS22917, TPS2051C) classified as LDO topology (MEDIUM)

**Symptom:** Power distribution switches with no voltage regulation are classified as
`topology: LDO` in power_regulators. They should be `load_switch` or `power_switch`.

**Root cause:** Topology detection defaults to LDO when it can't find an inductor
(switching) or identify the specific part as a load switch. The TPS22917 and TPS2051C
are listed in power_path as load switches but also appear in power_regulators as LDOs,
creating contradictory output.

**Impact:** Misleading topology label. The power_path section already has the correct
classification, so downstream analysis that reads power_path is unaffected, but
power_regulators consumers get wrong info.

**File:** `analyze_schematic.py`, regulator topology detection.

**Repro:** `dpmj/masters-thesis-lora-gateway...` (U501 TPS22917),
`Dylanfg123/Zebra-X` (U901 TPS2051CDBV).

**Discovered:** 2026-04-09 via Layer 3 batch review (2 repos).

---

### KH-220 — Active oscillators with custom lib symbols misclassified as connector (MEDIUM)

**Symptom:** ECS-2520MV series CMOS oscillators (33.333 MHz, 25 MHz, 13 MHz) classified
as `type: connector` instead of `oscillator`. Only 1 of 4 oscillators correctly typed.
Cascading false positive in esd_coverage_audit (oscillators flagged as connectors needing
ESD protection).

**Root cause:** KH-208 fix added lib_id overrides for standard KiCad library prefixes
(`Oscillator:*`), but custom library symbols (e.g., `SamacSys_Parts:ECS-2520MV...`)
don't match. The component description contains "XTAL OSC XO" and "Standard Clock
Oscillators" but description field is not checked for oscillator classification.

**Impact:** Missed crystal_circuits detection (3 of 4 oscillators missed), missed
clock_distribution, false ESD audit entries. Affects any design using custom oscillator
library symbols.

**File:** `kicad_utils.py`, `classify_component()` — needs description field check for
oscillator keywords.

**Repro:** `Dylanfg123/Zebra-X` — X400 (33.333 MHz), X800 (25 MHz), X900 (13 MHz) all
misclassified. X300 (12 MHz, different lib symbol) correctly typed.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-221 — Opamp TIA feedback classified as "compensator"; false voltage dividers (MEDIUM)

**Symptom:** Transimpedance amplifiers (R + C feedback from output to inverting input,
with low-value input resistor) are classified as `compensator` topology. Additionally,
the feedback R and input R are detected as a voltage divider (100x false dividers in nvm
repo). Spurious "capacitive load on output" warnings generated for the feedback cap.

**Root cause:** Opamp topology classification sees R+C feedback and labels it
`compensator` (control-loop compensation). Voltage divider detector sees two series
resistors to an opamp inverting input and calls it a divider. Capacitive load detector
sees cap connected to output without checking if it's in the feedback path.

**Impact:** 100 false "compensator" labels, 100 false voltage dividers, 100 false
stability warnings in the nvm nanovoltmeter (110-opamp parallel LNA). Massive noise in
outputs for precision analog designs.

**File:** `analyze_schematic.py` — opamp topology classification, voltage divider
detector, capacitive load warning.

**Repro:** `jaromir-sukuba/nvm` — 100 MCP6V51 instances with 10k feedback + 1nF cap +
100R input resistor.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-222 — Multi-unit symbol duplication in led_audit, sleep_current, usb_compliance (MEDIUM)

**Symptom:** Components in sub-sheets with multi-unit symbols (e.g., dual NUCLEO-F446RE)
generate duplicate entries. D115/D116 appear twice in led_audit, 4x in sleep_current.
USB-C connector J29 appears twice in usb_compliance. Inflates counts and current
estimates.

**Root cause:** Multi-unit symbols create multiple component entries per unit. Detectors
that iterate components don't deduplicate by reference designator, counting the same
physical component once per unit.

**Impact:** Inflated LED counts, inflated sleep current estimates, doubled USB compliance
entries. Affects any design using multi-unit symbols in sub-sheets.

**File:** `analyze_schematic.py` — led_audit, sleep_current_audit, usb_compliance
sections.

**Repro:** `biomimetics/MRIRobot_PCB` — U1/U2 (NUCLEO-F446RE) dual symbols cause D115,
D116, J29, R88-R93 duplications.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-223 — Power sequencing cascade not resolved into power_tree ordering (MEDIUM)

**Symptom:** power_tree shows all regulators at `sequence_order: 0` with
`enable_type: always_on` despite actual PG→EN cascading correctly detected in the
`dependencies` section. The cascade U101→PG_1V0→U102→PG_1V8→U103→PG_1V35→U104 is
known but not reflected in the tree.

**Root cause:** power_sequencing_validation detects EN/PG net connections in
`dependencies` but `power_tree` does not resolve the chain into proper sequence ordering.
The information exists but isn't propagated.

**Impact:** Power sequencing analysis gives no useful ordering information despite having
the data to compute it.

**File:** `analyze_schematic.py` — power_sequencing_validation, power_tree generation.

**Repro:** `Dylanfg123/Zebra-X` — 4 SY8003ADFC regulators with PG cascade chain all
shown as order 0.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-224 — Multi-unit IC power_domains only shows one unit's rails (LOW)

**Symptom:** Zynq U200 power_domains lists only `["+3V3"]` but the IC connects to 7
distinct power rails (+1V0, +1V35, +1V8, +1V8_PLL, +3V3, +0V675_REF, GND) across
multiple symbol units. Related to KH-216 pattern but specifically for power domain
aggregation.

**Root cause:** Power domain extraction reads power pins from individual symbol units
without aggregating across all units of the same multi-unit component.

**File:** `analyze_schematic.py` — power domain IC rail extraction.

**Repro:** `Dylanfg123/Zebra-X` — U200 (XC7Z010) has power pins spread across PS, PL,
DDR, power units.

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-225 — LM2664 charge pump classified as LDO topology (LOW)

**Symptom:** LM2664M6 switched-capacitor voltage inverter (+3.3V → -3.3V) classified as
`topology: LDO`. It has no linear regulation behavior — it's a charge pump.

**Root cause:** Same default-to-LDO fallback as KH-219 but for a different class of
device. The LM2664 is a voltage inverter, not a regulator or switch.

**Impact:** Misleading topology label for charge pump ICs. Minor — affects few designs.

**File:** `analyze_schematic.py` — regulator topology detection.

**Repro:** `esl-epfl/VersaSens` — IC14 (LM2664M6/NOPB).

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-226 — NUCLEO dev board module classified as switching regulator (LOW)

**Symptom:** U1 (NUCLEO-F446RE) classified as a power_regulator with `switching`
topology. It's an STM32 development board module (MCU), not a voltage regulator. Has
both power input (+5V, +3.3V) and output pins but is a consumer.

**Root cause:** The component has power pins in both directions (input and output from
its onboard regulator), triggering regulator detection heuristics.

**File:** `analyze_schematic.py` — regulator detection.

**Repro:** `biomimetics/MRIRobot_PCB` — U1 (NUCLEO-F446RE).

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

### KH-227 — Logic gates (inverter, NAND) misclassified as level_shifter_ic (LOW)

**Symptom:** SN74LVC1G14DBV (Schmitt inverter) and SN74LVC1G00DBV (NAND gate) classified
as `level_shifter_ic` in level_shifters section. These are logic gates in an RF TX/RX
control path, not level shifters.

**Root cause:** Level shifter detector matches any small IC between two voltage domains
without checking if the IC is a known logic gate family (74-series).

**Impact:** False level shifter entries. Minor — only affects designs with logic gates
between voltage domains.

**File:** `analyze_schematic.py` — level shifter detection.

**Repro:** `dpmj/masters-thesis-lora-gateway...` — U1104 (SN74LVC1G14), U1103
(SN74LVC1G00).

**Discovered:** 2026-04-09 via Layer 3 batch review.

---

## Deferred

### KH-205 — D+ net lost in KiCad 5 legacy net resolution (MEDIUM)

**Status:** Unreproducible — referenced file `Mouse/Mouse.sch` not found in repo
`prashantbhandary/Meshmerize-MicroMouse-`. No `.sch` files exist in the checked-out
repo (all converted to `.kicad_sch`). Reopen if repro file is located.

**Discovered:** 2026-04-08 via v1.2 pre-release assertion suite.

---

## Priority Queue (open issues, ordered by impact)

1. KH-218 — Vref heuristic wrong for TPS62912, TPS73601, LM22676 (HIGH)
2. KH-219 — Load switches classified as LDO topology (MEDIUM)
3. KH-220 — Active oscillators with custom libs misclassified as connector (MEDIUM)
4. KH-221 — Opamp TIA feedback as "compensator"; false voltage dividers (MEDIUM)
5. KH-222 — Multi-unit symbol duplication in led_audit/sleep_current/usb_compliance (MEDIUM)
6. KH-223 — Power sequencing cascade not resolved into power_tree ordering (MEDIUM)
7. KH-224 — Multi-unit IC power_domains only shows one unit's rails (LOW)
8. KH-225 — LM2664 charge pump classified as LDO topology (LOW)
9. KH-226 — NUCLEO dev board module classified as switching regulator (LOW)
10. KH-227 — Logic gates misclassified as level_shifter_ic (LOW)
11. TH-009 — Constants audit doesn't flag Vref heuristic fallback coverage gap (MEDIUM)
12. TH-010 — Legacy findings cleanup: missing IDs, non-standard analyzer_type values (LOW)
13. TH-011 — batch_review.py: multi-project repos select best per-project set (LOW — done)

---

## Test Harness Issues

### TH-009 — Constants audit doesn't flag Vref heuristic fallback coverage gap (MEDIUM)

**Symptom:** KH-218 (wrong Vref for TPS62912/TPS73601/LM22676) should have been caught
by `audit_constants.py corpus`, which cross-references the `_REGULATOR_VREF` lookup
table against corpus outputs. But the audit only counts table entries that matched or
didn't match — it does not check how many corpus regulators **fell back to the 0.6V
heuristic** because their part wasn't in the table.

**Scope:** 1,276 regulators across 368 unique parts hit the heuristic fallback (9.2% of
13,808 total). The data is available in outputs: `vref_source: "heuristic"` and
`assumed_vref: 0.6`. The audit just doesn't check it.

**Fix:** `audit_constants.py corpus` should scan `power_regulators` in all schematic
outputs, collect entries where `vref_source == "heuristic"`, and report:
- Count of heuristic-fallback regulators
- Top N unique part values by frequency
- Flag any part appearing 5+ times as a candidate for the lookup table

This would have surfaced TPS62912 (13 hits), TLV62569 (69 hits), AP64501 (26 hits)
etc. as missing table entries.

**Discovered:** 2026-04-09 — KH-218 found via Layer 3 review, not constants audit.

---

### TH-010 — Legacy findings cleanup: missing IDs, non-standard analyzer_type values (LOW)

**Symptom:** `batch_review.py status` shows 27 findings with `unknown` type, 3 with
`analyze_schematic`/`analyze_pcb`/`analyze_gerbers` (wrong prefix), and many old findings
with no ID (pre-FND era). These are from early manual reviews before the subagent workflow
was standardized.

**Scope:** ~30 findings with non-standard types, ~900+ findings with no `id` field.
Repos affected include Fescron/2ch-4-20mA-converter, Netlist-Studio/dut_hub_hw (22
findings with no id), torvalds/1590A, OLIMEX/USB-GIGABIT (analyze_* prefix), and
~1,000+ early findings across 1bitsquared, dbuchwald, etc.

**Fix:** Write a one-time migration script that:
1. Assigns FND-* IDs to all findings missing an `id` field
2. Normalizes `analyze_schematic` → `schematic`, `analyze_pcb` → `pcb`,
   `analyze_gerbers` → `gerber`
3. Sets `analyzer_type: "schematic"` for findings with no type (they're all schematic)
4. Re-renders findings.md for all affected repos

**Discovered:** 2026-04-09 via `batch_review.py status` type breakdown.

---

### TH-011 — batch_review.py: multi-project repos select best per-project set (LOW)

**Status:** Fixed. The `_collect_outputs()` function now groups outputs by project prefix
and selects the best matching set (schematic + PCB + gerber from the same project). For
multi-project repos (37% of corpus, 2,186 repos), this ensures cross-referencing between
analyzer types is meaningful. Previously, the best schematic and best PCB could come from
different projects in the same repo.

**Discovered:** 2026-04-09 during batch_review.py enhancement.
