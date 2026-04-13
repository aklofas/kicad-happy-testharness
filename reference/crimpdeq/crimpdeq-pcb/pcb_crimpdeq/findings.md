# Findings: crimpdeq/crimpdeq-pcb / pcb_crimpdeq

## FND-00002318: HX711 24-bit ADC misclassified as a power regulator; Crystal Y1 frequency not parsed from value '32.768Hz'; USB ESD protection, switching regulator, and differential pairs correctly detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_crimpdeq-pcb_pcb_crimpdeq_crimpdeq.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies: SY8088 (U6) as a switching regulator with inductor L1 converting +5V to +3V3; the USB_D+/USB_D- pair as type='USB' with ESD protection via D7, D9, D10 (LESD5D5.0CT1G TVS diodes) and U4; the P-channel MOSFET Q2 (DMG3415U) as a power path switch; and the MCP73831 (U2) as a battery charger on the VBUS/+BATT rails.

### Incorrect
- The analyzer lists U3 (HX711, lib_id 'Analog_ADC:HX711') under power_regulators with topology='ic_with_internal_regulator'. The HX711 is a 24-bit precision ADC for weigh-scale/load-cell applications; it has an onboard reference but is not a power regulator. It belongs in signal_analysis detectors such as current_sense or a dedicated ADC category, not power_regulators.
  (signal_analysis)
- Crystal Y1 has value '32.768Hz' (a 32.768 kHz RTC crystal with a non-standard value string). The analyzer outputs frequency=null and load_caps=[]. The analyzer should extract the numeric frequency from this value string (32.768 Hz or interpreting the context as 32.768 kHz). The null frequency means any downstream frequency-aware analysis (e.g. load capacitance recommendations, RTC detection) is skipped.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002319: Gerber completeness check correctly validates all 9 required layers including both copper layers

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber_crimpdeq-pcb_pcb_crimpdeq_production_gerber.json
- **Created**: 2026-03-24

### Correct
- The gerber analyzer correctly identifies all 9 expected layers (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) as present with no missing or extra layers, both PTH and NPTH drill files present, sourced from the .gbrjob file. This is consistent with the PCB using both copper layers for routing even though all components are on the front.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
