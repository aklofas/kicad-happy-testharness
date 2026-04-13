# Findings: florianmulatz/fsr_bed_occupancy_sensor / bed_occupacy_sensor

## FND-00002072: FSR voltage divider (R1, R2 with ESP32 ADC) not detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fsr_bed_occupancy_sensor_bed_occupacy_sensor.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The design is a Force Sensitive Resistor (FSR) bed occupancy sensor. R1 and R2 form a voltage divider connected to ADC inputs IO_34 (SIDE_B) and IO_35 (SIDE_A) of a mini_esp32 module. The J1/J2 screw terminals connect to the FSR. Despite this being a textbook resistive voltage divider feeding an ADC, the voltage_dividers detector returns an empty list. Likely cause: the +3V3 power rail has no connected pins in the net data (pin_count: 0), so the analyzer cannot trace a top-net → mid-net → GND path through R1/R2.
  (signal_analysis)

### Suggestions
(none)

---
