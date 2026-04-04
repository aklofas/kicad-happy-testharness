# Findings: VhARIO-ESPC3 / vhario-espc3

## FND-00001792: Total component count 57 matches source schematic; LDO regulator U5 (TLV75533PDBV) correctly detected; Ferrite beads L1 and L2 correctly classified; USB ESD protection (BV03C TVS diodes D4, D6, D7)...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: vhario-espc3.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- Source schematic has 57 unique placed component instances (BZ1, C1-C15, D2-D7, F1, H1-H2, J1-J2, JP1, L1-L2, Q1-Q2, R1-R16, SW1-SW4, U1-U5). The analyzer reports total_components=57, matching exactly.
- U5 TLV75533PDBV is correctly identified as a fixed 3.3V LDO with +VSW input rail and +3.3V output rail.
- L1 and L2 (value GZ2012D601TF, library 0-vhario-espc3:L_Ferrite) are correctly classified as ferrite_bead in component_types, not inductor. Statistics show ferrite_bead=2.
- Three BV03C TVS diodes (D6 on D+, D4 on D-, D7 on +3.3V) are correctly detected in protection_devices. USB data line observations also correctly flag ESD protection present on D+ and D- nets.
- Q2 (2N7002, N-channel) has gate driven by PWR_CTRL from U3 (ESP32-C3), source to GND, and gate pull-down R12 (10K). The analyzer correctly classifies this as a level_shifter topology with gate_driver_ics=[U3] and gate_pulldown=R12.
- Two voltage dividers detected: R7/R8 (2.7K/10K, mid=PWR_SENS) for battery voltage sensing, and R13/R14 (10K/2.2K, mid=ADC, top=+VSW) for switched voltage monitoring. Both feed ESP32-C3 (U3) ADC inputs.
- BZ1 buzzer is connected via R16 (10K series resistor) to U4 (driver IC output). The analyzer correctly identifies direct_gpio_drive=true, driver_ic=U4, and series_resistor=R16. has_transistor_driver=false is correct since no discrete transistor drives BZ1.

### Incorrect
(none)

### Missed
- Q1 (AO3401A, P-channel MOSFET, SOT-23) has all nets unnamed (__unnamed_29/30/31), preventing the topology classifier from identifying it as a power switch in the battery circuit. load_type='other' is assigned. Since Q1 is a P-MOSFET in the battery path (connected to +BATT/+VSW area), it is likely a load switch. The analyzer should detect P-channel MOSFETs with battery-adjacent nets as power_switch topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001793: PCB footprint count 57 matches schematic component count; GND copper pour with 89 stitching vias detected across both layers; SMD-dominant board with most components on back side correctly reported

- **Status**: new
- **Analyzer**: pcb
- **Source**: vhario-espc3.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB has 57 footprints matching the 57 schematic components. The reference naming in the PCB differs for 3 switches (SW1→RST, SW3→PWR, SW4→PCCA using value-as-reference) but footprint count is correct.
- A GND zone spanning B.Cu and F.Cu with 89 stitching vias at 0.4 mm drill is correctly detected. Via density of 1.8 per cm² is reported.
- The PCB has 52 SMD components (smd_count=52) and 3 through-hole (tht_count=3). Front side has 7 footprints, back side has 50, consistent with a back-mounted SMD assembly design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
