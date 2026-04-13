# Findings: LaserTag/Hardware / Generic2PCB

## FND-00000584: Component counts, BOM, and voltage divider correctly extracted; BJT collector topology not flagged: all 3 NPN transistors (Q2/Q3/Q4) have collector on GND_IR rail; I2C bus observation flags SDA/SCL...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: WeaponPCB_WeaponPCB.sch.json
- **Created**: 2026-03-23

### Correct
- 34 components, 43 nets, 9 resistors, 4 transistors, 10 connectors all match the schematic. Voltage divider R7/R8 (100k/100k, +5V to GND, mid=VIN_monitor, ratio=0.5) correctly identified.

### Incorrect
- In this design VCC_IR is the supply and GND_IR is a switched/isolated ground (via Net-Tie). The BJTs sink current through their emitter to IR*_SINK nets, with collector tied to GND_IR. The analyzer reports collector_net='GND_IR' and emitter_is_ground=False correctly, but emits no observation about the non-standard topology (collector at ground potential). This inverted-sink topology should be flagged as unusual.
  (signal_analysis)
- SDA and SCL label nets connect U1's I2C pins to J1 (a repurposed USB connector with a design note: 'not following USB standard'). The design_observations report i2c_bus with 'has_pullup: False' for both lines — this is technically correct but misleading since pull-ups are expected to be on the external I2C device connected via J1, not on this PCB. No false positive per se, but the observation is noise for a connector-exposed bus.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000585: Multi-sheet parsing, RF chain, LDO regulator, SPI/I2C buses, and I2C level-shifter BSS138 MOSFETs all detected; BSS138 I2C level-shifter topology not recognized as such; DNP parts correctly identif...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MainPCB_MainPCB.sch.json
- **Created**: 2026-03-23

### Correct
- 4 sheets parsed correctly (59 components, 136 nets). MCP1825S LDO identified. ESP32+Si4463 RF chain detected. I2C bus on I2C_SCL/SDA with pull-ups R13/R15 to +3.3V correctly found. BSS138 MOSFETs (Q1/Q2) correctly identified as N-channel with source on +3.3V (level-shifter topology). Voltage divider R12/R9 for supply monitoring correctly extracted.
- dnp_parts=2, and R14/R16 have dnp:true in BOM. These are also included in gate_resistors for Q2/Q1 respectively with value 'DNP', which is accurate.

### Incorrect
- The design_observation 'regulator_caps' for U9 (MCP1825S) reports missing input cap on '__unnamed_72'. The net is unnamed because it connects VBAT through a diode (D4) and is a short junction net. The C8 and C10 capacitors on +BATT/VBAT cover this, but the net name resolution fails to associate them with this local net. This is a net-naming limitation, not a genuine missing cap.
  (signal_analysis)

### Missed
- Q1 and Q2 are BSS138 N-channel MOSFETs with source on +3.3V and drain on I2C_SCL_HV/I2C_SDA_HV — the classic bidirectional I2C level shifter circuit. The analyzer classifies them as generic transistor_circuits with load_type='transistor' but does not identify the level-shifter pattern. A level-shifter detector or note in design_observations would be valuable.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000586: Output file does not exist — analyzer was not run on this file

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Charger_Charger.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The file /home/aklofas/Projects/kicad-happy-testharness/repos/Hardware/Charger/Charger.kicad_sch does not exist in the Hardware repo checkout. The Hardware repo is a KiCad 5 lasertag project and contains no .kicad_sch files. The requested outputs for Charger, Debug, Morsern, Nightrider, and RGBLed were never generated.
  (signal_analysis)

### Suggestions
(none)

---
