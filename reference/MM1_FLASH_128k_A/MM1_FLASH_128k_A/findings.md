# Findings: MM1_FLASH_128k_A / MM1_FLASH_128k_A

## FND-00000874: Legacy .sch parser misses U1 (SST39LF010 flash) data pin net connections

- **Status**: new
- **Analyzer**: schematic
- **Source**: MM1_FLASH_128k_A.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Same as EEPROM: all MEMDATA_0-7 nets only show J1, missing U1 I/O pin connections. This is a consistent bug across all MM1 boards with the legacy KiCad 5 schematic format.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000875: Drill classification correctly identifies via holes vs component holes for FLASH board

- **Status**: new
- **Analyzer**: gerber
- **Source**: documents_MM1_FLASH_128k_A_gerbert.json
- **Created**: 2026-03-23

### Correct
- FLASH: 16 vias at 0.2mm correctly classified; 32 component holes at 0.8mm (PLCC socket pins) and 2 holes at 1.0mm (pin header) correctly classified as component_holes. Total 50 holes matches PTH drill file count.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
