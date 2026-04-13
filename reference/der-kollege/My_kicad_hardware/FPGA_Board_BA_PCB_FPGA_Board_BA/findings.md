# Findings: der-kollege/My_kicad_hardware / FPGA_Board_BA_PCB_FPGA_Board_BA

## FND-00001999: Component count of 558 and power rail detection are accurate; 72 UART buses falsely detected; involved devices are level shifters and connectors, not UART ICs; H-bridge (Q5/Q6) correctly detected; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_My_kicad_hardware_FPGA_Board_BA_PCB_FPGA_Board_BA.kicad_sch
- **Created**: 2026-03-24

### Correct
- 558 placed components across hierarchical sub-sheets (motor controller with Zynq7020 FPGA). Power rails +1V8, +3.3V, +5V, +5VA, +5VA_2, +5V_Zynq, GND, PWR_FLAG, Vin all correctly identified. Component breakdown (178 caps, 269 resistors, 47 ICs, 23 diodes, 18 connectors) consistent with this design.
- One H-bridge detected: Q5 (high-side MOSFET), Q6 (low-side MOSFET), with output net, power net, and gate control signals all correctly attributed. Consistent with motor controller topology.
- Five regulators detected: U8 (TPS61022, switching), U4 (LM70860RRXR, ic_with_internal_regulator, +5V_Zynq), U3 (LM5143, ic_with_internal_regulator), U48 and U9 (MCP1703AT-5002EDB, LDO, +5VA_2/+5VA). UUID-path input rails for hierarchical nets are expected and correct behavior.
- All 13 instances of B72590D50H160 (Siemens TVS/varistors for motor phase protection) listed in signal_analysis.protection_devices with type=diode.

### Incorrect
- bus_analysis.uart reports 72 buses with devices U2 (Zynq7020), U26/U29/U32/U38/U46 (SN74LXCH8T245RHLR 8-bit bidirectional bus transceivers), and BoxHeader_24pin connectors. Net names like Ph_A_Tx1_5V and Rx_Ph1 reference motor phase signals ("Ph" = phase), not UART channels. No UART-specific ICs (RS-485 drivers, MAX232, etc.) exist in the BOM. The UART heuristic fires on Tx/Rx substrings in net names without verifying the device type.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002000: PCB footprint count of 580 confirmed; 22 PCB-only footprints over schematic count

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_My_kicad_hardware_FPGA_Board_BA_PCB_FPGA_Board_BA.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 580 footprints (474 front, 106 back), 555 SMD + 10 THT. Delta of 22 over 558 schematic parts accounts for logos, test points, PCB-only items. 4-layer, 320x160mm, 4399 track segments, 1066 vias, fully routed. 22.9m total track length consistent with large industrial board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002001: Gerber set complete for a 4-layer board; all 11 layers and 2 drill files present

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_My_kicad_hardware_FPGA_Board_BA_exports_Gerbers
- **Created**: 2026-03-24

### Correct
- 11 gerber files + 2 drill files. All expected layers present (F.Cu, B.Cu, In1.Cu, In2.Cu, F/B Mask, Paste, SilkS, Edge.Cuts). completeness.complete=true from gbrjob. 320x160mm matches PCB. 1263 holes, 11278 flashes, 243211 draws consistent with large dense board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
