# Issue Tracker

Tracker for kicad-happy analyzer bugs (KH-*) and test harness improvements (TH-*).
Contains enough detail to resume work with zero conversation history.

> **Protocol**: When fixing issues, remove them from this file and add to FIXED.md in the
> same session. See README.md "Issue tracking protocol" for full details. Closed issues
> with root cause and verification details are in [FIXED.md](FIXED.md).

Last updated: 2026-03-15

---

## Numbering convention

Issue numbers are **globally unique and never reused**. Before assigning a new number,
check both ISSUES.md (open) and FIXED.md (closed) for the current maximum. Next KH
number: **KH-101**. Next TH number: **TH-008**.

---

## Severity levels

- **CRITICAL** -- Causes cascading failures, major data loss, or makes large portions of output unusable
- **HIGH** -- Significant accuracy impact, many false positives/negatives, or missing important data
- **MEDIUM** -- Localized false positives or misclassifications; workarounds exist
- **LOW** -- Cosmetic, minor noise, or edge cases affecting few files

---

## kicad-happy Analyzer Issues

### KH-078 — `build_net_map()` crashes with `TypeError: unhashable type: 'list'` (MEDIUM)

**Affected**: `kicad_schemes` repo — `24V_shield/ps_2561_5_v_single_channel_kicad.kicad_sch`
**File**: `analyze_schematic.py`, `build_net_map()` line ~916
**Symptom**: `label_keys.setdefault(local_key, []).append(k)` fails because `local_key` is a list instead of a hashable type. The label's position or name is being parsed as a list rather than a string/tuple.
**Root cause**: Likely a malformed or unusual label s-expression in the `.kicad_sch` file where the label name/position parsing returns a list instead of a scalar value.
**Repro**: `python3 run/run_schematic.py --repo kicad_schemes`
**Impact**: Crashes the analyzer on this file; no output produced. Only one known affected file so far.


### KH-080 — Component classified as power symbol despite in_bom=yes (MEDIUM)

**Affected**: ethersweep
**File**: `analyze_schematic.py`, power symbol identification ~line 639
**Symptom**: DD4012SA (U4, Diodes Inc 1A buck converter) has lib_id `power:DD4012SA` and `in_bom=yes`. The analyzer treats it as a power symbol, excluding it from components, ic_pin_analysis, and power_regulators. The main power regulator converting +28V to TMC2209 VS rail becomes invisible.
**Fix direction**: Check `in_bom` flag before classifying as power symbol. Components with `in_bom=yes` should not be treated as power symbols regardless of library prefix.
**Findings**: FND-150

### KH-081 — Current sense false positives on Ethernet termination resistors (MEDIUM)

**Affected**: ethersweep
**File**: `signal_detectors.py`, current sense detection
**Symptom**: R4/R5 (33 ohm) detected as current sense shunts with nonsensical `max_current_100mV_A: 0.303`. These are standard Ethernet differential pair series termination resistors between W5500 TX/RX and HR911105A RJ45.
**Fix direction**: Add minimum resistance threshold or context-based filtering (e.g., connected to known Ethernet PHY TX/RX pins should disqualify from current sense).
**Findings**: FND-150

### KH-082 — TVS IC-packaged protection devices not detected (MEDIUM)

**Affected**: ISS-PCB
**File**: `signal_detectors.py`, protection device detection
**Symptom**: TVS1800DRV (U301, U302) from `Power_Protection:` library typed as "ic", not detected as protection device. ECMF02-2AMX6 (U108) USB ESD/CM filter also missed. Only discrete D-prefix TVS diodes (ESD321) are detected.
**Fix direction**: Add `Power_Protection:` library components to protection device detection. Check lib_id for protection-related keywords.
**Findings**: FND-153, FND-154


### KH-085 — RF chain detection keyword lists too narrow (MEDIUM)

**Affected**: vna
**File**: `signal_detectors.py`, `detect_rf_chains()` ~line 2614
**Symptom**: RF chain requires ≥2 recognized RF components, but keyword lists miss major IC families. Complete RF output chain with 7+ components returns empty `rf_chains[]`.
**Missing families**: ADRF (switches/attenuators), ADMV (tunable filters), MAAM (broadband amps, `maa-` pattern too narrow), HMC3xx (switches), LTC559x (power detectors), FPC0xx (couplers), XX1000 (doublers).
**Missing categories**: No attenuator, coupler, or power detector categories in RF chain model.
**Fix direction**: Expand keyword lists and add missing component categories. Extract `ki_description` from lib_symbols for description-based classification as a more robust approach.
**Findings**: FND-152


### KH-087 — Switching regulator output_rail missing (MEDIUM)

**Affected**: ISS-PCB, Power_HW
**File**: `signal_detectors.py`, regulator detection
**Symptom**: Switching regulators (TPS566242, TPS564247, MAX25262) report `input_rail` and `fb_net` but no `output_rail`. LDOs correctly have `output_rail`. Also, input_rail often null when connected through ferrite bead to named power rail.
**Fix direction**: Trace output rail from inductor/output cap connections. Trace through ferrite beads for input rail identification.
**Findings**: FND-155, FND-158


### KH-090 — LDO inverting flag incorrect for fixed-output LDOs (LOW)

**Affected**: ISS-PCB
**File**: `signal_detectors.py`, regulator topology detection
**Symptom**: TLV75733PDRV (fixed-output 3.3V LDO) marked as `inverting=true`. TLV757xx family is a standard positive fixed-output LDO.
**Fix direction**: Check for fixed-output LDOs (no FB pin, or fixed output voltage in part number) and set inverting=false.
**Findings**: FND-153


### KH-097 — CSYNC nets misclassified as chip_select (MEDIUM)

**Affected**: Duplicanator-Scart-Duplicator
**File**: `signal_detectors.py`, net classification
**Symptom**: CSYNC_IN/CSYNC_OUT1/CSYNC_OUT2 (composite sync video signals) classified as 'chip_select' due to 'CS' substring match. CSYNC/HSYNC/VSYNC are video synchronization signals.
**Fix direction**: Add CSYNC/HSYNC/VSYNC pattern exclusion before chip_select matching on 'CS' prefix.
**Findings**: FND-185


### KH-098 — Flyback diode not detected in drain-to-supply topology (MEDIUM)

**Affected**: KiDiff test cases
**File**: `signal_detectors.py`, transistor circuit analysis
**Symptom**: has_flyback_diode=false for Q3-Q10 MOSFET switches despite Schottky diodes D3-D10 with anode on drain net and cathode on VCC supply rail. Detector only checks drain-to-source diodes, missing the standard low-side switch flyback topology (drain to supply).
**Fix direction**: Extend flyback diode detection to check for diodes from drain net to any power supply rail (VCC, VIN, etc.), not just drain-to-source.
**Findings**: FND-191, FND-192


### KH-099 — I2S audio bus misidentified as I2C (MEDIUM)

**Affected**: NUS-CPU-03-Nintendo-64-Motherboard
**File**: `signal_detectors.py`, I2C detection
**Symptom**: 9480F.SDAT (I2S serial audio data) classified as I2C SDA. I2S uses SDAT/LRCK/BCLK which is distinct from I2C SDA/SCL. No I2S bus detector exists.
**Fix direction**: Exclude nets with I2S-related names (SDAT, LRCK, BCLK, WSEL) from I2C detection. Consider adding I2S bus detector.
**Findings**: FND-172


### KH-100 — WiFi/BT modules classified as power regulators (LOW)

**Affected**: OtterCam-s3
**File**: `signal_detectors.py`, regulator detection
**Symptom**: AP6236 WiFi/BT combo module classified as power regulator with topology ic_with_internal_regulator because it has an inductor on its power pin (filter inductor, not switching regulator inductor).
**Fix direction**: Add WiFi/BT/wireless module families (AP6xxx, ESP32, CYW43xxx, etc.) to the non-regulator exclusion list in detect_power_regulators().
**Findings**: FND-180

---

## Priority Queue (open issues, ordered by impact)

1. **KH-078** (MEDIUM) — `build_net_map()` unhashable list crash
2. **KH-080** (MEDIUM) — Power symbol despite in_bom=yes
3. **KH-081** (MEDIUM) — Current sense FPs on Ethernet termination
4. **KH-082** (MEDIUM) — TVS IC protection devices not detected
5. **KH-085** (MEDIUM) — RF chain keyword lists too narrow
6. **KH-087** (MEDIUM) — Switching regulator output_rail missing
7. **KH-097** (MEDIUM) — CSYNC nets as chip_select
8. **KH-098** (MEDIUM) — Flyback diode drain-to-supply not detected
9. **KH-099** (MEDIUM) — I2S misidentified as I2C
10. **KH-090** (LOW) — LDO inverting flag incorrect
11. **KH-100** (LOW) — WiFi modules as power regulators
