# Findings: HadesFCS / Hardware_HadesMicro_HadesMicro

## FND-00000300: Gerber review: 4-layer mini flight controller (50x50mm). Combined drill=unknown, has_pth=false

- **Status**: new
- **Analyzer**: gerber
- **Source**: Hardware/HadesMicro/gerbers/
- **Related**: KH-177, KH-183, KH-184
- **Created**: 2026-03-18

### Correct
- 172 vias all at 0.4mm, consistent single-via-size design

### Incorrect
- Drill extent coordinates not normalized to mm -- values 1000x too large. Affects alignment.layer_extents for drill entries
  (alignment.layer_extents)
- pad_summary.smd_apertures=0 and smd_ratio=0.0 wrong -- F.Paste has hundreds of flashes
  (pad_summary)
- Combined PTH+NPTH drill file classified as 'unknown', has_pth_drill=false and has_npth_drill=false despite vias and press-fit holes
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
