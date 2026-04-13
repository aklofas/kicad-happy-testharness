# Findings: maniekx86/M8SBC-486 / pcb_homebrew_486

## FND-00000844: AMS1117 regulators and voltage divider feedback networks correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_power.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Both AMS1117 adjustable regulators (U3, U4) are found in subcircuits with their feedback resistor dividers. Signal analysis correctly identifies the R5/R6 divider feeding U4 ADJ pin (+2V5 rail) and R7/R8 divider feeding U3 ADJ pin (+3.3V rail). Decoupling capacitors properly grouped by rail. No false positives in pwr_flag_warnings for this ATX-powered design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000845: Bus topology width count is wrong for address bus (37 instead of 30)

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_cpu.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The CPU sheet has A2..A31 (30 distinct address signals — 486 omits A0/A1, using BE0-BE3 instead). The analyzer reports width=37 for the A bus. This appears to be counting bus wire entry instances rather than unique net labels. The D bus reports width=32 for D0..D31 (32 signals), which is correct, suggesting the A bus count inflates due to duplicate bus entries or hierarchical sheet repetition.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000846: Top-level bus width counts are severely inflated (A bus reports width=289 for 32-line bus)

- **Status**: new
- **Analyzer**: schematic
- **Source**: pcb_homebrew_486.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The top-level sheet aggregates bus entries from all sub-sheets. The A bus reports width=289 and D bus width=144 for what are 32-bit buses. The IRQ bus reports width=3 for a range of IRQ0..IRQ0 (single signal), which is also wrong. The bus topology 'width' field is counting total bus wire entries across all uses rather than unique bit-positions, making it unreliable for multi-sheet designs.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000847: False missing layer alert: In1.Cu and In2.Cu reported as missing/extra due to non-sequential layer numbering in gbrjob

- **Status**: new
- **Analyzer**: gerber
- **Source**: pcb_output_homebrew_486-job.gbrjob.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The gbrjob declares In1_Cu.gbr as FileFunction 'Copper,L5,Inr' and In2_Cu.gbr as 'Copper,L7,Inr'. The analyzer maps L5->In4.Cu and L7->In6.Cu (following KiCad's layer numbering convention), then reports In4.Cu and In6.Cu as missing and In1.Cu/In2.Cu as extra. This is a false alarm — the files exist and are correct. The 4-layer board is complete; only the L-number in the gbrjob is non-standard (L5/L7 instead of L2/L3 for inner layers of a 4-layer stackup).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000848: PCB statistics, DFM tier, courtyard overlaps, and routing completeness correctly assessed

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_homebrew_486.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 130 footprints (87 SMD, 38 THT), 4-layer board, 10279 track segments, 1150 vias, fully routed (0 unrouted). DFM correctly flags 150x150mm size exceeding JLCPCB 100x100mm standard tier. Courtyard overlaps between decoupling caps (C17-C22) and U1 (486 socket) are real and flagged — these SMD caps are intended to be placed under the CPU socket. Board correctly identified as 4-layer with GND/+5V planes on In2/In1.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
