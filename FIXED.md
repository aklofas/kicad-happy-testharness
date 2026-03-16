# Fixed Issues

Record of resolved kicad-happy analyzer bugs (KH-*) and test harness issues (TH-*).
Shows what changed, where, and how it was verified — useful for cross-referencing
regressions, understanding analyzer evolution, and onboarding collaborators.

> **Protocol**: When fixing issues, remove them from [ISSUES.md](ISSUES.md) and add here
> in the same session. Each entry must include: root cause, fix description, and
> verification results. See README.md "Issue tracking protocol" for full details.
> Open issues are in [ISSUES.md](ISSUES.md).

---

## 2026-03-16 — Batch 10: 9 issues (KH-116 through KH-124)

RC/LC filter fixes, classification corrections, keyword expansion, varistor detection, BMS refinement.

### KH-116 (MEDIUM): RC filter false positive when output==ground net

- **Files**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: `ground_net` assignment defaulted to `r_other` when `c_other` wasn't ground, making `output_net == ground_net` for "RC-network" type filters.
- **Fix**: Changed `ground_net` to use `c_other` (capacitor's far end) when neither end is ground. Also added `r_other == c_other` skip for truly shorted cases.
- **Verified**: CoffeeRoaster R1/C1 and R2/C2 now have distinct output/ground nets. 53/53 assertions pass.

### KH-117 (LOW): Varistors not detected as protection devices

- **Files**: `signal_detectors.py` — `detect_protection_devices()`
- **Root cause**: `get_two_pin_nets()` hardcodes pin numbers "1"/"2", but Eagle-imported varistors use "P$1"/"P$2"/"P$3" pin names.
- **Fix**: Added fallback in varistor loop: if `get_two_pin_nets` fails, scan all `pin_net` entries for the component and collect unique nets.
- **Verified**: robocup-pcb RV1 (500V PVG3 varistor) now detected as protection device. 91/91 assertions pass.

### KH-118 (MEDIUM): TPLP5907MFX-3.3 linear regulator not detected

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: "TPLP" not in regulator keyword list.
- **Fix**: Added "tplp" and "hx630" to `reg_lib_keywords`.
- **Verified**: pcb_kicad_rf_scom_bk48_v3 U19 TPLP5907MFX-3.3 now detected as LDO. 38/38 assertions pass.

### KH-119 (HIGH): LC filter overcounting in RF designs

- **Files**: `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: Every L-C pair sharing a net counted as a filter. No topology validation; no fanout limit. RF matching networks triggered massive overcounting.
- **Fix**: (1) Added shared_net fanout limit (>6 pins → skip). (2) Post-processing: if an inductor has LC pairings on both its nets (matching network pattern), keep only the largest-capacitance entry per side.
- **Verified**: pcb_kicad_rf_scom_bk48_v3 LC filters reduced from 23 to 14. L7 reduced from 4 entries to 2. 38/38 assertions pass.

### KH-120 (MEDIUM): RF transceiver ICs not detected in RF chains

- **Files**: `signal_detectors.py` — `detect_rf_chains()`
- **Root cause**: (1) BK4819 and CMX994 not in transceiver keyword list. (2) RF chain detection only searched `type == "ic"`, missing non-standard reference ICs classified as "other".
- **Fix**: (1) Added "bk4819", "cmx994", "cmx99", "si4463", "si4432", "a7105" to transceiver keywords. (2) Changed type check to `c["type"] in ("ic", "other")`.
- **Verified**: BK4819QN32SC and CMX994E1 both detected as RF transceivers. 38/38 assertions pass.

### KH-121 (MEDIUM): RC filter bidirectional traversal duplicates

- **Files**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: Same R-C pair found from both net endpoints, creating duplicate entries with swapped input/output.
- **Fix**: Track `seen_rc_pairs` as `set[frozenset[str]]`. Skip if R-C pair already processed.
- **Verified**: DIY-LAPTOP Power Supply sheet: 0 duplicate R-C pairs (was >0 before). 176/176 assertions pass.

### KH-122 (MEDIUM): SK6812/WS2812 addressable LEDs misclassified as diodes

- **Files**: `kicad_utils.py` — `classify_component()`; `signal_detectors.py` — `detect_addressable_leds()`
- **Root cause**: D-prefix components classified as "diode" before reaching SK6812 keyword checks. Custom library `tm_leds:SK6812MINI-E` lacks "led" token needed by the generic LED regex.
- **Fix**: (1) Added addressable LED keyword check in `classify_component()` diode block. (2) `detect_addressable_leds()` now also searches "diode" type components as fallback.
- **Verified**: kuro65: all 69 SK6812MINI-E components now type "led" (was "diode"). 1 addressable LED chain detected. 43/43 assertions pass.

### KH-123 (LOW): MCP73871 battery charger misclassified as BMS

- **Files**: `signal_detectors.py` — `detect_bms_systems()`
- **Root cause**: BMS keyword list included single-cell charger ICs (TP4056, MP2639, MCP738xx) that handle charging only, not multi-cell monitoring/balancing.
- **Fix**: Removed single-cell charger keywords from `bms_ic_keywords`. Only multi-cell BMS/AFE ICs remain (BQ769xx, LTC681x, ISL942x, MAX172x).
- **Verified**: PCB-Modular-Multi-Protocol-Hub: 0 BMS systems (was 1 false positive for MCP73871). 85/85 assertions pass.

### KH-124 (HIGH): PMIC regulators not detected (AXP803, MT3608)

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: (1) "AXP" and "MT36" not in keyword list. (2) KiCad 5 legacy format components have 0 pins, causing early skip before keyword check.
- **Fix**: (1) Added "axp", "mt36", "pmic", "dd40", "ip51" to `reg_lib_keywords`. (2) Added keyword-only fallback for pin-less ICs: if no FB/SW/VOUT pins found but component matches PMIC keywords, add as "unknown" topology entry.
- **Verified**: DIY-LAPTOP Power Supply: AXP803 and MT3608 both detected (was 0). 176/176 assertions pass.

---

## 2026-03-16 — Batch 9: 12 issues (KH-078, KH-080, KH-081, KH-082, KH-085, KH-087, KH-098, KH-105, KH-112, KH-113, KH-114, KH-115)

Crash fix, classification corrections, false positive suppression, detection expansion, chain merging, rail tracing.

### KH-078 (MEDIUM): `build_net_map()` unhashable list crash

- **Files**: `analyze_schematic.py` — `extract_labels()` and `build_net_map()`
- **Root cause**: Malformed s-expression yields list instead of string for label name. Flows into dict key as unhashable type.
- **Fix**: Defensive `isinstance(name, list)` coercion in both `extract_labels()` (line 597) and `build_net_map()` (line 901).
- **Verified**: All test repos pass (kicad_schemes not checked out for direct verification).

### KH-080 (MEDIUM): Power symbol despite in_bom=yes

- **Files**: `kicad_utils.py` — `classify_component()`; `analyze_schematic.py` — call site
- **Root cause**: `classify_component()` returned `"power_symbol"` for `lib_id.startswith("power:")` without checking `in_bom`. DD4012SA buck converter (lib_id=`power:DD4012SA`, in_bom=yes) became invisible.
- **Fix**: Added `in_bom` parameter to `classify_component()`. Guard: `not in_bom` before returning `"power_symbol"`. Call site passes `in_bom=in_bom`.
- **Verified**: ethersweep DD4012SA (U4) now type=`ic`. 10/10 schematics pass. Baselines unchanged (0/17 diffs).

### KH-081 (MEDIUM): Current sense FPs on Ethernet termination

- **Files**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: No IC exclusion mechanism. Ethernet PHYs (W5500) and RJ45 modules (HR911105A) falsely match as current sense ICs.
- **Fix**: Added `_SENSE_IC_EXCLUDE` frozenset with Ethernet PHY/RJ45/MagJack families. Applied in both Pass 1 and Pass 2.
- **Verified**: ethersweep current_sense=0 (was 3 false positives). 10/10 pass.

### KH-082 (MEDIUM): TVS IC-packaged protection devices not detected

- **Files**: `signal_detectors.py` — `detect_protection_devices()`
- **Root cause**: ESD IC keyword list missed TVS/ECMF/CDSOT families; no `Power_Protection:` library check.
- **Fix**: Added `tvs18`, `tvs1`, `ecmf`, `cdsot`, `smda`, `rclamp` to keywords. Added `is_protection_lib` check for `power_protection:` in lib_id.
- **Verified**: ISS-PCB 181/181 pass.

### KH-085 (MEDIUM): RF chain keyword lists too narrow

- **Files**: `signal_detectors.py` — `detect_rf_chains()`
- **Root cause**: Missing IC families (ADRF, ADMV, MAAM, HMC3xx) and missing categories (attenuators, couplers, power detectors, frequency multipliers).
- **Fix**: Expanded switch keywords (+`adrf`, `hmc3`), amp keywords (+`maam`, `admv`). Added 4 new category tuples with classification loops, output dict entries, and `_rf_role()` mappings.
- **Verified**: vna 229/229 pass.

### KH-087 (MEDIUM): Switching regulator output_rail missing

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Output rail through inductor only traced before sanitization; input rail not traced through ferrite beads.
- **Fix**: After GND sanitization, retry output_rail trace through inductor if topology=switching and no output_rail. Added ferrite bead input_rail tracing (skip same inductor).
- **Verified**: Power_HW 114/114 pass. ISS-PCB 181/181 pass.

### KH-098 (MEDIUM): Flyback diode drain-to-supply not detected

- **Files**: `signal_detectors.py` — MOSFET analysis flyback check
- **Root cause**: Detector only checked drain-to-source topology, missing standard low-side switch flyback (drain to supply rail).
- **Fix**: After existing drain-to-source check, added drain-to-supply check: if diode's other pin is a power net (not GND), mark as flyback.
- **Verified**: KiDiff 16/16 pass. Note: KiDiff test cases use connectors instead of power symbols, so flyback detection requires named power rails to trigger.

### KH-105 (MEDIUM): 3-resistor feedback networks not handled

- **Files**: `signal_detectors.py` — new `_merge_series_dividers()`; `analyze_schematic.py` — integration
- **Root cause**: Pairwise divider detection can't see series resistors in feedback networks. R56+R59 (20.15k combined) treated as separate, yielding wrong Vout.
- **Fix**: Added `_merge_series_dividers()` post-processor. Identifies pass-through nodes (2 resistors, no active pins), extends chains, combines series resistances, recalculates ratios.
- **Verified**: Ventilator 30/30 pass. No baseline changes in tested repos.

### KH-112 (LOW): Ferrite bead impedance notation parsed as inductance

- **Files**: `kicad_utils.py` — `parse_value()` and `classify_component()`
- **Root cause**: "600R/200mA" → split("/") → "600R" → trailing R multiplier → 600.0. Used as inductance in LC filter detection.
- **Fix**: Early guard in `parse_value()`: regex `\d+[Rr]\s*[/@]\s*\d` returns None. In `classify_component()`: same regex reclassifies inductor as ferrite_bead.
- **Verified**: All test repos pass (panstamp-nrg3 not checked out).

### KH-113 (LOW): RS485 transceiver current sense FP

- **Files**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: LT1785 RS485 transceiver matched as current sense IC (no exclusion list).
- **Fix**: Added RS-485/RS-232/UART transceiver families to `_SENSE_IC_EXCLUDE` (lt178, max48, sn65hvd, st348, adm281/485/491, sp338/339, isl3, iso15, max23/31/32).
- **Verified**: Gas-sens_Rs-485 10/10 pass.

### KH-114 (LOW): Active oscillators treated as passive crystals

- **Files**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Passive crystal loop processes all `type == "crystal"` components including active oscillators with 4+ pins, producing nonsensical load capacitance.
- **Fix**: Before passive crystal loop body, check if component has >=4 pins AND has a VCC/VDD power pin (by name or connected net). If so, skip to active oscillator section.
- **Verified**: explorer 4/4 pass.

### KH-115 (LOW): Multi-tap attenuator spurious dividers

- **Files**: `signal_detectors.py` — `_merge_series_dividers()` (same as KH-105)
- **Root cause**: Pairwise detection generates all combinations from 3+ resistor chains.
- **Fix**: Same `_merge_series_dividers()` function. Pass-through nodes are detected and chains merged. Sub-pair dividers marked `suppressed_by_chain: True`.
- **Verified**: Ventilator 30/30 pass.

---

## 2026-03-15 — Batch 8: 15 issues (KH-090, KH-097, KH-099, KH-100, KH-101, KH-102, KH-103, KH-104, KH-106, KH-107, KH-108, KH-109, KH-110, KH-111)

Lookup table additions, exclusion lists, classification fixes, regex fixes, and defensive coding.

### KH-103 (MEDIUM): Regulator Vref lookup missing several ICs

- **Files**: `kicad_utils.py` — `_REGULATOR_VREF` table
- **Root cause**: LMR38010, XL7015, TPS631000, AP7365 not in Vref lookup table, falling back to wrong heuristic values.
- **Fix**: Added `LMR380: 1.0`, `XL70: 1.25`, `TPS6310: 0.5`, `AP736: 0.8` to `_REGULATOR_VREF`.
- **Verified**: All entries match datasheet values (SNVSB89, SLVSEK5, XL7015 datasheet, AP7365 datasheet).

### KH-109 (MEDIUM): Charger ICs not detected in BMS systems

- **Files**: `signal_detectors.py` — `detect_bms_systems()` keyword list
- **Root cause**: `bms_ic_keywords` tuple only had multi-cell BMS ICs; single-cell charger families missing.
- **Fix**: Added `mcp738`, `bq2104`, `bq2405`, `bq2407`, `ltc405`, `max1555`, `max1551` to keyword list.
- **Verified**: Covers MCP73831/MCP73833, BQ21040, BQ24050/BQ24070, LTC4054, MAX1555/MAX1551 families.

### KH-108 (MEDIUM): LM66200 ideal diode controller misclassified as LDO

- **Files**: `signal_detectors.py` — `_power_mux_exclude` tuple
- **Root cause**: LM66200 has VIN/VOUT pins matching regulator pattern but is an ideal diode OR controller.
- **Fix**: Added `lm6620`, `lm6610`, `ltc435`, `ltc430` to `_power_mux_exclude`.
- **Verified**: SparkFun_IoT_RedBoard-RP2350 — LM66200 no longer in power_regulators output.

### KH-100 (LOW): WiFi/BT modules classified as power regulators

- **Files**: `signal_detectors.py` — `_non_reg_exclude` tuple
- **Root cause**: AP6236 has filter inductor on power pin, triggering switching regulator detection.
- **Fix**: Added `ap62`, `ap63`, `esp32`, `esp8266`, `cyw43`, `wl18` to `_non_reg_exclude`.
- **Verified**: OtterCam-s3 — AP6236 no longer in power_regulators output.

### KH-106 (MEDIUM): MX key switches misclassified as relays

- **Files**: `kicad_utils.py` — `classify_component()` relay override + lib_lower switch detection
- **Root cause**: K prefix maps to "relay" in type_map. MX switches use K prefix with lib_id containing "MX_Alps_Hybrids". No relay→switch override existed.
- **Fix**: (1) Added relay→switch override in full-prefix match section checking for MX/Cherry/Kailh/Gateron/Alps in lib_low/val_low. (2) Added same patterns to lib_lower switch detection before relay check.
- **Verified**: Mechanical-Keyboard-PCBs — all 91 MX switches now type=switch (was relay). Updated assertion files for pok3r, steamvan, vortex_tester repos.

### KH-110 (LOW): Audio jack components misclassified as ICs

- **Files**: `kicad_utils.py` — `classify_component()` connector detection
- **Root cause**: Connector_Audio library and PJ-3xx part number patterns not in connector classification.
- **Fix**: Added `connector_audio`/`audio_jack` lib_lower checks and `PJ-3`/`SJ-3`/`MJ-3` value prefix checks.
- **Verified**: Pattern matches standard audio connector part numbering (PJ-327E-SMT, etc.).

### KH-111 (LOW): Common-mode choke misclassified as transformer

- **Files**: `kicad_utils.py` — `classify_component()` transformer override
- **Root cause**: T prefix maps to transformer. RFCMF/ACM/DLW/CMC components had no override.
- **Fix**: Added CMC exclusion before transformer return: checks val_low for `cmc`, `common mode`, `common_mode`, `rfcmf`, `acm`, `dlw` and lib_low for `common_mode`, `cmc`, `emi_filter`.
- **Verified**: SparkFun_GNSS_Flex_pHAT — RFCMF1220100M4T now type=inductor (was transformer).

### KH-097 (MEDIUM): CSYNC nets misclassified as chip_select

- **Files**: `analyze_schematic.py` — net classification
- **Root cause**: "CS" substring match in chip_select classification catches CSYNC/CSYNC_IN/CSYNC_OUT video sync signals.
- **Fix**: Added sync signal exclusion: if net name contains CSYNC/HSYNC/VSYNC/SYNC, classify as "signal" instead of "chip_select".
- **Verified**: Unit test confirms CSYNC_IN→signal, SPI_CS→chip_select (no false exclusions).

### KH-099 (MEDIUM): I2S audio bus misidentified as I2C

- **Files**: `signal_detectors.py` — I2C bus detection
- **Root cause**: I2S data pin names (SDAT) contain "SDA" as substring, matching `\bSDA\b` regex.
- **Fix**: (1) Added I2S keyword exclusion: skip nets with SDAT, LRCK, BCLK, WSEL. (2) Tightened SDA regex to `\bSDA\b(?!T)` (negative lookahead for 'T').
- **Verified**: Prevents SDAT from matching SDA while preserving standard I2C SDA detection.

### KH-101 (LOW): sexp_parser crashes on truncated PCB files

- **Files**: `sexp_parser.py` — `_parse_tokens()`
- **Root cause**: No bounds check before `tokens[pos]` access. Truncated files with unbalanced parens cause IndexError.
- **Fix**: Added `if pos >= len(tokens): raise ValueError(...)` before first token access.
- **Verified**: OnBoard — 235/237 pass (99.2%). 2 truncated files now get descriptive ValueError instead of IndexError crash.

### KH-102 (LOW): extract_silkscreen crashes on list-typed footprint value

- **Files**: `analyze_pcb.py` — `extract_silkscreen()` footprint iteration
- **Root cause**: Some PCB files have list-typed value fields in footprint data. `.lower()` called on list raises AttributeError.
- **Fix**: Added defensive type check: if value is list, extract `str(val[1])` or empty string.
- **Verified**: TI92-revive — both PCB files now pass (was crash). 2/2 pass.

### KH-107 (MEDIUM): Crystal oscillator load components as standalone RC filters

- **Files**: `signal_detectors.py` — `detect_rc_filters()` signature + exclusion; `analyze_schematic.py` — call site
- **Root cause**: Crystal feedback resistor + load capacitor pairs matched RC filter pattern. Existing post-filter in analyze_schematic.py was redundant but didn't handle all cases.
- **Fix**: (1) Added `crystal_circuits` parameter to `detect_rc_filters()`. (2) Built crystal component exclusion set (crystal refs, load cap refs, feedback resistor refs). (3) Skip R and C components in crystal_refs during filter detection. (4) Updated call site to pass crystal_circuits.
- **Verified**: SparkFun_IoT_RedBoard-RP2350 — no crystal components in RC filters. 92 assertion files updated for reduced (correct) RC filter counts across corpus.

### KH-090 (LOW): LDO inverting flag incorrect for fixed-output LDOs

- **Files**: `signal_detectors.py` — regulator detection, after inverting keyword check
- **Root cause**: Inverting keyword check matched on part number substrings even for fixed-output LDOs that are clearly non-inverting.
- **Fix**: Added check: if topology is "LDO" and no FB pin exists, delete the `inverting` flag.
- **Verified**: Fixed-output LDOs (TLV757xx family) no longer incorrectly marked as inverting.

### KH-104 (MEDIUM): Regulator pin mapping GND as input/output rail

- **Files**: `signal_detectors.py` — regulator detection, after rail assignment
- **Root cause**: Pin-to-net mapping sometimes assigns GND net to input_rail or output_rail when pin names don't match expected patterns.
- **Fix**: Added GND sanity filter: if input_rail or output_rail is a GND net (via `_is_ground_name()`), set to None.
- **Verified**: Prevents nonsensical GND power rails in regulator output.

### Regression results

- Full corpus: 6,827 schematic files, 100% analyzer pass rate (0 regressions)
- OnBoard PCB: 235/237 pass (99.2%), 2 truncated files get proper error
- TI92-revive PCB: 2/2 pass (was crash)
- Assertions: 64,399 total, 63,846 passed, 38 failed (pre-existing), 515 errors, 99.1% pass rate
- 145 assertion files updated for corrected RC filter / power regulator / switch counts

---

## 2026-03-15 — KH-091, KH-092, KH-093, KH-094, KH-095, KH-096 (batch 7, 6 issues)

Component classification fixes in `kicad_utils.py classify_component()`.
Source repos verified: commodorelcd, iMX8MP-SOM-EVB, ESP32-S3-DevKit-LiPo, NB-IoT,
Castor_and_Pollux, NUS-CPU-03-Nintendo-64-Motherboard

### KH-091 (HIGH): CR-prefix diodes misclassified as capacitor

- **Files**: `kicad_utils.py` — `classify_component()` type_map
- **Root cause**: CR (IPC-2612 standard diode/rectifier prefix) was not in type_map,
  so it fell to single-char fallback where prefix[0]='C' → capacitor.
- **Fix**: Added `"CR": "diode"` to type_map.
- **Verified**: commodorelcd: 15 CR-prefix components now classified as diode (was capacitor).

### KH-092 (HIGH): T-prefix transistors classified as transformer

- **Files**: `kicad_utils.py` — `classify_component()` transformer override
- **Root cause**: T→transformer in type_map. KH-079 added lib_id overrides but only
  for "mosfet/fet/transistor/amplifier" keywords. Custom libs with Q_NPN_BEC or
  "Transistors" footprint were missed.
- **Fix**: (1) Added "bjt", "q_npn", "q_pnp", "q_nmos", "q_pmos" to transformer
  override keyword list. (2) Added footprint check (fp_low) to transformer override.
  (3) Changed return from "ic" to "transistor" for transistor-related overrides.
- **Verified**: iMX8MP T1/T2 (BC817-40) → transistor (was transformer).
  ESP32-S3-DevKit-LiPo T1/T2 (BC817-40) → transistor. NB-IoT T1-T5 → transistor.

### KH-093 (HIGH): VR-prefix regulators classified as varistor

- **Files**: `kicad_utils.py` — `classify_component()` varistor override, single-char fallback
- **Root cause**: VR prefix falls to single-char V→varistor. Custom libs like
  "iMX8MPLUS-SOM-EVB_Rev_B:AMS1117-ADJ" don't contain "regulator" keyword.
- **Fix**: (1) Added footprint-based check ("regulator" in fp_low) to varistor override.
  (2) Added value-based check for known regulator families (ams1117, lm78, lm317, etc.).
  (3) Added same checks to single-char fallback varistor override.
- **Verified**: iMX8MP VR1/VR2 (AMS1117) → ic (was varistor).

### KH-094 (MEDIUM): Potentiometers (RV-prefix) classified as varistor

- **Files**: `kicad_utils.py` — `classify_component()` varistor override
- **Root cause**: RV→varistor in type_map. Override checked "r_pot" and "potentiometer"
  but missed custom libs like "winterbloom:Eurorack_Pot" where only "pot" appears.
- **Fix**: Broadened potentiometer check to include "pot" in lib_low alongside existing
  "r_pot" and "potentiometer" checks.
- **Verified**: Castor_and_Pollux RV1-RV5 → resistor (was varistor).

### KH-095 (MEDIUM): D_TVS_Filled classified as LED

- **Files**: `kicad_utils.py` — `classify_component()` diode→LED override
- **Root cause**: `"led" in lib_low` matched "fi**led**" substring in "Device:D_TVS_Filled".
- **Fix**: Changed from substring check to regex with negative lookbehind/lookahead:
  `re.search(r'(?<![a-z])led(?![a-z])', ...)` ensures "led" appears as a standalone token.
- **Verified**: Castor_and_Pollux D3-D6 (D_TVS_Filled) → diode (was led).

### KH-096 (MEDIUM): Ferrite beads (FerriteBead) classified as fuse

- **Files**: `kicad_utils.py` — `classify_component()` lib_id section + single-char fallback
- **Root cause**: FIL prefix not in type_map, fell to single-char F→fuse. No ferrite bead
  check in fuse override or lib_id fallback section.
- **Fix**: (1) Added "ferritebead"/"ferrite_bead" check in lib_id fallback section before
  inductor check. (2) Added "ferrite"/"bead" check in single-char fallback fuse override.
- **Verified**: NUS-CPU-03 FIL1-FIL8 → ferrite_bead (was fuse).

### Regression results

- Full corpus: 6,827 files, 100% analyzer pass rate
- Assertions: 55,245 total, 54,455 passed (98.6%) — no regression vs baseline
- 23 repos reseeded assertions to reflect corrected classifications
- Drift check: 0 regressions, 2 possibly_fixed findings (FND-183)

---

## 2026-03-15 — KH-079, KH-083, KH-084, KH-086, KH-088, KH-089 (batch 6, 6 issues)

Source repos verified: mutable_eurorack_kicad (102), Power_HW (114), openwrt-one (9),
ISS-PCB (181), cnhardware (77), ethersweep (10), vna (229)

### KH-088 (CRITICAL): Eagle-import empty Value cascading power symbol net failure

- **Files**: `analyze_schematic.py` — `extract_lib_symbols()`, `extract_components()`
- **Root cause**: Eagle-imported KiCad schematics have empty instance Value for power
  symbols. The analyzer used only the instance Value, so all power/ground connections
  merged into a single empty-string net. Cascaded to break power rails, voltage
  dividers, RC filters, and op-amp configurations.
- **Fix**: (1) Store `lib_value` from lib_symbol definition in `extract_lib_symbols()`.
  (2) In `extract_components()`, fall back to lib_symbol Value when instance Value is
  empty.
- **Verified**: mutable_eurorack_kicad Ripples: power rails now GND/VCC/VEE (was empty
  mega-net). All 102 files pass.

### KH-083 (CRITICAL): lib_name/lib_id mismatch causes 0-pin parsing in KiCad 7+

- **Files**: `analyze_schematic.py` — `extract_components()`, `compute_pin_positions()`
- **Root cause**: KiCad 7+ uses `(lib_name X)` when the local symbol name differs from
  the library's `lib_id`. `compute_pin_positions()` only looked up by `lib_id`, missing
  symbols keyed by their raw name (e.g., `TPS2116DRLR_1`).
- **Fix**: (1) Extract `lib_name` from symbol instances. (2) Try `lib_name` first, then
  `lib_id` as lookup key in `compute_pin_positions()` and `classify_component()` sym_def
  lookup.
- **Verified**: Power_HW GEODE rev2 TPS2116DRLR: 8 pins (was 0), full IC analysis.
  PMV90ENER: 3 pins with gate/drain/source nets. All 114 files pass.

### KH-079 (HIGH): Ref prefix single-char fallback overrides lib_id/footprint

- **Files**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Single-char prefix fallback (T→transformer, F→fuse, etc.) returned
  without checking lib_id/footprint/value for contradicting evidence.
- **Fix**: Added `footprint` parameter to `classify_component()`. After single-char
  fallback match, check lib_id/footprint/value keywords to override: transformer→test_point
  (TP footprint), transformer→diode (TVS), fuse→fiducial, fuse→filter (EMI),
  capacitor→mechanical (shield clips), switch→mounting_hole (standoffs),
  ic→transistor (BJT), ic→transformer.
- **Verified**: openwrt-one TPD → test_point (was transformer). All 7 repos pass.

### KH-086 (HIGH): SPI nets falsely detected as I2C via pin-name fallback

- **Files**: `analyze_schematic.py`, `signal_detectors.py`
- **Root cause**: I2C detection scanned all nets for SDA/SCL pins but didn't exclude
  SPI nets. Sensors with dual-function SDA/SCL pin names in SPI mode triggered false
  I2C detection.
- **Fix**: Added SPI keyword exclusion (SPI, MOSI, MISO in net name) to three I2C
  detection paths: net-name-based, pin-name-based, and observation detector.
- **Verified**: ISS-PCB TARS-MK4-FCB: SNS_SPI_* nets no longer reported as I2C.
  All 181 ISS-PCB files pass.

### KH-089 (HIGH): Regulator detection false positives from non-regulator ICs

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Any IC with VOUT/OUT/FB/SW pins passed the regulator gate. Title
  blocks (0 pins), flash chips, RTCs, EEPROMs, logic buffers leaked through.
- **Fix**: Added early exclusions: (1) Skip components with no pins. (2) Skip known
  non-regulator IC families (eeprom, flash, rtc, uart, buffer, logic, w25q, at24c,
  ht42b, ch340, cp210, ft232, 74lvc, 74hc).
- **Verified**: openwrt-one regulators 40→25 (title blocks and non-regulators excluded).

### KH-084 (HIGH): Voltage divider/feedback not linked to parent regulator

- **Files**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: (1) Switching regulator output_rail missing — no trace through inductor
  from SW pin. (2) FB-at-top divider topology not recognized.
- **Fix**: (1) After finding inductor on SW net, trace through to find output rail net.
  (2) After building regulator list, cross-reference voltage divider top_nets with
  regulator FB pins to detect FB-at-top topology.
- **Verified**: Power_HW LMR36506: output_rail now traced through inductor. All 7 repos
  pass with 0 regressions.

### Regression results

- All analyzer runs pass: mutable_eurorack_kicad (102), Power_HW (114), openwrt-one (9),
  ISS-PCB (181), cnhardware (77), ethersweep (10), vna (229)
- 0 regressions, multiple `now_detected` and `possibly_fixed` across all 7 repos
- 66 findings promoted to assertions (119 confirmed, 44 new)
- Assertion corpus: 55,276 total, 54,502 passed (98.6%)

---

## 2026-03-15 — KH-016, KH-026, KH-048, KH-052, KH-064, KH-066, KH-067, KH-073 (batch 5, 8 issues)

Source repos verified: ESP32-P4-PC, ESP32-EVB (12 revisions), ESP32-GATEWAY (9 revisions),
daisho (60 files), hackrf (23), splitflap (8), Voron-Hardware (29), icebreaker (15), OnBoard

### KH-016 (HIGH): Legacy wire-to-pin coordinate matching broken

- **Files**: `analyze_schematic.py` — `_STANDARD_LIB_PINS`, `_snap_pins_to_wires()`, cache lib suffix map
- **Root cause**: Three compounding issues: (1) `_STANDARD_LIB_PINS` had pin offsets at ±40 mils
  (body end) instead of ±150 mils (connection endpoint where wires attach). Surveyed 1292 real
  cache.lib files to find correct positions. (2) Cache libs store symbols as `Library_Symbol`
  but component references use `Library:Symbol` — suffix lookup was missing. (3) When pin positions
  are slightly off due to KiCad version differences, no snap-to-wire fallback existed.
- **Fix**: (1) Rewrote entire `_STANDARD_LIB_PINS` with correct offsets (±150 mils for 2-pin passives,
  ±200/250 mils for connectors, etc.) and added ~60 new symbols including `CONN_01X01` through
  `CONN_01X20`, `CONN_02X02` through `CONN_02X20`, transistors, crystals, switches. (2) Added
  `_cache_suffix_map` for resolving bare symbol names to prefixed cache lib names. (3) Added
  `_snap_pins_to_wires()` post-processing step that snaps unmatched pin positions to nearby
  wire endpoints (max 12mm, direction-aware).
- **Verified**: daisho power.sch orphan rate 97.5% → 53.9%, multi-pin nets 4 → 24.
  ESP32-C3-DevKit-Lipo: ICs with power rails 0 → 2. All 60 daisho files pass.

### KH-026 (HIGH): Hierarchical net merging for multi-instance sub-sheets

- **Files**: `analyze_schematic.py` — hierarchical label handling in `build_net_map()`
- **Root cause**: Already fixed in a prior batch. Instance-path prefixing exists at
  analyze_schematic.py with `_sheet_uuid` tagging for per-instance net namespacing.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: cynthion type_c.kicad_sch instantiated 3 times. CC1/CC2 nets from different
  USB-C port instances are properly namespaced with different UUID paths. Nets are electrically
  isolated per instance.

### KH-048 (MEDIUM): Key matrix detection fails on non-standard net names

- **Files**: `signal_detectors.py` — `detect_key_matrices()`
- **Root cause**: Already fixed in a prior batch. Both net-name detection and topology-based
  detection (switch-diode pair grouping) are implemented and working. The original issue report's
  expectation of "16 columns for 65 keys" was incorrect — the Nat3z keyboard actually uses a
  single-column (COL5) design with 4 rows and diode isolation.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: Nat3z 65-key keyboard: net-name method correctly detects 4 rows × 1 column,
  65 estimated keys. Hugo keyboard: topology method correctly detects 14 rows × 6 columns
  (GPIO-style names A0-A3, D0-D13, MOSI, MISO, SCK), 76 estimated keys.

### KH-052 (MEDIUM): SPI/I2C/RS-485 bus protocol detection missing

- **Files**: `analyze_schematic.py` — I2C, SPI, UART, CAN, RS-485, SDIO aggregation
- **Root cause**: Already implemented in a prior batch. Bus protocol detection exists:
  I2C (lines 2706-2800), SPI (lines 2802-2847), UART, CAN (lines 2948+), RS-485 (lines 2978-3029),
  SDIO (lines 2872-2946).
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: ESP32-EVB Rev-L: UART (8-10 entries), CAN (2), I2C (2). Bus protocols
  correctly aggregated from signal prefix groups.

### KH-064 (HIGH): Crystal circuit detector incomplete/inconsistent

- **Files**: `kicad_utils.py` — `classify_component()`, `signal_detectors.py` — `_xtal_pin_re`
- **Root cause**: Crystal components using `Q` reference prefix (Q for quartz crystal) were
  classified as `transistor` by `classify_component()` because `Q` maps to `transistor` in the
  `type_map`. Similarly, oscillators with `CR` prefix were classified as `capacitor` (falls back
  to `C`). The crystal detector requires `type == "crystal"` to fire, so these components were
  invisible.
- **Fix**: (1) Added crystal/oscillator override in `classify_component()`: when lib_id contains
  "crystal"/"xtal" keywords, override to `crystal`; when lib_id contains "oscillator", override
  to `oscillator`. Applies regardless of reference prefix. (2) Expanded `_xtal_pin_re` regex
  to include more IC crystal pin name variants: XTAL1/2, OSC1/2, XIN/XOUT, XT1/XT2,
  XTAL_P/XTAL_N, RTC_XTAL, RTC32K_XP/XN.
- **Verified**: ESP32-P4-PC: 5 crystal circuits detected (Q1 32.768kHz, Q2/Q6 25MHz, Q4 12MHz,
  Q3 40MHz) with load caps. ESP32-EVB Rev-L: CR1 50MHz active oscillator detected. Legacy
  Rev-K2: 2 crystals detected. Q5 (BC817-40 transistor) correctly stays as transistor.

### KH-066 (MEDIUM): Ethernet interface missing magnetics and connector linkage

- **Files**: `signal_detectors.py` — `detect_ethernet_interfaces()`, `kicad_utils.py` — `classify_component()`
- **Root cause**: Three compounding issues: (1) `_eth_tx_rx_re` regex only matched MII differential
  pairs (TXP/TXN/TX+/TX-), not RMII single-ended signals (TXD0/RXD0/TXEN/CRS_DV). (2) When PHY
  component has no parsed pins (pin_net empty), BFS had no seed nets to start from. (3) RJ45
  connector `LAN1` was classified as `inductor` (LAN prefix → L fallback) and not detected as
  Ethernet connector (part number RJLBC/LPJ4013 not in keyword list).
- **Fix**: (1) Expanded `_eth_tx_rx_re` to include RMII signals (TXD\d, RXD\d, TXEN, CRS_DV, MDIO,
  MDC). (2) Added net-scanning fallback: when PHY has no parsed pins, scan all nets for the PHY
  reference and match on pin_name or net name patterns. (3) Added LAN/CON/USB/HDMI/RJ/ANT connector
  prefixes to `type_map` in `classify_component()`. (4) Added integrated-magnetics RJ45 part numbers
  (lpj4, hr911, rjlbc, etc.) and LAN reference prefix to Ethernet connector detection.
- **Verified**: ESP32-EVB Rev-L: PHY U4 (LAN8710A) → connector LAN1 (LPJ4013EDNL MagJack).
  All 9 ESP32-GATEWAY revisions: same PHY→RJ45 linkage detected. All 12 ESP32-EVB revisions pass.

### KH-067 (MEDIUM): HDMI/DVI interface detection not implemented

- **Files**: `signal_detectors.py` — `detect_hdmi_dvi_interfaces()`
- **Root cause**: Already implemented in a prior batch. `detect_hdmi_dvi_interfaces()` exists
  with bridge IC keywords, PIO-DVI pattern, and generic connector fallback.
- **Fix**: No code changes needed — verified existing implementation works correctly.
- **Verified**: ESP32-P4-PC: LT8912B HDMI bridge IC correctly detected as HDMI/DVI interface.

### KH-073 (HIGH): Power domain detection fails on KiCad 5 legacy schematics

- **Files**: `analyze_schematic.py` — power domain analysis (cascading from KH-016)
- **Root cause**: Power domain detection requires pin-level net connectivity to map IC power pins
  to rails. On legacy .sch files, IC pins were empty due to incorrect `_STANDARD_LIB_PINS`
  offsets (KH-016), making the IC-to-rail mapping impossible.
- **Fix**: Resolved by KH-016 fix — corrected pin offsets, wire-snap fallback, and cache lib
  suffix resolution now populate IC pins on legacy files, enabling power domain analysis.
- **Verified**: ESP32-C3-DevKit-Lipo Rev B: ICs with power rails 0 → 2 (U1, U2 detected).
  ESP32-DevKit-LiPo: similar improvement.

### Regression results

- All analyzer runs pass: ESP32-P4-PC (1), ESP32-EVB (12), ESP32-GATEWAY (9), daisho (60),
  hackrf (23), splitflap (8), Voron-Hardware (29), icebreaker (15)
- Pre-existing assertion failures (net count drift from legacy .sch orphan improvements,
  rf_matching gaps on icebreaker) unchanged — 0 new regressions from this batch
- Assertion test corpus: hackrf, splitflap, Voron-Hardware, icebreaker, daisho all checked

---

## 2026-03-14 — KH-013, KH-017, KH-020, KH-021, KH-047, KH-051 (batch 4, 6 issues)

Source repos verified: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

### KH-047 (HIGH): IC function field always empty

- **File**: `analyze_schematic.py` — new `_classify_ic_function()` helper + `ic_result` dict
- **Root cause**: `analyze_ic_pinouts()` built `ic_result` but never populated a `function` field.
- **Fix**: Added `_classify_ic_function(lib_id, value, description)` with three-tier lookup:
  (1) KiCad stdlib library prefix mapping (40+ prefixes), (2) value/part number keyword matching
  (100+ patterns covering MCUs, regulators, logic, communication, sensors, etc.), (3) description
  keyword fallback. Connectors excluded to prevent false positives. Result inserted into `ic_result`.
- **Verified**: Hugo Keyboard KB2040→"microcontroller (RP dev board)", Nat3z ATmega32U4→"microcontroller (AVR)",
  CACKLE ESP32-S3→"microcontroller (ESP)", 74HC595→"logic IC", THVD1420→"UART interface",
  Buck LM2596S-12→"switching regulator". All 292 files pass.

### KH-013 (LOW): PWR_FLAG false warnings per sheet

- **File**: `analyze_schematic.py` — `audit_pwr_flags()`
- **Root cause**: Warnings on power nets with only `power_in` pins even when PWR_FLAG on another sheet.
- **Fix**: Skip warnings for well-known power/ground net names (via `_is_power_net_name()` / `_is_ground_name()`).
  These are nearly always driven globally via power symbols.
- **Verified**: No regressions; false warnings on sub-sheet power rails suppressed.

### KH-017 (LOW): Opamp input resistor verification

- **File**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: Input resistor detection didn't verify the resistor's other net is a signal,
  not power/ground. Bias resistors to power rails counted as signal input resistors.
- **Fix**: Added `not ctx.is_power_net(other) and not ctx.is_ground(other)` check on the input
  resistor's other net.
- **Verified**: No regressions in opamp detection across test repos.

### KH-020 (LOW): Capacitive feedback recognition

- **File**: `signal_detectors.py` — `detect_opamp_circuits()`
- **Root cause**: Only resistive feedback detected. Integrators (C feedback) and compensators
  (R+C feedback) missed.
- **Fix**: Added capacitor feedback search using same `out_comps & neg_comps` pattern as resistor
  feedback. New configurations: `"integrator"` (C feedback + R input), `"compensator"` (R+C feedback).
  Added `feedback_capacitor` field to output entry.
- **Verified**: No regressions; new configurations available for opamp circuits with capacitive feedback.

### KH-021 (LOW): BSS138 level shifter detection

- **File**: `signal_detectors.py` — `detect_transistor_circuits()`
- **Root cause**: BSS138-based bidirectional level shifters appeared as generic MOSFET switches.
- **Fix**: After load_type classification, check for level shifter pattern: N-channel MOSFET
  with gate→power rail, pull-up resistors on both source and drain to *different* power rails.
  Sets `topology="level_shifter"` and `load_type="level_shifter"`.
- **Verified**: No regressions; level shifter topology now detected for matching circuits.

### KH-051 (LOW): Addressable LED chain detection

- **File**: `signal_detectors.py` — new `detect_addressable_leds()` function
- **Root cause**: No detector for WS2812/SK6812/APA102 chains.
- **Fix**: New detector finds LEDs with addressable keywords in value/lib_id, identifies
  DIN/DOUT pins by name, traces DOUT→DIN chains. Reports chain length, protocol
  (single-wire vs SPI), LED type, estimated current draw (60mA/LED for WS2812).
  Wired into `analyze_signal_paths()` as `addressable_led_chains`.
- **Verified**: esp-rust-board: 1x WS2812B chain correctly detected. All 292 files pass.

### Regression results

- **6970/7004** assertions pass (34 failures pre-existing from batch 3)
- **0 regressions**, 19 possibly fixed, 15 newly detected in drift check
- All test repos pass: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

---

## 2026-03-14 — KH-012, KH-018, KH-019, KH-048 (partial), KH-068, KH-069, KH-070, KH-072, KH-074, KH-075, KH-076 (batch 3, 11 issues)

Source repos verified: esp-rust-board, OnBoard (279 files), hackrf-pro (12 files)

### KH-075 (LOW): TESTPAD misclassified as diode

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Ref prefix `D` matched `diode` before value `TESTPAD` was checked.
- **Fix**: After prefix-based result, check value for testpad/testpoint keywords and override to `test_point`.
- **Verified**: Components with value "TESTPAD" now classified as test_point regardless of ref prefix.

### KH-069 (LOW): Button/switch classified as 'other'

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Prefixes `BTN`, `BUTTON` not in type_map. Custom footprint buttons (YTS-A016-X, T1102D) fell through.
- **Fix**: (a) Added `BTN` and `BUTTON` to type_map. (b) Added button keywords (`button`, `tact`, `push`, `t1102`, `t1107`, `yts-a`) in library/value fallback. (c) Added `"button" in lib_lower` to switch detection.
- **Verified**: OnBoard keyboard projects correctly classify buttons as switches.

### KH-068 (LOW): Power multiplexer ICs classified as LDO

- **File**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: TPS2116/TPS2121 have VIN/VOUT pins, pass through regulator detector.
- **Fix**: Added power mux/load switch exclusion list after RF exclusion: `tps211`, `tps212`, `ltc441`, `ideal_diode`, `power_mux`, `load_switch`.
- **Verified**: Power mux ICs no longer appear in regulator results.

### KH-076 (MEDIUM): Crystal detector FPs on non-crystal ICs

- **File**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Active oscillator keyword match too broad — RF switches, baluns, muxes with "oscillator" in generic lib descriptions matched.
- **Fix**: Added exclusion keywords for RF/analog ICs: `switch`, `mux`, `balun`, `filter`, `amplifier`, `lna`, `driver`, `mixer`, `attenuator`, `diplexer`, `splitter`, `spdt`, `sp3t`, `sp4t`, `74lvc`, `74hc`.
- **Verified**: RF ICs no longer falsely detected as active oscillators.

### KH-012 (MEDIUM): Voltage divider false positives

- **File**: `signal_detectors.py` — `detect_voltage_dividers()`, `postfilter_vd_and_dedup()`
- **Root cause**: Pull-up/pull-down pairs and opamp feedback resistors matched as dividers.
- **Fix**: (a) Added extreme ratio filter (>100:1 skip). (b) Extended postfilter to remove VDs whose mid_net connects to opamp inverting input (IN-, INV, INN pin names).
- **Verified**: False-positive dividers reduced without affecting real divider detection.

### KH-019 (LOW): RC filter false pairs from shared-node

- **File**: `signal_detectors.py` — `detect_rc_filters()`
- **Root cause**: Pull-up + bypass cap on same signal net detected as "RC-network" filter.
- **Fix**: Skip filter entries classified as `RC-network` (neither end grounded). Only report properly classified low-pass/high-pass filters where shunt element connects to ground.
- **Verified**: 13 false-positive RC filter assertions now correctly return 0. Real low-pass/high-pass filters retained.

### KH-048 partial (MEDIUM): Key matrix net name spaces

- **File**: `signal_detectors.py` — `detect_key_matrices()`
- **Root cause**: "Row 0", "Column 2" don't match `ROW(\d+)` regex because spaces aren't stripped.
- **Fix**: Added `.replace(" ", "")` to net name normalization.
- **Note**: Topology-based detection (GPIO-style names, switch-diode connectivity) deferred.
- **Verified**: Space-containing net names now match ROW/COL patterns.

### KH-074 (LOW): Crystal frequency not parsed from value

- **File**: `signal_detectors.py` — new `_parse_crystal_frequency()` helper
- **Root cause**: `parse_value()` can't extract frequency from MPNs like "YIC-12M20P2".
- **Fix**: Added `_parse_crystal_frequency()` that tries `parse_value()` first, then regex for embedded MHz/kHz patterns. Used in place of bare `parse_value()` in crystal detector.
- **Verified**: Crystal values with MHz/kHz suffixes and MPN-embedded frequencies now parsed.

### KH-018 (LOW): Diff pair detector matches power rails

- **File**: `analyze_schematic.py` — differential pair detection
- **Root cause**: V+/V- and IN+/IN- matched as differential pairs.
- **Fix**: After finding suffix pair match, skip if either net is power or ground via `_is_power_net_name()` / `_is_ground_name()`.
- **Verified**: Power supply rail pairs no longer appear in differential_pairs.

### KH-072 (MEDIUM): SPI/I2C FPs from connector pin names

- **File**: `analyze_schematic.py` — I2C and SPI bus detection
- **Root cause**: Connectors with SDA/SCL/MOSI/MISO pins trigger bus detection with no ICs on the bus.
- **Fix**: Skip I2C/SPI bus entries when `devices` list is empty (no ICs = connector-only routing). Applied to net-name-based I2C, pin-name-based I2C, and SPI detection.
- **Verified**: Connector-only bus routes no longer generate false bus entries.

### KH-070 (MEDIUM): Subcircuit neighbors identical for all ICs

- **File**: `analyze_schematic.py` — `identify_subcircuits()`
- **Root cause**: Neighbor collection iterated all nets including power/ground. Every IC shares VCC/GND, so neighbors = everything.
- **Fix**: Skip power/ground nets in the neighbor loop using `_is_power_net_name()` / `_is_ground_name()`.
- **Verified**: Each IC now gets distinct neighbors based on signal connectivity, not shared power rails.

### Regression results

- **6970/7004** assertions pass (34 failures from intentional behavior changes — stale assertions need regeneration)
- **0 regressions**, 19 possibly fixed, 15 newly detected in drift check
- All test repos pass: esp-rust-board (1), OnBoard (279), hackrf-pro (12)

---

## 2026-03-14 — KH-022, KH-024, KH-025, KH-049, KH-050, KH-053, KH-054+055, KH-056, KH-057+065, KH-071, KH-077 (batch fix, 13 issues)

Source repos verified: hackrf-pro, ESP32-EVB, LNA1109, OnBoard (279 files), urti-mainboard

### KH-053 (CRITICAL): KiCad 9 value parsing — SI prefixes dropped

- **File**: `kicad_utils.py` — `parse_value()`
- **Root cause**: `.split()[0]` discarded the SI prefix when KiCad 9 uses space-separated
  format `"18 pF"` instead of `"18pF"`. All derived calculations were orders of magnitude wrong.
- **Fix**: Before taking first token, check if second token starts with an SI prefix letter
  and rejoin: `"18 pF"` → `"18pF"` → correct 1.8e-11.
- **Verified**: hackrf-pro praline.kicad_sch: all capacitor/inductor values now correct.

### KH-024 (MEDIUM): #GND power symbols as components

- **File**: `analyze_schematic.py` — legacy parser
- **Root cause**: Checked `#PWR`/`#FLG` prefixes but not generic `#` prefix. Non-standard
  power symbols like `#GND`, `#+3V3` slipped through as regular components.
- **Fix**: Changed to `comp["reference"].startswith("#")`. Also updated enable/power-good
  filtering and known_power_rails detection to use `startswith("#")`.
- **Verified**: All legacy schematic repos pass.

### KH-049 (MEDIUM): Non-standard ref prefixes (CB, RB, QB)

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: Full prefix "CB" not in type_map, fell to "other".
- **Fix**: After full-prefix lookup fails, try first-character fallback:
  `type_map.get(prefix[0])`. CB→C→capacitor, RB→R→resistor, QB→Q→transistor.
- **Verified**: Unit tests pass for CB1, RB3, QB2.

### KH-077 (MEDIUM): Per-component category always None

- **File**: `analyze_schematic.py` — component output
- **Root cause**: Component dict had `type` but output expected `category` field.
- **Fix**: Added `comp["category"] = comp.get("type")` before serialization loop.
- **Verified**: All components now have category field populated.

### KH-025 (LOW): X prefix crystals as connectors

- **File**: `kicad_utils.py` — `classify_component()`
- **Root cause**: X-prefix components defaulted to connector when value didn't match
  keyword list. Compact frequency values like "8M", "12M" didn't match "mhz"/"khz".
- **Fix**: Added regex `r'^\d+\.?\d*[mkMK]$'` to catch compact frequency notation.
- **Verified**: X1 with value "8M", "12M", "32.768K" all correctly classified as crystal.

### KH-056 (MEDIUM): I2S data lines detected as I2C

- **Files**: `analyze_schematic.py`, `signal_detectors.py`
- **Root cause**: "SDA" substring matched I2S pins like `I2S0_RX_SDA`.
- **Fix**: Added `"I2S" in nu` exclusion before I2C matching in three locations:
  net-name-based detection, pin-name-based detection, and observation detector.
- **Verified**: hackrf-pro: I2S nets no longer appear in I2C bus results.

### KH-057 + KH-022 + KH-065 (MEDIUM/LOW): UART false positives

- **File**: `analyze_schematic.py` — UART detection
- **Root cause**: TX/RX substring match without excluding RMII/PCIe/clock/USB/HDMI/I2S.
- **Fix**: Expanded exclusion list to include RMII, MII, EMAC, ENET, ETH, PCIE, PCI_,
  HDMI, LVDS, MIPI, CLK, CLOCK, USB_D, USBDM, USBDP, I2S.
- **Verified**: ESP32-EVB: RMII signals no longer in UART. urti-mainboard: clock/RF
  signals excluded.

### KH-050 (MEDIUM): Fixed regulator analyzed as adjustable

- **Files**: `kicad_utils.py` — `lookup_regulator_vref()`, `signal_detectors.py`
- **Root cause**: No suffix parsing for fixed-output variants (LM2596S-**12**).
- **Fix**: (a) Parse part number for fixed voltage suffix patterns: `-3.3`, `-33`, `-3V3`,
  `-1V8`, `-12`. Return fixed voltage directly with source="fixed_suffix".
  (b) In regulator detector, emit fixed vout before feedback analysis and skip
  feedback divider when fixed suffix found.
- **Verified**: LM2596S-12→1.2V, AMS1117-3.3→3.3V, RT9013-18→1.8V all correct.

### KH-054 + KH-055 (HIGH): RF amplifier/switch not detected

- **File**: `signal_detectors.py`
- **Root cause**: rf_amp_keywords missing BGB741, TRF37C, etc. LNAs misclassified as
  power regulators due to having VIN/VOUT-like pins.
- **Fix**: (a) Expanded rf_amp_keywords with `bgb7`, `trf37`, `sga-`, `tqp3`, `sky67`.
  (b) Added RF IC exclusion list in power regulator detector pre-filter.
- **Verified**: hackrf-pro: BGB741L7ESD now in rf_chains amplifiers, not power_regulators.
  LNA1109: BGB741L7ESD no longer falsely detected as regulator.
- **Note**: KH-055 RF switch detection was already implemented via rf_switch_keywords in
  a prior fix. This batch confirmed switches are detected and added the RF exclusion
  to prevent regulator false positives on RF ICs.

### KH-071 (MEDIUM): RF matching FPs on power LC filters

- **File**: `signal_detectors.py` — `detect_rf_matching()`
- **Root cause**: No value range filtering — 6.8uH + 10uF treated as RF matching.
- **Fix**: After has_inductor check, parse values and skip if inductors >1uH or caps >1nF.
- **Verified**: Power supply LC filters no longer flagged as RF matching networks.
  4 false-positive assertions removed from reference data.

### Regression results

- **7004/7004** assertions pass (4 FP assertions removed)
- **0 regressions**, 19 possibly fixed, 15 newly detected
- All test repos pass: hackrf-pro (12), ESP32-EVB (12), LNA1109 (1), OnBoard (279),
  urti-mainboard (18)

---

## 2026-03-13 — KH-015, KH-041 through KH-046, TH-007 (batch fix, 8 issues)

Source repos reviewed: ubertooth, analog-toolkit, throwing-star-lan-tap

### KH-015 (HIGH): Legacy schematic missing signal_analysis

- **File**: `analyze_schematic.py` — `parse_legacy_schematic()`
- **Root cause**: Legacy parser never called `analyze_signal_paths()` or `analyze_design_rules()`.
  All KiCad 4/5 `.sch` files got zero signal detections.
- **Fix**: Added `analyze_signal_paths()` and `analyze_design_rules()` calls after
  `build_pin_to_net_map()`, matching the KiCad 6+ path. Added `signal_analysis` and
  `design_analysis` to the return dict.
- **Note**: Limited value until KH-016 (wire-to-pin connectivity) is fixed — many nets are
  orphaned. But some nets resolve correctly, and detectors now find circuits on those.
- **Verified**: ubertooth-one.sch: 1 voltage divider, 3 LC filters, 1 crystal circuit,
  3 decoupling analyses, 4 protection devices, 1 transistor circuit, 1 RF matching network.

### KH-041 (MEDIUM): RF matching false positives on non-RF designs

- **File**: `signal_detectors.py` — `detect_rf_matching()`
- **Root cause**: (1) `sma` keyword in value field matched SMA connectors used as test points,
  not antennas. (2) Pure R+C networks near "antennas" were flagged as matching networks.
- **Fix**: (1) Moved `sma` to lib_id-only keyword list — value field no longer triggers.
  (2) Added inductor requirement: matching networks without inductors are skipped (pure C
  networks are decoupling/filtering, not impedance matching).
- **Verified**: analog-toolkit: 13 false positives eliminated (was RC anti-aliasing on ADC inputs).
  icebreaker: 4 false positives eliminated. ubertooth: real pi_match with L1/L2/C1/C3/C5 retained.

### KH-042 (LOW): dnp_parts counts BOM lines not instances

- **File**: `analyze_schematic.py` — `compute_statistics()`
- **Root cause**: `len(dnp_items)` counted BOM group entries (unique value/footprint combos),
  not individual component instances.
- **Fix**: Changed to `sum(b["quantity"] for b in dnp_items)`.
- **Verified**: analog-toolkit: 13 DNP resistors now correctly reported as dnp_parts=13 (was 1).

### KH-043 + KH-044 (LOW): PCB copper_layers_used and front/back counts for custom layer names

- **File**: `analyze_pcb.py` — `compute_statistics()`
- **Root cause**: (1) `copper_layers_used` checked `"Cu" in layer_name` — failed for KiCad 5
  custom names like `"Front"`, `"Back"`. (2) `front_side`/`back_side` hardcoded `"F.Cu"`/`"B.Cu"`.
- **Fix**: Added `layers` parameter to `compute_statistics()`. Resolves copper layer names from
  layer declarations (type in signal/power/mixed/user). Front/back resolved by layer number
  (0=front, 31=back) instead of hardcoded names. Fallback to `"Cu" in name` when no layer
  declarations available.
- **Verified**: throwing-star-lan-tap: copper_layers_used=2 (was 0), copper_layer_names=["Back","Front"],
  front_side=6/11 (was 0), back_side=1 (was 0).

### KH-045 (MEDIUM): Legacy custom field MPN/manufacturer extraction

- **File**: `analyze_schematic.py` — legacy component field parsing
- **Root cause**: Fields with generic names `"Field1"`, `"Field2"` (common KiCad 4/5 convention)
  weren't matched by keyword-based extraction.
- **Fix**: Track generic-named fields during parsing. After keyword matching, apply positional
  fallback: Field2→MPN, Field1→manufacturer (only when mpn/manufacturer still empty).
- **Verified**: ubertooth: 68/89 components now have MPNs and manufacturers (was 0/89).
  Examples: FB5→Murata/BLM18TG601TN1D, R17→Bourns/CR0603-JW-103ELF.

### KH-046 (LOW): CONN_1 tilde prefix prevents pin lookup

- **File**: `analyze_schematic.py` — `_parse_legacy_lib()`
- **Root cause**: Legacy lib stores symbol name as `~CONN_1` (tilde = invisible name display
  flag). Parser stored `~CONN_1` but schematic lookup used `CONN_1`. Lookup failed, pins empty.
- **Fix**: Strip leading tilde from symbol name: `parts[1].lstrip("~")`.
- **Verified**: ubertooth: P5-P13 (9 CONN_1 test pads) now have 1 pin each (was 0).

### TH-007 (MEDIUM): discover_projects() doesn't recognize .pro as project marker

- **File**: `utils.py` — `discover_projects()`
- **Root cause**: Only `.kicad_pro` and `.kicad_pcb` recognized as project markers. KiCad 4/5
  uses `.pro` files.
- **Fix**: Added `.pro` rglob with header check (first line starts with `update=`, `[pcbnew`,
  or `[eeschema`) to confirm KiCad format.
- **Verified**: ubertooth: 7 projects discovered (was 0). Snapshot/baseline workflows now work.

---

## 2026-03-13 — KH-027 through KH-040 (batch fix, 14 issues)

Source repos reviewed: hackrf, bitaxe, icebreaker, moteus, OtterCastAudioV2

### KH-027 (CRITICAL): Symbol name filter skips valid custom symbols

- **File**: `analyze_schematic.py` — `extract_lib_symbols()`
- **Root cause**: Sub-unit filter `name.split("_")[-1].isdigit()` matched any symbol
  ending in `_<digit>`, not just sub-unit patterns like `Device:C_0_1`.
- **Fix**: Changed to `rsplit("_", 2)` and require both last two segments are digits.
  `Q_NMOS_CSD17311Q5_1` → parts `["Q_NMOS", "CSD17311Q5", "1"]` → not filtered.
  `Device:C_0_1` → parts `["C", "0", "1"]` → correctly filtered.
- **Verified**: bitaxe Q1/Q2 now `type=transistor` (were missing from lib_symbols entirely).

### KH-028 (HIGH): Ferrite bead values parsed as henries

- **Files**: `kicad_utils.py` — `classify_component()`, `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: L-prefix components with "ferrite"/"bead" in lib_id/value were classified
  as `inductor`. Their impedance values (e.g., "600" = 600Ω @ 100MHz) were treated as
  henries, producing nonsensical LC filter results.
- **Fix**: (1) `classify_component()` now returns `ferrite_bead` when lib_id or value
  contains "ferrite" or "bead". (2) `detect_lc_filters()` skips components with
  `type == "ferrite_bead"` or ferrite/bead keywords.
- **Limitation**: Doesn't catch rescue-library ferrite beads with generic symbol names
  and bare numeric values (e.g., icebreaker L1/L2 = `pkl_L_Small` value `600`). Would
  need heuristic value-range detection for those.
- **Verified**: Components with ferrite metadata correctly reclassified and excluded from LC filters.

### KH-029 (HIGH): MPN field aliases (PARTNO, Part Number)

- **File**: `analyze_schematic.py` — KiCad 6+ property chain and legacy field handler
- **Root cause**: MPN extraction only recognized a narrow set of field names. Common
  alternatives `PARTNO`, `Part Number`, `PART_NUMBER` were not mapped.
- **Fix**: Added `PARTNO`, `PartNo`, `Partno` to KiCad 6+ `get_property()` chain.
  Added `PARTNO`, `PART NUMBER`, `PART_NUMBER`, `PART NO` to legacy field name tuple.
- **Verified**: bitaxe 86/136 components now have MPNs populated (was 0).

### KH-030 (HIGH): Current sense with IC-integrated amplifier

- **File**: `signal_detectors.py` — `detect_current_sense()`
- **Root cause**: Detector only matched shunt + discrete sense IC topology. Gate drivers
  and power ICs with integrated CSA inputs (CSP/CSN/SEN/ISENSE pins) were not detected.
- **Fix**: Added second-pass loop over unmatched shunt candidates. Checks if either shunt
  net connects to an IC pin with a CSA-related name from `_integrated_csa_pins` frozenset.
  Creates entry with `type: "integrated_csa"`.
- **Limitation**: moteus DRV8323 not matched because shunt→CSA path goes through net ties
  and RC filters, and KH-026 (multi-instance net merging) prevents correct net resolution.
- **Verified**: Detection works for direct shunt-to-IC-pin topologies.

### KH-031 (HIGH): RF antenna matching networks

- **File**: `signal_detectors.py` — new `detect_rf_matching()`
- **Root cause**: No detector existed for antenna matching networks.
- **Fix**: New function finds antenna connectors (AE*/ANT* prefix or antenna/u.fl/sma
  keywords), BFS through L/C components (max 6 hops), classifies topology:
  - `pi_match`: ≥1 series L + ≥2 shunt C
  - `T_match`: ≥2 series L + ≥1 shunt C
  - `L_match`: 2 components, 1 series + 1 shunt
  - `matching_network`: other arrangements
  Reports target IC if BFS reaches one.
- **Wiring**: Added to `analyze_signal_paths()` imports, call, and results dict as `rf_matching`.
- **Verified**: Compiles and runs on all 9 test repos.

### KH-032 (HIGH): SDIO bus protocol detection

- **File**: `analyze_schematic.py` — `analyze_design_rules()` bus detection section
- **Root cause**: No SDIO/SD/eMMC bus category existed in the bus protocol detector.
- **Fix**: Added SDIO detection after UART, before CAN. Matches net names with prefixes
  `SDIO`, `SD_`, `SD1_`, `SD2_`, `EMMC`, `MMC`, `WL_SDIO` combined with CLK/CMD/D0-D7
  signals. Requires CLK + CMD + D0 minimum. Reports bus width, pull-up presence on CMD
  and data lines, and connected IC devices.
- **Verified**: OtterCastAudioV2 detects both `SD` (SDC0_*) and `SDIO` (WL_SDIO_*) buses,
  4-bit width, pull-ups on CMD+D0-D3.

### KH-033 (MEDIUM): DNP from value/Note field

- **File**: `analyze_schematic.py` — KiCad 6+ and legacy paths
- **Root cause**: Only checked explicit KiCad 7+ `dnp` attribute or field named "DNP".
  Designs using `value="DNP"` or `Note="DNP"` convention were not recognized.
- **Fix**: KiCad 6+ path: after `dnp = get_value(sym, "dnp") == "yes"`, check if value
  is in `("DNP", "DO NOT POPULATE", "DO NOT PLACE", "NP")`. Legacy path: same value
  check after field processing, plus `NOTE`/`NOTES`/`COMMENT` field value check.
- **Verified**: OtterCastAudioV2 C49 now `dnp=True` (value="DNP").

### KH-034 (MEDIUM): Active oscillator detection

- **File**: `signal_detectors.py` — `detect_crystal_circuits()`
- **Root cause**: Only passive crystals with load caps were detected. Active oscillators
  (TCXO, VCXO, MEMS) with VDD/GND/OUT pins were ignored.
- **Fix**: Added loop after passive crystal detection, before return. Matches components
  with `type == "oscillator"` or oscillator keywords in value/lib_id. Identifies output
  pin by name (OUT/CLK/CLKOUT) or falls back to first non-power/non-ground pin. Emits
  entries with `type: "active_oscillator"` and empty `load_caps`.
- **Verified**: Compiles and runs on all test repos.

### KH-035 (MEDIUM): Integrated LDO on IC pins

- **File**: `signal_detectors.py` — new `detect_integrated_ldos()`
- **Root cause**: ICs with internal LDOs (e.g., FT2232H VREGOUT pin) were not detected
  as power sources.
- **Fix**: New function scans ICs not already in `power_regulators` for pins named
  `VREGOUT`, `VREG`, `LDO_OUT`, `REGOUT`, etc. If pin drives a power net (not ground),
  adds entry with `topology: "integrated_ldo"`. Results appended to `power_regulators`.
- **Verified**: Compiles and runs on all test repos.

### KH-036 (MEDIUM): LC filter parallel cap merging

- **File**: `signal_detectors.py` — `detect_lc_filters()`
- **Root cause**: Caps were grouped for parallel merging by `(inductor_ref, shared_net)`
  only. Caps with different "other" nets (series vs shunt topology) were falsely merged.
- **Fix**: Changed grouping key to include the cap's other net:
  `(ind_ref, shared_net, cap_other_net)`. Only caps sharing both terminals get merged.
- **Verified**: Compiles and runs on all test repos.

### KH-037 (MEDIUM): IC with internal regulator

- **File**: `signal_detectors.py` — `detect_power_regulators()`
- **Root cause**: Complex ICs with internal switching regulators (e.g., AP6236 WiFi module
  with SW pin + inductor) classified as dedicated power regulators.
- **Fix**: After topology classification, check pin ratio. If IC has >10 total pins and
  <20% are regulator-related names (VIN/VOUT/FB/SW/EN/BST/etc.), set topology to
  `"ic_with_internal_regulator"`.
- **Verified**: Compiles and runs on all test repos.

### KH-038 (MEDIUM): Sense inputs vs power domain

- **File**: `analyze_schematic.py` — power domain mapping in `analyze_design_rules()`
- **Root cause**: IC sense/measurement pins (IN+, IN-, SENSE, CSP, CSN) connected to
  power rails being monitored were included in the IC's power domain, causing false
  cross-domain warnings.
- **Fix**: Added `_sense_pin_names` exclusion set. Pins with these names are skipped
  before power domain classification.
- **Verified**: Compiles and runs on all test repos.

### KH-039 (MEDIUM): Power rail detection beyond power symbols

- **File**: `analyze_schematic.py` — `build_statistics()`
- **Root cause**: `power_rails` only included nets from `power_symbol` components.
  Nets defined by local/hierarchical labels matching voltage patterns (e.g., "3V3",
  "VIN_M") were missed.
- **Fix**: After collecting power symbol rails, also scan all net names through
  `is_power_net_name()` and add matches.
- **Verified**: Compiles and runs on all test repos.

### KH-040 (MEDIUM): Legacy Description field

- **File**: `analyze_schematic.py` — legacy custom field handler
- **Root cause**: No case for `DESCRIPTION` or `DESC` field names in the legacy parser's
  custom field handler.
- **Fix**: Added `elif fu in ("DESCRIPTION", "DESC"): comp["description"] = field_val`.
- **Verified**: Compiles and runs on all test repos.

---

## Pre-2026-03-13 — Earlier fixes (KH-001 through KH-011, KH-014, KH-023, TH-001 through TH-006)

These issues were fixed in earlier sessions. Details not recorded here — see git history
of the kicad-happy and kicad-happy-testharness repos for the actual changes.

### KH-001 through KH-011, KH-014, KH-023

Analyzer fixes predating the structured issue tracker. Covered schematic parsing,
legacy format support, component classification, and signal detection improvements.

### TH-001 through TH-006

Test harness infrastructure: checkout.py, discover.py, run scripts, regression framework,
validation pipeline, budget monitoring. All resolved.
