# Findings: kicad / panstamp-nrg3_nrg3

## FND-00000194: panStamp NRG3 wireless sensor node with XBee, MSP430, USB, and sensor subsystem across 5 sheets. The analyzer correctly identifies the multi-sheet hierarchy, RF matching, crystal circuits, and MOSFET power switching, but has issues with ferrite bead inductance parsing and the LDO output rail.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: panstamp-nrg3_nrg3.sch.json
- **Created**: 2026-03-15

### Correct
- Crystal X2 (32.768KHz) correctly identified with load caps C44/C45 (20pF each), effective CL 13pF
- Crystal X1 (26MHz) detected, no load caps noted (consistent with integrated oscillator)
- LDO U4 (AP7365-3.3) correctly identified with topology=LDO and estimated_vout=3.3V from fixed_suffix
- Q1 (DMG3415U) PMOS identified as p-channel with correct gate/drain/source nets, used as power switch between VBUS and battery
- Q3 (DMG3415U) PMOS correctly identified as high-side switch from +BATT
- Q2 (BSS138L) NMOS level shifter correctly identified on TXD net
- Decoupling analysis correctly identifies 4 rails (VCC, VAA, +5V, +3.3V) with appropriate capacitors
- ESD protection D3 (0402ESDA-MLP1) correctly detected on USB data line
- RC filter R6/C37 (10k/100n, fc=159Hz) correctly detected as low-pass on sensor enable net

### Incorrect
- L3 value '600R/200mA' parsed as 600H inductance; this is a ferrite bead rated at 600 ohms impedance at 100MHz, not a 600H inductor. The LC filter with C43 at resonant_hz=5.31kHz is nonsensical as a result.
  (signal_analysis.lc_filters)
- L2 value '600R/200mA' has the same ferrite bead misparsing issue (600H), making the LC filter calculation with C14/C7 (resonant_hz=2.04Hz) invalid
  (signal_analysis.lc_filters)
- U4 (AP7365-3.3) output_rail is 'GND' which is incorrect; the output should be the +3.3V rail. The input_rail is also unnamed when it should connect to a power source.
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Detect ferrite bead notation (xxxR or xxxR/xxxmA format) and exclude from LC filter calculations; ferrite beads have impedance ratings, not inductance
- Fix LDO output rail detection for AP7365 - the output pin should connect to the +3.3V rail, not GND

---
