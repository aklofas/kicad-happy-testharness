# Findings: openwrt-one / OpenWrt_ONE

## FND-00000156: OpenWrt One router with MT7981B SoC, MT7976C WiFi, EN8811 2.5G Ethernet. Altium-imported design with unannotated components. 60% false-positive rate on regulators; ref prefix classifier fails on Altium naming.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OpenWrt_ONE.kicad_sch.json
- **Related**: KH-079, KH-080
- **Created**: 2026-03-15

### Correct
(none)

### Incorrect
- TPD? (34 instances) classified as transformer -- should be test_point (footprint TP0_3mm, lib_id contains TP-SMD)
  (statistics.component_types)
- TVD? (8 instances) classified as transformer -- should be TVS diode (PAM02SD2303C for Ethernet ESD, lib_id contains TVSD)
  (statistics.component_types)
- SO? (2 instances) classified as switch -- SMTSO-M2 standoffs are mechanical hardware, not switches
  (statistics.component_types)
- CLIP? (32 instances) classified as capacitor -- SHIELD_CLIP components are RF shield clips, not capacitors
  (statistics.component_types)
- 24 of 40 regulators are false positives: 8x BLOCK_BPI_2 title blocks, 6x repeated MT7981B SoC, plus flash/RTC/EEPROM/logic ICs
  (signal_analysis.power_regulators)
- AP7366-W5-7 inconsistently classified as switching in some sheets but correctly as LDO in others
  (signal_analysis.power_regulators)
- POE-RT5400-12V has estimated_vout=1.2 -- parsed '12V' suffix as denominator giving 1.2V instead of 12V
  (signal_analysis.power_regulators)
- All switching regulators share identical rail names input_rail=DVDD33, output_rail=EN_1V8 -- rail assignment collapses across sheets
  (signal_analysis.power_regulators)

### Missed
- Zero voltage dividers detected across the entire design despite multiple feedback networks for buck converters
  (signal_analysis.voltage_dividers)
- Zero Ethernet interfaces detected -- EN8811 PHY + SQ24015-1PG/SG24002G magnetics + RJ45 connectors present
  (signal_analysis.ethernet_interfaces)
- Zero memory interfaces detected -- MT7981B to NT5AD512M16C4-JR DDR4 interface present
  (signal_analysis.memory_interfaces)
- Zero RF chains/matching detected -- MT7976C WiFi has SAW filters, BPFs, diplexers, matching inductors, MMCX connectors
  (signal_analysis.rf_chains)

### Suggestions
- Footprint-based override: TP* footprint should force test_point classification regardless of ref prefix
- Lib_id keywords TVSD/TVS should override T->transformer fallback
- Filter out title blocks (no pins, no electrical function) from regulator detection
- Part number Vout parsing should handle 12V suffix as 12V, not as divisor

---

## FND-00002509: OpenWrt ONE is a MediaTek MT7981B Wi-Fi 6 router with MT7976C radio, Airoha EN8811 2.5GbE PHY, DDR4, dual SPI flash, PCIe M.2, and USB 2.0. Analyzer traverses all 8 sub-sheets (994 components, 1005 nets) but has significant gaps: DDR4/Ethernet PHY/RF chain all undetected, 26 UART false positives from WiFi/Ethernet net name matching, and total_components reflects only 38 BOM lines instead of 994 instances.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: OpenWrt_ONE.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- SPI buses correctly detected: SPI0 with 2 chip selects (NOR + NAND flash), plus SPI1 and SPI2
- PCIe differential pairs correctly identified for M.2 Key-M slot
- HSGMII Ethernet differential pairs correctly identified between MT7981B and EN8811
- I2C buses correctly identified for RTC (AT8563S) and EEPROM (P24C02A)
- HT42B534 USB-to-UART bridge correctly identified
- All 8 sub-sheets correctly resolved

### Incorrect
- statistics.total_components = 38 but actual instance count is 994. Reflects unique unannotated reference prefixes (BOM lines) not instances.
  (statistics.total_components)
- CN? prefix (8 connector instances) misclassified as 'capacitor' because 'C' prefix fires before 'CN'.
  (statistics.component_types)
- USB ESD inconsistency: design_observations says has_esd_protection: false while differential_pairs says has_esd: true for same USB nets.
  (signal_analysis.design_observations)
- JTAG_JTCK and JTAG_JTMS falsely detected as I2C SDA/SCL lines.
  (design_analysis.bus_analysis.i2c)

### Missed
- DDR4 memory interface not detected despite 58 EMI0_* nets connecting MT7981B to NT5AD512M16C4-JR.
  (signal_analysis.memory_interfaces)
- EN8811 2.5GbE Ethernet PHY not detected despite HSGMII and SMI_MDC/MDIO connections.
  (signal_analysis.ethernet_interfaces)
- MT7976C Wi-Fi 6 radio entirely absent from rf_chains despite AFE0_WF* analog front-end nets.
  (signal_analysis.rf_chains)
- 26 of 30 UART detections are false positives: WiFi TX gain rails (AVDD18_WF3_TX_GA), Ethernet PHY nets (TXVP_A), SGMII nets.
  (design_analysis.bus_analysis.uart)
- Most power regulators missed: only one AP7366 detected, missing SY8089AAAC, MP8756GD, LA1314HD, LA3484A.
  (signal_analysis.power_regulators)

### Suggestions
- Fix total_components to use component instance count, not BOM line count for unannotated designs.
- Add 'CN' as connector prefix before 'C' capacitor catch-all.
- Narrow UART detection: exclude nets with TX/RX substrings from WiFi/Ethernet power and data domains.
- Detect DDR4 via EMI_*/DQ/DQS/CK net patterns even with unannotated refs.
- Detect EN8811 Ethernet PHY by part number matching.

---
