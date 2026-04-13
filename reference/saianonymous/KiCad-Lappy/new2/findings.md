# Findings: saianonymous/KiCad-Lappy / new2

## FND-00000684: LM741 inverting amplifier misclassified as comparator_or_open_loop

- **Status**: new
- **Analyzer**: schematic
- **Source**: new2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- R2 connects U1 output (__unnamed_4) back to U1 inverting input (-) forming negative feedback — this is an inverting amplifier, not open-loop. R1 (1k) is input-side pull-down to GND, R2 (series) is feedback resistor. The analyzer reports 'comparator_or_open_loop' but should report 'inverting_amplifier'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000685: LM741 inverting amplifier misclassified as transimpedance_or_buffer; Feedback resistor R2 (9k) correctly identified in opamp circuit; Voltage divider on non-inverting input not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: new3_new3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The analyzer correctly identifies R2 as the feedback resistor with ohms=9000 and correctly traces the output, inverting input, and non-inverting input nets.

### Incorrect
- R2 (9k) connects from U1 output (__unnamed_2) to U1 inverting input (-) with R1 (1k) pulling inverting input to GND. This is a classic inverting amplifier (gain = -R2/R1 = -9). The analyzer reports 'transimpedance_or_buffer' instead of 'inverting_amplifier'.
  (signal_analysis)

### Missed
- new3 has no voltage divider on the non-inverting input (J2 goes directly to + pin), so this is not missed. However, the 1k+9k resistor network (R1 as input resistor to GND, R2 as feedback) is not detected as a voltage_divider even though it forms the gain-setting resistor network.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000686: Component count, net count, board dimensions, and routing completeness all correct; DIP-8 SMDSocket footprint U1 misclassified as smd type with pad_count=8 but actual pad_count should be 8

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: new3_new3.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 6 footprints on F.Cu, 9 nets, 45.72x33.02mm board, routing_complete=true with 0 unrouted nets. All pad-to-net assignments match schematic nets. Single copper layer (F.Cu only) correctly identified.

### Incorrect
- U1 (Package_DIP:DIP-8_W7.62mm_SMDSocket_SmallPads) is classified as type='smd' with pad_count=8. The SMDSocket variant does use SMD pads so the type is defensible, but the tht_count remains 0 and smd_count=6 including connectors that are also SMD_Vertical variants. Classification is internally consistent but note that the physical package would be placed in a DIP socket, making assembly classification misleading.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000687: False alignment failure: empty back-copper layers with 0x0 extents inflate alignment variance metrics; Layer completeness, component count, pad count, and net analysis all correct

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: new3_gerber.json
- **Created**: 2026-03-23

### Correct
- 9 gerber files detected complete (all expected layers present), 6 components, 19 pads, 9 nets, 3 named power nets (+15V, -15V, GND). Single trace width 0.25mm matches PCB output.

### Incorrect
- aligned=false with 'Width varies by 8.5mm across copper/edge layers' and 'Height varies by 5.1mm across copper/edge layers'. The board is single-sided (all copper on F.Cu). B.Cu, B.Mask, B.Paste, B.SilkS all have width=0/height=0. The 0x0 extents of empty back layers should be excluded from the layer-extent variance calculation. The actual F.Cu vs Edge.Cuts offset (~8mm/5mm) is real but expected for a board where copper doesn't extend to edge.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
