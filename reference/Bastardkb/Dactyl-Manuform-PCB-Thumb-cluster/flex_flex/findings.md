# Findings: Dactyl-Manuform-PCB-Thumb-cluster / flex_flex

## FND-00000464: Component inventory correctly extracted: 5 diodes, 5 switches, 1 connector; Net connectivity correctly resolved for all 11 nets; Key matrix correctly detected as 1×5 with 5 switches and 5 diodes; J...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: flex_flex.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All 11 components are identified with correct references (D1, D5, D9, D14, D19, SW1, SW5, SW9, SW14, SW19, J1), correct lib_ids, correct footprints, and correct coordinates. BOM groupings are accurate: 5×D (custom:Diode_TH_SOD123), 5×SW_Push (custom:SW_MX_reversible), 1×Conn_01x06_Female.
- All net memberships are correct. row1 connects J1 pin1 plus SW1/SW5/SW9/SW14/SW19 pin1. col2→D5 pin2 (A)+J1 pin2, col3→D9 pin2 (A)+J1 pin3, col4→D14 pin2 (A)+J1 pin4, col5→D19 pin2 (A)+J1 pin5, col6→D1 pin2 (A)+J1 pin6. Each unnamed net correctly pairs one diode cathode (K, pin1) with the corresponding switch pin2. Pin names (K/A) from the Device:D symbol are correctly resolved despite 180° component rotation.
- signal_analysis.key_matrices reports rows=1, columns=5, row_nets=['row1'], col_nets=['col6','col2','col3','col4','col5'], estimated_keys=5, switches_on_matrix=5, diodes_on_matrix=5. This matches the schematic exactly: one row bus (row1) and five column nets driving five switch+diode pairs.
- ic_pin_analysis for J1 correctly shows: pin1→row1 (connected to all 5 SW pin1), pin2→col2 (D5 anode), pin3→col3 (D9 anode), pin4→col4 (D14 anode), pin5→col5 (D19 anode), pin6→col6 (D1 anode). The connector serves as the interface to the main keyboard matrix controller board.
- labels array contains all 12 global_label instances: 2×row1 (at 52.705/46.355 and 77.47/36.83), 2×col2, 2×col3, 2×col4, 2×col5, 2×col6. All positions, angles, and shapes match the source. hierarchical_labels.global_label_count=12 is correct.
- All 6 named nets (row1, col2, col3, col4, col5, col6) carry 'input'-shaped global labels and have no driver pins (all component pins are passive). The warnings are valid and expected for a flex sub-sheet — the drivers live on the main controller board sheet. No false positives or missed warnings.
- All 5 diodes use footprint 'custom:Diode_TH_SOD123' which does not match the Device:D standard filter patterns (TO-???*, *_Diode_*, *SingleDiode*, D_*). The warnings are accurate and correctly set custom_library=true. The switch footprint custom:SW_MX_reversible is not flagged because Switch:SW_Push has no fp_filters defined, which is also correct behavior.

### Incorrect
- bus_topology.detected_bus_signals reports {prefix:'col', width:10, range:'col2..col6'}. The schematic has exactly 5 column nets: col2, col3, col4, col5, col6. The range col2..col6 spans indices 2 through 6, which is 5 values — width should be 5, not 10. The value 10 appears to double-count: the schematic has 12 global labels total (2 instances each of row1, col2, col3, col4, col5, col6), and 10 of those are col labels, suggesting the analyzer is counting label instances rather than unique net names.
  (signal_analysis)
- assembly_complexity reports smd_count=11, tht_count=0. The footprint for switches is custom:SW_MX_reversible (Cherry MX key switches are through-hole). The diode footprint is custom:Diode_TH_SOD123 — the 'TH' in the name stands for through-hole. Since these are custom library footprints the analyzer cannot inspect pad types directly, but the footprint names are strong indicators of THT parts. At minimum, the SW_MX_reversible footprint name should be flagged as likely THT. All 11 components being classified as SMD is incorrect.
  (signal_analysis)
- The file header is '(kicad_sch (version 20210126) (generator eeschema))'. File version 20210126 corresponds to the KiCad 6 release era (.kicad_sch format). The output reports kicad_version='unknown' while correctly capturing file_version='20210126'. The analyzer should map known file version numbers to KiCad major releases.
  (signal_analysis)

### Missed
- The design is a thumb-cluster extension flex PCB for a Dactyl Manuform split keyboard. It is a sub-circuit (not a standalone design) intended to connect to a main controller board via J1. The signal_analysis correctly detects the key matrix but design_analysis.design_observations is empty. An observation noting the sub-sheet nature (only global labels, no power pins, no MCU) and the standard diode-per-key anti-ghosting topology would improve usability of the output.
  (signal_analysis)

### Suggestions
(none)

---
