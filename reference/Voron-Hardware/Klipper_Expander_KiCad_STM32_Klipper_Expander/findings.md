# Findings: Voron-Hardware / Klipper_Expander_KiCad_STM32_Klipper_Expander

## FND-00000075: Klipper Expander - STM32F042 GPIO/PWM expander with 4 MOSFET outputs, good transistor detection but missing regulator

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/Voron-Hardware/Klipper_Expander/KiCad/STM32_Klipper_Expander.sch
- **Related**: KH-012
- **Created**: 2026-03-14

### Correct
- 4x IRLML6344TRPBF N-channel MOSFETs correctly identified with drain/source/gate nets and ground-referenced source
- Thermistor filter circuits detected: 2x RC low-pass (4.7K + 4.7uF, fc=7.2Hz) on T0/T1 channels - correct for NTC thermistor filtering
- Fuse detected on Vin input as protection device
- USB D+ ESD protection correctly flagged as absent
- Decoupling analysis shows +3V3 has 3 caps (4.9uF total) with bulk and bypass coverage
- STM32F042F6Px correctly identified as main IC

### Incorrect
- Voltage divider detection false positive: R7 (100 ohm) / R11 (10K) with ratio 0.99 is actually a series resistor + pulldown on a PWM output, not a signal-conditioning divider
  (signal_analysis.voltage_dividers)
- NRST pin flagged as connected to Neopixel net - this is likely a net naming/mapping error in the legacy parser, NRST would not be intentionally connected to a Neopixel data line
  (signal_analysis.design_observations)
- MOSFET load_type reported as led for all 4 channels - these are general-purpose PWM outputs for fans/heaters/LEDs, not specifically LED loads
  (signal_analysis.transistor_circuits)

### Missed
- AP2127K-3.3 LDO (U2) not detected as power regulator despite being present in BOM with correct value
  (signal_analysis.power_regulators)
- No SWD debug interface detection despite SWDIO net being classified as debug
  (signal_analysis)
- Neopixel/WS2812 level-shifted output circuit not characterized
  (signal_analysis)

### Suggestions
- Filter out voltage dividers where ratio > 0.95 (effectively just a pulldown) or flag them differently
- Verify NRST net assignment in legacy parser - may be a pin mapping error
- Improve power regulator detection for SOT-23-5 LDO packages like AP2127K

---
