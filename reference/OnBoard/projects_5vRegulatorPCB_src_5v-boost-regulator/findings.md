# Findings: OnBoard / projects_5vRegulatorPCB_src_5v-boost-regulator

## FND-00000090: TPS61032 boost regulator design accurately analyzed. Switching topology, feedback divider, and output voltage estimation all detected correctly.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/5vRegulatorPCB/src/5v-boost-regulator.kicad_sch
- **Created**: 2026-03-14
- **Datasheets**: TPS61032 datasheet (TI)

### Correct
- TPS61032PWPR correctly identified as switching regulator with inductor L1
- Feedback divider R3/R4 (1M62/180k) correctly detected with ratio 0.1 feeding FB pin
- Second voltage divider R1/R2 (1M95/390k) on LBI pin correctly found as battery low indicator
- Output voltage estimated at 5.95V using Vref=0.595V from lookup, reasonable for TPS61032
- Decoupling analysis correctly identified caps on both +5V and VBat rails
- VBat input rail and +5V output rail correctly classified as power nets

### Incorrect
- Estimated Vout of 5.95V flagged with 19% mismatch vs +5V net name, but TPS61032 Vref is actually 0.5V not 0.595V, so actual Vout = 0.5*(1+1620k/180k) = 5.0V exactly matching +5V rail
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- TPS61032 Vref should be 0.5V per datasheet, not 0.595V. The lookup table may have an incorrect entry for this part.

---
