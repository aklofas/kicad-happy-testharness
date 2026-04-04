# Findings: Arduino_LMeter_shield / Arduino_LMeter_shield

## FND-00000371: LC oscillator circuit not detected; RC high-pass filter false positive on BJT emitter degeneration network; Duplicate I2C bus entries for Arduino A4/A5 analog pins; OLED display not counted as I2C ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Arduino_LMeter_shield.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer detects an RC high-pass filter at 72.34 kHz comprising R3 (2k2) and C2 (1n) with input_net '__unnamed_0' and output_net 'GND'. In reality, R3 is the emitter degeneration resistor of Q1 and C2 is a coupling/bypass capacitor in the oscillator tank circuit between the collector (__unnamed_4) and a shared node (__unnamed_0). The circuit is not functioning as a filter with an intentional signal path from __unnamed_0 to GND through R3; R3 sets the emitter DC operating point.
  (signal_analysis)
- The Arduino UNO R3 symbol has both dedicated I2C pins (pin 31 SDA/A4 and pin 32 SCL/A5, connected to the OLED M1) and analog-pin duplicates (pin 13 SDA/A4 and pin 14 SCL/A5, unconnected with no-connect marks). The analyzer produces 4 I2C bus entries: real SCL and SDA nets, plus __unnamed_38 (A4 duplicate) and __unnamed_39 (A5 duplicate). The unnamed nets have only single-pin connections to no-connect stubs and are not real bus segments.
  (design_analysis)

### Missed
- The design is an inductance meter that uses Q1 (2SC3356 NPN BJT), L1 (1uH), C2 (1n), C4 (1n), and R1/R2/R4 to form an LC oscillator whose frequency is measured by the 74HC590 counter to determine unknown inductance. The analyzer reports lc_filters:[], crystal_circuits:[], and feedback_networks:[] — none of these detectors fires. The transistor_circuits entry for Q1 correctly identifies the BJT with emitter resistor R3 and base resistors R1/R2, but the oscillator topology (L1 in collector, tank capacitors C2/C4 coupling base to emitter) is not recognized as an LC oscillator.
  (signal_analysis)
- The OLED M1 (1.3" I2C OLED, footprint LCD_OLED_128X64_1.3_I2C) has its SCL pin connected to the SCL net and SDA pin to the SDA net, making it an I2C bus participant. The bus_analysis.i2c entries for SCL and SDA list only 'A1' in their devices arrays; M1 is absent. While M1 is a Conn_01x04 symbol without explicit I2C pin names, the footprint and net names clearly identify it as an I2C peripheral.
  (design_analysis)

### Suggestions
(none)

---
