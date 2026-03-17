# Findings: tokay-lite-pcb / ai-camera-rev2_ai-camera-rev2

## FND-00000278: Tokay-lite AI camera rev2 (ESP32, 176 components). Multiple issues: Q8 false LED driver association (no net connectivity to D7). 3 TVS diodes (BSD5C051L) missed in protection_devices. USB-C CC pull-down check fails despite correct 5.1k resistors (relies on net names not connectivity). MT9284 LED driver misclassified as voltage regulator with output_rail=VBUS. I2C bus_analysis reports has_pull_up=false despite pull-ups present.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ai-camera-rev2_ai-camera-rev2.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Power regulators correctly detected (SY8089 buck, RT9166 LDO, XC6206 LDO)
- Q1/Q2 bidirectional I2C level shifters correctly identified
- USB D+/D- differential pair correctly detected

### Incorrect
- Q8 AO3401A false led_driver for D7/R25 — D7 is on net __unnamed_32 (USR_LED), Q8 drain is on __unnamed_4; no connectivity. R25 (215k) is Q10 gate pull-down, not LED current resistor
  (signal_analysis.transistor_circuits)
- protection_devices empty — D3/D4/D5 BSD5C051L TVS diodes on USB D-/D+ and +5V all missed
  (signal_analysis.protection_devices)
- USB-C CC pull-down check reports fail for cc1 and cc2 — R8/R9 (5.1k) are correctly wired but CC nets are anonymous (__unnamed_46/33), checker uses net name matching
  (design_analysis.usb_compliance)
- Q5/Q7/Q9 has_snubber=true false positive — R18 (215k) is an open-drain pull-up, not a snubber
  (signal_analysis.transistor_circuits)
- I2C bus_analysis has_pull_up=false for CAM.SDA/SCL despite R29/R30 (10k to +3V3) present; design_observations correctly detects them
  (design_analysis.bus_analysis.i2c)
- U11 MT9284-28J LED driver misclassified as switching regulator with output_rail=VBUS and estimated_vout=2.8V — drives 10 IR LEDs, not a voltage output
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- LED driver association requires net connectivity between transistor drain and LED
- TVS detection should scan diodes with 'TVS' in keywords
- USB CC check should trace connectivity from CC pins, not rely on net names
- Snubber detection should require low R (<1k) in RC pair across drain-source
- Reconcile I2C pull-up detection between bus_analysis and design_observations
- LED driver ICs should not be classified as voltage regulators

---

## FND-00000279: Tokay-lite AI camera rev3.1 (176 components). Same issues as rev2. Additionally, U8/U7 input_rail degrades to __unnamed_0 (was +3.3VA in rev2 — power label removed in this revision).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: ai-camera-rev3.1_ai-camera-rev3.1.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Power regulators correctly detected

### Incorrect
- Same Q8 false LED driver, TVS missed, CC check fail, snubber false positive, I2C pull-up inconsistency, MT9284 misclassification as rev2
  (signal_analysis)
- U8/U7 input_rail=__unnamed_0 instead of named rail — +3.3VA label removed between rev2 and rev3.1
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- When regulator input rail is unnamed, infer name from upstream ferrite bead connection to named rail

---
