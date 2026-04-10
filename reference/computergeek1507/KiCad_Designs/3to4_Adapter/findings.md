# Findings: KiCad_Designs / 3to4_Adapter_3to4_Adapter

## FND-00002274: OKI-78SR-5 switching regulator misclassified as LDO with wrong Vout estimate; SPI bus to 74HCT595 shift registers not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad_Designs_ESP32_Shift_Test_ESP32_Shift_Test.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U4 (OKI-78SR-5, value 'OKI-78SR-5') is classified as topology='LDO' and estimated_vout=7.8V. The OKI-78SR-5 is a Murata/Recom step-down switching regulator (SIL package), not an LDO. The '-5' suffix should parse to 5.0V output, but the fixed_suffix path returns 7.8V. Both the topology and the Vout estimate are wrong.
  (signal_analysis)

### Missed
- U2, U3, U5 are 74HCT595 shift registers driven by the WT32_ETH01 (U1) via SER1/SER2/SER3 (MOSI), SRCLK (serial clock), and RCLK (latch clock). This is a classic SPI-driven shift register topology. design_analysis.bus_analysis.spi is empty because the detector relies on standard SPI pin name patterns (SCK/MOSI/MISO/CS) rather than 74HCT595-specific pin names (SRCLK/SER/RCLK). The design also has AM26C31 RS-422 drivers (U6, U7) for differential output lines which are also undetected.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002275: VR10S05 switching regulator misclassified as LDO; LTV-214G optocouplers not detected as isolation barriers; RS-485 transceiver (SP3485EN) correctly detected with DE/RE nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad_Designs_PicoDMXStepper_PicoDMXStepper.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- design_analysis.bus_analysis.rs485 correctly identifies U3 (SP3485EN) as the RS-485 transceiver, resolving its A/B differential nets, DI (transmit data), RO (DMX_OUT receive), and combined DE/RE enable net. This is a complete and accurate detection for a DMX512 protocol interface.

### Incorrect
- U1 (VR10S05) is classified as topology='LDO' because it uses the Regulator_Linear:L7805 lib_id. The VR10S05 is a Murata SIL-package isolated DC/DC switching converter, not a linear regulator. The classifier relies solely on lib_id family and does not check the component value string for known switching regulator part numbers. This is the same root cause as the OKI-78SR-5 misclassification.
  (signal_analysis)

### Missed
- U4 and U5 are LTV-214G phototransistor optocouplers used to isolate limit switch inputs from the Pico's GPIO. signal_analysis.isolation_barriers is empty. The isolation_barriers detector does not recognize optocouplers by lib_id pattern (LTV-214:LTV-214G) or value string. The subcircuits section does identify these as neighbor components of the Pico, but no structural isolation analysis is performed.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002276: bus_topology false positives: component-ref-like net names detected as bus members; I2C pull-up resistors correctly identified on both SDA and SCL nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad_Designs_Lora_Keypad2_Lora_Keypad2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- design_analysis.bus_analysis.i2c correctly reports I2C_SCL and I2C_SDA each with two 4.7K pull-up resistors (R1/R3 on SCL, R2/R4 on SDA) referenced to +3.3V. The doubled pull-ups (parallel 4.7K = 2.35K effective) are a design decision for a two-device bus (Adafruit Feather + XBee), and the analyzer faithfully lists all four resistors across both lines.

### Incorrect
- bus_topology.detected_bus_signals reports two false buses: prefix='C' (width=6, range='C1..C3') and prefix='R' (width=8, range='R1..R4'). In this schematic, C1/C2/C3 and R1/R2/R3/R4 are global labels representing video switch row/column signal lines on a GSCARTSW chip, not any kind of bus. There are zero bus wires or bus entries in the schematic. The detector is pattern-matching net name prefixes against component reference conventions (C=capacitor, R=resistor) yielding nonsensical bus detections.
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002277: AMS1117-5.0 LDO regulator not detected in power_regulators

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad_Designs_RP2040_Count2_RP2040_Count2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- U2 (AMS1117-5.0, Regulator_Linear:AMS1117-5.0) drives the +5V rail (pin VO connected to +5V) but does not appear in signal_analysis.power_regulators. The schematic has duplicate reference assignments: U2 is used for both the AMS1117-5.0 and the rp2040-zero module, and U4 is used for both the 74AHCT1G125 and the INA219BxD. The duplicate ref likely causes the regulator detector to either skip or discard the AMS1117 entry when resolving net-to-component mappings.
  (signal_analysis)

### Suggestions
(none)

---
