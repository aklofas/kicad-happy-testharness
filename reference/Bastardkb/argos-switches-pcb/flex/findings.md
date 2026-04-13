# Findings: Bastardkb/argos-switches-pcb / flex

## FND-00001944: All 12 components correctly identified including 4 in-BOM LEDs and 4 not-in-BOM switches; SK6812MINI addressable LED chain of 4 LEDs correctly detected; Power rails correctly identified as 'Gnd' an...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex.kicad_sch
- **Created**: 2026-03-24

### Correct
- The flex sub-PCB has 12 total components: 4x SW_Push (in_bom=false, footprint 'custom:choc'), 4x SK6812MINI LEDs (RIGHT_LED), 2 connectors (J2, J7), 1 resistor R3 (in_bom=false), and 1 capacitor C3 (in_bom=false). The component_types breakdown (switch:4, connector:2, led:4, resistor:1, capacitor:1) matches exactly.
- The 4 SK6812MINI LEDs (D13, D14, D15, D16) are correctly identified as a single-wire (WS2812) addressable LED chain of length 4, with first_led=D13 and last_led=D16. The estimated current of 240mA (4 x 60mA) is appropriate.
- The schematic uses global labels 'Gnd' and 'Vcc' (not the standard KiCad 'GND'/'VCC' power symbols), and the analyzer correctly picks these up as power rails from global label context.

### Incorrect
(none)

### Missed
- C3 (value 'NA_C', in_bom=false) is connected to Vcc and Gnd on the flex board, functioning as an optional decoupling capacitor placeholder. The decoupling_analysis section is empty (no rail analyzed) despite Vcc being a power rail with an associated capacitor. This is a minor miss since the capacitor is a placeholder (NA value), but the power rail should still appear in decoupling_analysis.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001945: Footprint count of 14 correct for flex PCB with 2-layer stackup; smd_count=0 is wrong: SK6812MINI LEDs are SMD components

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: flex.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The flex PCB has 14 footprints (9 front, 5 back), 2 copper layers, 15 vias, 2 zones, 12 nets, and 323 track segments. Board dimensions 41.614 x 42.28mm. All statistics are internally consistent.

### Incorrect
- The PCB reports smd_count=0 and tht_count=12. However, the SK6812MINI (SK6812_mini_e_corners footprint) is an SMD component — it has surface-mount pads. The 4 LEDs should be counted as SMD, giving smd_count>=4. The switches using the 'custom:choc' footprint (Choc key switches) have through-hole pins, so tht_count=12 for switches + some connectors may be partially correct, but zero SMD components is wrong for a board with addressable SMD LEDs.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
