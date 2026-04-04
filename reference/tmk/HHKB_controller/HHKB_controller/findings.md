# Findings: HHKB_controller / HHKB_controller

## FND-00000591: U2 MIC5504-3.3YMTR LDO has zero pins resolved — topology=unknown, no I/O rails

- **Status**: new
- **Analyzer**: schematic
- **Source**: bluetooth.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- In bluetooth.sch, U2 (MIC5504-3.3YMTR, lib_id=LDO_REGULATOR) has an empty pins list. The KiCad5 legacy 'LDO_REGULATOR' symbol has no pin entries in the cache lib, so the analyzer cannot determine IN/OUT connections. Result: topology='unknown', input_rail=null, output_rail=null. The correct detection should show input=+5V, output=+3.3V.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000592: single_pin_nets falsely reports U1 ATmega32U4 GND pin connected to net PC7; Crystal X1 (16MHz) with 22pF load caps correctly detected; USB D+/D- lines present but usb_circuits list is empty; LC fil...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HHKB_controller.sch.json
- **Created**: 2026-03-23

### Correct
- Crystal circuit detection correctly identifies X1=16MHz with C5 and C6 (both 22pF), effective load of 14pF (series combination), and marks it within typical range. This is correct for the ATmega32U4 application.
- L1/C15 LC filter on the PSEL net is correctly identified. Resonant frequency 7.34 kHz and impedance 2.17 ohm are mathematically correct for these values.

### Incorrect
- design_observations lists U1 pin 'GND' on net 'PC7' and pin 'UGnd' on net 'PD0'. These are hardware USB pins of the ATmega32U4 (D+/D-/UGnd); the net names reflect pin mapping from the KiCad5 legacy library where pin names don't match net labels. This is likely a pin-name vs net-name ambiguity in KiCad5 legacy parsing, producing false single-pin-net warnings for what are actually multi-pin nets.
  (signal_analysis)

### Missed
- The design has J1 USB connector with D+ and D- signals (via R2/R3 series resistors to ATmega32U4 U1). design_observations correctly notes usb_data for D+ and D- but signal_analysis.usb_circuits is empty. The analyzer detected the USB nets but did not produce a USB circuit entry.
  (signal_analysis)

### Suggestions
(none)

---
