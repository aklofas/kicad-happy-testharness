# Findings: Alcyone-0022/hotdoggu_smolSlimeVR / hotdoggu_smolSlimeVR

## FND-00002128: USB-C CC pulldowns R2/R3 (value '5.1k, 1%') not recognized as valid 5.1k pulldowns due to value parsing failure; Correctly identifies I2C bus with SDA/SCL pull-ups, LP5907 LDO regulator topology, a...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_hotdoggu_smolSlimeVR_hotdoggu_smolSlimeVR.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The I2C bus detection finds SDA and SCL nets connecting U2 (LSM6DSV16X IMU) to U1 (ESP32-C3-MINI-1) with R13/R14 (10k) pull-ups to +3V3 — all correct. The power_regulators detector identifies U4 (LP5907MFX-3.3) as an LDO with input_rail=VIN and output_rail=+3V3, correctly estimating 3.3V output from the part name suffix. The power_budget correctly estimates 250mA load on +3V3 (ESP32-C3 at 240mA + LSM6DSV at 10mA). The MCP73831 is correctly identified as a battery management IC with function='battery management'.

### Incorrect
- R2 and R3 are wired as CC1 and CC2 pulldowns to GND on the USB-C connector J1 (TYPE-C-31-M-12). Their values are '5.1k, 1%'. The component parser returns parsed_value=None for this format (comma+tolerance suffix not handled), while R5 with value '5.1k' correctly parses to 5100.0. As a result the usb_compliance check reports cc1_pulldown_5k1: fail and cc2_pulldown_5k1: fail when the pulldowns are actually present and correct. This is a false negative — the device is USB-C power delivery compliant for device/sink role.
  (usb_compliance)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002129: layer_count reported as 4 instead of 2 due to Syncthing conflicted-copy files doubling the copper layer count; Conflicted-copy gerber files in directory not detected or warned about

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_hotdoggu_smolSlimeVR_hotdoggu_smolSlimeVR_Gerber.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The hotdoggu_smolSlimeVR_Gerber directory contains Syncthing conflict copies of every gerber file (e.g., 'hotdoggu_smolSlimeVR-F_Cu (conflicted copy 2025-03-27 113857).gbr' alongside the canonical 'hotdoggu_smolSlimeVR-F_Cu.gbr'). The analyzer parses all 18 files in the directory, finding 4 files that match the .Cu pattern (2 F.Cu + 2 B.Cu), and sets layer_count=4. Both gbrjob files (the canonical and its conflict copy) correctly report LayerNumber=2. The PCB also uses only 2 copper layers. The layer_count=4 output is a false positive caused by duplicate files that the analyzer does not filter by filename uniqueness.
  (layer_count)

### Missed
- The gerber directory contains 18 files, 9 of which are Syncthing conflict copies identifiable by '(conflicted copy YYYY-MM-DD HHMMSS)' in the filename. The analyzer processes all 18 without warning. This causes the statistics.gerber_files count of 18 (vs the expected 9), doubles the flash/draw counts, and inflates the layer_count to 4. The analyzer should detect filenames matching common conflict-copy patterns (Syncthing, Dropbox, etc.) and either skip them or issue a warning, since submitting conflicted gerbers to a fab would produce incorrect boards.
  (statistics)

### Suggestions
(none)

---
