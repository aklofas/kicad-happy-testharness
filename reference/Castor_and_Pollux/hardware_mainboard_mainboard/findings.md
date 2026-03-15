# Findings: Castor_and_Pollux / hardware_mainboard_mainboard

## FND-00000164: Eurorack Castor & Pollux synthesizer mainboard. TVS diodes and potentiometers misclassified; I2C and USB detection missing.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_mainboard_mainboard.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 191 components correctly enumerated
- LD1117-3.3 correctly identified as voltage regulator with 3.3V output
- 8 hierarchical sheets correctly detected (castor, pollux, mcu, leds, etc.)
- Power rails (+12V, -12V, 3.3V, 5V) correctly identified
- Opamp circuits correctly detected in analog signal path

### Incorrect
- D3-D6 TVS diodes (D_TVS_Filled footprint) misclassified as LED
  (components)
- RV1-RV12 potentiometers (Eurorack_Pot) misclassified as varistor
  (components)

### Missed
- I2C bus to MCP4728 DAC not detected
  (signal_analysis.bus_interfaces)
- USB connection for programming/configuration not detected
  (signal_analysis.bus_interfaces)

### Suggestions
- Recognize D_TVS and D_TVS_Filled library symbols as TVS diodes, not LEDs
- Classify components with 'Pot' in library name as potentiometer, not varistor
- Detect I2C bus from SCL/SDA net names connecting to known DAC parts like MCP4728

---

## FND-00000165: Castor oscillator sub-sheet with opamp analog circuits. Potentiometers misclassified as varistors; false voltage divider and ERC warnings.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_mainboard_castor.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Opamp circuits correctly identified: integrator, buffer, inverting stages
- Q1 PNP transistor correctly identified
- Cross-domain signals between hierarchical sheets correctly tracked

### Incorrect
- RV6-RV8 potentiometers (Eurorack_Pot) misclassified as varistor
  (components)
- R18/R16 flagged as voltage divider but is actually a transistor bias network for Q1
  (signal_analysis.voltage_dividers)
- False ERC warnings generated on hierarchical labels that are properly connected in parent sheet
  (erc_warnings)

### Missed
(none)

### Suggestions
- Classify Eurorack_Pot and similar pot library symbols as potentiometer not varistor
- Check if resistor divider feeds a transistor base before classifying as voltage divider
- Suppress ERC warnings on hierarchical labels when the parent sheet connection is valid

---

## FND-00000178: Castor & Pollux Eurorack synthesizer mainboard (191 components). Correct: 8 hierarchical sheets, LD1117-3.3 regulator, power rails, opamp circuits, USB ESD protection. Incorrect: D3-D6 TVS diodes (D_TVS_Filled) classified as LED, RV1-RV12 potentiometers (Eurorack_Pot) classified as varistor. Missed: I2C for MCP4728 DAC, USB interface, addressable LED chain.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_mainboard_mainboard.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- LD1117-3.3 correctly detected as LDO with +12V input and +3.3V output
- 191 components with correct breakdown
- USBLC6-2SC6 ESD protection correctly detected

### Incorrect
- D3-D6 (Device:D_TVS_Filled) misclassified as LED instead of TVS diode
  (statistics.component_types)
- RV1-RV12 (winterbloom:Eurorack_Pot) misclassified as varistor instead of potentiometer
  (statistics.component_types)

### Missed
- I2C bus for MCP4728 DAC not detected
  (design_analysis.bus_analysis.i2c)
- USB interface not detected
  (design_analysis.bus_analysis)

### Suggestions
- Classify D_TVS_Filled as TVS diode not LED
- Classify symbols with Pot in name as potentiometer not varistor

---

## FND-00000179: Castor oscillator sub-sheet (46 components). Correct: opamp circuits (integrator, buffer, inverting stages), Q1 PNP transistor, cross-domain signals, RC filters, decoupling. Incorrect: RV6-RV8 potentiometers classified as varistor, R18/R16 transistor bias reported as voltage divider, false ERC warnings on hierarchical labels. Missed: oscillator core topology not detected, sub-octave divider function not identified.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_mainboard_castor.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U7/U8/U10 opamp circuits correctly analyzed with accurate gains
- Q1 MMBT3906 PNP correctly detected with base resistor

### Incorrect
- RV6-RV8 (winterbloom:Eurorack_Pot) classified as varistor instead of potentiometer
  (statistics.component_types)
- R18/R16 transistor bias network reported as voltage divider
  (signal_analysis.voltage_dividers)
- Hierarchical label input nets flagged as single_pin_nets
  (connectivity_issues.single_pin_nets)

### Missed
- Oscillator core topology (current source + integrator + comparator + flip-flop) not detected
  (signal_analysis)

### Suggestions
- Suppress single-pin-net and no-driver warnings for hierarchical label inputs in sub-sheets

---
