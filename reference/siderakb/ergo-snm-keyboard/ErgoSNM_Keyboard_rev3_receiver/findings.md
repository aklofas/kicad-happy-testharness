# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev3_receiver

## FND-00002191: E73-2G4M08S1C (nRF52840 module) not classified as IC, preventing BLE/wireless interface detection

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ErgoSNM_Keyboard_rev3_receiver_receiver.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The rev3 receiver uses U3 (E73-2G4M08S1C), an nRF52840-based BLE/Bluetooth 5.0 module, as the central wireless controller. This module is in a custom library (ErgoSNM_Keyboard_Library:E73-2G4M08S1C) and receives component_type='?' in the output. The statistics correctly count it as 'ic: 1' (via category field), but signal_analysis finds no wireless interfaces, no SPI/I2C buses, and no power sequencing observations. The 25 single-pin nets flagged in design_observations represent GPIO pins going to external connectors (ROW/COL/SERIAL etc.) that should trigger observations about unconnected keyboard matrix signals.
  (findings)

### Suggestions
(none)

---
