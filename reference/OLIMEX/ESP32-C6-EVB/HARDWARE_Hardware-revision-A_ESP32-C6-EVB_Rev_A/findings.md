# Findings: OLIMEX/ESP32-C6-EVB / HARDWARE_Hardware-revision-A_ESP32-C6-EVB_Rev_A

## FND-00000115: Legacy KiCad 5 format parsed but signal analysis almost entirely empty - only 2 design observations (USB data without ESD); I2C/UART buses detected from net names but all subcircuit neighbor_components lists are empty; 11 components misclassified as other

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/ESP32-C6-EVB/HARDWARE/Hardware-revision-A/ESP32-C6-EVB_Rev_A.sch
- **Related**: KH-016
- **Created**: 2026-03-14

### Correct
- I2C bus correctly identified from net names GPIO7/LP_I2C_SCL and GPIO6/LP_I2C_SDA
- UART correctly identified: LP_UART (GPIO5/4) and U0 UART (GPIO16/17)
- USB data lines GPIO13/USB_D+ and GPIO12/USB_D- correctly flagged as lacking ESD protection in design_observations
- Component counts correct: 110 total, 50 unique parts
- Power rails correctly identified: +3.3V, +5V, +5V_EXT, +5V_USB, GND, VIN
- 4 relays correctly identified as relay type
- 4 transformers correctly identified (likely isolation/optocoupler related)

### Incorrect
- 11 components classified as type other - these likely include optocouplers (OPT1-OPT4 listed in BOM), ESP-PROG connector, and other identifiable components that should have proper types
  (statistics.component_types)
- I2C bus shows has_pull_up: false but these ESP32-C6 I2C lines typically have pull-ups; the analyzer may not be finding them in legacy format
  (design_analysis.bus_analysis.i2c)

### Missed
- Zero voltage dividers detected despite the board having a buck regulator (SY8089) that requires a feedback divider
  (signal_analysis.voltage_dividers)
- Zero RC filters detected in the entire design
  (signal_analysis.rc_filters)
- Zero power regulators detected - SY8089AAAC (U2) is a buck regulator and TX4138 (U1) is a DC-DC controller, both should be identified
  (signal_analysis.power_regulators)
- Zero protection devices detected despite SMAJ58A TVS diode (D1) and multiple Schottky diodes for reverse polarity protection
  (signal_analysis.protection_devices)
- Zero decoupling analysis despite having 11 capacitors on the board
  (signal_analysis.decoupling_analysis)
- All subcircuit neighbor_components lists are empty - no neighboring components linked to any IC
  (subcircuits)
- Optocoupler-isolated relay driver circuits (OPT1-4 driving REL1-4) completely undetected - this is the main function of this EVB
  (signal_analysis.isolation_barriers)
- Crystal circuit for ESP32-C6 module not detected (12pF cap C5 suggests external crystal)
  (signal_analysis.crystal_circuits)
- No USB interface detected despite USB-OTG1 connector present
  (design_analysis.bus_analysis)

### Suggestions
- KiCad 5 legacy format parsing appears to have significantly degraded signal analysis - nearly all detectors return empty results. This is likely KH-016 impact.
- Verify that net connectivity is being properly extracted from legacy .sch format - the empty signal_analysis suggests nets may not be resolved to component pins
- Optocoupler detection should identify OPTx components (or PC817, TLP281 values) as isolation barriers
- Component classification should recognize optocoupler footprints/values rather than defaulting to other

---
