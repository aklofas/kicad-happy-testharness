# Findings: PCRD04 / hw_sch_pcb_PCRD04B

## FND-00001053: Op-amp circuit detection correct: U1/U2 (OPA2314) as TIA/buffer/inverting, U4 (TS7211) as comparator; U6 'neosazovat' DNP marker not detected — dnp_parts=0, U6 dnp=false; Decoupling analysis misses...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCRD04B.kicad_sch
- **Created**: 2026-03-23

### Correct
- All five op-amp configurations correctly identified including transimpedance amplifier (U1 unit1), inverting amplifiers with correct gains (-4.7x), and buffer (U2 unit2). RC filter network on REF rail (R7+C10, 159Hz) also correctly identified.
- Power comes in from J1 (a 3.6V connector). Since KH-160 only suppresses PWR_FLAG warnings for known power-source footprints, this connector-powered design correctly still reports the warnings — reflecting the missing ERC annotation.

### Incorrect
- U6 value is 'LM4041CIM3-1.2(neosazovat)' where 'neosazovat' is Czech for 'do not populate'. The analyzer does not detect DNP information embedded in the value field using localized terms. U6 should be flagged as DNP.
  (signal_analysis)
- VCC rail correctly shows 47uF+10uF (has_bulk=True, has_bypass=False). However, each derived rail VCC1-4 has a 100nF bypass capacitor (C11-C14) and 10uF (C6-C9) via 100-ohm resistors — these are power supply bypass caps that aren't counted for VCC. The design_observation 'has_bypass=False' is misleading since the circuit is well-bypassed at the point of use.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001054: PCB statistics accurate: 62 footprints, 2 layers, 115 vias, 385 segments, routing complete

- **Status**: new
- **Analyzer**: pcb
- **Source**: PCRD04B.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Footprint count, front/back split (17F/45B), layer count, via count, and board dimensions all match gerber data. 28 nets in PCB matches 28 in schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001055: Gerber completeness, alignment, and drill classification all correct for 2-layer board

- **Status**: new
- **Analyzer**: gerber
- **Source**: hw_cam_profi
- **Created**: 2026-03-23

### Correct
- All 8 expected layers present. X2-attribute-based drill classification correctly identifies 115 vias (0.4mm) and 27 component holes (0.762mm, 0.889mm, 3.0mm). 4 mounting holes (3.0mm) classified as component holes due to X2 ComponentDrill attribute — technically correct since they are connected to GND.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
