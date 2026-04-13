# Findings: sparkfun/SparkFun_Qwiic_Directional_Pad / Hardware_SparkFun_Qwiic_Directional_Pad

## FND-00001503: Component count of 43 and type breakdown are accurate; I2C pull-up resistors (R13, R7) reported as absent despite being present via JP6 jumper; PCA9554PW I2C GPIO expander correctly identified on I...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Qwiic_Directional_Pad.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic correctly identifies 43 components: 15 resistors, 8 jumpers, 4 connectors, 4 fiducials, 4 mounting holes, 3 aesthetic logos, 2 LEDs (D1 red, D2 RGB), 1 switch (SW2 5-way nav switch), 1 capacitor (C1), and 1 IC (U4 PCA9554PW). The 5-way navigation switch is correctly counted as a single component (SW2).
- U4 (PCA9554PW) is correctly identified as the I2C device on SDA/SCL. Address pins A0/A1/A2 are connected through jumpers JP1/JP2/JP3 with pull-down resistors R1/R2/R3 (10k). The 5 directional switch inputs (SW_Up/Down/Left/Right/Center) correctly connect SW2 pins to U4 GPIO pins IO0-IO4.
- SW2 (SparkFun-Switch:Navigation_5Way_SMD_9.9x9.9mm) is a single physical package containing 5 directional buttons. The analyzer correctly identifies switch_count=1, consistent with one schematic symbol representing the 5-way switch. All 5 direction outputs (Up/Down/Left/Right/Center) are correctly routed to U4 GPIO pins IO0-IO4.
- The analyzer correctly identifies led=2 in component_types: D1 (Red, LED_Red_0603) and D2 (LED_RGB, LED_RGB_1205_Bottom). D1 is a power/status indicator with current-limiting series resistor R14 (2.2k). D2 is an RGB LED driven from PCA9554PW GPIO outputs. Both are correctly classified as 'led' type.

### Incorrect
(none)

### Missed
- The I2C bus analysis reports has_pullup=false for both SDA and SCL. However, R13 (2.2k) connects SDA to JP6 pin 1(A), and R7 (2.2k) connects SCL to JP6 pin 3(B). JP6 is a SolderJumper_3_Bridged123 (all pins bridged by default) with its center pin 2(C) on the 3.3V rail, making the pull-ups active by default. This is the same jumper-mediated pull-up pattern seen on the ADS1219 board.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001504: PCB statistics are accurate: 2-layer, 25.4x25.4mm, 33 SMD, 2 THT, fully routed; Courtyard overlaps between Qwiic connectors and back-side components correctly detected; Single GND zone spanning bot...

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_Qwiic_Directional_Pad.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The Directional Pad PCB correctly reports 69 total footprints (33 SMD + 2 THT + 28 board-only + 5 solder-mask-bridge + 1 exclude-from-bom), 280 track segments, 42 vias, 1 GND pour zone spanning F&B.Cu, 30 nets matching schematic, and routing_complete=true.
- The placement_analysis correctly identifies courtyard overlaps on B.Cu between the right-angle Qwiic connectors (J1, J3) and closely packed back-side components (U4 PCA9554PW, C1, R1). These overlaps are characteristic of compact Qwiic breakout design where connector courtyard boundaries intentionally extend over the PCB area.
- The thermal_analysis.zone_stitching correctly reports a single GND zone covering F&B.Cu with 645.2mm² area and 17 stitching vias (2.6/cm²). This represents the full-board GND pour. The zone_count=1 in statistics is consistent with a single polygon spanning both layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
