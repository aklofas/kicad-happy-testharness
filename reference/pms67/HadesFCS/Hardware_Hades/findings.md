# Findings: HadesFCS / Hardware_Hades_Hades

## FND-00000080: Hades flight controller - 208 components with zero signal detections due to KH-016 legacy wire-to-pin matching failure

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/HadesFCS/Hardware/Hades/Hades.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- Component enumeration correct: 208 total with plausible type breakdown (71 caps, 59 resistors, 12 ICs, 20 connectors)
- Power rails identified: +3.3V, +3V3, +5V, GND, VCC - reasonable for a flight controller
- 377 nets and 491 wires parsed from legacy format
- 76 no-connect markers counted
- Component type classification reasonable: ferrite beads (6), test points (4), jumpers (4) correctly categorized

### Incorrect
- Dual naming of 3.3V rail as both +3.3V and +3V3 suggests possible net aliasing issue in the legacy parser
  (statistics.power_rails)

### Missed
- Zero signal analysis results - no voltage dividers, RC filters, regulators, crystals, or any other signal patterns detected on a 208-component flight controller board
  (signal_analysis)
- Flight controller should have: IMU (accelerometer/gyroscope), barometer, voltage regulators, motor driver outputs, RC receiver input - none detected
  (signal_analysis)
- No design observations generated at all
  (signal_analysis.design_observations)
- 12 ICs not analyzed for any signal paths - likely includes STM32 MCU, IMU sensors, regulators
  (signal_analysis)

### Suggestions
- Fix KH-016 legacy wire-to-pin coordinate matching to enable signal analysis on this board
- This board is a good regression test case for KH-016 fixes - expect dozens of signal detections once wiring works

---

## FND-00000299: Gerber review: 4-layer flight controller (100x60mm). Drill unit bug + smd_apertures=0

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware/Hades/Hades gerbers/
- **Related**: KH-177, KH-183
- **Created**: 2026-03-18

### Correct
- All 11 layers present, 4-layer stackup correct from X2. Separate PTH/NPTH drill files correctly identified
- 382 vias (0.3/0.4mm) correctly classified. 8 NPTH press-fit holes at 0.8mm identified

### Incorrect
- Drill extent coordinates not normalized to mm -- values 1000x too large. Affects alignment.layer_extents for drill entries
  (alignment.layer_extents)
- pad_summary.smd_apertures=0 and smd_ratio=0.0 wrong -- F.Paste has hundreds of flashes
  (pad_summary)

### Missed
(none)

### Suggestions
(none)

---
