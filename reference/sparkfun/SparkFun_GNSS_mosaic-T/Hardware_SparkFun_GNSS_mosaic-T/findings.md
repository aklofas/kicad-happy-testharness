# Findings: sparkfun/SparkFun_GNSS_mosaic-T / Hardware_SparkFun_GNSS_mosaic-T

## FND-00000231: GNSS mosaic-T board (106 components). Protection device count inflated (40 reported vs 14 actual) due to multi-pin TVS array per-pin counting. Regulators and RC filters correctly detected.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_GNSS_mosaic-T.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- 1 regulator correctly detected
- 4 RC filters correctly detected

### Incorrect
- Protection device count inflated from 14 actual to 40 reported - multi-pin TVS arrays counted per-pin instead of per-device
  (signal_analysis.protection_devices)

### Missed
(none)

### Suggestions
- Count multi-pin TVS arrays as single protection devices instead of per-pin

---
