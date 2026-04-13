# Findings: machdyne/eis / pcb_eis_v0_eis

## FND-00002034: bus_topology.width counts label occurrences, not unique nets — systematically 2x actual width; CSPI_SI and CSPI_SO misclassified as chip_select instead of data signals; Footprint filter warnings co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_eis_pcb_eis_v0_eis.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- C19, C20, C21, C22, C23, C37, C38, C45 all carry capacitor values (100nF, 1uF, 4.7uF, 10uF) but use Resistor_SMD:R_0603 or R_0402 footprints. The footprint_filter_warnings section catches all eight with messages like 'footprint R_0603_1608Metric doesn't match any filter pattern [C_*]'. FB1 and FB2 (ferrite beads using R_0603 footprints — a common but deliberate practice) are also flagged. The 15 total warnings correctly identify real footprint mismatches in this design.
- The FPGA-driven DVI output on J5 (footprint LD-HDMI:HDMI_TE_1827059-3-FIXED) is detected as type 'pio_dvi' with 8 series resistors. The design has two sets of differential signals: DDMI_* (FPGA I/O side) and DDMIC_* (connector side, after resistors), which are the before/after nodes of the 8 series impedance resistors — not two separate outputs. Only one hdmi_dvi_interfaces entry is correct.

### Incorrect
- Every detected bus in the eis schematic has width equal to the sum of label occurrences across member signals, not the count of unique net names. SRAM_D has 16 unique nets (SRAM_D0..D15) but width=32; SRAM_A has 18 unique nets but width=36; HRAM_ADQ has 8 unique nets but width=16; SD_DAT has 2 unique nets but width=4. The formula is: width = sum over each member signal of (number of times that label appears in the schematic file). For SRAM_A, every signal appears exactly twice (connecting FPGA to SRAM), giving 18x2=36. RP_QSPI_IO appears 3x each giving 4x3=12. The width field should count unique net names in the bus group.
  (bus_topology)
- In design_analysis.net_classification, CSPI_SI and CSPI_SO are classified as 'chip_select'. These are the Configuration SPI Serial-In (MOSI) and Serial-Out (MISO) lines used to program the FPGA flash; they are SPI data signals, not chip selects. Only CSPI_SS is a legitimate chip select. The heuristic appears to match the 'CS' substring within 'CSPI' and promotes all CSPI_* signals to chip_select class, instead of restricting the match to signals ending in _SS, _CS, or _CE. CSPI_SCK is correctly classified as 'clock', confirming the bug is selective to SI/SO.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---
