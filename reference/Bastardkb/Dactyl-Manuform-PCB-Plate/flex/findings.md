# Findings: Bastardkb/Dactyl-Manuform-PCB-Plate / flex

## FND-00000463: Component counts are accurate: 32 diodes, 32 switches, 15 connectors, total 79; kicad_version reported as 'unknown' but schematic has version 20210126 (KiCad 6 RC); Key matrix correctly detected: 3...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex_flex.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic contains D1–D26 (26 diodes in the main switch area) plus D27–D32 (6 thumb-cluster diodes) = 32 total diodes, SW1–SW26 + SW27–SW32 = 32 switches, and J1–J15 = 15 connectors. The analyzer reports component_types: {diode: 32, connector: 15, switch: 32} and total_components: 79. All correct.
- The analyzer reports a key_matrices entry with rows=7, columns=6, row_nets=[row0..row6], col_nets=[col1..col6], switches_on_matrix=32, diodes_on_matrix=32, estimated_keys=32, detection_method='net_name'. The 32 switches and 32 diodes on the matrix are accurately counted. The col1–col6 and row0–row5 nets all carry actual switches; this is confirmed by net membership in the schematic.
- Verified by inspection: col1 net includes D27 pin K, D1 pin K, D2 pin K, D3 pin K, D4 pin K plus connector pins on J9, J14 pin 1, and J1 pin 1. Each column net carries the cathode (pin 1, K) of 4–6 diodes. Each row net (row0–row5) carries pin 1 of the corresponding switch group. The SW-diode-A (anode) connections are correctly captured as unnamed nets (e.g., __unnamed_0 = D27 pin A + SW27 pin 2). Net tracing is accurate.
- The schematic contains no PWR_FLAG, VCC, GND, or any other power symbols. The analyzer reports power_rails: [] and power_domains: {ic_power_rails: {}, domain_groups: {}}. This is correct. The schematic is purely a keyboard matrix with connectors to an external MCU board.
- The schematic has only passive components (diodes, switches) and connectors with no analog circuits, bus interfaces, or power conversion. The analyzer correctly returns empty arrays for voltage_dividers, rc_filters, lc_filters, power_regulators, crystal_circuits, bus_analysis (i2c, spi, uart, can), and all other signal path detectors.
- The schematic defines: J1 and J14 as Conn_01x06_Female (6 pins each), J2 as Conn_01x07_Female (7 pins), and J3–J13 + J15 as Conn_01x02_Female (2 pins each, 12 total). The analyzer correctly reflects these in both the BOM (quantities 2, 1, and 12) and the component list with correct pin_uuids counts per reference.
- The schematic uses global_label (not local net_label) for row0–row5 (at x=30.48), col1–col6 (at x=43–128), row0–row6 and col1–col6 in the MCU connector area (x=158.75), row6 in thumb connector area, and additional connector labels at x=203.2. The analyzer captures all of these in the labels array with type='global_label', correct x/y coordinates, and shape='input'. The total_nets=45 includes both named nets (col1–col6, row0–row6 = 13) and the 32 unnamed SW-diode anode nets.
- No component in the schematic has an MPN, manufacturer, DigiKey, Mouser, LCSC, or Element14 field populated. The analyzer correctly lists all 79 references (D1–D32, J1–J15, SW1–SW32) in the missing_mpn list and reports missing_footprint as empty (all footprints are assigned).
- The connectivity_issues section reports all empty: unconnected_pins=[], single_pin_nets=[], multi_driver_nets=[]. This is correct. Every connector pin and component pin in the schematic is wired to at least one other pin. The Conn_01x02 dual-pin connectors on single nets each contribute 2 pins to a shared net, so no single-pin nets result.

### Incorrect
- The schematic header is `(kicad_sch (version 20210126) (generator eeschema))`. Version 20210126 is a KiCad 6 release-candidate era format (early KiCad 6 S-expression format). The analyzer outputs `"kicad_version": "unknown"` instead of resolving this version token to a KiCad version string (e.g., "6" or "6.0-rc"). The file_version field is correctly populated as "20210126".
  (signal_analysis)
- The analyzer reports rows=7, including row6. However, net 'row6' contains only two pins: J1 pin 1 (Conn_01x06_Female) and J2 pin 7 (Conn_01x07_Female). There are no switches or diodes on the row6 net. Row6 is a connector-only routing net (likely a reserved/future or thumb extension line), not an active keyboard matrix row. The active matrix is 6 rows (row0–row5) × 6 columns. Including row6 inflates the row count and the implied capacity (7×6=42 vs 6×6=36, either way the 32 actual keys is less). The estimated_keys=32 is correct despite the rows overcounting.
  (signal_analysis)

### Missed
- J3–J13 and J15 are Conn_01x02_Female components with footprint 'customs2:SolderWire-0.15sqmm_1x01_D0.5mm_OD1.5mm'. Both pins of each connector are tied to the same net (e.g., both pins of J3 are on 'row0'). This is a solder-wire loopback/jumper pattern used to route wires from this flex PCB to an external controller. The analyzer notes the connection (both pins appear in the net) but does not flag this as a design observation or unusual pattern. This could be a design_observation noting 'duplicate-pin connectors used as wire attachment points'.
  (signal_analysis)

### Suggestions
(none)

---
