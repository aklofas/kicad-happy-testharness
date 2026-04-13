# Findings: Open-Authenticator/hardware-design / kicad_project_open_authenticator

## FND-00002117: KiCad 5 legacy parser assigns IC1 GND/IN/ON pins and ESP32 GND pins to +3.3V net due to coordinate-matching bug with mirrored components; I2C false positive: LOAD_SWITCH_VCC power net classified as...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hardware-design_kicad_project_open_authenticator.sch.json
- **Created**: 2026-03-24

### Correct
- The design intentionally has two 3.3V rails: +3.3V used for the DS3231M and backup domain, and +3V3 from the TPS63001 boost-buck regulator (input rail unnamed, output +3V3). The analyzer correctly lists both as separate power_rails entries and identifies TPS63001 as a switching regulator with output_rail='+3V3'. This is a genuine design pattern for an IoT device with battery backup.

### Incorrect
- IC1 (TPS22919DCKR) has mirror_x=True. Pins 1 (IN), 2 (GND), and 3 (ON) are all placed on the +3.3V net, while only pin 6 (OUT) correctly appears on LOAD_SWITCH_VCC. GND and ON should not be on +3.3V. Similarly U1 (ESP32-WROOM-32) pins 1, 15, 38, 39 — all named GND — appear on +3.3V while pin 2 (VDD) appears on GND. This is a coordinate-based wire-to-pin matching failure in the legacy KiCad 5 parser when components are horizontally mirrored.
  (nets)
- Due to the legacy parser coordinate bug, the DS3231M (U2) SDA pin (pin 15) is placed on the LOAD_SWITCH_VCC net instead of the IO21_SDA net. The I2C bus detector then sees a pin named 'SDA' on LOAD_SWITCH_VCC and reports it as an I2C bus entry with line='SDA'. Similarly U2 SCL (pin 16) lands on an unnamed net (__unnamed_26) and is reported as a second spurious I2C entry. This produces 6 I2C entries where there should be 2 buses (4 entries).
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002118: Gerber set correctly identified as complete with all 9 expected layers present and layer extents aligned

- **Status**: confirmed
- **Analyzer**: gerber
- **Source**: gerber_hardware-design_gerber.json
- **Created**: 2026-03-24

### Correct
- The KiCad 5 gerber export for this 2-layer ESP32 authentication board has all expected layers (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). The gbrjob file is present and used as the authoritative source for board dimensions (82.05x42.05mm). All layer extents are within the board outline. 149 vias (all 0.4mm), 161 total holes, and 727 flashes are correctly parsed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
