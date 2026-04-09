# Findings: Duet3D/Duet-2-Hardware / Duet2_Duet2v1.04_DuetWifi

## FND-00002515: Complex 7-sheet 3D printer controller (Duet 2) with ATSAM4E8E, 5x TMC2660 stepper drivers, AP64200 buck + AP7361C LDO, ESP-WROOM-02 WiFi. Correct hierarchical parsing, regulator detection, crystal/RC filters. Issues: 4 MOSFETs as transformers (custom lib_id), 5 TMC2660 motor drivers undetected, ferrite bead part numbers parsed as inductance, sense resistors as voltage dividers, USB Micro-B flagged as Type-C.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Duet2_Duet2v1.06_Duet2.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- All 7 hierarchical sheets correctly parsed (Duet2, Power, Processor, Stepper_Drv, Htr_Fan, Comms, Headers)
- U2 (AP7361C) correctly identified as LDO with 3.3V output, U3 (AP64200) as switching regulator with L1/FB
- R80/R81 VIN monitor divider correctly detected with ratio 0.0909
- Crystal X2 correctly detected with 10pF load caps
- Thermistor RC filters correctly detected at 7.23 Hz
- 3 fan MOSFETs correctly identified as N-channel with load_type=fan
- TVS protection diodes D30/D31 correctly identified

### Incorrect
- TR7/TR2/TR4/TR8 are N-channel MOSFETs but classified as transformer due to custom lib_id (DuetWifi:BSH105, DuetWifi:IPD036N04L)
  (statistics.component_types)
- 5V_INT classified as 'interrupt' — is a 5V internal power rail
  (design_analysis.net_classification)
- L5/L6 value '742792662' is Wurth part number (ferrite bead), parsed as 742M henries producing absurd LC filter results (0.02 Hz)
  (signal_analysis.lc_filters)
- 10 stepper sense resistor chains (22R+0R050) misidentified as voltage dividers with ratio 0.002268
  (signal_analysis.voltage_dividers)
- J22 (USB Micro-B, MPN 10103594-0001LF) incorrectly flagged as is_type_c=true
  (usb_compliance)
- SPI protocol compliance reports 0 CS lines — TMC2660 chip selects named _EN not _CS
  (protocol_compliance)
- Power budget estimates 250 mA per 74HC125/74HCT02 (should be <10 mA)
  (power_budget)

### Missed
- 5 TMC2660 stepper motor drivers (U5-U9) not detected by motor_drivers
  (signal_analysis.motor_drivers)
- 10 current sense resistors (0R050 on TMC2660 BRA/BRB pins) not detected
  (signal_analysis.current_sense)
- ESP-WROOM-02 (U4) WiFi module not identified
  (signal_analysis)
- Many power rails missing from statistics.power_rails (V_FUSED, 5V_INT, 5V_EXT, V_FAN, etc.)
  (statistics.power_rails)

### Suggestions
- TR-prefixed components with FET pin names should be transistors regardless of lib_id
- Add TMC2660/TMC2xxx to motor_drivers detector
- Parse Wurth 742792xxx as ferrite beads not inductance
- Filter sense resistor chains (<1 ohm bottom R + motor driver sense pin) from voltage dividers
- Fix USB type detection: Micro-B lib_id + 5-6 pins should not be Type-C
- Recognize _EN nets on IC ~{CS} pins as chip selects

---
