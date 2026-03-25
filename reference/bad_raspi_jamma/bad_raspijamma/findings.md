# Findings: bad_raspi_jamma / bad_raspijamma

## FND-00001849: Component counts and types are accurate for bad_raspi_jamma; I2C bus detected with missing pull-up resistors; RC low-pass filters on PWM audio paths correctly detected; pwr_flag_warnings incorrectl...

- **Status**: new
- **Analyzer**: schematic
- **Source**: bad_raspijamma.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- 39 total components, 23 resistors (R, RB, RG, RR prefix groups), 8 capacitors, 4 connectors, 3 ICs (MCP23017 x2, LM4952TS), 1 switch, 1 potentiometer — all verified against the .kicad_sch source. BOM correctly identifies U2 (LM4952TS/NOPB) as the only component with an MPN.
- I2C_SCL and I2C_SDA nets are correctly identified as I2C signals driven by U1 and U3 (both MCP23017), and has_pull_up=False is correct — the schematic explicitly notes 'No pullup on I2C' as one of its design errors.
- R3/C2/C4 and R4/C1/C3 form RC low-pass filters for PWM_LEFT and PWM_RIGHT audio signals. The analyzer detects 4 RC filter instances (two true low-pass and two RC-network pairs) which correctly reflects the two symmetric filter channels in the schematic.

### Incorrect
- The schematic contains 4 PWR_FLAG power symbols placed adjacent to +12V, +3.3V, +5V, and GND rails and connected to them by wires. The analyzer treats PWR_FLAG as its own isolated net (visible as 'PWR_FLAG' in power_rails) rather than recognizing it is wired to the adjacent power rail. This causes false positive warnings that +12V, +3.3V, +5V, and GND lack PWR_FLAG, when in fact all four rails are flagged.
  (pwr_flag_warnings)
- Nets B2..B7 form a 6-signal Blue bus, G2..G7 a 6-signal Green bus, and R2..R7 a 6-signal Red bus (GPIO outputs driving R-2R DAC ladders for JAMMA RGB video). The range field correctly shows e.g. 'B2..B7' but width=12 for each, which appears to count total pin-connections across all nets in the bus (6 nets × 2 pins each = 12) rather than the number of signal lines. Standard bus width should be 6.
  (bus_topology)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001850: Component counts, IC types, and transistor circuits correctly identified; MK1 (Microphone_Ultrasound) classified as 'fiducial' instead of a sensor/transducer type

- **Status**: new
- **Analyzer**: schematic
- **Source**: bat-detector.sch.json.json
- **Created**: 2026-03-24

### Correct
- 26 total components: 3 ICs (NE555, TL072, LM386), 12 resistors, 7 capacitors, 2 BC548 transistors, 1 speaker, 1 microphone/fiducial, 1 potentiometer. Transistor circuits for Q1 and Q2 are correctly detected with their base resistors and bias networks. RC filters (7 instances) around the ultrasound amplifier chain are accurate.

### Incorrect
- MK1 uses lib_id 'Device:Microphone_Ultrasound' and value 'Microphone_Ultrasound' — it is an ultrasonic transducer (microphone) used as the bat detector's sensor input. The analyzer classifies it as 'fiducial' which is incorrect; it should be classified as a sensor, transducer, or microphone type. This causes the component_types count to show fiducial=1 rather than the correct category.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: MK1 (Microphone_Ultrasound) classified as 'fiducial' instead of a sensor/transducer type

---

## FND-00001851: PCB analyzer correctly handles stub KiCad v4 dummy file with zero content

- **Status**: new
- **Analyzer**: pcb
- **Source**: bat-detector.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The bat-detector.kicad_pcb file contains only '(kicad_pcb (version 4) (host kicad "dummy file") )' — a one-line placeholder. The analyzer returns all zero statistics, empty footprint list, and no routing data, which accurately reflects the file's content. The silkscreen section correctly flags missing_board_name and missing_revision.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001852: Component count of 16 is correct including 4 non-BOM mounting holes; HX-2S-JH20 BMS protection IC (U2) not detected as a BMS system; multi_driver_nets false positive: U1 and U3 OUT- both on GND is ...

- **Status**: new
- **Analyzer**: schematic
- **Source**: battery_ups.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- 16 total_components matches the schematic: 2 batteries (BT1/BT2), 2 diodes (D1/D2), 1 fuse (F1), 4 mounting holes (H3-H6, in_bom=false), 3 connectors (J1/J2/J3), 1 switch (SW1), 3 ICs (U1/U2/U3). BOM correctly lists 12 components (excludes mounting holes). The split is verified against the source .kicad_sch.

### Incorrect
- connectivity_issues.multi_driver_nets flags GND as having two 'power_out' drivers (U1 pin 4 OUT- and U3 pin 4 OUT-). These are custom VoltageConverter modules (XL4015 step-down and a step-up module) where the OUT- pin is a power return/ground. Two power converters sharing the same GND return is completely normal and not a real conflict. The flag occurs because the custom symbols define OUT- as power_out type rather than power_in/passive.
  (connectivity_issues)

### Missed
- U2 uses lib_id 'MySymbols:HX-2S-JH20', value '~', and connects to BT1 (B-), BT1/BT2 midpoint (BM), BT2 (B+), a fuse (P+), and GND (P-) — a classic 2-cell lithium battery management/protection circuit topology. The bms_systems list is empty and protection_devices is also empty. The analyzer does not detect BMS ICs from custom/non-standard library names, and the generic value '~' provides no clue. This should be flagged as a BMS or protection device.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001853: PCB footprint counts, layer distribution, and board dimensions are accurate; Via-in-pad correctly detected for J3 battery tester connector

- **Status**: new
- **Analyzer**: pcb
- **Source**: battery_ups.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- footprint_count=16 (14 on F.Cu + 2 on B.Cu), tht_count=12 (real THT), exclude_from_pos_files=4 (mounting holes H3-H6). Board is 85.5×122.0mm matching the Edge.Cuts rect. 2 copper layers (F.Cu, B.Cu). 78 track segments, 2 vias, 1 GND zone. All verified against the source .kicad_pcb file.
- J3 uses a custom 'BattTester' footprint that places two through-hole vias (drill 0.5mm and 0.6mm) within the courtyard bounds of the connector pads. The analyzer correctly identifies both via-in-pad instances on pad 1 and pad 2 of J3, with same_net=true confirming they are intentionally connected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
