# Findings: futurewidgets/esphome-entry / docs_schematics_esphome-entry board

## FND-00002057: LM393 dual comparator ic_pin_analysis shows only 2 pins (power unit only); the 3 functional comparator pins from unit 1 are reported separately as a second ic_pin_analysis entry

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esphome-entry_docs_schematics_sound trigger sensor_sound trigger sensor.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The LM393 is a dual comparator with power on unit 3 and comparator inputs/output on unit 1. The schematic places both unit 1 and unit 3 as U1. The ic_pin_analysis section contains two separate entries for U1: one with total_pins=2 (V+ and V- from the power unit) and one with total_pins=3 (IN+, IN-, OUT from unit 1). These should be merged into a single entry showing all 5 pins of the placed U1 component. As a result, the functional comparator pins are effectively orphaned from the IC's power context.
  (ic_pin_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002058: PC817 optocoupler (U2) not detected as an isolation barrier despite being a classic optocoupler isolation circuit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esphome-entry_docs_schematics_esphome-entry board_esphome-entry board.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- U2 is a PC817 optocoupler connecting the remote button input (J2) to the ESP32-C3 GPIO21 via the TRIGGER_REMOTE net. The input side has the LED (anode via R1 to J2 pin 1, cathode to GND) and the output side connects to the microcontroller GPIO. This is a textbook galvanic isolation circuit. The isolation_barriers section is empty, and the signal_analysis.isolation_barriers list contains no entries. The PC817 is classified as a generic 'ic' type rather than being recognized as an optocoupler.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002059: Stub PCB file (79 bytes, no footprints) analyzed silently with all-zero statistics and no warning

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_esphome-entry_docs_schematics_esphome-entry board_esphome-entry board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- Both PCB files in esphome-entry are empty stubs: '(kicad_pcb (version 20240108) (generator "pcbnew") (generator_version "8.0"))' — 79 bytes, no footprints, no nets, no tracks. The analyzer processes them without error and produces a valid JSON with footprint_count=0, copper_layers_used=0, routing_complete=True. There is no warning or flag to indicate the PCB is an empty placeholder. This makes the result indistinguishable from a legitimate PCB with zero components. The same issue affects the sound trigger sensor PCB.
  (statistics)

### Suggestions
(none)

---
