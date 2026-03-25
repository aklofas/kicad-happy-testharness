# Findings: hardware / mainboard_mainboard_smd

## FND-00002115: SPI bus not detected despite nets named 11_MOSI0, 13_LED_SCK0, 10_CS0, 12_MISO0, 0_MOSI1, 1_MISO1, 6_CS1 existing in the design; Six separate I2C entries reported instead of grouping paired SDA/SCL...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hardware_mainboard_mainboard_smd.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The design has three I2C buses on the Teensy-LC (ports 0 and 1 plus a third). The analyzer reports 6 individual I2C line detections (3 SDA + 3 SCL entries) rather than pairing them into 2-3 complete buses. Two of the six entries lack pull-up resistors (SCL1 on 22_A8_SCL1 and SDA1 on 23_A9_SDA1) while their paired lines do have pull-ups; this pairing relationship is lost in the flat list output.
  (design_analysis)

### Missed
- The design uses a Teensy-LC (U1) with two SPI buses. Nets are named with Teensy pin numbers prepended to the signal name (e.g., '11_MOSI0', '13_LED_SCK0', '10_CS0', '12_MISO0'). The SPI bus detector returned zero results. The issue is that the detector does not recognise signal names where a numeric prefix precedes the canonical name (MOSI, MISO, SCK, CS). The SPI LCD connector J9 is wired to these nets, making this a clear miss.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002116: MOSFET high-side switching circuit correctly detected with gate resistor, LM358 gate driver, flyback diodes, and current-sense resistors

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hardware_solenoid_driver_compact.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Both IRLZ34N N-channel MOSFETs (Q1, Q2) are correctly identified as mosfet type with gate resistors R3/R4 (1k), LM358 op-amp as gate driver, flyback diodes D1/D2, and source-side current-sense resistors R1/R2 (1 ohm). The LM358 units are correctly identified as open-loop comparator configuration driving the gates. The L7805 linear regulator converting +12V to +5V is also correctly detected.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
