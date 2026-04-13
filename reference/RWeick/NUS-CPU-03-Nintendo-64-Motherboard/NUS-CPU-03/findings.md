# Findings: RWeick/NUS-CPU-03-Nintendo-64-Motherboard / NUS-CPU-03

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

## FND-00002504: Nintendo 64 NUS-CPU-03 motherboard with 271 components including CPU-NUS, RCP-NUS, two RDRAM chips, AMP-NUS audio, ENC-NUS/VDC-NUS video, and Sharp 7VZ5 VTERM regulator. Analyzer handles most detections well but incorrectly associates power LED D3 with Q1 (CSYNC emitter-follower), misclassifies Q1 load type, and misses all 6 ESD diode arrays and 4 ferrite-bead LC power filters.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: NUS-CPU-03.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- U13 (LM78M05) linear regulator correctly detected: input rail +12V, output rail +5V
- U12 (Sharp 7VZ5) adjustable regulator correctly detected: input +3.3V, output +VTERM; feedback divider R26/R27 correctly identified
- Both crystal circuits correctly detected: X1 (D143A7) with C39/C40 (43pF) and X2 (D147A7) with C146/C147 (40pF)
- Component counts correctly classified: 178 capacitors, 46 resistors, 8 ferrite beads, 15 ICs, 271 total
- Power rail decoupling coverage correctly analysed for +3.3V (96 caps, 437uF), +5V, +12V, +VTERM, and +RAM.VREF rails
- Voltage divider R13/R12 on U7 (MX8330) FSC pin correctly identified as bias network
- I2C bus detection: 9480F.SDAT net shared between U1 and U9 correctly found
- 8 DNP parts correctly identified
- RC filter for audio signals correctly detected: R17/R21 + C29/C30 on RAUDIO/LAUDIO into U2 AMP-NUS

### Incorrect
- Q1 (2SC2412K) incorrectly identified as led_driver with D3/R31. Q1 is a CSYNC emitter follower: base from U4/U5 SYNC via R16, emitter to P7.CSYNC through R14 (75 Ohm). D3 is independently powered LED on +3.3V rail.
  (signal_analysis.transistor_circuits)
- Q1 load_type classified as 'inductive' but actual load is resistive: R14 (75 Ohm) to CSYNC output net.
  (signal_analysis.transistor_circuits)
- U13 (LM78M05) topology listed as 'LDO' but LM78M05 is a standard fixed-output linear regulator with ~2V dropout, not low-dropout.
  (signal_analysis.power_regulators)

### Missed
- 6 ESD diode arrays (DA1, DA3, DA5, DA6, DA7, DA8) not detected as protection devices. DA1/DA3 protect controller port inputs, DA5/DA6 protect video signals, DA7/DA8 protect composite output.
  (signal_analysis.protection_devices)
- 4 ferrite-bead LC power filters missed on controller port 3.3V supply rails: FIL1+C104, FIL3+C106, FIL5+C107, FIL7+C108.
  (signal_analysis.lc_filters)
- RDRAM memory interface (U11, U14 connected to U9 RCP-NUS via Rambus bus, and expansion slot P1) not detected in memory_interfaces.
  (signal_analysis.memory_interfaces)

### Suggestions
- Fix transistor topology: when collector is on power rail and emitter drives signal net through resistor, classify as emitter follower; don't search for LED loads on collector-rail transistors.
- Extend lc_filters detection to ferrite beads: ferrite bead in series with shunt capacitor on power rail qualifies as LC filter.
- Extend protection_devices to recognize dual-diode arrays (3-pin common-cathode/anode) as ESD protection.
- Refine regulator topology: match LM78xx/LM79xx to 'linear' topology, reserve 'LDO' for low-dropout parts.

---
