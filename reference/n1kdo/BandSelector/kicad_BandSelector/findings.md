# Findings: n1kdo/BandSelector / kicad_BandSelector

## FND-00000397: Inrush analysis reports 22000A inrush and 2200000uF due to bare-numeric capacitor value misparse; Inconsistent capacitor unit parsing: bare numeric 'uF' values parsed as picofarads in decoupling_an...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_BandSelector_BandSelector.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- C10 has value '2.2' (aluminum electrolytic, CP_Radial_D5.0mm footprint — clearly 2.2uF). The inrush_analysis section treats this as 2.2 Farads, giving total_output_capacitance_uF: 2200000.0 and estimated_inrush_A: 22000.0. These values are physically impossible for a small THT electrolytic capacitor. The correct capacitance is 2.2 uF.
  (inrush_analysis)
- Capacitors C9 and C10 have value '2.2' and C8 has value '220'. These are aluminum electrolytic capacitors (CP_Radial footprints) and the bare numeric convention for this component class is microfarads (2.2uF and 220uF). In signal_analysis.decoupling_analysis the farads values are 2.2e-12 and 2.2e-10 (picofarad range — wrong), causing total_capacitance_uF: 0.0 for +12V and +5V rails. In pdn_impedance the same caps are parsed as 2.2F and 220F (Farad range — also wrong). Neither interpretation is correct.
  (signal_analysis)
- U2 (L7805) is a classic fixed positive linear voltage regulator from the 78xx series. It is NOT an LDO — it requires a dropout voltage of ~2V. The signal_analysis.power_regulators entry reports topology: 'LDO', which is incorrect. The correct classification is 'linear' or 'fixed_linear'. This also propagates to power_budget and inrush_analysis which also show topology: 'LDO'.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: L7805 linear voltage regulator misclassified as LDO topology

---

## FND-00000398: HD44780-compatible character LCD (U1, NHD-0220FZW) classified as generic 'ic' type; Potentiometer RV1 classified as 'resistor' type instead of 'potentiometer'; HD44780 parallel LCD interface not de...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: kicad_DisplayBoard_display-board.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- U1 has lib_id 'New_Library:NHD-0220FZ-FSW-GBW-P-33V3' and footprint 'Library:NHD-0220FZW-GBW-P-33V3'. This is a 2x20 character LCD module with HD44780 controller. The analyzer classifies it as type 'ic' and component_types shows ic: 1. A display module is not an IC. No display-specific detection is triggered.
  (statistics)
- RV1 uses lib_id 'Device:R_Potentiometer_US' with keywords 'resistor variable'. The analyzer assigns type: 'resistor' and it appears under component_types.resistor count (2). A potentiometer has three terminals and serves a different function from a fixed resistor. It is used here as a contrast adjustment voltage divider for the LCD.
  (statistics)

### Missed
- The display board interfaces a 2x20 HD44780-compatible LCD (U1) with a 4-bit parallel bus: RS, RW, E, D4, D5, D6, D7 signals are wired from J1 (the inter-board connector) to the LCD. The signal_analysis.memory_interfaces array is empty and bus_analysis shows no detected buses. The parallel HD44780 interface could be recognized as a character LCD protocol with the classic RS/RW/E control plus D4-D7 data lines.
  (signal_analysis)

### Suggestions
- Fix: HD44780-compatible character LCD (U1, NHD-0220FZW) classified as generic 'ic' type
- Fix: Potentiometer RV1 classified as 'resistor' type instead of 'potentiometer'

---
