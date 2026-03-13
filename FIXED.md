# Fixed Issues

Record of resolved kicad-happy analyzer bugs (KH-*) and test harness issues (TH-*).
Shows what changed, where, and how it was verified — useful for cross-referencing
regressions, understanding analyzer evolution, and onboarding collaborators.

See ISSUES.md for open issues.

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
