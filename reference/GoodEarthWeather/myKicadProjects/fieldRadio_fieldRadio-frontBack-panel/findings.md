# Findings: GoodEarthWeather/myKicadProjects / fieldRadio_fieldRadio-frontBack-panel

## FND-00002516: 12-sheet SDR field radio (491 components, QSD receiver, Si5351A clock, MSP430 controller). Good structural accuracy. Issues: VR1 potentiometer as varistor, INA821 instrumentation amps as comparator, Si5351A clock output_net pointing at VDD3.3, spurious I2C detections, power_rails missing major rails.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: fieldRadio_fieldRadio.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- All 12 hierarchical sheets correctly traversed, 491 components, 315 nets
- U10 (LM1085-5.0), U7 (MIC5219-3.3), U1 (MIC5235-5.0) correctly identified as LDOs
- Y1 (32.768kHz) and Y2 (25MHz) crystals correctly detected
- 36 LC filters in preselector/LPF correctly identified
- Q20 (J309 JFET) correctly classified in QSD front-end
- U6 (LM386) correctly identified as audio_amplifier

### Incorrect
- VR1 (Bourns 3296W trimmer potentiometer) misclassified as varistor due to VR prefix
  (signal_analysis.protection_devices)
- IC7/IC8 (INA821) instrumentation amps classified as comparator_or_open_loop — RG gain resistor topology not recognized
  (signal_analysis.opamp_circuits)
- Si5351A clock output_net is VDD3.3 (power pin) instead of actual CLK0/1/2 outputs
  (signal_analysis.clock_distribution)
- power_rails missing VDD12, VDD5, VDD3.3, VCC5.0, VCC3.3, HV
  (statistics.power_rails)
- 3 spurious I2C bus detections on non-I2C GPIO nets
  (protocol_compliance)
- VDD flagged as bus prefix with VDD6-VDD11 as 'missing' members — these are independent power rails
  (bus_topology)

### Missed
- Si5351A (U8) not in I2C device list despite sharing SDA/SCL nets
  (protocol_compliance)
- QSD topology (Tayloe detector) not recognized as RF receiver front-end
  (signal_analysis)

### Suggestions
- Recognize VR-prefix with potentiometer footprint as potentiometer not varistor
- Add instrumentation amplifier recognition for INA-type ICs with RG pins
- Fix clock_distribution to use clock output pins not power pins for Si5351A
- Don't flag power rail name prefixes (VDD, VCC) as bus signals

---
