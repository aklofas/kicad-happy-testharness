# Findings: cnlohr/cnhardware / esp32s2-funprog3_esp32s2-funprog

## FND-00000159: ESP32-S2 development board with PCB antenna, USB, LEDs. Antenna A1 misclassified as IC via A-prefix; complementary BJT U11 ZDT6790TA classified as IC despite BJT in lib_id.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: esp32s2-funprog3_esp32s2-funprog.kicad_sch.json
- **Related**: KH-079
- **Created**: 2026-03-15

### Correct
- USBLC6-2P6 protection device correctly detected

### Incorrect
- A1 (PCB antenna, Device:R, value='ANT', 1206 footprint) classified as IC due to 'A' ref prefix -- should be antenna
  (statistics.component_types)
- U11 ZDT6790TA with lib_id 'cnhardware:ZDT6790-COMPLEMENTARY-BJT' classified as IC -- 'BJT' in lib_id should override U prefix
  (statistics.component_types)

### Missed
(none)

### Suggestions
- Ref prefix 'A' should map to antenna, not IC
- Lib_id containing 'BJT' should override IC classification from U prefix

---
