# Findings: hw_projects / skadis_clock_kicad_skadis_clock

## FND-00000188: Skadis clock (112 components, 5 sheets). Correct: crystal, BC807 PNP transistors, USB-C CC pulldowns, SPI bus, decoupling. Incorrect: duplicate SPI bus detection (MCU and ISP connector report same bus twice), crystal frequency null despite Crystal value.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: skadis_clock_kicad_skadis_clock.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Crystal Y1 with 22pF load caps correctly detected
- Q1-Q4 BC807 PNP LED drivers correctly identified
- USB-C 5.1k CC pulldowns pass

### Incorrect
- Duplicate SPI bus: bus_id 0 and pin_J1 contain identical signals
  (design_analysis.bus_analysis.spi)

### Missed
(none)

### Suggestions
- Deduplicate SPI bus when connector and MCU share same nets

---
