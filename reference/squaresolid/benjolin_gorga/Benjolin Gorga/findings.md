# Findings: squaresolid/benjolin_gorga / Benjolin Gorga

## FND-00001949: Component counts correctly extracted from hierarchical subsheet; Power regulators IC7 (LM78L09) and IC8 (LM79L09) detected with correct topology; Op-amp circuits correctly identified for TL072/TL07...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Benjolin Gorga.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic is a hierarchy with one sheet reference to benjolin_1.6_2.kicad_sch. The analyzer correctly resolves 137 total components (66 resistors, 34 capacitors, 13 diodes, 9 ICs, 12 connectors, 1 transistor, 1 switch, 1 jumper) from the subsheet, matching what is in the actual source. The 10k potentiometers (R51-R61) with 5-pad footprints are correctly typed as resistors.
- Both linear regulators are identified: IC7 (lm78l09) as LDO with input VCC / output V+, and IC8 (lm79l09) as LDO with input VEE / output V-. This matches the actual schematic where IC7 produces the positive 9V rail and IC8 produces the negative 9V rail.
- Multiple op-amp configurations are detected across IC2, IC4, IC5, IC6, IC9 (TL074D and TL072D). Inverting and comparator/open-loop configurations are correctly identified. The Benjolin is an analog noise/chaos circuit using op-amps as comparators and integrators, and the multi-unit decomposition per op-amp package unit is correct.
- Q1 is detected as BJT with base on unnamed net (driven by IC), collector connected to the rungler circuit, and emitter at GND. Base resistor R17 (100k) is identified. This matches the actual schematic topology.

### Incorrect
- The net V- is the regulated negative supply output from IC8 (LM79L09). It is connected to the V- power pins of multiple op-amp ICs (pin_type 'power_in'). However, in design_analysis.net_classification it is listed as 'signal' rather than 'power'. Similarly, V- does not appear in statistics.power_rails even though it is a supply rail alongside V+, VCC, and VEE. This misclassification could cause downstream analysis to miss decoupling on this rail.
  (statistics)
- The design_observations list includes a 'regulator_caps' entry for IC8 (lm79l09) noting missing input and output caps. However, IC7 (lm78l09) similarly lacks dedicated bypass capacitors on VCC (input) and V+ (output) beyond the shared op-amp decoupling caps on V+. IC7's subcircuit shows no neighbor capacitors. The omission of an IC7 regulator_caps observation is asymmetric with the IC8 treatment and likely a false negative.
  (signal_analysis)

### Missed
- IC3 is an SSM2164S, a four-quadrant voltage-controlled amplifier (VCA) commonly used in analog synthesizers. It is central to the Benjolin's signal processing. The analyzer categorizes it generically as 'ic' with no signal path detection. The SSM2164 library ID is 'digikey-footprints:DIP-16_W7.62mm', and the part appears in the schematic as value 'SSM2164S'. No dedicated VCA or audio-gain-element detector fires for it. This is an expected gap for exotic audio ICs but worth noting.
  (statistics)

### Suggestions
(none)

---

## FND-00001950: Footprint count matches gerber component count

- **Status**: new
- **Analyzer**: pcb
- **Source**: Benjolin Gorga.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The PCB analyzer reports 140 total footprints (116 front, 24 back), matching the gerber analyzer's 140 unique components in the F.SilkS layer. The smd/tht split (109 SMD, 28 THT) aligns with the mixed SMD+THT design seen in the gerbers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001951: Gerber set is complete with correct 2-layer stackup and all expected layers present; Drill classification correctly separates vias (61 x 0.4mm) from component holes (115) and NPTH holes (12); Fab l...

- **Status**: new
- **Analyzer**: gerber
- **Source**: Benjolin_Gerber
- **Created**: 2026-03-24

### Correct
- All 9 expected layers (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) are found. The gbrjob file correctly drives layer discovery. PTH and NPTH drills are both present. Board dimensions (77.6 x 100.1 mm) are consistent across layers.
- 61 via holes at 0.3988mm, 115 component PTH holes across 4 tool sizes (0.8, 0.889, 1.0, 1.016mm), and 12 NPTH holes at 2.1996mm (likely panel mounting) are all correctly identified with appropriate classification methods. Total 176 holes.
- The F.Fab and B.Fab assembly drawing layers have FileFunction 'AssemblyDrawing,Top/Bot' which does not map to any standard copper/mask/silk type. The analyzer labels them 'unknown', which is the correct fallback rather than misclassifying them.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
