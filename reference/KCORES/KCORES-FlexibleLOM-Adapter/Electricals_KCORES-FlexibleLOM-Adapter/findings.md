# Findings: KCORES/KCORES-FlexibleLOM-Adapter / Electricals_KCORES-FlexibleLOM-Adapter

## FND-00000658: 34 UART false positives: SerDes RX0_P/N through RX7_P/N and TX0_P/N through TX7_P/N all flagged as UART; Differential pairs correctly detected: 17 pairs (RX0..7 P/N, TX0..7 P/N, NCSI pair) between ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Electricals_KCORES-FlexibleLOM-Adapter_KCORES-FlexibleLOM-Adapter.sch.json
- **Created**: 2026-03-23

### Correct
- All differential pairs correctly identified with shared ICs J1 and J2. has_esd=false correctly noted (no ESD protection on SerDes lanes in this simple adapter). 5 components total (2 connectors + logo + 2 mounting holes) and 67 nets correctly counted.

### Incorrect
- This is a PCIe x8 to HPE FlexibleLOM adapter with 8 differential SerDes lanes (RX0..7 P/N, TX0..7 P/N = 32 nets) plus NCSI_RX0/RX1. All 34 are misidentified as UART by the bus detector. The differential_pairs detector correctly identifies them as differential pairs. The UART detector must be excluding differential pairs (nets ending in _P/_N) from UART classification.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000659: PCB statistics (6 footprints, 2-layer, 96.3x25.75mm, 188 vias, 610 track segments, 4 zones, routing complete) correctly extracted; Edge connector clearance warnings for J1 (-5.0mm) and J2 (0.0mm) a...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Electricals_KCORES-FlexibleLOM-Adapter_KCORES-FlexibleLOM-Adapter.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Via size distribution (173× 0.6/0.3mm + 15× 0.7/0.3mm) and fanout pattern for J1 (98-pad PCIe edge connector, 107 fanout vias) and J2 (100-pad FlexibleLOM, 18 vias) all correctly reported. Track widths (0.208mm diff pairs, 0.7mm wide traces, 2.7mm power traces) correctly captured.
- J1 (PCIe x8) is a card-edge connector with fingers extending beyond board edge (center at y=150.0, board bottom at 148.95mm). J2 (HPE FlexibleLOM straddle-mount) sits at the exact board top edge (y=123.2mm). Both are correct for this connector adapter design; the analyzer flags but does not misclassify them.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
