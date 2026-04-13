# Findings: koron/yuiop / yuiop60pi_main2

## FND-00002514: Keyboard PCB (PGA2040, 5x15 key matrix, 56 WS2812 LEDs). Component counts and key matrix correct, but U1 pin-to-net mapping severely wrong due to mirrored placement, LED chain detection fragmented into 55+ pieces instead of 1 chain.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: yuiop60pi_main2_main2.sch.json
- **Created**: 2026-04-09

### Correct
- 191 components correct: 1 IC, 4 connectors, 1 MOSFET, 2 resistors, 61 switches, 4 caps, 1 fuse, 61 diodes, 56 LEDs
- Key matrix correctly detected as 5x15 with 60 switches and 60 diodes
- Q1 BSS138 transistor correctly identified with gate/source/drain nets
- SWD debug interface correctly detected on J3
- USB differential pair correctly identified

### Incorrect
- U1 PGA2040 pin-to-net mapping severely wrong due to mirrored placement (-1 X scale). GND pins mapped to COL4/COL5, GPIO pins mapped to GND. Coordinate-based wire matching assigns nets to wrong physical pins on mirrored components.
  (components[U1].pin_nets)
- J1 USB_B_Micro pin mapping wrong: VBUS/D+/D- assignments swapped due to same mirror issue
  (components[J1].pin_nets)
- Addressable LED chain detection fragmented: 56 WS2812C-2020 LEDs form single daisy chain but analyzer reports 55+ separate entries with LED27 repeated. Chain-tracing fails across sub-sheet.
  (signal_analysis.addressable_led_chains)
- 3V3 net classified as 'signal' but is a 3.3V power rail from PGA2040
  (design_analysis.net_classification)
- BOOTSEL classified as 'chip_select' but is boot mode selection signal
  (design_analysis.net_classification)

### Missed
- Q1 BSS138 with R1/R2 pull-ups is a bidirectional MOSFET level shifter (3V3 to 5V for WS2812 data) but level_shifters is empty
  (signal_analysis.level_shifters)
- VBUS->F1->DS1->VCC power path (fuse + Schottky for USB protection) not in power_path
  (signal_analysis.power_path)

### Suggestions
- Fix pin-to-net mapping for mirrored components in KiCad 5 legacy: apply component transform before coordinate-based wire matching
- Fix LED chain tracing across hierarchical sheets to follow DOUT->DIN connections
- Classify net names matching power rail patterns (3V3, 1V8, 5V) as power not signal

---
