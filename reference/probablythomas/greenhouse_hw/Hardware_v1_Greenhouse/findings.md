# Findings: probablythomas/greenhouse_hw / Hardware_v1_Greenhouse

## FND-00002107: TL2575-05IN switching buck converter not detected as power regulator; MOSFET Q1 drain and source nets are swapped relative to schematic symbol placement

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_greenhouse_hw_Hardware_v1_Greenhouse.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer reports Q1 (IRLB8721PBF N-channel) with drain_net=GND and source_net=LED_ON, and drain_is_power=True while source_is_ground=False. This is a faithful reading of the KiCad 5 legacy schematic where the designer appears to have placed the Q_NMOS_GDS symbol with D (pin 2) connecting to GND and S (pin 3) to the LED load net, which is the reverse of a typical N-channel low-side switch. The analyzer correctly reports what is in the schematic but does not flag that drain=GND and source=load is an unusual and likely erroneous topology for an N-ch low-side switch.
  (signal_analysis)

### Missed
- U1 (TL2575-05IN) with external inductor L1 (330uH) and freewheeling diode D1 (1N5819) forms a classic Simple Switcher step-down buck converter topology converting +9V to +5V. The analyzer returns power_regulators: [] despite having all the circuit elements present (regulator IC, inductor, catch diode). The pin-name mapping in the KiCad 5 legacy symbol is unusual (GND at V_IN pin, multiple NC pins for a DIP-16 symbol), which may interfere with detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002108: Layer transition on /3V3 net without vias correctly detected

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_greenhouse_hw_Hardware_v1_Greenhouse.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The /3V3 net runs on both B.Cu and F.Cu with zero vias, which the analyzer correctly identifies in layer_transitions. This indicates the signal jumps layers without a via, which is a genuine layout concern. The PCB has 44 track segments and 0 vias, so the layer transition relies on pads bridging the layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002109: Main drill file classified as type 'unknown' despite containing 64 PTH component holes

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_greenhouse_hw_Hardware_v1.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The primary drill file Greenhouse.drl (66 holes including 64 component holes and 2 mounting holes) is classified as type='unknown' because it lacks an explicit M48 header identifying it as PTH. This causes has_pth_drill=False in the completeness section, which is misleading since the board is all THT with many component holes. The separate NPTH file is correctly classified. The alignment=False warning is a false alarm caused by the F.SilkS layer extending 3mm beyond the board edge due to component silkscreen overhang (consistent with J1 and Q1 having negative edge clearance), not a real manufacturing defect.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
