# Findings: FHNW-Pro4E-FS19T8-3DPrinterBoard-STM32 / FHNW-Pro4E-FS19T8-3DPrinterBoard-STM32

## FND-00000289: 3D printer controller (STM32F103+ESP32, KiCad 5, 264 components). BUK963R3-60E power MOSFETs (T101/T402/T403) misclassified as transformers due to passive pin types. Fan MOSFET drain/source nets inverted. Fan MOSFETs falsely linked to LED D401 as LED drivers. LM2675M buck regulators have null input_rail and unknown topology.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: FHNW-Pro4E-FS19T8-3DPrinterBoard-STM32.sch.json
- **Created**: 2026-03-16

### Correct
- SG-210STF active oscillator correctly identified
- Thermistor RC filters (R401/C401 etc, 3.39Hz ADC anti-alias) correctly detected
- Endstop debounce filters (10k/10u, 1.59Hz) correctly detected
- ESP32 auto-reset BJT pair (Q1/Q2 2N3904) correctly identified
- 4 protection devices (fuses F101/F401/F402, USBLC6 USB ESD) correct
- LC input filters for buck regulators (47uH/10nF, 232kHz) correct
- VBUS detection divider (R503/R506, ratio 0.68) correct

### Incorrect
- T101/T402/T403 BUK963R3-60E power MOSFETs (60V N-ch, heater switches) misclassified as type='transformer' — custom library symbol has all pins typed 'passive', name doesn't match transistor patterns. Missing from transistor_circuits entirely.
  (statistics.component_types)
- T401/T404/T405 PMV40UN2 fan MOSFETs have drain/source inverted: drain_net='GND', source_net='Fan1_pwr' — should be source=GND, drain=Fan_pwr (load)
  (signal_analysis.transistor_circuits)
- T401/T404/T405 each get false led_driver record pointing to D401 LED_YEL with R422 (100k) — D401 is in a different circuit section, no connectivity to fan MOSFETs
  (signal_analysis.transistor_circuits)
- LM2675M-3.3 (U101) and LM2675M-5 (U102) both show input_rail=null and topology='unknown' — can't trace through input inductor to find +24V source
  (signal_analysis.power_regulators)
- SD_DETECT RC filter R216/C203 has wrong input_net='SD_DAT0' — should be +3.3V (R216 pulls up from +3.3V)
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Component classification should check for MOSFET-like footprints (TO-263, DPAK) even when pin types are passive
- Verify drain/source assignment using pin position relative to gate
- LED driver detection requires net connectivity
- Buck regulator: trace through input LC filter to find source rail

---
