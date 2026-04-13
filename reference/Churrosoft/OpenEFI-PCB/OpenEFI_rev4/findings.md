# Findings: Churrosoft/OpenEFI-PCB / OpenEFI_rev4

## FND-00002520: Complex automotive ECU (339 components, 8 sheets, STM32F407, TPS5430 + AMS1117 + REF3033 power chain). Strong analysis overall. Issues: LT4363 surge stopper misclassified as regulator, LED resistor networks not traced, A4988 stepper driver missed, Graphic symbol as switch.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OpenEFI_rev4_OpenEFI_rev4.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- TPS5430 switching regulator with L1, feedback divider R68/R70 correctly identified
- AMS1117-3.3 LDO and REF3033 voltage reference correctly identified
- Y1 (25MHz) and Y3 (32.768kHz) crystals with load caps correctly detected
- 8-channel RC filter bank for analog inputs correctly detected
- CAN bus with differential pair and SPI bus correctly detected
- R21 (0.01R) current sense with U6 correctly detected
- U26 SP720ABTG ESD protection for 14 analog channels correctly identified

### Incorrect
- SYM1 (Graphic:SYM_Hot_Small) classified as 'switch' — should be 'graphic', no electrical function
  (statistics.component_types)
- U6 LT4363 surge stopper classified as 'ic_with_internal_regulator' — it's an OV/OC protection controller driving external MOSFET Q10, not a regulator. FB sets OV trip threshold (1.5V ref), not regulated output.
  (signal_analysis.power_regulators)
- 16 LEDs (D16-D77) flagged as 'direct_drive' with no current limiter — actually limited through RN1-RN4 (1k resistor network arrays). Analyzer doesn't trace R_Pack04 as series elements.
  (signal_analysis.led_audit)

### Missed
- U23 A4988 stepper motor driver module not detected in motor_drivers
  (signal_analysis.motor_drivers)
- TC4424A (U21/U24/U29/U30) MOSFET gate drivers for ignition coils not detected
  (signal_analysis.transistor_circuits)
- U36 MAX9926 VR sensor interface not detected in sensor_interfaces
  (signal_analysis.sensor_interfaces)

### Suggestions
- Classify Graphic:* lib_id as 'graphic' not 'switch'
- Add LT4363/LT4356 to protection_devices, not regulators
- Trace R_Pack/R_Array resistor networks as LED series limiters
- Add A4988/DRV8825 stepper driver detection to motor_drivers

---
