# Findings: led-controller-hardware / led-controller

## FND-00002377: False positive I2C detection: ENABLE and RESET pins on ATWINC1500 are not I2C; LTV-814 optocoupler not detected as isolation barrier; 12 N-channel MOSFETs correctly detected as LED driver circuits ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_led-controller-hardware_led-controller.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified all 12 IRLML6344 N-channel MOSFETs (Q1-Q12) as transistor_circuits with load_type 'led', organized as 4 groups of 3 (RGB channels). Each transistor correctly shows a gate pull-down resistor (10k) and a gate series resistor (100 ohm). The topology matches the LED controller design intent: 4 connectors (J3-J6) for 4 LED groups, each with 3 PWM-driven MOSFET channels.

### Incorrect
- The analyzer detected an I2C bus with ENABLE mapped to SCL and RESET mapped to SDA, both on U4 (ATWINC15x0 WiFi module). The ATWINC1500's ENABLE and RESET are control pins, not I2C bus signals. The detection likely triggered because pin names or net names partially matched I2C patterns. No pull-up resistors were found (has_pull_up: false), which is also consistent with these not being I2C lines. The actual I2C interface (if any) between U4 and U5 (24LC16 EEPROM) was not detected.
  (design_analysis)

### Missed
- U2 (LTV-814) is a well-known 4-pin optocoupler (phototransistor output type). It is classified as a generic 'ic' type and does not appear in signal_analysis.isolation_barriers. The optocoupler appears to be used for electrical isolation in a control signal path (context: LED controller with 12V power and MCU logic). Missing isolation detection means the cross-domain signal analysis also misses the isolated signal path.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002378: Q13 (DMP4015SK3 P-channel MOSFET) not detected in transistor_circuits

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_led-controller-hardware_file5A5126D2.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- Q13 is a DMP4015SK3 P-channel MOSFET (lib_id 'Q_PMOS_GDS') in the PSU sub-sheet (file5A5126D2.sch). It is classified as type 'transistor' in the components list but does not appear in signal_analysis.transistor_circuits. The P-channel MOSFET likely acts as a reverse-polarity protection or load switch on the 12V input. The transistor_circuits detector appears to have missed it, possibly because pin data is empty for KiCad 5 legacy components or because the PMOS topology was not recognized.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002379: PCB correctly identified as fully routed with DFM tier classification

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_led-controller-hardware_led-controller.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly reports routing_complete: true with 0 unrouted nets, 907 track segments, 119 vias, and 5 copper zones across 2 layers (F.Cu + B.Cu). The DFM tier is correctly elevated to 'advanced' due to the 0.1mm annular ring (below the 0.125mm standard threshold). Board dimensions 100x67mm are correctly captured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
