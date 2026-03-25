# Findings: PICTAS / hardware_pictas-pcb_pictas

## FND-00001049: SPI, UART, I2C, USB differential pair, memory interface all correctly detected; No power regulator detected despite power mux sub-sheet (power-select with TPS2115APWR)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pictas.kicad_sch
- **Created**: 2026-03-23

### Correct
- SPI1 bus (U3 PIC18LF47K42 ↔ U4 W25Q128JVSIQ with CS), UART between U1/U3, I2C on U2 MCP2221A, D+/D- differential pair, and W25Q128 memory interface are all correctly identified. Transistor circuits Q1 (BC546) and Q2 (BC556) correctly found.

### Incorrect
(none)

### Missed
- The design uses a TPS2115APWR power-path switch/mux in a sub-sheet (power-select.kicad_sch), but since the analyzer processes each sheet independently and the main sheet has no power regulator components directly, the power_regulators list is empty. This is expected behavior but means the power architecture is invisible in the top-level analysis.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001050: False positive single_pin_nets and undriven_input_label warnings on hierarchical labels; TPS2115APWR pin D0 connected to GND incorrectly classified as having a decoupling cap

- **Status**: new
- **Analyzer**: schematic
- **Source**: power-select.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- USB_PWR and OUT_PWR are flagged as single-pin nets and undriven input labels, but they are hierarchical labels connected to the parent sheet. The analyzer doesn't resolve hierarchical connectivity, so it incorrectly treats these as isolated. This is a known limitation but generates misleading warnings for sub-sheets.
  (signal_analysis)
- Pin 2 (D0) of TPS2115APWR is connected to GND and the output says 'has_decoupling_cap: true' with 'note: Ground net — decoupling caps listed on VCC/VDD pins'. D0 is a logic input used to control priority, not a power supply pin, so this 'decoupling cap present' annotation is misleading.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001051: Gerber alignment false positive: normal silk/paste size variation triggers 'aligned: false'

- **Status**: new
- **Analyzer**: gerber
- **Source**: out
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The alignment check reports 6.3mm width and 5.3mm height variance across layers and marks the set as misaligned. B.Paste and drill extents being smaller than Edge.Cuts is expected (paste only covers SMD pads, copper stays within board). This pattern is a recurring false positive — the board is actually a correctly exported 2-layer THT-dominant design.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001052: PCB stats correct: 2-layer, 37 footprints, 82 nets, routing complete, 2 SMD parts

- **Status**: new
- **Analyzer**: pcb
- **Source**: pictas.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Board dimensions (74.93×89.15mm), layer count (2), footprint count (37), via count (24), and routing_complete=true are all consistent with the schematic (36 components + 1 extra) and gerber data. SMD count of 2 (U4 W25Q128 SOIC-8 and U5 LM1881 SOIC-8) is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
