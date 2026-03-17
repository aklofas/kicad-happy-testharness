# Findings: QFHMIX01 / hw_sch_pcb_QFHMIX01E

## FND-00000264: QFH antenna RF mixer board (235 components). AD8343 active mixers not detected in rf_chains. Power bypass caps falsely labeled as 'antenna' in rf_matching. LO port series RC networks misclassified as high-pass with wrong output_net=GND.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_QFHMIX01E.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- LC filter networks correctly identified with inductor-capacitor topology
- RF matching networks correctly detect target ICs
- Power regulators correctly detected

### Incorrect
- C18/C19/C20/C21 (100nF power bypass caps) falsely labeled as 'antenna' components in rf_matching — 100nF is far too large for RF coupling
  (signal_analysis.rf_matching)
- 3 RC networks (R14/C11 68R/10nF, R11/C13, R15/C12) misclassified as 'high-pass' with output_net='GND' — actual cap terminals connect to CLK_MIX2_P/CLK_MIX1_P/CLK_MIX1_N, not GND
  (signal_analysis.rc_filters)

### Missed
- AD8343 active mixer ICs (U2, U3) not detected as mixers in rf_chains — rf_chains[0].mixers is empty on a board named QFHMIX01
  (signal_analysis.rf_chains)
- LT6604-5 (U4) dual anti-aliasing filter IC absent from rf_chains.filters — dedicated analog filter IC for IF/baseband output
  (signal_analysis.rf_chains)

### Suggestions
- Add AD8343 to mixer component recognition
- rf_matching should exclude bypass caps (>10nF) from antenna classification
- RC filter topology detection should not assign GND as output_net when cap terminal connects to a signal net
- Recognize LT6604 as analog filter IC in rf_chain

---
