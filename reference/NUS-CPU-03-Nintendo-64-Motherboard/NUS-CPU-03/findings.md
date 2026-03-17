# Findings: NUS-CPU-03-Nintendo-64-Motherboard / NUS-CPU-03

## FND-00000172: Nintendo 64 NUS-CPU-03 motherboard with 271 components. Correct: LM78M05/7VZ5 regulators, crystal circuits, voltage dividers, LED driver, bus topology, RC filters, decoupling. Incorrect: I2S SDAT misidentified as I2C, VOUT signal net as power rail, ferrite beads as fuses, BOM grouping merges inductors+caps, reset observation shows entire +3.3V rail. Missed: RDRAM memory interface, I2S audio bus, video encoder output path, clock generator function.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: NUS-CPU-03.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U13 LM78M05 correctly detected as LDO +12V to +5V
- Crystal X1/X2 with load caps correctly detected
- Q1 2SC2412K LED driver for D3 correctly detected
- AD0-AD15 16-bit bus correctly detected
- 271 components with correct type breakdown

### Incorrect
- 9480F.SDAT (I2S audio data) incorrectly classified as I2C SDA
  (design_analysis.bus_analysis.i2c)
- VOUT (video encoder composite output) incorrectly listed as power rail
  (statistics.power_rails)
- FIL1-FIL8 (Device:FerriteBead) classified as fuse instead of ferrite_bead
  (statistics.component_types)
- Reset pin observation for U10 shows entire +3.3V rail instead of tracing through U3 PST9128 supervisor
  (signal_analysis.design_observations)

### Missed
- RDRAM memory interface (U11/U14 to U9 RCP) not detected
  (signal_analysis.memory_interfaces)

### Suggestions
- Add I2S bus detection (SDAT/LRCK/BCLK distinct from I2C SDA/SCL)
- Reclassify Device:FerriteBead as ferrite_bead not fuse
- Do not classify nets as power rails when driving pin type is output

---
