# Findings: tmk/keyboard_converter / converter

## FND-00002234: MINI_DIN_8P_JACK (CN1) misclassified as type 'capacitor' instead of 'connector'; False positive single-pin-net observations for PB0/PB1/PB2 crystal and GND net labels; Crystal oscillator circuit co...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_keyboard_converter_converter.sch.json.json
- **Created**: 2026-03-24

### Correct
- The 16MHz crystal X1 is correctly identified with both load capacitors C5 (10p) and C6 (10p), effective load capacitance 8pF calculated correctly, and flagged as within typical range. The USB differential pair D+/D- with series resistors R1/R2 is also correctly detected.

### Incorrect
- In the BOM, the component CN1 with value 'MINI_DIN_8P_JACK' is assigned type 'capacitor'. This is a clear misclassification — a Mini-DIN 8-pin jack is a connector. The value does not contain any capacitor keywords, so the classifier likely fell through to a default 'capacitor' bucket for unrecognized values.
  (statistics)
- The design_observations lists 10 'single_pin_nets' including PB2 (U1.XTAL1), PB1 (U1.XTAL2), and PB0 (U1.GND). These are KiCad 5 legacy net labels that alias the actual connection nets: the crystal X1 is truly connected via __unnamed_3 (X1, C5, U1.XTAL2 via PB2 label) and __unnamed_4. The labels have point_count=2 confirming wire connections. The crystal_circuits detector correctly found X1 with load caps C5/C6, showing the underlying connectivity is parsed correctly — but the single-pin-net observation wrongly reports these aliased label-nets as floating.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002235: copper_layers_used=0 and front_side/back_side=0 due to KiCad 5 layer names 'Front'/'Back' not recognized as copper layers

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_keyboard_converter_converter.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB has 61 footprints (31 on 'Front', 30 on 'Back'), 497 track segments, 26 vias, and 3 copper zones — clearly a routed 2-layer board. However statistics report copper_layers_used=0, copper_layer_names=[], front_side=0, back_side=0. The layer table shows layers named 'Front' and 'Back' (KiCad 5 legacy naming), not 'F.Cu' and 'B.Cu' (KiCad 6+ naming). The analyzer appears to match copper layers by the modern 'F.Cu'/'B.Cu' names only, failing to count 'Front'/'Back' as copper layers.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
