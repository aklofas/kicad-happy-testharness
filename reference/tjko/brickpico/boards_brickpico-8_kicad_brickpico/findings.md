# Findings: brickpico / boards_brickpico-8_kicad_brickpico

## FND-00000133: BrickPico is an 8-channel LED brick controller with RP2040 (Pico module) and AP62301WU buck converter. The analyzer correctly identifies 8 MOSFET transistor circuits (2N7002K for LED switching) and the AP62301WU power regulator. However, it generates 9 false positive RF matching networks from the buck converter input filter (polyfuses misidentified as antennas), and all 118 components have category=None.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/brickpico/boards/brickpico-8/kicad/brickpico.kicad_sch
- **Related**: KH-047
- **Created**: 2026-03-14

### Correct
- Eight 2N7002K MOSFET transistor circuits correctly identified as open-drain LED drivers with gate resistors and protection diodes
- AP62301WU correctly identified as power regulator (buck converter)
- 16 protection devices correctly identified (polyfuses on each LED channel output for overcurrent protection)
- Transistor load_type correctly classified as LED for all 8 channels
- Power rails correctly identified: GND, VBUS, VSYS, PWR_FLAG

### Incorrect
- 9 false positive RF matching networks. All 9 polyfuses (F2-F10) are falsely identified as antennas with pi_match topology. The buck converter inductor L1 (3.3uH) and its input/output capacitors (22uF) form a power filter, not an RF matching network. The polyfuses are overcurrent protection on LED outputs, not RF components.
  (signal_analysis.rf_matching)
- All 118 components have category=None despite correct component_types in statistics
  (components[*].category)
- LC filter detected between L1 (3.3uH) and capacitors is actually the buck converter output filter, not a signal filter. Should be associated with the power regulator.
  (signal_analysis.lc_filters)

### Missed
- LED driver topology not identified. The core function (RP2040 PWM driving 2N7002K MOSFETs to switch LED strings with current-limiting resistors and polyfuse protection) is a common pattern not captured as a higher-level circuit.
  (signal_analysis)
- Buck converter LC output filter not associated with the AP62301WU regulator. The L1/C5/C6/C7 network is the critical output filter for the switching regulator.
  (signal_analysis.power_regulators)
- No USB detection for the Pico module USB connection
  (design_analysis.bus_analysis)

### Suggestions
- RF matching detector should exclude fuses/polyfuses from antenna candidates - check component type or value for fuse keywords
- RF matching detector should require at least one actual RF-frequency component (sub-1uH inductors, sub-1nF capacitors) to qualify as RF matching
- Buck converter output filter (inductor + bulk caps) should be excluded from RF matching and associated with nearby switching regulator instead

---
