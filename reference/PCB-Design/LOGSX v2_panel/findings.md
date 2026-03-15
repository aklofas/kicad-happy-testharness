# Findings: PCB-Design / LOGSX v2_panel

## ?: GPS/LoRa asset tracker with STM32F103, SX1273 radio, TESEO-LIV3 GNSS, BGA725L6 LNA, and LT1129-3.3 LDO. Analyzer correctly identified multi-sheet hierarchy and component types but has significant regulator rail detection errors.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: LOGSX v2_ArmTrax.sch.json

### Correct
- Correctly parsed 4 sheets (root, MCU, Power, Radio) with 93 components total
- Correctly identified 3 crystal circuits Y1, Y2, Y3 with appropriate load caps (C1/C2, C7/C8, C46/C47)
- LC filter L3/C21 at 205 MHz and L6/C37 at 129 MHz correctly detected in radio section - plausible for sub-GHz RF matching
- I2C bus detection for SCL/SDA nets with pullups R2/R3 to +3.3V on accelerometer U9 (STM32F103) is correct
- Ferrite beads FB1, FB2 correctly classified as ferrite_bead type
- RC filter R9/C22 at 159kHz on RXTX net correctly detected

### Incorrect
- U2 (LT1129-3.3) regulator detected with input_rail=GND and output_rail=GND. Source shows input from BATTERY via FB1/D1 and output to +3.3V via L1/D3/C17
  (signal_analysis.power_regulators)
- RC filter R7/C19 at 7.23 MHz: R7 (1K) is a charging LED current-limiting resistor in the MCP73113 circuit, not part of an RC filter with C19 (22pF load cap for the crystal). These are on different nets in the Power sheet
  (signal_analysis.rc_filters)
- RC filter R4/C19 at 14.47 MHz and R4/C16 at 318 kHz: R4 (500 ohm) is an ADC voltage divider resistor, not connected to C19 or C16 in a filter topology
  (signal_analysis.rc_filters)
- L3 value incorrectly parsed as '5nF' (henries=5e-09). L3 is an inductor with value 5nF in the schematic - this is likely a mislabeled component in the source, but the analyzer should not treat nF as henries
  (signal_analysis.lc_filters)

### Missed
(none)

### Suggestions
- Fix regulator rail detection for LT1129-3.3 - the IN/OUT pins should map to the actual power nets, not GND
- Add topological validation for RC filters: ensure R and C actually share exactly one node and the other nodes connect to signal/ground appropriately

---
