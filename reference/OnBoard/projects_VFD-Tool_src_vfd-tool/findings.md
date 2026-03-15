# Findings: OnBoard / projects_VFD-Tool_src_vfd-tool

## FND-00000087: RP2040-based VFD driver tool with USB-C. Good signal detection overall. TPS562200 estimated Vout only computed for one of two identical regulators. W25Q32 flash memory interface correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/VFD-Tool/src/vfd-tool.kicad_sch
- **Created**: 2026-03-14

### Correct
- Three voltage dividers correctly identified for voltage sensing/feedback
- W25Q32JVSS flash memory interface detected with 6 shared signal nets to RP2040
- Three TPS562200/TPS54331 switching regulators detected
- CMS04 reverse polarity protection correctly identified
- Three crystal circuits detected (32.768kHz, 24MHz, 12MHz)
- USB differential pairs detected (multiple USB ports) with ESD protection
- FUSB302 USB-C controller recognized
- 6 RC filters and 5 LC filters detected

### Incorrect
- TPS562200 U7 estimated Vout=2.58V but U8 (identical part) has no estimated Vout
  (signal_analysis.power_regulators)
- TPS54331DR U10 has no estimated Vout despite likely having feedback divider
  (signal_analysis.power_regulators)
- BOM sum (171) does not match total_components (174) — 3 missing, test_points=4 but test_points appear in BOM for other projects
  (statistics)

### Missed
- VFD (vacuum fluorescent display) driver circuitry not detected — this is the main function of the board
  (signal_analysis)
- No current sense detection despite likely having sense resistors for VFD filament drive
  (signal_analysis.current_sense)

### Suggestions
- Ensure estimated_vout is computed consistently for all switching regulators with feedback dividers
- Consider VFD driver detection as a signal path

---
