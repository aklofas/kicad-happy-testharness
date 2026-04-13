# Findings: perehinik/Logic_Analyzer_PCB / Project_GND_PCB

## FND-00000831: JTAG interface (TCK, TMS, TDI_FPGA, TDO_FPGA) not detected in bus_analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Project_FPGA_Config.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- FPGA_Config.sch and LogAn.sch contain clear JTAG net names (TCK, TMS, TDI_FPGA, TDO_FPGA) used for FPGA programming/debugging. The bus_analysis output has no 'jtag' key at all, and the FPGA_Config output shows zero items across all bus types. This is a missed JTAG bus detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000832: DDR3 memory interface (MT41K128M16JT, IC301) not detected in memory_interfaces

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Project_DDR3.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- DDR3.sch contains IC301 (MT41K128M16JT-125K FBGA96 DDR3 SDRAM) with a full DDR3 bus (DDR3_CK_P/N, DDR3_DQS0/1_P/N, DDR3_A[0..14], DDR3_nRAS/nCAS/nWE). The LogAn.sch.json output reports memory_interfaces: 0 items. The differential pairs for DDR3_CK and DDR3_DQS are correctly detected, but the memory interface itself is not recognized.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000833: Power regulators (ADP2164 x2, ADP5052), inductors, and multi-rail detection all correct

- **Status**: new
- **Analyzer**: schematic
- **Source**: Project_Power_supply.sch.json
- **Created**: 2026-03-23

### Correct
- Power_supply.sch has ADP2164 (buck) x2, ADP5052 (multi-output), and MAX5417 (digital pot for adjustable rail). The output correctly identifies 3 power regulator instances with switching topology, 6 inductors, correct rail names (VCC_2V5, VCC_ADJ, VREG), and I2C bus on TRIM_SDA/SCL. The missing MPN list is complete and accurate (no MPNs were filled in the source).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000834: 6-layer PCB correctly identified with accurate DFM tier, unrouted net, and board dimensions

- **Status**: new
- **Analyzer**: pcb
- **Source**: Project_LogAn.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- PCB analyzer correctly identifies 6 copper layers (F.Cu, In1-In4.Cu, B.Cu), 366 footprints, 1 unrouted net (Net-(J103-Pad1)), DFM tier 'advanced' due to 0.105mm tracks, board 74.94x52.0mm. The routing_complete:false and the specific unrouted net are accurate. Thermal analysis identifies GND zone stitching across 4 layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000835: 6-layer gerber set correctly parsed with all layers identified and alignment verified

- **Status**: new
- **Analyzer**: gerber
- **Source**: Project_GERBER.json
- **Created**: 2026-03-23

### Correct
- Gerber analyzer correctly identifies all 13 functional layers (6 copper + mask/paste/silk + drill files), layer_count:6, board dimensions 74.94x52.0mm matching PCB. All copper layer x2 attributes parsed. The 'layer_function' field shows '?' for non-copper layers (CrtYd, Fab, etc.) but this is a minor display issue — the layer_type field is correctly populated for copper/mask/paste/silk layers.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000836: GND_PCB 2-layer gerber correctly flagged incomplete (only NPTH drill, no PTH)

- **Status**: new
- **Analyzer**: gerber
- **Source**: Project_GND_PCB_GERBER.json
- **Created**: 2026-03-23

### Correct
- The GND_PCB is a simple 2-layer ground plane board with only NPTH mounting holes (no plated through-holes). The analyzer correctly reports complete:false with has_pth_drill:false. This is an accurate representation of the actual gerber set contents.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
