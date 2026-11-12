# Findings: siderakb/ergo-snm-keyboard / ErgoSNM_Keyboard_rev2_plate_ergosnm_plate

## FND-00002193: Keyboard switch plate PCB (mechanical only, no copper) correctly analyzed as zero-net board

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: ErgoSNM_Keyboard_rev2_plate_ergosnm_plate.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The rev2 plate PCB is a pure mechanical switch plate with 11 footprints (switch cutout shapes and mounting holes), zero copper layers used, zero tracks, zero vias, and zero nets. The analyzer correctly reports all these as zero and routing_complete=true (vacuously, no nets to route). Board dimensions 116.25x111.5mm are correctly computed from the edge cuts. The DFM board_size violation is correctly triggered. This demonstrates the analyzer handles purely mechanical PCBs without false errors.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
