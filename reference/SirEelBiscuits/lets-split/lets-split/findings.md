# Findings: SirEelBiscuits/lets-split / lets-split

## FND-00002380: Key matrix estimated_keys and switches_on_matrix report 48 instead of 24; Voltage divider (HalfSelector bias network) correctly detected for split keyboard half-identification; USB Type-C CC pull-d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_lets-split_lets-split.sch.json.json
- **Created**: 2026-03-24

### Correct
- R1 (9.1k) and R2 (9.1k) form a 0.5-ratio divider from VCC to GND with mid-point HalfSelector connected to MCU pin B2. This is the standard technique used in Let's Split designs to let the MCU detect which half it's on. The analyzer correctly identifies both resistor values, the VCC/GND rails, and the MCU pin connection.

### Incorrect
- The analyzer detects a 4-row x 6-col matrix (row_nets: Row1-Row4, col_nets: Col1-Col6) and correctly reports rows=4, columns=6. However, estimated_keys=48 and switches_on_matrix=48 instead of the correct 4*6=24. The actual component count is also 24 switches (SW1-SW24; SW25 is a reset button, not a key switch). The doubling suggests the analyzer is somewhere counting each switch twice — possibly iterating both row→diode and diode→switch paths.
  (signal_analysis)

### Missed
- J1 is a USB-C receptacle (GCT USB4085). R1 and R2 (both 9.1k) are connected to USB CC lines (PadA5/PadB5 net area) for USB 2.0 downstream-facing port configuration. However the analyzer classifies these resistors only as a voltage divider for the HalfSelector net, not as USB CC configuration resistors. It does not detect the USB 2.0 interface at all — no USB detection in signal_analysis. The CC resistors should be recognized as part of a USB-C configuration network rather than solely as a voltage divider.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002381: Reversible PCB board layout correctly identified with dual-sided silkscreen text (Left/Right labels)

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_lets-split_lets-split.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB has 'Left' and 'Right' labels on both B.SilkS and F.SilkS layers at the same X coordinate, reflecting the reversible design where the board can be used as either half. The analyzer captures all six board_texts including the 'USB on far side' instruction. Front-to-back component split (57 front, 3 back) with only 1 via across the entire board correctly characterizes a primarily single-layer-routed keyboard PCB.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
