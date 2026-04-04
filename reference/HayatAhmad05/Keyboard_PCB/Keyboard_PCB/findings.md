# Findings: Keyboard_PCB / Keyboard_PCB

## FND-00000660: Key matrix correctly detected: 5×14, 70 switches, 70 diodes; Component counts correct: 70 diodes, 70 switches, 1 IC (ESP32-WROOM-32E); No power rails or PWR_FLAG warnings correctly reported for pow...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Keyboard_PCB.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- signal_analysis.key_matrices reports rows=5, cols=14, estimated_keys=70, detection_method=net_name. Matches the 70 S-refs and 70 D-refs in the schematic exactly.
- statistics.component_types matches the schematic: all 141 total components parsed correctly, with proper typing of D-refs as diode, S-refs as switch, U1 as ic.
- The schematic has no power symbols (only ESP32 module and passive keyboard matrix), so empty power_rails and empty pwr_flag_warnings is correct behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000661: PCB correctly identified as empty/unpopulated (footprint_count=0)

- **Status**: new
- **Analyzer**: pcb
- **Source**: Keyboard_PCB.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The .kicad_pcb source file contains only layer definitions and a single empty net — no footprints, no tracks, no vias. The analyzer correctly reports all zeros and routing_complete=true (nothing to route).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
