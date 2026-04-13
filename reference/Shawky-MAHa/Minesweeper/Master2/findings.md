# Findings: Shawky-MAHa/Minesweeper / Master2

## FND-00000952: kicad_version reported as 'unknown' for file_version 20230121 (KiCad 7); sheets_parsed is None for a single-sheet file; L7812 and L7805 classified as topology='LDO' — they are standard linear regul...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Master2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- File header is '(kicad_sch (version 20230121) (generator eeschema)'. Version 20230121 is KiCad 7.0. The analyzer should map this to '7' or '7.0' but returns 'unknown'. Similarly sheets_parsed returns None instead of 1 for this single-sheet .kicad_sch file.
  (signal_analysis)
- L78xx series regulators require ~2V input-to-output differential (not low dropout). The analyzer classifies both as 'LDO' topology. This propagates to power_budget where both rails show 'topology: LDO'. Should be 'linear' or 'fixed_linear'.
  (signal_analysis)

### Missed
- Nets MISO, MOSI, SCK, SCK all exist and connect A1 (Arduino Mega) to NRF1 (nRF24L01 module connector). The SPI bus is present but bus_protocols returns []. R8/R11 are series resistors on MISO/MOSI. I2C (SCL/SDA for LCD16x2 via LCD16*2.I2C1) is also not detected in bus_protocols.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000953: Missing board outline (no Edge.Cuts graphics drawn) correctly results in null board dimensions and 0 edge_count; 15 courtyard overlaps correctly detected

- **Status**: new
- **Analyzer**: pcb
- **Source**: Master2.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Edge.Cuts layer is defined in layer table but has no drawn geometry (only 1 occurrence in PCB file, in the layer definition). board_outline reports edge_count=0 and bounding_box=null. This is correct. The 15 courtyard overlaps (some >90mm2) indicate a schematic-only design without proper PCB layout — correctly flagged.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
