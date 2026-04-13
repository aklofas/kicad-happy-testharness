# Findings: doitaljosh/gea-interface-board / adapter

## FND-00002078: UART bus not detected despite J1201 connector labeled 'UART' carrying explicit TX/RX lines; AMS1117-5.0 linear regulator classified with topology 'unknown' and null input/output rails; R102/R202 (1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_gea-interface-board_adapter.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U1201 is an AMS1117-5.0 LDO regulator. The analyzer reports topology='unknown', input_rail=null, output_rail=null. In the schematic, U1201 is powered by +5V (supply side) and its output drives the +5V rail for downstream circuits — the component has a fixed 5.0V output so the output rail should be identifiable as +5V. The LM78M05 in the fuel_capacity_sensor design is correctly identified as 'LDO' with input/output rails, suggesting this is a library-id recognition gap for AMS1117.
  (signal_analysis)
- R102 and R202 are 120-ohm resistors used as CAN bus termination resistors on the GEA bus differential lines (the GEA appliance bus uses a CAN-like physical layer). The analyzer classified each as a low-pass RC filter paired with C103/C203 (100nF bypass caps), reporting a 13.26 kHz cutoff. These 120-ohm resistors are bus terminations, not filter elements — the 100nF caps are decoupling, not filter capacitors. This is a false positive RC filter detection.
  (signal_analysis)

### Missed
- J1201 is a 20-pin 2.54mm header connector whose value field is literally 'UART' and whose schematic context is a GEA (General Electric Appliance) bus interface with UART signaling. The bus_analysis.uart list is empty. The analyzer should detect this UART interface either by the connector's value string or by tracing the TX/RX pin names through the net. This is a missed detection of an obvious protocol connector.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002079: Drill-only directory falsely flagged as incomplete — missing required copper/mask layers that exist in the separate plots/ directory

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_gea-interface-board_drill.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gea-interface-board repo splits gerbers into two directories: drill/ (Excellon drill files only) and plots/ (all Gerber layers). When analyzing drill/ in isolation, the analyzer correctly finds 0 Gerber files but reports missing_required=['B.Cu','B.Mask','Edge.Cuts','F.Cu','F.Mask'] and complete=false. This is technically accurate for the drill/ subdirectory alone, but misleading at the project level since the full fabrication package is present across both directories. The plots/adapter gerber correctly reports complete=true with all 9 layers found.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
