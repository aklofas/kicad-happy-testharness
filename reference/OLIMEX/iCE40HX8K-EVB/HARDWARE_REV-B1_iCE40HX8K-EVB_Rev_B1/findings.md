# Findings: OLIMEX/iCE40HX8K-EVB / HARDWARE_REV-B1_iCE40HX8K-EVB_Rev_B1

## FND-00002212: SY8009 switching regulators have input_rail=null despite being on +5V supply; JTAG connector (JTAG1/CON6) and JTAG enable jumper (JTAG_E1) not detected in bus analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_iCE40HX8K-EVB_HARDWARE_REV-B1_iCE40HX8K-EVB_Rev_B1.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Both SY8009AAAC regulators (U2, U3) report input_rail=null in power_regulators. Investigation shows U2's IN pin (pin 4, type=input) is parsed onto the GND net in the legacy KiCad 5 format — a net assignment error likely caused by the pin coordinate-to-net lookup in legacy .sch parsing. The +5V net does contain U2 and U3, but only their EN and GND pins are found there. The regulator input detection logic apparently looks for a specific input-type pin connection to a named power net, but the legacy format coordinates mislead the parser. The correct input rail for both SY8009s is +5V (5V input, stepping down to 3.3V and 1.2V).
  (signal_analysis)

### Missed
- The iCE40HX8K-EVB schematic has an explicit JTAG connector component (JTAG1, a 6-pin CON6) and a JTAG option enable jumper (JTAG_E1, a JP1E component). The net names visible in the source .sch file include JTAG-related labels. The bus_analysis has keys for i2c, spi, uart, and can, but no jtag key. Neither JTAG1 nor JTAG_E1 appears in any detected bus or protocol section of the analyzer output. A JTAG detector would be a valuable addition, especially for FPGA development boards which commonly include JTAG programming interfaces.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002213: F.SilkS layer extends 9mm beyond board edge but alignment reports 'aligned: true' with no issues

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_iCE40HX8K-EVB_HARDWARE_REV-B1_Gerbers.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The F.SilkS gerber layer has extents of 74.206mm x 86.729mm, while the board outline (Edge.Cuts) is 65.0mm x 67.0mm. The silkscreen overhangs by approximately 9.2mm in width and 19.7mm in height. Despite this large discrepancy, the alignment analysis reports 'aligned: true' with an empty issues list. The same overhang exists in the REV-B gerbers (same dimensions). This appears to be due to the alignment check comparing relative extents rather than checking whether each layer's content falls within the board boundary. Silkscreen outside the board outline would be cut off by the fab and is a real manufacturing concern that should be flagged.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002214: DFM tier correctly classified as 'challenging' with accurate annular ring violation detected

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_iCE40HX8K-EVB_HARDWARE_REV-B1_iCE40HX8K-EVB_Rev_B1.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies DFM tier 'challenging' for the iCE40HX8K-EVB Rev B1, which has a 256-ball caBGA FPGA (iCE40HX8K-CT256). The minimum annular ring of 0.075mm is correctly flagged as below the advanced process minimum of 0.1mm, earning the 'challenging' tier. Track spacing of 0.1093mm is correctly identified as requiring advanced process. These are accurate assessments for a dense FPGA breakout board with fine-pitch BGA routing.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
