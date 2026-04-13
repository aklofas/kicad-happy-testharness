# Findings: mlab-modules/BP02 / hw_sch_pcb_BP02

## FND-00000393: rf_matching detector fires 13 times on a pure bandpass filter — all false positives; 5 parallel LC resonators (shunt tank circuits) not detected in lc_filters; Component counts, net count, BOM, and...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_BP02.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic contains exactly 38 components (13 capacitors, 19 inductors, 2 SATA7 connectors, 4 mounting holes), 27 nets, 111 wires, and 14 unique BOM line items. All of these match the analyzer output precisely. The 4 differential pairs (3rd_order_in P/N, 3rd_order_in N, 3rd_order_out P/N, 2rd_order_out P/N, 2rd_order_in P/N) are correctly identified. The component type classification (capacitor/inductor/connector/other) is accurate throughout.

### Incorrect
- The schematic is titled 'Universal symmetric RF filter' and is a differential multi-order LC bandpass filter with no antenna or antenna feed point. The rf_matching detector incorrectly identifies every capacitor in the filter (C1–C13) as an 'antenna' component in a matching network topology. None of these capacitors are antennas; they are all series/shunt filter elements in a ladder/lattice bandpass filter connected between SATA7 differential connectors J1 and J2. The 13 rf_matching entries should all be absent.
  (signal_analysis)

### Missed
- The lc_filters detector only pairs components that share exactly one net (series connection). In this filter, five L-C pairs are wired in parallel (both terminals of the inductor and capacitor connect to the same two nodes): L11/C7, L5/C5, L17/C9, L12/C8, and L6/C6. Because each such pair shares TWO nets rather than one, the detector misses them entirely. These are legitimate LC resonators (shunt parallel tank circuits) forming the transmission zeros of the elliptic/Chebyshev filter. The current lc_filters list has 28 entries; it should have 33 (5 additional parallel LC pairs).
  (signal_analysis)

### Suggestions
(none)

---
