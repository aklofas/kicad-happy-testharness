# Findings: OnBoard / projects_Duck_src_Duck

## FND-00000093: STM32F411 flight computer with GPS, flash, pyrotechnic channels. Pyro continuity sense dividers correctly detected. STM32 internal regulator classified as power_regulator which is debatable.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/Duck/src/Duck.kicad_sch
- **Created**: 2026-03-14

### Correct
- 4 voltage dividers correctly detected for pyro channel continuity sensing (R16/R17, R14/R15, R10/R11, R12/R13)
- W25Q512JV flash memory interface detected with 4 shared signal nets to STM32
- TLV76133DCY LDO and LMR33640DDDA switching regulator correctly identified
- 16MHz crystal with 10pF load caps correctly detected
- USB differential pair (USB_D+/USB_D-) detected
- 4 IRLML0030 MOSFET transistor circuits detected (pyro fire channels)
- Feedback network R19(100k)/R20(24.9k) for LMR33640 correctly identified
- Decoupling analysis on 4 rails (VDB, +3.3V, +3.3VA, +5V)

### Incorrect
- STM32F411VETx classified as power_regulator with topology=ic_with_internal_regulator — this is an MCU, not a regulator
  (signal_analysis.power_regulators)
- BOM sum (89) does not match total_components (94) — 5 missing, mounting_hole(4)+other(5)=9 but only 5 gap
  (statistics)

### Missed
- No barometric pressure sensor or IMU detection despite being a flight computer
  (signal_analysis)
- GPS module (MAX-M10S) not recognized as GNSS receiver in bus_analysis
  (design_analysis.bus_analysis)

### Suggestions
- MCUs with internal regulators should not appear in power_regulators list — they are not regulators
- Consider GPS/GNSS module detection

---
