# Findings: OtterCam-s3 / OtterCam-s3

## FND-00000166: Allwinner S3-based camera board top-level sheet. U.FL connector classified as IC, Ethernet nets misidentified as UART, WiFi module as regulator.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OtterCam-s3.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U1 Allwinner S3 SoC correctly identified as main IC
- U3 SY8089 buck converter correctly identified as regulator
- SDIO bus interfaces correctly detected
- MIPI differential pairs correctly identified
- Crystal oscillators correctly detected
- TVS protection devices correctly classified

### Incorrect
- AE1 U.FL antenna connector classified as IC instead of connector
  (components)
- EPHY_TX/RX Ethernet PHY nets misidentified as UART interface
  (signal_analysis.bus_interfaces)
- AP6236 WiFi/BT module classified as voltage regulator
  (signal_analysis.power_regulators)
- AXP209 PMIC estimated_vout 4.8V is incorrect
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Recognize U.FL and similar antenna connector footprints as connectors, not ICs
- Distinguish EPHY_ prefixed nets as Ethernet, not UART
- Do not classify WiFi/BT combo modules (AP6236, ESP32, etc.) as regulators
- Improve PMIC output voltage estimation for multi-output PMICs like AXP209

---

## FND-00000167: OtterCam-s3 power sub-sheet with AXP209 PMIC and SY8089 buck. AXP209 vout wrong, USB ESD marking inconsistent, VINT misclassified.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Power.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- SY8089 buck converter correctly identified with proper output voltage
- TVS D4 correctly identified for USB protection
- USB-C CC pulldown resistors correctly identified
- Q1 LED driver transistor correctly identified
- RC reset filter correctly detected

### Incorrect
- AXP209 PMIC estimated_vout 4.8V is wrong for a multi-rail PMIC
  (signal_analysis.power_regulators)
- USB differential pair has_esd flag inconsistent across detections
  (signal_analysis.usb_compliance)
- VINT net classified as interrupt signal but is actually a voltage reference rail
  (signal_analysis.power_rails)

### Missed
(none)

### Suggestions
- For multi-output PMICs, list per-rail outputs instead of a single estimated_vout
- Ensure has_esd is consistent for the same USB pair across all detection passes
- Do not assume nets named VINT are interrupts; check context (power pin vs signal pin)

---

## FND-00000180: OtterCam-s3 ESP32-S3 camera board main sheet. Correct: Allwinner S3, SY8089 buck, SDIO buses, MIPI pairs, crystals, TVS. Incorrect: AE1 U.FL connector as IC, EPHY nets as UART, AP6236 WiFi as regulator, AXP209 vout 4.8V wrong. Missed: Ethernet PHY interface, I2C SCL line, DDR memory interface.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OtterCam-s3.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U1 AllWinner-S3 correctly identified with 234 pins
- U3 SY8089 correctly detected as switching regulator
- Two SDIO buses correctly detected
- 5 MIPI differential pairs detected

### Incorrect
- AE1 U.FL antenna connector classified as IC (should be connector)
  (bom.type)
- EPHY_TX/RX Ethernet PHY nets misidentified as UART
  (design_analysis.bus_analysis.uart)
- AP6236 WiFi module classified as power regulator
  (signal_analysis.power_regulators)
- AXP209 estimated_vout 4.8V incorrect (programmable PMIC)
  (signal_analysis.power_regulators)

### Missed
- Ethernet PHY interface not detected
  (signal_analysis.ethernet_interfaces)
- DDR memory interface not detected
  (signal_analysis.memory_interfaces)

### Suggestions
- Recognize U.FL/coaxial connectors by Connector_Coaxial footprint
- Add EPHY prefix to Ethernet detection, exclude from UART
- Do not classify WiFi/BT modules as regulators

---

## FND-00000181: OtterCam-s3 Power sub-sheet (70 components). Correct: SY8089 buck, TVS D4, USB-C CC pulldowns, Q1 LED driver, RC reset filter. Incorrect: AXP209 vout 4.8V wrong, USB diff pair has_esd inconsistent, VINT classified as interrupt (is voltage ref), USB_DRV classified as high_speed. Missed: Multiple AXP209 output rails not enumerated.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Power.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U3 SY8089 correctly detected with feedback divider R29/R30
- D4 P6SMB6.8CA TVS correctly detected on +5V
- USB-C CC 5.1k pulldowns pass

### Incorrect
- AXP209 estimated_vout 4.8V wrong (programmable PMIC)
  (signal_analysis.power_regulators)
- USB differential pair has_esd inconsistent with protection_devices
  (design_analysis.differential_pairs)
- VINT (voltage reference) classified as interrupt
  (design_analysis.net_classification)

### Missed
- AXP209 multiple output rails not enumerated (only +3V3 reported)
  (signal_analysis.power_regulators)

### Suggestions
- For multi-output PMICs, detect all output rails
- Fix has_esd to check protection_devices
- Do not classify VINT as interrupt

---
