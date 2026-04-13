# Findings: Jana-Marie/OtterControlNG / AluPCB

## FND-00001001: CAN bus, regulators, crystal, LED chain, and protection devices all correctly detected

- **Status**: new
- **Analyzer**: schematic
- **Source**: STM32G431_STM32G431.sch
- **Created**: 2026-03-23

### Correct
- bus_analysis.can correctly identifies CANTX/CANRX with STM32G431 (U1) and CAN transceiver (U2). power_regulators finds XL7015 boost, ACT4088 switcher, and AP2204R-3.3 LDO. Crystal Y1 (8MHz) with load caps detected. SK6812 addressable LED chain found. ESD protection (USBLC6-4) detected. UART and RS485 found in bus_analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001002: PAC5523 BLDC motor controller IC not identified as motor driver; bridge_circuits and motor_drivers both empty

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PAC5523_PAC5523.sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The PAC5523 is an integrated 3-phase BLDC motor controller with built-in gate drivers. DRH0-5 (high-side drive) and DRL0-2 (low-side drive) gate signals are present, as well as IUH/IUL/IVH/IVL/IWH/IWL current sense nets and VP bus net. The analyzer returned empty bridge_circuits and motor_drivers despite clear BLDC topology. This is a missed detection for integrated motor controller ICs that drive external gate drive signals but do not have discrete MOSFETs in the same schematic sheet.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001003: Empty hierarchical block sub-sheet correctly produces zero-component output

- **Status**: new
- **Analyzer**: schematic
- **Source**: STM32G431_IC.sch
- **Created**: 2026-03-23

### Correct
- IC.sch is a KiCad 5 hierarchical sheet symbol file with no real components (it only defines the sheet interface pins, not the actual schematic content). The analyzer correctly returns 0 components and empty analysis for it. Same pattern holds for PAC5523/IC.sch.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001004: PCB analysis is accurate: 4-layer, routing complete, power regulators and thermal vias identified; 50 courtyard overlaps on a 60x44mm board is implausibly high — likely false positives from KiCad 5...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32G431_STM32G431.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Connectivity correctly shows 0 unrouted nets. Thermal pad via analysis for STM32G431 QFN (9 vias vs recommended 14-22) is a valid real-world finding. DFM tier standard with no violations. CAN/HALL/motor nets correctly appear in net_classes. Tombstoning risk on C20 (0402 with thermal asymmetry) is plausible.

### Incorrect
- Both STM32G431 and PAC5523 boards (identical physical size, KiCad 5.x file_version 20171130) each report exactly 50 courtyard overlaps. The KiCad 5 PCB format stores courtyard polygons in module-local coordinates; if the analyzer is not transforming courtyard vertices by component rotation/position, it will incorrectly compute overlap. J2 overlapping U2 by 16.2mm² and U1 overlapping Y1 by 15.0mm² on a production PCB would have been caught by KiCad's own DRC — these are almost certainly parsing artifacts.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001005: AluPCB (aluminum/IMS single-sided board) incorrectly flagged as incomplete for missing B.Cu and B.Mask

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- AluPCB is a deliberately single-sided aluminum (IMS) PCB: 1 copper layer (F.Cu only), 0 back-side components, no B.Cu gerber. The analyzer reports complete=false with missing_required=['B.Cu','B.Mask']. This is a false positive — single-sided IMS boards legitimately have no back copper. The completeness checker should not require B.Cu when the PCB has only 1 copper layer.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001006: STM32G431 4-layer gerber set correctly identified as complete with all layers aligned

- **Status**: new
- **Analyzer**: gerber
- **Source**: STM32G431_gerber
- **Created**: 2026-03-23

### Correct
- 11 gerber files + 2 drill files detected, all 4 copper layers plus mask/paste/silkscreen/edge present, aligned, complete=true. Generator correctly identified as KiCad Pcbnew 5.1.2.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001007: PAC5523 out/ gerber directory correctly analyzed as 4-layer complete set

- **Status**: new
- **Analyzer**: gerber
- **Source**: PAC5523_out
- **Created**: 2026-03-23

### Correct
- Both PAC5523/gerber and PAC5523/out report complete=true with all 4 copper layers. Generator KiCad 5.1.2 correctly detected. This validates the analyzer handles multiple gerber output directories in the same repo correctly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
