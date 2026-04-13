# Findings: wodowiesel/SW-Meter / pcb_swmeter

## FND-00001315: SW-Meter: LM3914N bar-graph LED driver correctly identified as IC, all THT components correctly classified; LM3914N power domain not detected — U1 appears in power_net_summary GND but not in ic_pow...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: swmeter.kicad_sch
- **Created**: 2026-03-24

### Correct
- 16 total components: 5 connectors, 3 switches (SW1 SPDT, SW2 SPDT, SW3 DIP3), 4 resistors (including 3 potentiometers classified as resistor which is acceptable), 1 IC (LM3914N), 1 diode (1N5711), 1 capacitor, 1 LED display (BAR1=HDSP-4836 classified as led). Power rails +9V and GND correctly identified.
- D0 (1N5711 diode) and J0 (2-pin connector) use non-standard zero-indexed references. The analyzer correctly identifies these in annotation_issues.zero_indexed_refs.

### Incorrect
- ic_power_rails is empty ({}), meaning the LM3914N is not placed in any power domain. The LM3914 VCC pin connects to +9V. The analyzer failed to associate U1 with the +9V power rail. Additionally +9V pin_count=2 shows only D0 and J0 connected, missing U1's VCC. This suggests the power rail connectivity for the LM3914 was not traced correctly.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001316: smd_count=0 for SW-Meter PCB despite schematic having SMD components; all 31 footprints classified as THT or untyped

- **Status**: new
- **Analyzer**: pcb
- **Source**: swmeter.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The schematic includes BAR1 (HDSP-4836 DIP display) and U1 (LM3914N DIP-18) which are THT, but also potentiometers and resistors that could be SMD or THT. PCB reports smd_count=0 and tht_count=16. 15 unclassified footprints is suspicious — likely footprints using older pad type conventions that the analyzer fails to classify as SMD or THT. Worth investigating whether the analyzer correctly handles vintage KiCad footprint pad types.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001317: Gerber set reports 35 files but drill_files=0 and total_holes=0; PTH and NPTH drill files exist but are not counted as drill files; Component refs in gerber output contain quoted duplicates ('C1' a...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gbr
- **Created**: 2026-03-24

### Correct
- The .gbrjob file correctly drives the completeness check — all 9 standard layers found, none missing. Board dimensions correctly read from gbrjob as 53.08×66.08mm. Layer alignment correctly reported as aligned (all layers share same extents from gbrjob coordinates).

### Incorrect
- The gerber directory contains swmeter-PTH-drl.gbr and swmeter-NPTH-drl.gbr which are drill files in Gerber RS-274X format (not Excellon), plus swmeter-PTH-drl-drl_map.gbr and swmeter-NPTH-drl-drl_map.gbr. The analyzer correctly shows flashes in swmeter-PTH-drl.gbr (165 holes including 77 via drills and 88 component drills) but reports drill_files=0 — it is not recognizing Gerber-format drill files as drill files. has_pth_drill and has_npth_drill are both false, which contradicts the file content parsed.
  (signal_analysis)
- The component_refs list contains both quoted variants (e.g., '"BAR1"', '"C1"', '"U1"') and unquoted variants (BAR1, C1, U1). This creates doubled/duplicate entries in pads_per_component as well, and inflates total_unique from 15 to 45 components. The X2 attribute parser is not stripping quotes from component reference attribute values.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
