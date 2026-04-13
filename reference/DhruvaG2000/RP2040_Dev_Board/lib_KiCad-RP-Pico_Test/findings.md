# Findings: DhruvaG2000/RP2040_Dev_Board / lib_KiCad-RP-Pico_Test

## FND-00001165: Test.sch parsed correctly as minimal Pico breakout board

- **Status**: new
- **Analyzer**: schematic
- **Source**: Test.sch
- **Created**: 2026-03-23

### Correct
- 4 components (U1 Pico, J1/J2 20-pin connectors, J3 3-pin), 1 net (GND), correct component types, PWR_FLAG presence noted. All component data looks accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001166: RP2040Board1 (Raspberry Pi Pico) classified as type 'resistor' instead of 'ic'; LM1117-3.3 power regulator has input_rail '+3V3' — should be '+12V' (the supply input); Decoupling cap warnings for L...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: picoDevR0_picoDevR0.sch
- **Created**: 2026-03-23

### Correct
- 16 components total, correct breakdown (5 connectors, 4 caps, 2 ICs, 2 resistors, 1 LED, 1 switch, 1 diode — modulo the RP2040Board1 misclassification). Power rails +12V/+5V/+3V3/GND correctly identified. D2 (1N4148) as diode and D1 as LED are correct.

### Incorrect
- Component RP2040Board1 has value 'Pico', lib_id 'picoLibRP2040:Pico', footprint 'picoFootPrint:RPi_Pico_SMD_TH', and 90 bidirectional GPIO pins — clearly a microcontroller board. The BOM entry also marks it 'type: resistor'. The type classifier is falling back to 'resistor' for custom lib symbols that don't match known library prefixes. Should be 'ic'.
  (signal_analysis)
- The analyzer reports LM_3V3 (LM1117-3.3) with input_rail '+3V3' and output_rail '__unnamed_53'. In this design +12V is the primary supply from the barrel jack; +3V3 is the regulated output label used as a power symbol. The analyzer is confusing the named power rail connected to the regulator's output pin with its input rail. The LM1117-3.3 input should come from +12V or +5V, not from +3V3. Similarly LM_5 has input_rail '+5V' which is its own output voltage — the input should be +12V.
  (signal_analysis)
- The design has 4 capacitors (C_op1, C_ip1, C_op2, C_ip2 — electrolytic, CP_Radial_D10mm footprint) which are the input/output caps for the two LM1117 regulators. The analyzer reports 'rails_without_caps' for +3V3 and +5V. The issue is likely that the caps are on unnamed nets rather than the named +3V3/+5V rails, so the analyzer misses them. The 'regulator_caps' warnings claiming missing input and output caps are therefore false positives.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001167: Test PCB parsed correctly: 4 footprints, 2-layer, fully routed, dual GND zones

- **Status**: new
- **Analyzer**: pcb
- **Source**: Test.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 4 THT footprints all on F.Cu, 37 track segments on F.Cu only, 2 GND copper fills (F.Cu + B.Cu), routing_complete=true, 36 nets, 43x65mm board with rounded corners. All looks accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001168: copper_layers_used=2 and copper_layer_names=[In1.Cu, In2.Cu] but board defines 4 copper layers (F.Cu, B.Cu, In1.Cu, In2.Cu)

- **Status**: new
- **Analyzer**: pcb
- **Source**: picoDevR0_picoDevR0.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The board has 0 track segments (unrouted). The analyzer reports only 2 copper layers used (In1.Cu and In2.Cu), apparently derived from the zone definitions rather than the layer stack definition. F.Cu and B.Cu are omitted from copper_layer_names. The board is defined as 4-layer; copper_layers_used should reflect the stack, not just active-track layers. Also board_width/height are null despite footprints being placed, indicating missing Edge.Cuts.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001169: copper_layers_used=0 and copper_layer_names=[] despite board defining F.Cu and B.Cu in the layer stack

- **Status**: new
- **Analyzer**: pcb
- **Source**: picoDevR0_picoDevR01.kicad_pcb
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- picoDevR01 has 7 footprints, 0 tracks, and 0 zones. The analyzer reports copper_layers_used=0 with empty copper_layer_names. The board file defines F.Cu and B.Cu as signal layers. With no tracks or zones, the analyzer produces 0 — it should instead report the declared copper layer count from the board setup (2), or at minimum not misrepresent a 2-layer board as having 0 copper layers.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001170: picoDevR02 correctly parsed as 4-layer near-complete board with 134 tracks, 3 unrouted nets

- **Status**: new
- **Analyzer**: pcb
- **Source**: picoDevR0_picoDevR02.kicad_pcb
- **Created**: 2026-03-23

### Correct
- copper_layers_used=4, copper_layer_names=[B.Cu, F.Cu, In1.Cu, In2.Cu], 16 footprints all THT, 607mm total track length, 3 unrouted nets, 50 nets total, same component groups as picoDevR0. board_outline is null (no Edge.Cuts), which is expected for an in-progress design. All data appears accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
