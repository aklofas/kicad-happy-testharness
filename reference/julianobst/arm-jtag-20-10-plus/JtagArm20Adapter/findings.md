# Findings: arm-jtag-20-10-plus / JtagArm20Adapter

## FND-00001946: All 6 components correctly identified: 4 connectors and 2 solder jumpers; All 11 JTAG/SWD signal nets correctly parsed from KiCad 5 legacy format; No signal_analysis detections despite this being a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: JtagArm20Adapter.sch.json
- **Created**: 2026-03-24

### Correct
- The KiCad 5 legacy schematic is correctly parsed with 6 components: J1 (2x5 SMD header), J2 (2x10 SMD header), J3 (1x6 THT header), J4 (2x10 horizontal socket), JP1 and JP2 (SolderJumper_2_Open). BOM and component types are correct.
- The 11 nets (VTref, TDI, SWDIO\TMS, SWDCLK\TCK, SWO\TDO, RESET, GND, DBGRQ, RTCK, DBGACK, nTRST) are all correctly identified, with appropriate net_classification (debug, clock, control, ground, signal). The backslash-escaped net names are handled correctly.

### Incorrect
(none)

### Missed
- All signal_analysis arrays are empty. The design is a JTAG/SWD 20-pin to 10-pin adapter — the nets SWDIO\TMS, SWDCLK\TCK, SWO\TDO, TDI, RESET, nTRST are JTAG/SWD signals but no detection of any debug interface is made. While this is a passive adapter (no active components), it would be useful for the analyzer to recognize it as a debug interface adapter in the design_observations.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001947: PCB statistics correct: 6 footprints, 11 nets, 2-layer board with GND fills; DFM tier correctly flagged as 'challenging' due to 0.09mm tracks below advanced process minimum; Edge clearance warnings...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: JtagArm20Adapter.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB has 6 footprints matching the schematic (J1-J4, JP1, JP2), 11 nets, 83 track segments, 52 vias, 2 GND fill zones (F.Cu and B.Cu), and board dimensions 22.86 x 30.48mm. Routing is complete.
- The design uses 0.09mm tracks (net class Default trace_width) which is below the 0.1mm advanced process minimum. The DFM analysis correctly identifies this as 'challenging' with one violation. The VTref net class correctly uses wider 0.508mm traces for the power reference line.
- J4 has edge_clearance_mm=-9.24 (its courtyard extends well beyond the board edge due to the horizontal socket connector body hanging off-board), and J1/J2 SMD headers also violate edge clearance. These are correct observations for a compact adapter PCB where the female socket body is intentionally designed to extend beyond the PCB edge.

### Incorrect
- The silkscreen documentation_warnings flags J1, J2, J3, J4 as connectors lacking silkscreen labels. However, J3's silkscreen clearly has individual signal name labels (VTref, SWDCLK, GND, SWDIO, RST, SWO visible in the PCB silkscreen text list). The warning about missing connector labels is partially a false positive for J3 which has pin-by-pin signal labels. The warning should not include J3.
  (silkscreen)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001948: Complete 2-layer gerber set with 7 layers and 1 drill file, all expected layers present; Drill classification correctly separates 52 vias from 26 component holes; F.SilkS layer extent (31.68mm wide...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: production_files.json
- **Created**: 2026-03-24

### Correct
- All expected layers for a 2-layer board are present (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts) plus one PTH drill file. The completeness check passes with no missing or extra layers.
- The 78 total holes are correctly split: 52 vias (13x 0.2mm, 39x 0.4mm) and 26 component holes (1.0mm THT holes for J3 and J4 through-hole connectors). Via counts match the PCB analyzer output exactly.
- The .gbrjob file reports 22.91 x 30.53mm which matches the board_outline bounding box from the PCB analyzer (22.86 x 30.48mm, with small rounding difference from the job file). The layer count (2), thickness (1.6mm), and FR4 material are all correct.

### Incorrect
- The F.SilkS layer has width=31.68mm vs all other layers at 22.86mm — an 8.82mm overrun. This is caused by the silkscreen text 'JTAG/SWD Cortex' and signal labels extending outside the board edge. The gerber analyzer reports aligned=true with no issues, but this overshoot means silkscreen will print outside the PCB outline. The alignment check should flag F.SilkS as having an outlier extent compared to the copper layers.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
