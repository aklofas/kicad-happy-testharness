# Findings: SPIKExCM4 / rpi-cm4-carrier__autosave-rpi-cm4-carrier

## FND-00001320: Empty/stub schematic correctly produces zero-component output

- **Status**: new
- **Analyzer**: schematic
- **Source**: PSUs.kicad_sch
- **Created**: 2026-03-24

### Correct
- PSUs.kicad_sch is a stub file with no placed components (only a uuid and paper size). The analyzer correctly reports 0 components, 0 nets, and empty signal analysis. No false positives.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001321: Power regulator detection correct for TPS61235P boost and BQ25616 charger; MPN cross-reference data copied incorrectly across resistors with different values

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: psu.kicad_sch
- **Created**: 2026-03-24

### Correct
- Correctly identifies U4 (TPS61235PRWLR) as a switching boost regulator with L1 and U5 (BQ25616RTWT) as a charger IC. CR1 (SMBJ5.0A-TR) correctly identified as TVS protection on VBUS. Component counts (32 total, 2 IC, 2 inductor) look accurate.

### Incorrect
- R10 (value '1M', 1 megohm) has DigiKey PN '311-1.00KHRCT-ND' and MPN 'RC0603FR-071KL' which are 1K parts. R12 (150 ohm), R13 (510 ohm), R14/R15 (1k) all share the same DigiKey PN '311-5.10KHRCT-ND' and MPN 'RC0603FR-075K1L' (a 5.1K part). The analyzer faithfully transcribes these values from the schematic — the data is wrong in the source, but the analyzer does not flag these MPN/value mismatches as warnings.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001322: USB mux (FSUSB42MUX) and USB Micro-B connectors correctly parsed

- **Status**: new
- **Analyzer**: schematic
- **Source**: usb.kicad_sch
- **Created**: 2026-03-24

### Correct
- 13 components correctly identified (2 connectors, 1 IC, 2 resistors, 8 capacitors). FSUSB42MUX classified as 'ic' correctly. All missing MPNs flagged appropriately.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001323: MIPI CSI differential pairs on CM4 not detected as differential pairs or MIPI interfaces

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: cm4-high-speed.kicad_sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The cm4-high-speed sheet carries CAM0/CAM1 MIPI CSI lanes (CAM0_C_N/P, CAM0_D0_N/P, CAM1_C_N/P, CAM1_D0-D3 N/P) visible in the PCB net list. The schematic analyzer reports 0 differential pairs and no memory/high-speed interfaces for this sheet. These are driven from Module1 (CM4) with hierarchical labels only, so the local topology lacks enough context, but the missed detection is worth noting.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001324: 4-layer PCB with CM4 module correctly parsed; all 64 footprints on front side

- **Status**: new
- **Analyzer**: pcb
- **Source**: rpi-cm4-carrier.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Correctly identifies 4 copper layers, 64 footprints all on front (consistent with CM4 design), 252 vias, 184 nets, routing complete. The 'REF**' placeholder footprint is included in component list as expected. Net analysis correctly labels named vs unnamed nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001325: 4-layer gerber set parsed completely with correct layer completeness

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers_rpi-cm4-carrier-spike-rev2
- **Created**: 2026-03-24

### Correct
- All 11 expected layers found (F/B Cu, F/B Mask, F/B Paste, F/B SilkS, In1/In2 Cu, Edge.Cuts), drill file with 275 holes (252 vias + 19 component + 4 mounting). Board dimensions match PCB file (52.38x84.35mm). Fab layers correctly classified as 'unknown' (not assembly layers).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001326: Rev3 gerber set identical structure to rev2 — both correctly parsed

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerbers_rpi-cm4-carrier-spike-rev3
- **Created**: 2026-03-24

### Correct
- Rev2 and rev3 gerbers are identical in structure and counts (same generator, same layer set, same totals). Both parse cleanly with complete=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
