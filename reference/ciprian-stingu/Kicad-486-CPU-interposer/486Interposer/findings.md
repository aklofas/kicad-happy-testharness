# Findings: Kicad-486-CPU-interposer / 486Interposer

## FND-00000777: Component enumeration and net extraction correct for 486 interposer; Decoupling warning for 486 socket is a false positive — interposer passes through signals, doesn't power the CPU; No JTAG bus de...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 486Interposer.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Correctly identified 5 components (4 connectors + 486 socket), 119 nets including full address/data/control bus naming, and 2 power rails (VCC, GND). Net names with tilde/slash escaping handled correctly.

### Incorrect
- design_observations reports 'rails_without_caps: [VCC]' for U1 (486Socket). This is a passthrough interposer: J4 is the VCC connector that feeds the board. The interposer itself should not have decoupling caps — those belong on the CPU board. The warning is technically true but misleading for this design topology.
  (signal_analysis)

### Missed
- The net list includes /TCK, /TDI, /TDO, /TMS — classic JTAG signals. bus_analysis shows i2c/spi/uart/can all empty. A JTAG protocol detector would flag this as a JTAG interface routed through the interposer.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000778: PCB correctly identified as all-THT with 5 components, 119 nets, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: 486Interposer.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- smd_count=0, tht_count=5, footprint_count=5, net_count=119, routing_complete=true. Matches schematic component/net counts perfectly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000779: Gerber completeness check correct — all 9 required layers plus drill files present; B.Paste and F.Paste empty layers reported but not flagged — expected for all-THT board

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: pcb.json
- **Created**: 2026-03-23

### Correct
- Layer set complete (F/B Cu, Mask, Paste, SilkS, Edge.Cuts), both PTH and NPTH drill files present. 336 total holes (290 component + 46 vias) consistent with PCB analysis. User_Comments layer classified as 'unknown' with FileFunction 'Other,Comment' — acceptable.

### Incorrect
- Both paste layers have aperture_count=0, flash_count=0, draw_count=0, yet completeness shows them as 'found' and the board is marked complete=true. For an all-THT board (smd_ratio=0.0) this is correct behavior, but there is no annotation in the output noting why paste is empty. Minor: not actually incorrect, but could be more informative.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
