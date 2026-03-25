# Findings: KCORES-CSPS-to-ATX-Converter / Electrical_KCORES CSPS to ATX Converter_KCORES CSPS to ATX Converter

## FND-00000656: UART false positives: ATX_PSON and ATX_PWOK flagged as UART nets; Mini560 DC-DC regulators (U1, U2, U3) not detected as power_regulators; Voltage divider R2/R3 (22K/3.3K) on +12V→~PSON input correc...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Electrical_KCORES CSPS to ATX Converter_KCORES CSPS to ATX Converter.sch.json
- **Created**: 2026-03-23

### Correct
- voltage_dividers correctly identifies R2=22K (top, +12V) and R3=3.3K (bottom, GND) with mid-point connected to U4 pin ~PSON, ratio 0.130 (≈12V × 0.13 = 1.56V). This is a pull-down divider for ATX PS-ON logic level conditioning.
- Six power rails (+12V, +12VSB, +5V, +5VSB, +3V3, GND) extracted correctly. Decoupling observations note missing bypass/high-frequency caps on all rails (only bulk 100uF Tantalum present). ERC no-driver for ~ATX_PSON is a real issue — the external CSPS drives this signal via the J1 connector but the connector pin is passive-typed.

### Incorrect
- bus_analysis.uart contains {net: '~ATX_PSON', devices: ['U4'], pin_count: 4} and {net: 'ATX_PWOK', devices: ['U4'], pin_count: 3}. These are ATX power control signals (PS-ON open-collector control, power-good), not UART. The UART detector is triggering on net names or pin patterns that match PSON/PWOK spuriously. TPS3511 is a power supervisor IC, not a UART device.
  (signal_analysis)

### Missed
- U1 (Mini560 5V), U2 (Mini560 3.3V), and U3 (Mini560 5V) are switching step-down converters providing the ATX 5V, 3.3V, and 5VSB rails from 12V. power_regulators is empty. The Mini560 is classified as 'ic' but not recognized by the regulator detector — likely because 'Mini560' is not in the known regulator keyword list.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000657: PCB statistics (26 footprints, 2-layer, 86.1x86.1mm, 6 zones, 1 via, routing complete) correctly extracted; Courtyard overlaps detected between J7/J9 (228mm2), J9/J8 (127mm2), J2/R3, J2/R2 — plausi...

- **Status**: new
- **Analyzer**: pcb
- **Source**: Electrical_KCORES CSPS to ATX Converter_KCORES CSPS to ATX Converter.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Board dimensions, copper layer count, footprint count, and routing status all match source file. Power tracks correctly show 3.0mm max width on +12V and 1.5mm on +5V — appropriate for high-current ATX power rails.
- J7 (8-pin PCIe), J8 (4-pin ATX), J9 (24-pin ATX) are all at x=172.2 and stacked in Y (79.8, 100.8, 113.4mm). Given the 24-pin ATX connector is ~55mm long, overlap with neighboring connectors is plausible as a true courtyard issue (either intentional stacking or footprint courtyard over-extension). Correct to flag.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
