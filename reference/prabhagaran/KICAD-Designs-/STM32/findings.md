# Findings: prabhagaran/KICAD-Designs- / STM32

## FND-00000668: STM32F103C8T6 + AMS1117-3.3 LDO correctly detected with I2C pull-ups, UART, and SWD; USB ESD: differential_pairs reports has_esd=true crediting U2 (MCU) as ESD protection device; assembly_complexit...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Regulator topology (LDO, 3.3V output), I2C2 SCL/SDA with 1K5 pull-ups to +3.3V, UART1 TX/RX, and SWD debug connector J3 are all correctly identified.
- vbus_esd_protection: fail is correct — there is no dedicated VBUS ESD diode or TVS. The 1K5 D+ series resistor (R5) is found but D- has no series resistor (R2/R3 are I2C pull-ups, not USB), which is correctly marked as informational.
- U1 (AMS1117-3.3) with VBUS input and +3.3V output, and the +3.3VA analog domain via FB1 ferrite bead, are all correctly detected.

### Incorrect
- The STM32F103 MCU (U2) shares the USB D+/D- nets but is not an ESD protection component. The analyzer incorrectly treats any shared IC on the differential pair net as an ESD device. The usb_compliance section correctly flags vbus_esd_protection as 'fail', creating an internal inconsistency — differential_pairs says ESD is present, usb_compliance says it fails.
  (signal_analysis)
- The schematic analyzer classifies all 32 components as SMD with 0 THT. However, J1-J3 (Conn_01x04_Male, PinHeader_1x04_P2.54mm_Vertical) are standard THT pin headers, and the USB Micro-B connector (J4) has THT retention pins. This is a systematic issue where schematic-level analysis cannot determine THT/SMD without footprint inspection, and the 0 THT result is incorrect.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000669: Board dimensions, footprint count, layer count, via count all correctly extracted; B.Cu layer classified as 'power' type instead of 'signal' — it carries signal routing not just ground/power planes

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 44x35.5mm board with rounded corners (4 arcs + 4 lines), 32 footprints all on F.Cu, 2-layer design, 21 vias, 4 zones, fully routed (0 unrouted nets) — all consistent with the schematic.

### Incorrect
- The PCB B.Cu layer has type='power' in the layer listing. Looking at the board's net list, B.Cu carries 2227 draw segments and only a GND zone — but the layer definition in the KiCad file assigns it a type. With 220 track segments and 21 vias in a 2-layer board, B.Cu is used for signal routing too. This may be a literal read of the KiCad layer attribute rather than a misclassification by the analyzer.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000670: Gerber alignment flagged as 'aligned: false' due to normal copper/paste layer size differences relative to edge cuts; Drill classification puts the 4x 2.2mm M2 mounting holes in 'component_holes' r...

- **Status**: new
- **Analyzer**: gerber
- **Source**: manufacturing.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer reports misalignment: copper layers 43.4x34.9mm vs edge cuts 44x35.5mm (3.1mm width, 3.7mm height variance). This is expected behavior — copper/paste/mask layers are always inset from edge cuts because tracks and pads don't extend to the board edge. Reporting this as a misalignment issue is a false positive. The KLOR gerber correctly reports aligned=true despite similar relative size differences.
  (signal_analysis)
- The 4 NPTH 2.2mm holes (T7, used for H1-H4 MountingHole_2.2mm_M2 footprints) are classified under component_holes (count=20) with mounting_holes count=0. These should clearly be mounting holes. The X2-attribute based classification (classification_method='x2_attributes') appears to not assign mounting_holes correctly for NPTH holes that lack explicit X2 attributes marking them as mountings.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
