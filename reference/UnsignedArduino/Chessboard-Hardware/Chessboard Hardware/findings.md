# Findings: UnsignedArduino/Chessboard-Hardware / Chessboard Hardware

## FND-00000438: Bus width for COM bus reported as 24 instead of 8; 12 cross-domain signal warnings are false positives caused by misidentifying Arduino VIN as a power domain; Analog multiplexer chain (64 Hall sens...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Chessboard Hardware.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The detected_bus_signals entry for the COM bus reports width=24 with range=COM0..COM7. There are exactly 8 unique COM net signals (COM0 through COM7) in the design, confirmed by the nets dictionary. The width of 24 equals 8 signals × 3 label occurrences per signal in the root sheet, meaning the analyzer is counting total label occurrences rather than the number of unique parallel bus signals. The correct width should be 8.
  (bus_topology)
- design_analysis.cross_domain_signals reports 12 entries, all claiming signals cross between the 'VCC' domain and '__unnamed_11'. However, __unnamed_11 is a single-pin net containing only A1 pin 30 (VIN — the Arduino Nano's unconnected power input). VIN is floating/unconnected and is not a real power domain. Both the Arduino (A1) and all mux ICs (U5, U14, U23, U32, U41, U50, U59, U68) are powered solely by VCC. All COM0–COM7, A, B, C, and INH signals are intra-domain connections within VCC and should not trigger cross-domain warnings.
  (design_analysis)

### Missed
- The design implements a clear sensor-to-ADC readout chain: 64 SS49E Hall sensors are grouped 8-per-mux, feeding 8 SN74HC4851N 8:1 analog multiplexers, whose COM outputs (COM0–COM7) connect to the Arduino Nano analog inputs (A0–A7 implied through J1 connector). The address bus (A, B, C) and inhibit (INH) from the Arduino select which sensor is read. Signal analysis produces no entries for this analog mux topology — no detector fires for the analog switching network. The design_observations section also has no entry describing this architecture.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000439: 5 single-pin-net warnings for hierarchical label ports in sub-sheet standalone analysis; SS49E Hall-effect sensors classified as generic 'ic' type instead of 'sensor'

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Chessboard Eighth.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- When the Eighth sub-sheet is analyzed standalone, connectivity_issues.single_pin_nets reports 5 single-pin nets: A, B, C, COM, and INH on U23 (SN74HC4851N). These nets are driven by hierarchical labels (confirmed: hierarchical_label_count=5) that connect to parent sheet pins. In the flat/hierarchical context (Chessboard Hardware.kicad_sch), these signals are fully driven by the Arduino Nano (A, B, C, INH as address/control lines) and produce COM as the mux output. The warnings are an artifact of sub-sheet isolation and do not represent real connectivity gaps.
  (connectivity_issues)
- All 64 SS49E instances (8 per sub-sheet × 8 sheets in main, and 8 in standalone Eighth) are classified as type='ic' and category='ic'. The SS49E is a linear Hall-effect sensor (description: 'SENSOR HALL ANALOG RADIAL LEAD', datasheet confirms it). While ic_pin_analysis correctly identifies function='sensor IC', the top-level component type classification misses the sensor category. This causes the statistics.component_types to report 73 ICs in the main schematic instead of a mix of 64 sensors + 9 logic ICs, obscuring the design's primary function as a Hall-sensor chessboard.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: SS49E Hall-effect sensors classified as generic 'ic' type instead of 'sensor'

---
