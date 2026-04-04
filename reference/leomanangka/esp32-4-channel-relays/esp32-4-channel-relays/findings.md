# Findings: esp32-4-channel-relays / esp32-4-channel-relays

## FND-00000139: ESP32 relay board with CH340C USB-UART, 4x relay drivers with optocouplers, and PRTR5V0U2X ESD protection. Good detection of relay driver transistors, USB ESD, fuse, and LDO. PC817 optocouplers provide relay isolation but isolation_barriers not detected.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/esp32-4-channel-relays/esp32-4-channel-relays.kicad_sch
- **Created**: 2026-03-14

### Correct
- AMS1117-3.3 LDO correctly identified with +5V to +3.3V conversion
- PRTR5V0U2X USB ESD protection correctly detected on DP/DN lines
- Fuse F1 (500mA) correctly identified as protection on +5V/VCC
- 4x BC547A relay driver transistors correctly detected with base resistors (1K)
- Power domains correctly map ESP32, CH340C to +3.3V domain and PC817s to +5V domain
- SRD-05VDC-SL-C relays correctly classified as relay type
- Decoupling analysis shows adequate coverage on both +3.3V (44.2uF) and +5V (22.1uF) rails
- CH340C USB-UART UART TX/RX connection to ESP32 correctly detected
- 1N4007 flyback diodes (D5, D9, D7, D3) correctly classified as diodes

### Incorrect
- Subcircuit neighbors are identical for all 8 ICs - listing same components regardless of actual proximity
  (subcircuits)
- Transistor load_type shown as other for all 4 relay drivers - should be relay or indicate relay coil load
  (signal_analysis.transistor_circuits)
- PRTR5V0U2X decoupling warning for VCC rail - PRTR5V0U2X does not need dedicated decoupling on VCC (it is internally clamped)
  (signal_analysis.design_observations)

### Missed
- PC817 optocoupler isolation barrier between ESP32 control and relay power not detected in isolation_barriers
  (signal_analysis.isolation_barriers)
- Relay flyback/freewheeling diodes (1N4007) not linked to their corresponding relay coils
  (signal_analysis)
- MBT3904DW1 (Q1) dual transistor auto-program circuit for ESP32 boot/reset not detected as auto-program
  (signal_analysis.transistor_circuits)
- Relay indicator LEDs (D2, D4, D6, D8 RED_LED) not linked to relay channels
  (signal_analysis)
- Complete relay driver chain (GPIO -> optocoupler -> transistor -> relay coil + flyback diode) not detected as unified circuit
  (signal_analysis)

### Suggestions
- Detect optocoupler isolation barriers (PC817, 6N137, etc.)
- Link flyback diodes to relay/inductor loads
- Detect auto-program circuits (DTR/RTS -> transistor -> GPIO0/EN)
- Identify relay driver chains as a composite circuit pattern
- Fix subcircuit neighbor detection

---
