# Findings: ktauchathuranga/esp32-s3-testboard / esp32-s3-testboard

## FND-00002049: D5 (CLV1L-FKB bi-color LED) misclassified as diode instead of led; I2C bus correctly detected with pull-ups and both devices (ESP32-S3, Si7020); RC filter on EN net misidentified as low-pass with +...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32-s3-testboard_esp32-s3-testboard_esp32-s3-testboard.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the I2C bus on SCL/SDA nets with two devices (U2=ESP32-S3-WROOM-1, U4=Si7020-A20 humidity sensor) and pull-up resistors R7 and R8 (both 2.2K to +3V3). The USB-C compliance check correctly identifies the USBLC6-2SC6 ESD IC (U1) protecting D+/D- and passes the CC1/CC2 5.1K pull-down check.

### Incorrect
- CLV1L-FKB is a Kingbright bi-color chip LED, but because it is stored in a custom library ('oddibits:CLV1L-FKB') with no standard LED keyword in the lib path or component name, the analyzer classifies it as type='diode'. This inflates the diode count to 5 (should be 4: D1, D2, D4, D6) and undercounts the LED count to 1 (should be 2: D3 PURPLE + D5 bi-color). The component type statistics in statistics.component_types are consequently wrong.
  (statistics)

### Missed
- The RC filter R1+C4 (10K+1uF, fc=15.92 Hz) is correctly detected, but its functional role is a power-on reset timing circuit for the ESP32-S3 EN (enable) pin. The same circuit in esp32bb (R3+C1, same component values, same topology) is labeled 'RC-network' instead of 'low-pass'. Inconsistent type labeling ('low-pass' vs 'RC-network') for identical topologies suggests the classification criterion is unstable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002050: 4-layer board correctly identified with GND planes on 3 layers and +3V3 inner plane

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_esp32-s3-testboard_esp32-s3-testboard_esp32-s3-testboard.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu). Thermal zone stitching shows GND covering B.Cu+F.Cu+In1.Cu with 80 stitching vias, and +3V3 on In2.Cu with 11 vias. All 58 nets are routed with routing_complete=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
