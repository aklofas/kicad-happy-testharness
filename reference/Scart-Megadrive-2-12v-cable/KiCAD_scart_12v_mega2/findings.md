# Findings: Scart-Megadrive-2-12v-cable / KiCAD_scart_12v_mega2

## FND-00001318: Scart cable board: TPS61040 boost converter with inductor L1 correctly identified as switching regulator; TPS61040 boost converter output rail identified as '__unnamed_4' (same as input) — input/ou...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: scart_12v_mega2.kicad_sch
- **Created**: 2026-03-24

### Correct
- power_regulators correctly lists U1=TPS61040DBVR with topology=switching and inductor=L1. switching_regulator observation is correctly emitted. Three 220uF tantalum caps (CB1, CG1, CR1) and Schottky diodes D1/D2 correctly parsed. Full MPNs from Samsung/Kemet/TDK/YAEGO/UNI-ROYAL correctly extracted with LCSC part numbers.
- All components have MPNs and footprints. 8 connectors (J1-J8 with J2/J4/J6/J8 not in BOM), 6 caps, 6 resistors (including 3 RGB 75-ohm termination), 3 diodes, 1 switch (S1), 1 inductor, 1 IC. Component type 'inductor' for L1 correctly classified.

### Incorrect
- The TPS61040 is a boost converter: its input is 5V (from J7/SCART) and output is a higher voltage (for SCART +12V switching). The analyzer sets both input_rail and output_rail to '__unnamed_4'. This is because the boost output net has no named power symbol. The regulator_caps observation similarly misses caps on the correct output net. The LC filter (L1+C2) is correctly detected as an LC pair but the regulator's output vs input rails are conflated.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001319: Scart PCB correctly analyzed: 27 footprints, 26 SMD, 0 THT, 2-layer, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: scart_12v_mega2.kicad_pcb
- **Created**: 2026-03-24

### Correct
- smd_count=26, tht_count=0 consistent with an all-SMD design. Board 39.5×20.8mm, 165 track segments, 16 vias, 1 zone, 25 nets, routing_complete=true, unrouted=0. These figures are internally consistent.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
