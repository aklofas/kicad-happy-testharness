# Findings: jellyfish-and-starfish / hardware_starfish_starfish

## ?: Winterbloom Starfish pick-and-place controller: RP2040 MCU, 3x TMC2209 stepper drivers, PCA9545 I2C mux, 2x XGZP6857D vacuum sensors, RS-485 via MAX3078E, USB-B, 24V power chain. Analyzer correctly identifies power regulators, I2C buses, crystal, differential pairs, protection devices, and MOSFET circuits. VX7805-500 DC-DC converter misclassified as LDO. TMC2209 stepper motor drivers not identified as motor drivers. QSPI bus missed in SPI analysis.

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_starfish_starfish.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- RP2040 MCU with W25Q128JVS flash correctly identified as memory interface with 6 shared QSPI signal nets
- Crystal Y301 12MHz with 15pF load caps (C313, C314) correctly detected with effective load 10.5pF
- Two power regulators correctly identified: VX7805-500 (24V->5V) and MIC5317-3.3 (5V->3.3V) with correct rail assignments
- 9 I2C bus segments detected including 4 PCA9545 muxed channels plus main bus, all with 4.7k pull-ups to +3V3
- USB differential pair (D+/D-) with ESD protection (U403 TVS IC) and series resistors (R303, R304) correctly detected
- RS-485 differential pair correctly identified as type RS-485 with MAX3078E transceiver and SM712 on the bus
- 5 MOSFET transistor circuits correctly identified: 1 P-channel reverse polarity (Q201) and 4 N-channel pump/valve drivers with flyback diodes and LED indicators
- Decoupling analysis correctly identifies 4 power rails (+3V3, +24V, +5V, +1V1) with appropriate capacitor counts and totals
- 12 protection devices detected: 4 PESD3V3 ESD diodes on I2C, 1 SMAJ28CA TVS on power input, 6 MOVs on motor outputs, 1 USB ESD IC
- 229 total components accurately counted with correct type breakdown including 74 capacitors, 62 resistors, 16 ICs, 18 connectors, 13 ferrite beads
- 6 power rails correctly identified: +1V1, +24V, +3V3, +5V, GND, PWR_FLAG
- UART bus detection found TMC2209 shared UART line connecting 3 motor drivers and RP2040
- Q201 P-channel MOSFET correctly identified with gate pulldown R201 (47k) forming reverse polarity protection

### Incorrect
- VX7805-500 classified as 'LDO' topology but it is a CUI switching DC-DC converter module (VX78xx series). From 24V to 5V an LDO would dissipate excessive heat. Should be 'switching' or 'DC-DC'.
  (signal_analysis.power_regulators)
- RS-485 differential pair esd_protection field lists U801 (MAX3078E transceiver) as ESD protection, but the actual ESD device is D801 (SM712_SOT23 TVS diode). U801 is the bus transceiver, not a protection device.
  (design_analysis.differential_pairs)
- Net QWIIC1_SCK classified as 'spi' category but it is I2C SCL. QWIIC is SparkFun's standardized I2C connector; 'SCK' here is the I2C clock line, not SPI clock.
  (design_analysis.net_classification)
- OA1/OA2/OB1/OB2 output_conflict ERC warnings are false positives from multi-instance hierarchical sheet handling. motor.kicad_sch is instantiated 3 times with local labels that should be instance-scoped, but analyzer conflates them into shared global nets.
  (design_analysis.erc_warnings)

### Missed
- 3 TMC2209 stepper motor drivers (U1501, U1601, U1401) not identified in any motor_drive or stepper_driver category. These have STEP/DIR/EN/UART interfaces and H-bridge motor outputs but are only seen as generic ICs.
  (signal_analysis)
- PCA9545 4-channel I2C multiplexer role not explicitly identified. While downstream I2C buses are detected, there is no mux/switch detection showing U501 routes main I2C to 4 channels with interrupt aggregation.
  (signal_analysis)
- QSPI bus between RP2040 and W25Q128JVS not detected in bus_analysis.spi. The QSPI_CS, QSPI_SCLK, QSPI_SD0-SD3 nets form a quad SPI interface but spi array is empty.
  (design_analysis.bus_analysis.spi)
- Reverse polarity protection circuit topology not explicitly identified. Q201 P-channel MOSFET with D202 Zener gate clamp and R201 47k pulldown is a classic pattern but not called out as a named protection topology.
  (signal_analysis.protection_devices)

### Suggestions
- Add stepper motor driver detection for TMC2xxx, DRV8xxx, A4988 and similar ICs with STEP/DIR/EN pin patterns and H-bridge motor outputs
- Improve switching regulator classification: VX78xx, TRACO TSR, Murata OKI-78SR series are DC-DC modules not LDOs. The LDO fallback should check known DC-DC module families
- Add I2C mux/switch detection for PCA9545, PCA9548, TCA9548A that connect one upstream I2C bus to multiple downstream channels
- Fix RS-485 ESD attribution: SM712 TVS diode (D801) should be the ESD protection device, not the MAX3078E transceiver (U801)
- Improve QWIIC net name recognition: nets containing QWIIC should be classified as I2C regardless of SCK/SCL naming
- Handle multi-instance hierarchical sheets more carefully for ERC: local labels inside multi-instance sheets should not generate output_conflict warnings across instances

---
