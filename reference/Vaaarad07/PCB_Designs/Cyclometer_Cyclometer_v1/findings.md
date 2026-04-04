# Findings: PCB_Designs / Cyclometer_Cyclometer_v1

## FND-00001042: XBee module (XB24CDMPIT-001) not detected as RF chain; STM32F407 microcontroller misclassified as a power regulator; MORNSUN isolated DC-DC (U7), I2C buses with pullups, and CAN transceiver (MCP255...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32F407_MVCU_MVCU_F407.kicad_sch
- **Created**: 2026-03-23

### Correct
- design_observations correctly identifies I2C buses on I2C3_SCL/I2C_SDA with pullups (R8, R7 to +3.3V) and I2C1 without pullups. MCP2551 CAN transceiver captured in subcircuits. AMS1117 regulator caps observation correctly flags missing caps.

### Incorrect
- U2 STM32F407VGTx is listed in power_regulators with topology 'ic_with_internal_regulator'. While it has an internal regulator, it is a microcontroller first. Including it in the power_regulators array alongside AMS1117 LDOs is misleading and inflates the regulator count.
  (signal_analysis)

### Missed
- U9 XB24CDMPIT-001 is an 802.15.4 RF transceiver module. The rf_chains and rf_matching arrays are both empty. The analyzer has subcircuits for this IC but fails to classify it as an RF device, missing an important design feature.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001043: TP4056 LiPo charger not detected as a BMS/charger circuit

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Cyclometer_v1.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- U4 TP4056 is a single-cell Li-Ion battery charger. The bms_systems array is empty. This is a distinct power management circuit that should be flagged — it controls charge current and has PROG pin for charge rate setting.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001044: AMS1117-3.3 output rail reported as unnamed net instead of +3.3V

- **Status**: new
- **Analyzer**: schematic
- **Source**: STM32F103_InverterVCU_inverter_vcu.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The power_regulators entry for U4 AMS1117-3.3 shows output_rail as '__unnamed_3' when the rail should resolve to +3.3V (listed in power_rails). This suggests the analyzer fails to connect the unnamed net to its named power symbol in this schematic, producing a less useful output.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001045: CAN transceiver (MCP2551), LM7805+AMS1117 regulator chain, voltage divider, and RC filter all correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: STM32F103_VCU_VCU.kicad_sch
- **Created**: 2026-03-23

### Correct
- Subcircuits identify MCP2551 CAN transceiver and ACS712 current sensor. signal_analysis correctly finds voltage divider (R14/R15 on +5V→volt_measure), RC filter (R1/C1 for RESET), and regulator chain. IC analysis is thorough.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001046: 9 courtyard overlaps correctly detected on this student-designed STM32 dev board

- **Status**: new
- **Analyzer**: pcb
- **Source**: STM32F103_board_f103_V2.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Overlaps between connectors (J9/J11: 81mm², J8/J5: 27.4mm²) and Y1/SW1 (21.3mm²) are real placement issues. DFM tier 'standard' and dfm metrics look reasonable for a 2-layer board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001047: Thermal pad on U3 detected with nearby via count; GND pour across B.Cu and F.Cu correctly analyzed

- **Status**: new
- **Analyzer**: pcb
- **Source**: RP2040_Audio_player.kicad_pcb
- **Created**: 2026-03-23

### Correct
- U3 thermal pad (pad 57, 10.24mm²) with 2 thermal vias is correctly identified. Zone stitching shows GND across both layers with 31 vias. The 22 courtyard overlaps suggest a densely packed board worth flagging.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001048: Gerber set with only F.Cu for a 2-layer board with 45 vias reported as 'complete'

- **Status**: new
- **Analyzer**: gerber
- **Source**: STM32F103_VCU
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The .gbrjob only lists VCU-F_Cu.gbr as expected (one layer). The analyzer trusts the gbrjob definition of 'expected', so complete=True. However, the PCB has 2 copper layers (B.Cu+F.Cu), 45 vias, and 25 THT pads — none of which have drill files. Missing B.Cu and drill files should be flagged as an incomplete export, not reported as complete.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
