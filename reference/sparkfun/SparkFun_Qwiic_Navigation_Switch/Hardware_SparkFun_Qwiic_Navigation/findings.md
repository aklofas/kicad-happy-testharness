# Findings: SparkFun_Qwiic_Navigation_Switch / Hardware_SparkFun_Qwiic_Navigation

## FND-00001510: Component count of 43 is accurate; I2C pullups on SDA (R13) and SCL (R7) not detected — has_pullup reports false; I2C bus (SDA, SCL) and PCA9554 IC correctly detected; Power rails (3.3V, GND), deco...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Qwiic_Navigation.kicad_sch
- **Created**: 2026-03-24

### Correct
- The output reports 43 total_components matching all 43 unique refs in the source schematic (ST1-ST4, FID1-FID4, G1/G3/G5, JP1-JP8, R1-R15, D1/D2, C1, J1-J3/J5, SW2, U4). Component type breakdown is also correct: 15 resistors, 8 jumpers, 4 mounting holes, 4 fiducials, 4 connectors, 2 LEDs, 3 other (logos), 1 switch, 1 capacitor, 1 IC.
- The bus_analysis detects both SDA and SCL nets, associates U4 (PCA9554PW 8-bit I2C I/O expander) with both lines, and reports them as i2c type. The IC classification as type 'ic' is correct. The 32 nets matches the PCB net count exactly.
- Two power rails (3.3V, GND) are correctly identified. The single 0.1uF capacitor (C1) on the 3.3V rail is detected in decoupling_analysis with correct total_capacitance_uF=0.1. Net count of 32 matches the PCB output exactly.

### Incorrect
- R13 (2.2k) is connected between the SDA net and JP6 pin1; R7 (2.2k) is connected between the SCL net and JP6 pin3; JP6 is a 3-pole closed solder jumper whose center pin (pin2) connects to 3.3V. The net trace is: SDA -> R13 -> unnamed_net -> JP6 -> 3.3V and SCL -> R7 -> unnamed_net -> JP6 -> 3.3V. These are I2C pullup resistors switched through a solder jumper. The analyzer fails to trace through the intermediate unnamed nets created by the solder jumper and therefore reports has_pullup: false for both SDA and SCL bus observations.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001511: Footprint, via, track, and zone counts all correct; B.Cu layer classified as 'jumper' type — correctly parsed from source; GND zone stitching with via density and SDA/SCL net routing correctly anal...

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_Qwiic_Navigation.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=68 matches the 68 (footprint ...) entries in the source PCB. via_count=42, track_segments=286, and zone_count=1 all verified against the source file. Net count of 32 matches the schematic exactly. Board dimensions 25.4x25.4mm are correct (standard 1-inch square SparkFun Qwiic format).
- The PCB file defines B.Cu with layer type 'jumper' in the layer stack definition: '(31 "B.Cu" jumper)'. The analyzer correctly parses and reports this as type: 'jumper'. This is an unusual but valid KiCad 8 layer type designation for a design where the back copper is used as a jumper layer. The layer is actively used for routing (multiple tracks, vias, and a GND zone on F&B.Cu).
- The thermal_analysis correctly identifies the single GND zone spanning F&B.Cu with area 645.2mm2 and 19 stitching vias. The net_lengths section shows SDA and SCL routed across both layers with 4 vias each, accurately reflecting the cross-layer I2C routing in this compact 25.4mm square design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
