# Findings: daisho / hw_main_board_main_board

## FND-00000007: Legacy KiCad 5 .sch files (daisho: 60 files, OpenVent: 19 files) have 0 signal detections. Component extraction and net connectivity work, subcircuit detection works (231 subcircuits in daisho, 98 in OpenVent), but signal pattern analysis not wired up for legacy format.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_main_board_main_board.sch.json
- **Created**: 2026-03-13

### Correct
- All legacy components correctly extracted with reference, value, lib_id
- 231 subcircuits detected in daisho, demonstrating IC+neighbor grouping works

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Wire up run_signal_analysis() in parse_legacy_schematic() return path — the net data and component data exist, just need to pass them through the signal detectors

---

## FND-00000008: Legacy power.sch has 160 nets but only 4 with multiple pins. Most components appear isolated (single-pin nets). Wire-to-pin matching may have gaps in complex legacy sheets.

- **Status**: new
- **Analyzer**: schematic
- **Source**: hw_main_board_power.sch.json
- **Created**: 2026-03-13

### Correct
- GND net correctly has 10 pins, VUSB has 3 — named nets work

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Investigate legacy wire-to-pin matching tolerance. KiCad 5 uses mils coordinates; ensure endpoint matching handles coordinate precision correctly.

---

## FND-00000028: X1/X2/X3 (40/12/25 MHz crystals, QUARTZCMS4_GROUND lib) classified as "connector" instead of "crystal"

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_main_board_main_board.sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- 3 crystals with ref prefix X misclassified as connectors. Library symbol is QUARTZCMS4_GROUND.
  (components)

### Missed
(none)

### Suggestions
- Add X prefix to crystal classification, or check library name for crystal/quartz keywords

---
