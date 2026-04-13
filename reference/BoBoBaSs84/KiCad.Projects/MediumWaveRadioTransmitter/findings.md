# Findings: BoBoBaSs84/KiCad.Projects / MediumWaveRadioTransmitter

## FND-00000734: Qz2 (Device:Crystal) misclassified as 'transistor' due to 'Qz' reference prefix; Crystal circuit (Qz2 resonator oscillator) not detected in crystal_circuits; No power rails reported correctly — sch...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MediumWaveRadioTransmitter_MediumWaveRadioTransmitter.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- power_rails=[], power_symbols=[], pwr_flag_warnings=[] all correct. Design is powered via J1 (WAGO connector) with no explicit power symbols, so empty power rail list is appropriate.
- RC filters detected with correct component refs, values, and calculated cutoff frequency. Appropriate for a medium wave transmitter circuit.

### Incorrect
- lib_id is Device:Crystal and value is '400kH' (ceramic resonator), but type='transistor' and category='transistor'. Analyzer uses reference prefix heuristic ('Q' prefix -> transistor) which overrides lib_id lookup. This inflates transistor count to 3 (should be 2) and deflates crystal count.
  (signal_analysis)

### Missed
- crystal_circuits=[] despite Qz2 being a Device:Crystal used in an LC/oscillator circuit with capacitors C4/C5/C6 and transistors T3/T4. Because Qz2 is misclassified as a transistor, the crystal circuit detector never finds it.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000735: Board outline correctly shows 0 edges and null bounding box — Edge.Cuts layer has no geometry; Layer transitions reported for 8 nets without vias — no vias exist (via_count=0)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: MediumWaveRadioTransmitter_MediumWaveRadioTransmitter.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Edge.Cuts layer is defined (layer 44) but has zero graphic items. Analyzer correctly reports edge_count=0 and board_width_mm/board_height_mm=null. No false detection.

### Incorrect
- layer_transitions lists 8 nets each spanning B.Cu and F.Cu with via_count=0. Via count is correctly 0, but having B.Cu+F.Cu layer transitions with zero vias is physically impossible for routed through-hole tracks without vias. This is a topological inconsistency in the output, likely due to THT pad nets being counted on both layers.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
