# Findings: hackquad / ecad_hackquad_hackquad

## FND-00002110: Quad-SPI PSRAM interface (ESP32 to LY68L6400) not detected as SPI bus; Four N-channel MOSFETs driving DC motors (quadcopter) not recognized as motor drive topology; RT6150AGQW switching regulator a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hackquad_ecad_hackquad_hackquad.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies U7 (RT6150AGQW) as a switching regulator converting VBUS to +3.3V with feedback divider R12/R13 (487k/86.6k), and U9 (XC6221B132MR-G) as an LDO converting VBUS to CAM_1.2V for camera power. The estimated Vout of 3.974V for RT6150AGQW is close to the calculated value (Vref=0.6V assumed). In contrast, the KiCad 5 legacy .sch parser detects the same regulators but with wrong rails (input=REG_EN, output=None), showing clear improvement in the .kicad_sch parser.
- The main I2C bus (SDA/SCL nets) between U1 (ESP32-PICO-D4) and U6 (MPU-6050) has no pull-up resistors — confirmed by inspecting all net connections. The analyzer correctly flags has_pull_up=False for both SDA and SCL. R14 and R15 (5.1k each) are correctly identified as pull-ups on CAM_SIOD/CAM_SIOC (camera SCCB bus), not on the main I2C bus.

### Incorrect
(none)

### Missed
- U1 (ESP32-PICO-D4) connects to U4 (LY68L6400 SPI PSRAM) via a Quad-SPI interface using nets PSR_SIO0, PSR_SIO1, PSR_SIO2, PSR_SIO3, PSR_SCLK, and PSR_CE. The SPI bus detector returns an empty list because the signal names use PSR_ prefix rather than canonical MOSI/MISO/SCK/CS patterns. This is a missed SPI/QSPI bus detection.
  (design_analysis)
- Q3-Q6 (each AO3400A N-ch MOSFET) are four independent low-side switches driving motors M0-M3 (all 'Motor_DC' type) with individual flyback diodes D3, D4, D6, D7 and 1k gate resistors driven by ESP32 PWM outputs. This is a classic 4-motor brushed DC drive for a quadcopter. The analyzer correctly detects Q3-Q6 as transistor_circuits with flyback diodes and gate resistors, but motor_drivers remains empty and load_type is 'other' rather than 'motor'. The circuit would benefit from explicit motor-drive topology recognition.
  (signal_analysis)

### Suggestions
(none)

---
