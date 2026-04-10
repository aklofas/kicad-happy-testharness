# Findings: Jordan87M/DCMG / DCMGv2wBUFFERS

## FND-00002512: DC Microgrid signal routing schematic with 301 CONNECTOR symbols for relay contacts and bus segments. Analyzer correctly parsed all components, wiring, and connectivity with no significant errors.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: DCMGv2_SIGNALROUTING.sch.json
- **Created**: 2026-04-09

### Correct
- All 301 components correctly identified as CONNECTOR type (P1-P301)
- 146 nets correctly extracted with proper connectivity
- No false-positive signal detections — all detector sections correctly empty for a connector-only schematic

### Incorrect
- kicad_version reported as '5 (legacy)' but file uses EELAYER 27 0 (KiCad 4 format, dated March 2016). Cosmetic since both parse identically.
  (kicad_version)
- file_version reported as '4' but actual EESchema Schematic File Version in header is 2
  (file_version)

### Missed
(none)

### Suggestions
- Consider distinguishing KiCad 4 (EELAYER 27, file version 2) from KiCad 5 legacy (EELAYER 25+, file version 4) in version detection

---
