# Findings: Kicad-Breakout-Boards / Breakout Board STM32L041x6 - TSSOP20_Breakout Board STM32L041x6 - TSSOP20

## FND-00000782: RC filter false positive: C8 paired with both R5 and R6 producing two spurious filter entries; single_pin_nets observation incorrectly identifies U1 VDDA pin as net 'pa0'; Crystal circuit correctly...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breakout Board STM32L041x6 - TSSOP20_Breakout Board STM32L041x6 - TSSOP20.sch.json
- **Created**: 2026-03-23

### Correct
- Y1 (32.768kHz crystal) with C6 and C7 (both 6pF) correctly detected. effective_load_pF=6.0 and in_typical_range=true. Crystal frequency parsed correctly.

### Incorrect
- C8 (100nF) is detected as part of two RC low-pass filters: R5+C8 (1.59kHz) and R6+C8 (159Hz). C8 is a decoupling cap, not a filter cap. R5 and R6 are separate pull-up/debounce resistors on different nets. Analyzer is spuriously pairing C8 with any nearby resistors sharing a GND connection.
  (signal_analysis)
- design_observations reports {component: U1, pin: VDDA, net: 'pa0'} as a single-pin net. VDDA is the analog power supply pin of the STM32L041, not a signal labeled 'pa0'. This suggests a pin-to-net mapping error in the legacy schematic parser where pin names from adjacent symbols are conflated.
  (signal_analysis)
- In the legacy schematic output, capacitors C2, C3, C4, C5, C6, C7, C8 all have footprint 'Diode_SMD:D_0805_2012Metric_Pad1.15x1.40mm_HandSolder'. This is a real schematic error (wrong footprint assigned to capacitors). The analyzer correctly extracts the data but does not flag the semantic mismatch between component type 'capacitor' and a 'Diode_SMD' footprint library. A footprint/type consistency check is missing.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000783: PCB correctly identified mixed THT/SMD board with 31 footprints on 2 layers

- **Status**: new
- **Analyzer**: pcb
- **Source**: Breakout Board STM32L041x6 - TSSOP20_Breakout Board STM32L041x6 - TSSOP20.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- footprint_count=31, front_side=22, back_side=9, smd_count=19, tht_count=12, net_count=29, routing_complete=true, board dimensions 35.56×33.02mm all consistent with a STM32 breakout board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000784: Gerber layer completeness correct and SMD ratio accurately computed from paste layer

- **Status**: new
- **Analyzer**: gerber
- **Source**: Breakout Board STM32L041x6 - TSSOP20_Fabrication Outputs.json
- **Created**: 2026-03-23

### Correct
- All 9 standard layers present plus both drill files. smd_ratio=0.61 correctly derived from paste_layer_flashes (57 SMD pads vs 36 THT holes). Layer extents aligned. Board dimensions 35.56×33.02mm match PCB analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
