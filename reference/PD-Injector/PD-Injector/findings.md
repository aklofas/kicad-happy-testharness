# Findings: PD-Injector / PD-Injector

## FND-00001058: USB SuperSpeed lanes (TX1+/TX1-/TX2+/TX2-/RX1+/RX1-/RX2+/RX2-) falsely detected as UART nets; MK1 (Mechanical:Mounting_Hole_PAD) classified as 'fiducial' instead of 'mechanical' or 'other'; USB-C d...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PD-Injector.sch.json
- **Created**: 2026-03-23

### Correct
- All 5 USB differential pairs identified. ESD protection correctly reported as absent (has_esd=False) — the board is a pass-through injector with no ESD protection components (only two CC resistors R1/R2).

### Incorrect
- The bus_analysis UART detector matches net names containing TX/RX patterns and reports 8 empty UART-like nets. These are USB 3.x SuperSpeed differential pairs routed through a USB-C pass-through board, not UART signals. This is a false positive from name-based UART detection without semantic validation.
  (signal_analysis)
- MK1 uses footprint Mounting_Holes:MountingHole_3.2mm_M3_Pad_Via and lib_id Mechanical:Mounting_Hole_PAD. The BOM type field shows 'fiducial' which is incorrect — this is an M3 mounting hole with a grounded pad, not a fiducial marker. The component type classifier is not recognizing Mechanical: library prefix correctly.
  (signal_analysis)

### Missed
- The PCB has 34 nets (J1/J2/P1 USB-C connectors have individual pad nets like J1-PadA2 etc.) while the schematic shows only 17. The schematic parser is not flagging this discrepancy. A cross-check observation would be useful here since the extra PCB nets represent unconnected/floating pads on the USB-C connectors.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001059: PCB zone stitching detected: GND and VBUS copper pours on both layers with via stitching

- **Status**: new
- **Analyzer**: pcb
- **Source**: PD-Injector.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Zone analysis correctly identifies GND pour (780mm², 27 stitching vias, 3.5/cm²) and VBUS pour (137mm², 16 vias, 11.6/cm²). Both on F.Cu and B.Cu. Compact USB-C board (16.9×25mm) correctly measured.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001060: Gerber layers complete (9 files including F.Paste), board dimensions correct from edge cuts; via_apertures=0 in pad_summary despite 56 drilled vias present in the design

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-23

### Correct
- No .gbrjob file so board dimensions derived from Edge.Cuts extents (16.91×25.0mm), matching PCB output. All copper layers have consistent extents. Drill classification uses diameter heuristic (no X2 data): 56 vias, 8 component holes, 1 mounting hole correctly separated.

### Incorrect
- pad_summary reports via_apertures=0 because these older gerbers (KiCad 6.0.0-rc1-dev) lack X2 aperture function attributes needed to distinguish via pads from component pads in copper layers. The fallback smd_source is 'paste_layer_flashes' which doesn't count via apertures. Via count is correct in drill_classification (56 vias). The pad_summary via_apertures field is misleading/zero when X2 data is absent.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
