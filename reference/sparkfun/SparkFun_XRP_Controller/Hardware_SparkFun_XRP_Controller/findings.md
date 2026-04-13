# Findings: sparkfun/SparkFun_XRP_Controller / Hardware_SparkFun_XRP_Controller

## FND-00000168: SparkFun XRP robot controller with RP2350B. AP63357 reference voltage wrong, bus widths inflated, QSPI interface missed.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- RP2350B microcontroller correctly identified with proper pin count
- DRV8411A dual motor drivers correctly identified

### Incorrect
- AP63357 buck converter Vref reported as 0.6V but datasheet specifies 0.765V reference
  (signal_analysis.power_regulators)

### Missed
- QSPI flash memory interface to W25Q128 not detected as memory bus
  (signal_analysis.bus_interfaces)

### Suggestions
- Use correct Vref of 0.765V for AP63357 (check datasheet feedback divider reference)
- Count unique data signals in bus, not total net segments, to avoid inflated bus widths
- Detect QSPI memory interfaces from CS/CLK/D0-D3 net patterns to flash ICs

---

## FND-00000174: SparkFun XRP Controller (RP2350B robotics board). Correct: 184 components, DRV8411A motor drivers, LSM6DSOX IMU, crystal, USB compliance, WS2812B, power OR-ing. Incorrect: AP63357 Vref wrong (0.6V vs 0.765V giving 3.87V vs actual 5V), bus widths inflated by counting label instances across sheets. Missed: QSPI memory interface, SPI to radio module, I2C bus to IMU.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_SparkFun_XRP_Controller.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U1 RP2350B correctly identified with 81 pins
- U7/U8 DRV8411A motor drivers correctly identified
- Crystal Y1 12MHz with 15pF load caps correctly detected
- USB-C compliance with 5.1k CC pulldowns pass
- D4 WS2812B addressable LED chain detected

### Incorrect
- AP63357 output voltage calculated as 3.873V using wrong Vref=0.6V (correct Vref=0.765V gives 4.94V matching 5V rail)
  (signal_analysis.design_observations)
- Bus signal widths inflated: QSPI_D width=12 (actual 4), IMU_INT width=4 (actual 2)
  (bus_topology.detected_bus_signals)

### Missed
- QSPI memory interface between RP2350B and W25Q128/APS6404L not detected
  (signal_analysis.memory_interfaces)
- SPI interface to RM2 radio module not detected
  (design_analysis.bus_analysis.spi)

### Suggestions
- Add AP63357 Vref=0.765V to lookup table
- Fix bus width to count unique signal names not label instances
- Add QSPI bus detection

---

## FND-00000305: Gerber review: beta (2L Eagle) vs production (6L KiCad 8). GKO misclassified as In4.Cu from conflicting X2 FileFunction

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware/Production/
- **Related**: KH-178, KH-181, KH-185, KH-186
- **Created**: 2026-03-18

### Correct
- Production 6-layer stackup correctly determined from X2 FileFunction (L1-L6) and drill MixedPlating,1,6
- Production drill uses X2 attributes correctly: 3060 vias (0.3mm), 4 component hole sizes

### Incorrect
- Production .GKO has X2 FileFunction=Copper,L5,Inr but AperFunction=Profile with draw-only outline content. Classified as In4.Cu instead of Edge.Cuts. Cascades: Edge.Cuts missing, empty board_dimensions, broken alignment
  (completeness)
- Beta .TXT Excellon drill file not recognized -- 0 holes reported despite vias and THT connectors
  (drill_classification)
- Production front_side=0 despite 209 X2 component refs on front silk. back_side=13. Front/back derivation wrong
  (component_analysis)
- 24x 3.1mm NPTH holes classified as component_holes -- M3 chassis mounting for robotics controller
  (drill_classification.mounting_holes)

### Missed
(none)

### Suggestions
- Cross-check: if AperFunction=Profile + draw-only content, classify as Edge.Cuts

---
