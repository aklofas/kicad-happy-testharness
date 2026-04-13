# Findings: CesarOtoniel/charlieplexedHeart / _autosave-heart

## FND-00002304: Charlieplexed LED topology not detected for 20-LED ATtiny13 design; Power net summary misses ATtiny13A VCC pin; only 3 components on VCC

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_charlieplexedHeart_heart.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The connectivity_issues.power_net_summary reports VCC with pin_count=3 and components=[BT1, SW2, TP7]. The ATtiny13A (U1) has a VCC pin (pin 8) that should also be on this net. U1 appears only on the GNDREF net in the summary. This indicates U1's unnamed power pin is connected to a different net or the VCC pin is connected through an unnamed net and not recognized as the VCC rail.
  (connectivity_issues)

### Missed
- The design is explicitly a 'Charlieplexed LED sequencer' (per README and repo name). An ATtiny13A drives 20 LEDs via 5 GPIO pins through 5 resistors using charlieplexing (5 pins × (5-1) = 20 LEDs). The analyzer produces empty signal_analysis.key_matrices and no charlieplex observation anywhere in the output. The topology is recognizable: a single MCU with N outputs driving N×(N-1) LEDs. This is a missed detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002305: Correctly detects heartLED.kicad_pcb as a bare footprint placement with no routing

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_charlieplexedHeart_heartLED.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- heartLED.kicad_pcb is a separate PCB file containing only 20 LED THT footprints with no nets, no tracks, and no zones — apparently a placement reference or panel for the LED positions. The analyzer correctly reports track_segments=0, via_count=0, zone_count=0, net_count=0, and copper_layers_used=0, and reports routing_complete=true (correct since there is nothing to route).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
