# Findings: fidget / hardware_Fidget_Fidget

## FND-00000214: FPGA development board with ICE40HX4K-TQ144 (U2), AT25SF081 SPI flash (U1), three LDO regulators, two active oscillators, and bus-level I/O via 74-series buffers/transceivers. The analyzer correctly identified the power regulation chain, memory interface, oscillators, and decoupling. No significant errors found.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_Fidget_Fidget.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Three-stage LDO power chain correctly detected: U3 AP2112K-3.3 (5V->3.3V), U4 MIC5365-1.2YC5 (3.3V->1.2V), U5 MIC5365-2.5YC5 (3.3V->2.5V) with correct input/output rails and estimated voltages from fixed_suffix
- AT25SF081 SPI flash (U1) correctly detected as memory interface connected to ICE40HX4K (U2) with 6 shared signal nets
- Two active oscillators U6 KC2520Z16.0000C15XXK (16 MHz) and U7 KC3225Z3.68640C1KX00 (3.6864 MHz) correctly identified as active_oscillator type with no load caps (correct for active oscillators)
- RC filter R2 (100 ohm) / C4+C2 (10.1uF parallel) at 157.58 Hz correctly detected as low-pass on +1V2 rail to GND
- 5-rail decoupling analysis correctly identified: +3.3V (18 caps, 4.5uF), +1V2 (3 caps, 1.11uF including C6 0.01uF high-freq), +5V (2 caps, 1.1uF), +2V5 (2 caps, 1.1uF), VBUS (9 caps, 0.9uF)
- USB data lines USB_DN and USB_DP correctly flagged with has_esd_protection=false, noting only R6/R5 series resistors and U2 FPGA connections
- Component types correctly classified: 15 ICs, 7 jumpers, 3 switches, 2 oscillators, 3 test points, 5 LEDs, 11 connectors

### Incorrect
(none)

### Missed
- The 74ALVC16245DG (U8-U11, U13-U14) bus transceivers and 74AHC16373DG (U15-U16) latches forming bus-level I/O from the FPGA are not characterized in design_observations. These 8 bus interface ICs represent the primary I/O expansion architecture.
  (signal_analysis.design_observations)

### Suggestions
- Detect 74-series bus transceivers/buffers/latches as bus interface topology in design_observations
- Consider flagging missing ESD protection on USB data lines as a more prominent design concern

---
