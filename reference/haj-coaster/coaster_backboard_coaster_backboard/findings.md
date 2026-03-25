# Findings: haj-coaster / coaster_backboard_coaster_backboard

## FND-00002111: IS31FL3733 LED matrix driver topology not detected; 20 RGBA multi-LED components misclassified as diodes

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_haj-coaster_coaster_backboard_coaster_backboard.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- U2 is an IS31FL3733-QF (12x16 LED matrix driver, up to 192 LEDs), controlling 58 single-color LEDs (Device:LED) and 20 RGBA_P1 components via I2C from U1 (STM32F072). The analyzer identifies U2 as 'LED driver' in ic_pin_analysis but does not produce any LED matrix detection (addressable_led_chains is empty, no matrix driver output). Additionally, the 20 RGBA_P1 components (custom multi-LED device with 4 LEDs each) are classified as type='diode' rather than type='led' or a custom multi-LED type, understating the total LED count.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002112: Advanced DFM tier correctly identified with 0.12mm track spacing on a dense LED matrix board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_haj-coaster_coaster_backboard_coaster_backboard.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The 93x93mm backboard has 128 footprints, 1900 track segments, 499 vias, and a 0.12mm minimum track spacing (below the 0.127mm standard process limit). The analyzer correctly assigns dfm_tier='advanced' and flags the one violation. The courtyard overlap between U3 and U1 (2.4mm^2) is also correctly detected, likely from the STM32 and LDO sharing tight placement.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002113: Mechanical connector board with no copper traces correctly identified

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_haj-coaster_coaster_midboard_coaster_midboard.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The midboard is a 93x93mm mechanical inter-board connector plate containing only 6 THT connectors (J1-J6) with no copper traces, no vias, and no copper zones. The analyzer correctly reports copper_layers_used=0, track_segments=0, via_count=0. Net count of 6 with routing_complete=True is consistent with the footprint pad assignments carrying through even though there are no routed tracks.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
