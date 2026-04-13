# Findings: martinchez/Full-Mechanical-keyboard-PCB / 1. mechanical keyboard

## FND-00000565: Component counts accurate: 41 diodes, 41 switches (MX_SW_solder), 3 stabilizers (MX_stab), 4 mounting holes, 1 connector; Key matrix detected: 4 rows × 11 columns, 41 switches, 41 diodes; kicad_ver...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 1. mechanical keyboard.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- BOM quantities sum to 90 total_components, correctly split by footprint variant (1u, 1.25u, 1.5u, 1.75u). Diode count matches switch count (1 diode per key). All correct.
- key_matrices[0] reports rows=4, columns=11, estimated_keys=41, switches_on_matrix=41, diodes_on_matrix=41. All match the actual schematic contents. Row and column net names (ROW1-4, COL1-11) are correctly enumerated.
- The nets section shows exactly the expected keyboard matrix wiring: ROW nets carry multiple diode K pins plus a J1 row pin; COL nets carry multiple switch pin-1 connections plus a J1 col pin; unnamed nets each pair one switch pin-2 with one diode anode. This is textbook diode-protected keyboard matrix wiring and is accurately captured.
- total_components=90 minus 4 MountingHole_Pad yields 86, matching sourcing_audit.total_bom_components. Mounting holes (H1-H4) are absent from sourcing missing_mpn lists, which is appropriate since mechanical items don't require distributor part numbers.

### Incorrect
- The file header is (version 20230121) which corresponds to KiCad 7.x. The analyzer correctly extracts file_version='20230121' but sets kicad_version='unknown' instead of mapping to the correct version string. This is a known mapping gap.
  (signal_analysis)
- J1 (Conn_02x12_Top_Bottom, ProMicro footprint) has pins 1, 3, 4, 6, 7, 12, 13, 14, 15, 16 each landing on a single-component unnamed net with no other connections. These are functionally unconnected pins (no no-connect markers either). The ic_pin_analysis reports unconnected_pins=0, which is wrong. The pins are on nets but those nets have only J1 as the sole occupant.
  (signal_analysis)
- There are 14 nets with only one connected pin: 10 dangling J1 pins (__unnamed_28 through __unnamed_37) and 4 mounting hole pads (__unnamed_52–54, __unnamed_9). All are single-occupant nets but connectivity_issues.single_pin_nets=[] reports none. This would be useful for catching unintentional dangling connections.
  (signal_analysis)
- All 15 ROW/COL signals are flagged as 'undriven_input_label' because the ProMicro MCU (which drives them) is on a separate schematic page that doesn't appear in this file. For a single-sheet keyboard matrix schematic where the MCU is implicit, these warnings are expected design practice, not errors. The warnings are technically correct per ERC rules but misleading in context.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
