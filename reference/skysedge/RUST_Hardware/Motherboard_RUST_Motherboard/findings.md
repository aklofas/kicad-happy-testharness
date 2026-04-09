# Findings: skysedge/RUST_Hardware / Motherboard_RUST_Motherboard

## ?: ATmega1280+ATmega16U2 motherboard: good component/crystal/regulator detection, but OLED SPI clock misclassified as I2C SCL, MCP1661 boost converter output rail wrong (+3V8 vs +12V), ceramic resonators correctly flagged as no load caps

- **Status**: new
- **Analyzer**: schematic
- **Source**: Motherboard_RUST_Motherboard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 271 components correctly counted
- Crystal/resonator circuits Y1 and Y2 (16MHz AWSCR ceramic resonators) detected
- Ceramic resonators correctly noted as having no external load caps (built-in)
- Power regulators detected including LDOs
- SPI buses correctly detected

### Incorrect
- OLED_SCL_3V3 net classified as I2C SCL but it is actually SPI clock for OLED display - 'SCL' substring triggered false I2C classification
  (design_analysis.bus_analysis.i2c)
- MCP1661 (U7) boost converter output_rail listed as +3V8 (which is the input rail VIN). Actual output is +12V via SW->L2->D23 boost topology
  (signal_analysis.power_regulators)

### Missed
- Boost converter topology (U7 MCP1661: +3V8->SW->L2->D23->+12V) not fully traced through inductor-diode chain
  (signal_analysis.power_regulators)

### Suggestions
- SPI clock nets (SCK, SCLK, SCL in SPI context) should not be classified as I2C when other SPI signals (MOSI, MISO, CS) are on the same IC
- Boost converter output rail detection should trace through the SW->inductor->diode chain to find the actual output rail, not just use VIN/VOUT pin names

---

## FND-00002529: 4G rotary cellphone mainboard (RUST_Motherboard) with ATmega1280, ATmega16U2 USB bridge, LARA-R6 LTE module, MAX9860 audio CODEC, and MCP1661 12V boost converter. Analyzer handles 9-sheet hierarchy well but misclassifies MK1 (electret microphone) as fiducial, and mis-identifies the boost converter output rail as +3V8 (input) instead of +12V (output).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Motherboard_RUST_Motherboard.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- U6 (AP2112K-3.3) correctly identified as LDO: input=+3V8, output=+3V3
- Voltage divider R21/R22 from +12V correctly identified as boost converter feedback to U7 V_FB
- I2C bus correctly detected: LARA-R6 and MAX9860 on SDA/SCL with 4k7 pullups on +1V8
- SPI bus with 5 chip-selects correctly detected across U4, U2, U8
- U13 (ADA4807-2ACP) dual opamp units correctly analyzed as inverting gain=-1
- Q6-Q9 (MMBT3904) correctly detected as LED drivers
- USB-C J1 compliance checks pass for CC pulldowns and D+/D- resistors
- TXB0108PWR level shifters U2/U8/U10 correctly identified bridging +3V8 and +3V3/+1V8
- All 9 hierarchical sheets correctly parsed and merged
- Y1/Y2 (16MHz ceramic resonators) correctly show empty load_caps
- UART paths correctly detected for MCU-to-FTDI and MCU-to-LARA via level shifter

### Incorrect
- MK1 (Device:Microphone_Condenser, '2k2 Electret Mic') classified as type=fiducial instead of microphone/transducer.
  (statistics.component_types)
- U7 (MCP1661 boost converter) output_rail reported as '+3V8' — this is the input. Output is +12V via L2 -> D23 Schottky.
  (signal_analysis.power_regulators)
- U7 design_observation also reports output_rail='+3V8' and input_rail=None, both wrong.
  (signal_analysis.design_observations)
- power_sequencing dependency for U7 inherits the wrong output_rail.
  (power_sequencing)

### Missed
- Battery management system not detected: BQ2970 (U3, undervoltage protection) + MCP73831 (U5, LiPo charger) + Q3/Q4 (CSD16301Q2 charge/discharge FETs). bms_systems is empty.
  (signal_analysis.bms_systems)
- Q4 gate net (__unnamed_86) appears disconnected from U3 Cout (__unnamed_74) — possible schematic wiring gap or netlist extraction issue.
  (signal_analysis.transistor_circuits)

### Suggestions
- Map Device:Microphone_Condenser lib_id to 'microphone' or 'transducer' type.
- Fix boost converter output rail: trace from inductor SW-node through rectifier diode to power net.
- Add BMS system detection for Battery_Management: prefixed ICs driving power MOSFETs on BATT rail.
- Investigate Q4 disconnected gate net as potential ERC warning.

---
