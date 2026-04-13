# Findings: sparkfun/SparkFun_Qwiic_ADC_ADS1219 / Hardware_Qwiic_ADC_ADS1219

## FND-00001500: Component count of 37 and type breakdown are accurate; I2C pull-up resistors (R2, R3) reported as absent despite being present via JP3 jumper; Reset pin (~RESET) pull-up correctly identified with R...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Qwiic_ADC_ADS1219.kicad_sch
- **Created**: 2026-03-24

### Correct
- The schematic correctly identifies 37 total components: 11 jumpers (JP1-JP11), 5 resistors (R1-R5), 6 connectors (J1-J6), 4 capacitors (C1-C4), 4 mounting holes (ST1-ST4), 3 aesthetic logos, 2 fiducials (FID1, FID3), 1 IC (ADS1219IPW), and 1 LED (D1). Power rails 3.3V, GND, and VDDA are correctly listed.
- The design_observations correctly identifies a reset_pin for U1 (~RESET) with has_pullup=true, correctly attributing R5 (10k, connected from 3.3V to ~RESET) as the pull-up resistor. The reset pin is also exposed on connector J5 for external control.
- The decoupling_analysis correctly identifies two-capacitor decoupling on both rails: 3.3V rail has C1 (2.2uF) and C2 (0.1uF) totaling 2.3uF; VDDA analog rail has C3 (2.2uF) and C4 (0.1uF) also totaling 2.3uF. This is an appropriate bulk+bypass combination for an ADC with separated digital/analog power.
- The bus_analysis.i2c section correctly identifies two I2C lines (SDA and SCL) with U1 (ADS1219IPW) as the device on both. The 23 nets total match the PCB net count, confirming accurate net extraction.

### Incorrect
(none)

### Missed
- The I2C bus analysis reports has_pullup=false for both SDA and SCL. However, R3 (2.2k) is connected between SDA and JP3 pin 1(A), and R2 (2.2k) is connected between SCL and JP3 pin 3(C). JP3 is a SolderJumper_3_Bridged123 (all pins bridged by default) with its center pin 2(B) on the 3.3V rail, making the pull-ups active in the default configuration. The analyzer fails to trace pull-up paths through solder jumpers.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001501: PCB statistics are accurate: 2-layer, 25.4x25.4mm, 4 THT connectors, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: Qwiic_ADC_ADS1219.kicad_sch
- **Created**: 2026-03-24

### Correct
- The ADS1219 PCB correctly reports 77 total footprints (25 SMD + 4 THT + 43 board-only + 5 solder-mask-bridge), 2-layer board, 238 track segments, 48 vias, 3 zones (GND on F.Cu, GND on B.Cu, and a keepout zone), 23 nets matching schematic, and routing_complete=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001502: GND zones on both copper layers correctly identified with stitching vias

- **Status**: new
- **Analyzer**: pcb
- **Source**: Qwiic_ADC_ADS1219.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The thermal analysis correctly identifies a GND zone on F.Cu (619.6mm² outline, 331mm² filled) and a GND zone on B.Cu (619.6mm² outline, 365mm² filled), plus a keepout zone. The zone_stitching reports GND on F&B.Cu with 24 stitching vias. This dual-layer GND pour is appropriate for an ADC requiring low-noise ground.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
