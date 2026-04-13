# Findings: hackclub/OnBoard / projects_onboard-live-icepi-zero_src_icepi-zero

## FND-00000088: ECP5 FPGA board with SDRAM, SPI flash, and FTDI USB. MEMS oscillator SIT8008 misidentified as crystal. Good power regulation and memory interface detection. Feedback networks duplicated with voltage dividers.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/onboard-live-icepi-zero/src/icepi-zero.kicad_sch
- **Created**: 2026-03-14

### Correct
- Three switching regulators (TLV62569DBV) correctly detected with feedback dividers
- W9825G6KH SDRAM interface detected with ECP5 FPGA connection
- W25Q128JVS SPI flash interface detected with 6 shared signal nets
- TPD2EUSB30A ESD protection correctly identified on USB data lines
- Multiple power domains correctly identified: +1V1, +2V5, +3V3, +5V
- Decoupling analysis covers 4 rails with appropriate capacitance
- Three differential pairs detected for USB interfaces

### Incorrect
- SIT8008 MEMS oscillator classified as crystal — it is a packaged oscillator, not a crystal requiring load caps
  (signal_analysis.crystal_circuits)
- All 3 voltage dividers duplicated in feedback_networks (same R5/R6, R9/R10, R13/R14 pairs)
  (signal_analysis)
- TLV62569 estimated Vout=1.1V for all three regulators despite different output rails (+1V1, +2V5, +3V3)
  (signal_analysis.power_regulators)
- BOM sum (116) does not match total_components (121) — 5 missing, only mounting_hole(4) accounted for
  (statistics)

### Missed
- No FPGA-specific analysis (ECP5 I/O banks, SERDES, PLL configuration)
  (design_analysis)
- FTDI FT2232 USB bridge not recognized as bus bridge/protocol converter
  (design_analysis.bus_analysis)

### Suggestions
- Distinguish MEMS oscillators from crystals (no load caps needed)
- Deduplicate voltage_dividers and feedback_networks when they share the same components
- Verify regulator Vout estimates use correct feedback ratios per instance

---
