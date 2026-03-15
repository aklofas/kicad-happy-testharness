# Findings: OpenCAPI-to-PCIe / OpenCAPI-to-PCIe

## FND-00000024: 32 PCIe Rx/Tx differential lanes falsely classified as UART signals due to net name pattern matching on "Rx"/"Tx"

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OpenCAPI-to-PCIe.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- All 32 Rx/Tx PCIe differential nets classified as UART. These are multi-gigabit serial lanes, not UART.
  (design_analysis.net_classification)

### Missed
(none)

### Suggestions
- UART detector should verify presence of UART transceiver IC, not just pattern-match on Rx/Tx net names

---
