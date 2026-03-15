# Findings: OnBoard / projects_PixelWave_src_PixelWave

## FND-00000085: SK6812 addressable LEDs (310x) misclassified as diodes. Switching regulator XL4016 correctly identified with feedback network. USB diff pair detected with ESD protection.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/PixelWave/src/PixelWave.kicad_sch
- **Created**: 2026-03-14

### Correct
- BOM quantity sum (663) matches total_components (663)
- XL4016 switching regulator detected with feedback divider R7/R8, estimated Vout 2.418V
- HT7533-1 LDO correctly identified with input/output rails
- USB differential pair detected (USB_DP/USB_DM) with ESD protection
- ESDA5V3L ESD protection devices correctly identified
- Decoupling analysis found caps on VCC, VBUS, and +3V3 rails
- 310x 0.1uF bypass caps correctly counted (one per SK6812 LED)

### Incorrect
- 310 SK6812 addressable RGB LEDs classified as diode instead of led
  (statistics.component_types)
- R7/R8 voltage divider duplicated in both voltage_dividers and feedback_networks sections
  (signal_analysis)

### Missed
- No LED matrix or addressable LED chain detection for 310 SK6812 LEDs
  (signal_analysis)
- Crystal circuits list is empty despite ESP32-S3 likely having crystal
  (signal_analysis.crystal_circuits)

### Suggestions
- Classify SK6812/WS2812 as led type, not diode
- Add addressable LED chain detector for WS2812/SK6812 patterns
- Deduplicate entries appearing in both voltage_dividers and feedback_networks

---
