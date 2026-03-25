# Findings: Meshmerize-MicroMouse- / ArduinoNano_micro_mouse_v1-files_design_Ckt_PCB_files_Micro_mouse1

## FND-00000910: FPC-05F-12PH20 (FPC1) classified as 'fuse' instead of 'connector'; L293D motor driver (U1) not detected as a bridge/motor driver circuit

- **Status**: new
- **Analyzer**: schematic
- **Source**: ArduinoNano_micro_mouse_v2-files_micro_mouse_v2-pcb_micro_mouse_v2-pcb.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- FPC-05F-12PH20 is a 12-pin FPC/FFC flat cable connector. The analyzer matches 'FPC' prefix to fuse, but FPC stands for Flexible Printed Circuit connector. This causes it to appear in protection_devices as a 'fuse' protecting a net, which is completely wrong. Same bug appears in ESP32 schematic (FPC1 and FPC2). Should be 'connector' type.
  (signal_analysis)
- The L293D is a well-known quadruple half-H motor driver IC. It appears in v2, v3 prashant, and ESP32 schematics as motor controllers for the micromouse motors, but bridge_circuits is empty in all cases. The analyzer detects L293D as a generic IC but misses classifying it as a motor driver/bridge topology. This is a missed detector that would be valuable for this class of designs.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000911: Voltage regulators (LM7805, AMS1117-3.3), I2C bus, UART, decoupling cap analysis all correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: Esp32_micromouseEsp32_v1_PCB_micromouse3.0.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- LM7805 +12V->+5V and AMS1117-3.3 +7.5V->+3V3 regulators correctly identified with proper input/output rails. I2C SDA/SCL correctly flagged as missing pull-up resistors (has_pull_up: false). Dual UART nets detected. Decoupling analysis on both rails is accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000912: LM7805 regulator detected with correct VCC->+5V topology; decoupling cap warnings accurate

- **Status**: new
- **Analyzer**: schematic
- **Source**: ArduinoNano_micro_mouse_v1-files_design_Ckt_PCB_files_Micro_mouse1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U1 LM7805 correctly detected as LDO with input_rail=VCC, output_rail=+5V. Decoupling warnings for both Arduino Nano and LM7805 missing caps are legitimate (no bypass caps on VCC or +5V). PWR_FLAG warnings for VCC and GND are accurate—this design has a board-power connector but no PWR_FLAG symbols.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000913: routing_complete=True but routed_nets (30) is less than total_nets_with_pads (38)

- **Status**: new
- **Analyzer**: pcb
- **Source**: ArduinoNano_micro_mouse_v2-files_micro_mouse_v2-pcb_micro_mouse_v2-pcb.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In v2 PCB, total_nets_with_pads=38 but routed_nets=30, yet unrouted_count=0 and routing_complete=True. This same pattern appears in v3.0, v3.1, prashant PCBs (all show routed_nets < total_nets_with_pads with unrouted_count=0). The discrepancy suggests 'routed_nets' counts only nets with actual track segments while power/GND nets covered solely by copper zones are not counted — but the reporting is inconsistent and may mislead users into thinking 8 nets are partially unrouted.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000914: Missing board outline (no Edge.Cuts) correctly detected as board_width_mm=None

- **Status**: new
- **Analyzer**: pcb
- **Source**: ArduinoNano_micro_mouse_v3_files_micro_mouse_prashant_micro_mouse_prashant_micro_mouse_prashant.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The prashant PCB has edge_count=0 and bounding_box=None, which correctly reflects that no Edge.Cuts outline was found in the PCB file. The 28 footprints and routing data are correctly parsed.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000915: Alignment false positive: copper layers narrower than board edge is expected, not a gerber misalignment; Layer completeness, drill classification, board dimensions from gbrjob all correctly parsed

- **Status**: new
- **Analyzer**: gerber
- **Source**: ArduinoNano_micro_mouse_v3_files_micro_mouse_prashant_micro_mouse_prashant_.json
- **Created**: 2026-03-23

### Correct
- All 9 gerber layers correctly identified. Drill classification correctly separates vias (12x 0.8mm), component holes (98 PTH), and mounting holes (8 NPTH at 2.5/3.0mm). Board dimensions match the gbrjob (95.8x73.05mm). smd_ratio=0.0 correctly reflects an all-THT design (smd_apertures=0).

### Incorrect
- The analyzer flags 'Width varies by 48.5mm across copper/edge layers' as an alignment issue. B.Cu/F.Cu extent is 47.28mm wide while Edge.Cuts is 95.75mm. The gbrjob confirms the board is 95.8mm wide. However, copper traces not reaching board edges is completely normal—copper only runs where traces are placed. The alignment check incorrectly treats copper layer extents as board boundaries when the Edge.Cuts layer is the authoritative outline. This is a false positive that would need the alignment checker to use Edge.Cuts as the reference and only flag copper layers that fall outside it, not that are smaller than it.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
