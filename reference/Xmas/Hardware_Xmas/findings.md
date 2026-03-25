# Findings: Xmas / Hardware_Xmas

## FND-00001771: 56 components detected correctly across all types; WS2812B addressable LED chain of 12 LEDs correctly detected; TPS7A2633DRVR LDO regulator correctly identified from VDD to 3V3; SPK1 (MLT-7525 piez...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Xmas.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Analyzer counts 56 total components: 14 resistors, 15 capacitors, 13 LEDs, 3 switches, 3 ICs, 2 transistors, 1 diode, 5 test points, plus 2 DNP capacitors. Source file counts confirm all categories.
- The chain of LED1-LED12 (WS2812B-2020) on the DIN net is correctly identified as a 12-element single-wire chain with 720mA estimated current (12 × 60mA). LED13 is a separate standard indicator LED and is correctly excluded from the chain.
- U1 (TPS7A2633DRVR) is detected as an LDO regulator with input_rail=VDD and output_rail=3V3, which is correct for this 3.3V fixed-voltage LDO.

### Incorrect
- SPK1 with value MLT-7525 (a magnetic buzzer/speaker) is classified as type 'switch'. The 'SPK' reference prefix is not a standard KiCad prefix so it falls through to a wrong classification. It should be classified as a buzzer or speaker. The component_types dict shows switch=3 which includes this misclassified buzzer; correct value would be switch=2 and buzzer=1.
  (statistics)

### Missed
- AO3401A is a well-known P-channel MOSFET used here as a high-side switch (source=VDD, drain=WS_SUPPLY). The analyzer checks lib_id, ki_keywords, and value for 'pmos', 'p-channel', 'pchannel', 'q_pmos' strings, but the custom library BornaKiCadLibrary:AO3401A encodes none of these keywords. The circuit behavior (source at VDD=power, gate pulled toward VDD via R11=100k) is consistent with P-channel operation, but is_pchannel is reported as false.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001772: 56 SMD footprints, 2-layer board, 124 vias correctly reported; 1 unrouted net correctly detected (CONN1 thermal pad)

- **Status**: new
- **Analyzer**: pcb
- **Source**: Xmas.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analyzer correctly identifies 56 footprints all SMD, 2 copper layers (F.Cu + B.Cu), 432 track segments, and 124 vias matching the drill file exactly.
- routing_complete=false with 1 unrouted net ('unconnected-(CONN1-PadPAD)') is correct — the thermal pad of CONN1 (USB-C connector) has no copper connection defined in the PCB layout.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
