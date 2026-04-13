# Findings: hstarmans/firestarter / base_extension

## FND-00002608: Hexastorm laser PCB extension with USB-C PD, 3x TMC2209 stepper drivers, and FPGA expansion connector; power chain and RC filters correct, but SPI/I2C bus detection missed and USB PD controller misidentified as ESD protection

- **Status**: new
- **Analyzer**: schematic
- **Source**: base_extension_extension.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U1 LM7805 correctly identified as LDO regulator with +12V input and +5V output
- U2 MCP1700T-3302E/TT correctly identified as LDO regulator with +5V input and +3.3V output
- 3 RC low-pass filters correctly detected on X_PO, Y_PO, Z_PO position feedback nets (R3/C27, R4/C28, R5/C29) with 159 Hz cutoff
- Total component count of 76 is correct (29 caps, 12 resistors, 3 diodes, 6 ICs, 22 connectors, 2 mounting holes, 1 fuse, 1 logo)
- 3 TMC2209-LA-T stepper motor drivers (IC1, IC2, IC3) correctly identified as ICs with quantity 3
- F1 fuse correctly detected as protection device on the +12V/VBUS path
- UART bus detected with UARX net connecting IC1, IC2, IC3 (daisy-chained TMC2209 single-wire UART)
- 7 power rails correctly identified including +12V, +5V, +3.3V, VDD, VBUS, GND, PWR_FLAG
- USB DP/DM differential pair correctly detected between J1 USB-C connector and U3 CH224K
- 4 decoupling rails correctly identified (+5V, +12V, VDD, +3.3V) with reasonable capacitance totals
- CH224K (U3) correctly identified as USB PD controller IC
- Net classification correctly identifies POT_SDA as data and POT_SCL as clock for I2C signals
- 2 power regulators correctly detected forming the 12V to 5V to 3.3V power chain

### Incorrect
- DP/DM differential pair reports has_esd=true with U3 (CH224K) listed as ESD protection. CH224K is a USB PD power negotiation controller, not an ESD protection device. It uses DP/DM for PD communication but does not provide ESD clamping.
  (design_analysis.differential_pairs[0].has_esd)
- Cross-domain signals analysis flags UARX, STEP_ENABLE, and DIAG as needing level shifters between TMC2209 domains. This is incorrect because the TMC2209 VCC_IO pin (pin 15) is connected to +3.3V, meaning its logic I/O operates at 3.3V matching the controller domain. No level shifter is needed.
  (design_analysis.cross_domain_signals)
- SPI_SI and SPI_SO nets classified as 'signal' in net_classification instead of 'data'. These are SPI data lines (MOSI/MISO) routed through FPC connectors J3/J5 to the main board connector J2.
  (design_analysis.net_classification)
- USB compliance check reports cc1_pulldown_5k1 and cc2_pulldown_5k1 as fail. With a CH224K USB PD controller managing the CC lines, CC1/CC2 are handled by the CH224K internally with integrated CC logic. External 5.1K pulldowns are not required and would conflict with PD negotiation.
  (usb_compliance)

### Missed
- SPI bus not detected in bus_analysis despite SPI_SI, SPI_SO, SPI_SCK nets being present and routed through FPC connectors J3/J5 and the 2x20 expansion connector J2
  (design_analysis.bus_analysis.spi)
- I2C bus not detected in bus_analysis despite POT_SDA and POT_SCL nets being present and correctly classified as data/clock, routed through FPC connectors J3/J5 and J2 for digital potentiometer control
  (design_analysis.bus_analysis.i2c)
- 6 current sense resistors (R8, R9, R10, R11, R12, R13) at 0.5 ohm in 1206 package not detected in current_sense. These are connected to the TMC2209 BRA/BRB sense pins for motor current measurement.
  (signal_analysis.current_sense)
- 3 decoupling capacitors (C12, C16, C19, all 0.1uF) missing from +12V rail decoupling analysis. These are on the +12V rail per power_net_summary but absent from decoupling_analysis, which shows 10 caps instead of 13.
  (signal_analysis.decoupling_analysis)

### Suggestions
- USB PD controllers (CH224K, HUSB238, FUSB302, STUSB4500) should be recognized as a specific device category rather than generic ICs, and should not be classified as ESD protection even though they connect to USB data lines.
- Cross-domain analysis should check if the VCC_IO pin of motor drivers like TMC2209 is connected to the same rail as the controller domain before flagging level shifter requirements.
- SPI bus detection should work even when all devices on the bus are passive connectors (through-board routing), since the net names clearly indicate SPI protocol.
- Current sense detection should identify low-value resistors (typically under 1 ohm) connected to dedicated sense pins on motor driver ICs.
- For USB-C connectors with dedicated PD controller ICs managing CC lines, the CC pulldown check should be marked as handled rather than failed.

---
