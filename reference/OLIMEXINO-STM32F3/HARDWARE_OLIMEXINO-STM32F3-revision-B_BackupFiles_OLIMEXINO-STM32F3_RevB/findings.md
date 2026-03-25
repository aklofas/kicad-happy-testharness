# Findings: OLIMEXINO-STM32F3 / HARDWARE_OLIMEXINO-STM32F3-revision-B_BackupFiles_OLIMEXINO-STM32F3_RevB

## FND-00000975: Crystal frequency parsed as 0.0327681206125 Hz instead of 32768 Hz; assembly_complexity reports tht_count=0 while PCB analyzer correctly reports tht_count=12; PWR_FLAG warning on +BATT is a false p...

- **Status**: new
- **Analyzer**: schematic
- **Source**: HARDWARE_OLIMEXINO-STM32F3-revision-D_OLIMEXINO-STM32F3_Rev_D.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Q1 value '32768_1206_12.5pF' is treated as a decimal float rather than extracting the leading numeric token. The '1206' package code and '12.5pF' load cap spec are folded into the frequency value. Expected 32768 Hz (32.768 kHz). Same bug in Rev B and C1.
  (signal_analysis)
- The schematic analyzer classifies all 104 components as SMD (tht_count=0) because it cannot reliably determine THT vs SMD from footprint library strings alone. PCB analyzer correctly shows 12 THT and 104 SMD footprints. The schematic-derived assembly complexity is misleading.
  (signal_analysis)
- +BATT rail shows pin_types=['output','passive','power_in'] but is still flagged for missing PWR_FLAG. A net with an output-typed pin is driven and should not trigger this warning. The +3.3VA, +5V, GND, GNDA warnings look legitimate (no output driver).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000976: Board outline not detected — edge_count=0, board_width_mm=null across all PCB revisions

- **Status**: new
- **Analyzer**: pcb
- **Source**: HARDWARE_OLIMEXINO-STM32F3-revision-D_OLIMEXINO-STM32F3_Rev_D.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- PCB analyzer reports zero Edge.Cuts edges and null board dimensions for all revisions (B, C, C1, D), while the gerber analyzer correctly extracts 68.54x53.34 mm from the same design's edge cuts. The PCB parser is not reading the Edge.Cuts layer geometry.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000977: Gerber layer detection and completeness check correct across all revisions

- **Status**: new
- **Analyzer**: gerber
- **Source**: HARDWARE_OLIMEXINO-STM32F3-revision-D_Gerbers
- **Created**: 2026-03-23

### Correct
- All revisions correctly identify 9 signal layers (F/B Cu, Mask, Paste, Silk + Edge.Cuts), PTH+NPTH drill files, board dimensions 68.54x53.34 mm, 2-layer stackup, alignment verified. No false completeness failures.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000978: Legacy KiCad 5 schematic (version 4) parsed correctly with 101 components, 5 ICs, crystal circuits, and ERC warnings

- **Status**: new
- **Analyzer**: schematic
- **Source**: HARDWARE_OLIMEXINO-STM32F3-revision-B_OLIMEXINO-STM32F3_RevB.sch
- **Created**: 2026-03-23

### Correct
- Rev B legacy .sch file parsed without errors. Component counts (101), power rails (8), crystal detection, and subcircuit detection all appear accurate. ERC produced 10 no_driver warnings which are plausible for a design with pulled-up nets and connector-exposed signals.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
