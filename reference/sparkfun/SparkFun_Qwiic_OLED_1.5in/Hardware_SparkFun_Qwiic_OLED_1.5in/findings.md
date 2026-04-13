# Findings: sparkfun/SparkFun_Qwiic_OLED_1.5in / Hardware_SparkFun_Qwiic_OLED_1.5in

## FND-00001512: I2C and SPI bus signals not detected in bus_analysis due to slash-encoded net names; AP3012 boost converter output_rail incorrectly reported as '3.3V' — should be '12V'; I2C pullups on SDA{slash}SD...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Qwiic_OLED_1.5in.kicad_sch
- **Created**: 2026-03-24

### Correct
- U5 (AP3012) is correctly classified as a switching regulator with topology 'switching', the associated inductor L1 is correctly linked, and the feedback divider (R1=18k, R2=2.1k connecting 12V to FB) is correctly extracted as a voltage divider and feedback network. The 5 capacitors (C1-C5) are correctly enumerated. The decoupling analysis for both 3.3V (C1+C4=5.7uF) and 12V (C2+C5=5.7uF) rails is accurate.
- The output's 39 total_components matches the actual unique placed symbol instances in the SparkFun_Qwiic_OLED_1.5in project context. The 25 nets matches the PCB net count exactly. Component type breakdown (5 caps, 9 resistors, 1 inductor, 1 diode, 2 ICs, 4 connectors, 5 jumpers, 4 mounting holes, 2 fiducials, 1 LED, 1 test_point, 4 other) is correct.

### Incorrect
- U5 (AP3012) is a boost converter (labeled 'Contrast Boost - AP3012' in schematic annotations) that takes 3.3V input and boosts to ~12V for the OLED contrast voltage. The SW output pin connects to local label '12V_OUT', which connects through Schottky diode D2 (PMEG4005EJ anode) to the 12V global power rail. The analyzer reports output_rail: '3.3V' (incorrectly matching the IC's input power rail) and input_rail: '3.3V' (correct). The true output_rail is '12V'. The estimated_vout of 5.743V is a heuristic approximation given the AP3012 Vref=0.6V and the R1=18k/R2=2.1k feedback divider, while the actual 12V output suggests a different Vref or the design targets VCOMH voltage not directly tied to the feedback.
  (signal_analysis)
- R4 (2.2k) connects SDA{slash}SDI to JP2 pin3 and R5 (2.2k) connects SCL{slash}SCK to JP2 pin1. JP2 is a 3-pole solder jumper (I2C jumper) whose center pin connects to 3.3V. These are I2C pullup resistors that can be disconnected by cutting the jumper. The analyzer reports no pullup detection (the bus is not even recognized due to {slash} encoding), missing the presence of switchable I2C pullups in this design.
  (signal_analysis)

### Missed
- The OLED schematic uses combined net names 'SDA{slash}SDI' and 'SCL{slash}SCK' (KiCad encodes '/' as '{slash}' in global labels) for the dual-mode I2C/SPI interface. The bus_analysis.i2c and bus_analysis.spi arrays are both empty. The analyzer's pattern matching does not handle the {slash} encoding and fails to match these nets against SDA/SCL/SDI/SCK patterns. Notably, the test_coverage section correctly identifies the same nets as 'i2c' category, demonstrating an inconsistency between the two subsystems.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001513: All PCB statistics correct: 72 footprints, 81 vias, 231 tracks, 5 zones, 25 nets; Three copper zones (12V, 3.3V, GND) correctly identified in thermal analysis

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_Qwiic_OLED_1.5in.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=72, via_count=81, track_segments=231, zone_count=5, and net_count=25 all verified against the source KiCad PCB file. Board dimensions 34.29x49.53mm are correct (includes arc extremes from rounded board corners). The 5 zones (12V F.Cu, 3.3V F.Cu, GND B.Cu, GND F.Cu, plus one more) are correctly counted.
- The thermal_analysis.zone_stitching correctly identifies three zone fill nets: 12V (6.0mm2 on F.Cu with 4 vias), 3.3V (6.2mm2 on F.Cu with 8 vias), and GND (1323.9mm2 on B.Cu+F.Cu with 57 vias). The large GND pour is correctly identified as a ground plane flood fill.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
