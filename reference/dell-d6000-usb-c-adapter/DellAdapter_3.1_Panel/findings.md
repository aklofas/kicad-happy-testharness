# Findings: dell-d6000-usb-c-adapter / DellAdapter_3.1_Panel

## FND-00002311: TX1+/TX1-/RX1+/RX1-/TX2+/TX2-/RX2+/RX2- falsely detected as UART nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_dell-d6000-usb-c-adapter_DellAdapter_3.1.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- bus_analysis.uart contains 8 entries for nets named TX1+, TX1-, RX1+, RX1-, TX2+, TX2-, RX2+, RX2-. These are SuperSpeed USB differential pair names on a USB4/USB3 adapter (USB-C to USB-A/DisplayPort), not UART signals. The naming follows the USB-C connector specification (Txn+/Txn- are SuperSpeed transmit lanes). All entries have empty 'devices' arrays, confirming these are passthrough connector pins with no UART IC involved. The UART detector is triggering on TX/RX substrings in standard USB-C pin names.
  (bus_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002312: smd_count reported as 0 despite many SMD pads on USB-C connectors; Board height mismatch vs gerber: PCB reports 20.83mm but gerber reports 50.29mm

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_dell-d6000-usb-c-adapter_DellAdapter_3.1.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- statistics.smd_count is 0 and tht_count is 2, yet the PCB source file contains numerous 'smd' pad definitions — the USB-C connector J2 (GCT USB4151-GF-C_REVA) has all SMD pads. The analyzer is misclassifying footprints: the USB-C connector's 'smd' pads with a drill offset (used for board-edge contacts) may be confusing the footprint-type classifier into calling them through-hole or virtual.
  (statistics)

### Missed
- The PCB analyzer reports board_height_mm as 20.828, while the gerber analyzer reports board_dimensions.height_mm as 50.29 for the same design. The gerber measurement is based on edge_cuts_extents and is likely correct for the full panel. The PCB analyzer appears to derive dimensions from the bounding box of only part of the edge cuts geometry (24 edges), possibly due to parsing arcs or complex cutouts in the board outline incorrectly.
  (statistics)

### Suggestions
(none)

---

## FND-00002313: Gerber set is complete with all required layers and both drill files

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_dell-d6000-usb-c-adapter_DellAdapter3_2.json.json
- **Created**: 2026-03-24

### Correct
- completeness.complete is true, missing_required and missing_recommended are both empty, has_pth_drill and has_npth_drill are both true. All 9 standard layers (F.Cu, B.Cu, F/B.Mask, F/B.Paste, F/B.SilkS, Edge.Cuts) are present. The gerber output is a well-formed 2-layer PCB set.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
