# Findings: calcite / Calcite52_pcb_Calcite52

## FND-00002298: RP2040 + W25Q128 flash memory interface detected correctly

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_calcite_Calcite52_pcb_RP2040.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified the W25Q128JVS flash IC (U3) as a memory interface connected to the RP2040 (U4) with 6 shared signal nets, and detected the 12 MHz crystal circuit with 20 pF load caps on Y1. Component counts (25 total: 14 caps, 6 resistors, 2 ICs, 1 crystal, 2 switches) are correct for a typical RP2040 sub-sheet.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002299: 5x12 key matrix with 52 switches and 52 diodes correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematic_calcite_Calcite52_pcb_key_matrix.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer found a 5-row by 12-column key matrix (ROW_0..ROW_4, COL_0..COL_11) with 52 switches and 52 diodes, matching the Calcite52 keyboard's 52-key layout. Detection method was net_name-based, which is reliable here.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002300: USB_D- falsely reported as lacking ESD protection despite connecting to SRV05-4

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_calcite_Calcite52_pcb_Calcite52.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- design_observations lists USB_D- with has_esd_protection=false, while USB_D+ on the same net has has_esd_protection=true. Both nets connect to the same SRV05-4 quad-channel ESD protection IC (U2) on pins IO3 and IO2 respectively. The differential_pairs analysis correctly reports has_esd=true for the pair, so only the per-line design_observation is wrong. The ESD device recognition logic likely uses a pin-name heuristic that matches IO2 but not IO3.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
