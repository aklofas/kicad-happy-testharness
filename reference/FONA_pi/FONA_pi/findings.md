# Findings: FONA_pi / FONA_pi

## FND-00000563: Component count and BOM extraction accurate; Net extraction and connectivity correct; assembly_complexity classifies 24 THT connectors as SMD (other_SMD); assembly_complexity.unique_footprints repo...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: FONA_pi.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 37 total components correctly identified (20 connectors, 6 resistors, 4 jumpers, 4 mounting holes, 3 LEDs). BOM grouping by value/footprint is correct. Mounting holes (H1-H4) correctly excluded from sourcing_audit's 33-component count.
- 82 nets correctly identified. All connector pin-to-pin routing through the RPi GPIO adapter topology is correctly traced. LED cathodes correctly on the shared 5V GPIO net, anodes through individual current-limiting resistors (R1→D3, R2→D2, R3→D1).
- No (label), (global_label), or (hierarchical_label) entries exist in the schematic. All nets are unnamed. Bus detectors (UART, I2C, SPI) correctly return empty since they rely on net label names. This is the correct behavior for an unlabeled connector-routing board.
- G5 uses the lib_id Jumper:Jumper_2_Bridged and is correctly classified as type 'jumper'. The non-standard 'G' reference prefix did not cause misclassification.

### Incorrect
- The _extract_package_info function only matches THT if footprint path contains 'tht', 'through_hole', 'dip', 'to-220', or 'to-92'. PinSocket, PinHeader, JST_XH, Wago, and MountingHole footprints all lack these keywords so they fall through to 'other_SMD'. Result: smd_count=28, tht_count=9. Correct values should be ~smd_count=4 (solder jumpers only), tht_count=29 (all connectors, LEDs with THT name already work, resistors). The design is almost entirely through-hole.
  (signal_analysis)
- The field counts len(package_breakdown) which is the number of distinct package category buckets ('other_SMD' and 'THT'), not distinct footprint strings. The correct unique footprint count is 12 (correctly reported in bom_optimization.total_unique_footprints=12). This metric is misleading — it measures package buckets, not actual footprint variety.
  (signal_analysis)
- The file has (version 20230121) and (generator eeschema) but no (generator_version ...) field, which was only added in KiCad 8+. The analyzer falls back to get_value(root_tree, 'generator_version') which returns None, then defaults to 'unknown'. For pre-8 KiCad schematics, the version could be inferred from the file_version number (20230121 → KiCad 7).
  (signal_analysis)

### Missed
- Three LEDs (D1-D3) each have a series resistor (R1-R3) connected to their anodes, with cathodes all on a shared GPIO/power net. This classic LED + series resistor pattern is not detected in signal_analysis or design_observations. A design observation noting the LED driver topology would be useful.
  (signal_analysis)

### Suggestions
(none)

---
