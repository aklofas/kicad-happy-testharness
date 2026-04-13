# Findings: linguini1/pygmy / ground-station

## FND-00000241: Ground station (30 components). Protection device U4 (USBLC6-2SC6) counted as 4 entries (per-net duplication). 1 regulator and 2 RC filters correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ground-station.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 1 regulator correctly detected
- 2 RC filters correctly detected

### Incorrect
- Protection device U4 (USBLC6-2SC6) counted as 4 entries due to per-net counting instead of per-device
  (signal_analysis.protection_devices)

### Missed
(none)

### Suggestions
- Count multi-channel protection devices as single device instead of per-net

---
