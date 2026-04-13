# Findings: duckyb/eternal-keypad / bottom-plate-kicad_eternal-keypad-bottom

## FND-00002061: Key matrix correctly detected: 5x8, 36 keys with per-key diodes; WS2812B addressable LED chain of 8 LEDs correctly detected; bus_topology 'width' field counts label placement instances, not unique ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_eternal-keypad_pcb-kicad_eternal-keypad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the keyboard matrix with ROW0-ROW4 (5 rows) and COL0-COL7 (8 columns), estimates 36 keys (not 40 = 5x8, because 4 positions are unpopulated), and confirms 36 diodes on the matrix. The 2 non-matrix switches (POWER1 SPDT and RSW1 reset push-button) are correctly excluded. Detection method is 'net_name', which is appropriate since nets are explicitly named ROW/COL.
- The analyzer correctly identifies the 8-LED WS2812B chain (LED1-LED8) chained via the 'RGB' net from ProMicro1 TX pin, estimates 480mA current draw (8 LEDs x 60mA), and correctly identifies the protocol as 'single-wire (WS2812)'. The separate 'RGB VCC' power rail (routed through JP1 jumper) for LED power is also captured in the power net summary.

### Incorrect
- For COL0..COL7 (8 unique nets), width=16; for ROW0..ROW4 (5 unique nets), width=10. In both cases width equals 2x the actual net count because each net appears exactly twice as a schematic label (once near the switch, once near ProMicro1). The 'width' field is semantically wrong — it should report the number of unique signals in the bus (derivable from range: max_index - min_index + 1), not the raw count of label placements. The same bug is present in fc980c-controller: COL_BIT0..COL_BIT3 has 4 signals but width=8; ROW_BIT0..ROW_BIT2 has 3 signals but width=6.
  (bus_topology)
- The ProMicro development board (ATmega32U4-based) is typed as 'connector' because its schematic symbol comes from the 'promicro:ProMicro' library and the classifier falls back to connector for unknown/third-party libraries. ProMicro1 drives the key matrix, WS2812B data line, and power switching — it is unambiguously the MCU in this design. The ic_pin_analysis does capture it with 24 pins and pin names like TX/RX/GND/RAW, but the BOM type is 'connector'. The component_types stats show connector:1 for ProMicro1 when it should be in an mcu or ic bucket.
  (statistics)
- The battery wire attachment pads (references Batt-1 and Batt+1) use the MountingHole_Pad symbol with a 1-pin connector footprint ('duckyb-collection:1pin_conn'). They are functional electrical connection points — Batt- connects to GND and Batt+ connects to the power switch input. The 'mounting_hole' classification is misleading and causes them to be excluded from connector-related analysis. These should be typed as single-pin connectors or power connectors.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002062: Unrouted net pads listed with duplicate pad IDs due to multi-pad reversible ProMicro footprint

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_eternal-keypad_pcb-kicad_eternal-keypad.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The four unrouted nets (unconnected ProMicro1 pads 2, 5, 6, 7) each list the same pad identifier five times: e.g., pads=['ProMicro1.2', 'ProMicro1.2', 'ProMicro1.2', 'ProMicro1.2', 'ProMicro1.2']. This occurs because the 'Promicro-Jumpers:ProMicro_facedown' footprint has pad_count=242 — a reversible footprint where each logical pin maps to multiple physical copper pads (5 pads per pin for the jumper/castellated variant). The pad de-duplication logic in the PCB analyzer is not handling multi-pad-per-pin footprints correctly, leading to repeated pad references that overcount the physical connections.
  (connectivity)

### Missed
(none)

### Suggestions
(none)

---
