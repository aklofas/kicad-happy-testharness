# Findings: tiacsys/ecad-coffeecaller / coffeecaller

## FND-00002346: KEY1 (TS-1003S-07026 tactile switch) misclassified as type 'relay'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ecad-coffeecaller_in_output.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- KEY1 uses lib_id 'EASYEDA:DTSM-24N-V-S-T_R' and value 'TS-1003S-07026'. The datasheet URL explicitly includes 'Tactile-Switches' in the LCSC product path, confirming it is a tactile switch. The analyzer maps this to type 'relay' — likely because the EASYEDA lib symbol name or footprint path triggered the relay heuristic. It should be classified as type 'switch'. This also inflates component_types.relay (1) and deflates switch counts.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002347: Q2 transistor circuit gate_driver_ics list incorrectly includes regulator U4 and sensor U5; I2C bus between nRF52840 (U1), SHT40 sensor (U5), and Qwiic connector (X1) not detected; WS2812 addressab...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_ecad-coffeecaller_coffeecaller.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies D1-D4 as a WS2812E-V5 chain of length 4, with data_in_net '__unnamed_35', protocol 'single-wire (WS2812)', and estimated current 240mA (4 × 60mA). The associated level-shifter MOSFET Q2 and data resistor R15 (820R) are also correctly linked.

### Incorrect
- The transistor circuit analysis for Q2 (2N7002 level shifter) shows gate_net as '+3V3' (correct — this is a source-follower level shifter with gate tied to supply). However, gate_driver_ics lists U4 (XC6206P332MR LDO regulator) and U5 (SHT40-CD1B-R3 humidity sensor) multiple times as gate drivers, simply because they are connected to the +3V3 rail. These are power supply and sensor ICs, not gate drivers. Only U1 (nRF52840) is a plausible signal driver here, and even that interpretation is debatable since the gate is statically biased.
  (signal_analysis)

### Missed
- The schematic has a clear I2C bus: nets SDA_qwIIC and SCL_qwIIC connect U1 (nRF52840, pins P0.20/P0.24), U5 (SHT40-CD1B-R3, pins SDA/SCL), and X1 (Qwiic connector). Pull-up resistors R12 and R13 are on these nets. The analyzer populates the nets and bus_topology.detected_bus_signals with prefixes like 'SW', 'LD', 'NFC', 'Servo', 'XC' but does not detect or report an I2C bus in signal_analysis. There is no i2c_buses key in signal_analysis at all.
  (signal_analysis)

### Suggestions
(none)

---
