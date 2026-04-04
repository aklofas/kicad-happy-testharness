# Findings: Zynq-SoM / Zynq_SoM

## FND-00000290: Zynq XC7Z020 SoM (288 components). TPSM82864 voltage monitoring divider (R78/R79 to STM32 ADC) misidentified as regulator feedback divider. RTL8211F Ethernet interface not detected (custom lib_id). Duplicate reset_pin observations for eMMC (3x). has_high_freq=false on rails with 47nF 0201 caps (standard FPGA HF bypass).

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Zynq_SoM.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- MPM3834/MPM3822 switching regulators correctly identified
- TPS7A20 LDO correctly identified
- DDR3L SDRAM interface correctly detected
- STM32G431 system controller crystal correctly detected

### Incorrect
- TPSM82864 (U8) feedback divider misidentified — R78/R79 (100k/100k) are STM32 ADC voltage monitoring dividers on +1V0 rail, not regulator FB divider. TPSM82864 FB pin ties directly to +1V0, voltage set via VSET pin R25.
  (signal_analysis.power_regulators)
- Duplicate reset_pin observations for U7 (IS21ES08G eMMC) — emitted 3 times identically
  (signal_analysis.design_observations)
- has_high_freq=false on +1V35 with 11x 47nF/0201 caps (SRF ~23MHz) — 47nF in 0201 is standard FPGA HF bypass
  (signal_analysis.decoupling_analysis)
- TPSM82864 multi-VOUT pins flagged as multi_driver_net — internal connection of power module QFN pads is expected
  (connectivity_issues.multi_driver_nets)

### Missed
- RTL8211F Ethernet PHY interface not detected — custom lib_id MyLibrary:RTL8211F-CG not matched by Ethernet detector
  (signal_analysis.ethernet_interfaces)

### Suggestions
- When FB pin ties directly to output rail with no divider, don't attribute separate monitoring dividers as feedback
- Deduplicate reset_pin observations by component reference
- Raise has_high_freq threshold or make it footprint-aware (47nF/0201 is HF bypass)
- Ethernet detector: match on part value (RTL8211) not just lib_id prefix

---

## FND-00002508: Zynq-7020 SoM with DDR3L, QSPI flash, eMMC, Gigabit Ethernet PHY (RTL8211F), ULPI USB PHY, STM32G431 system controller, and 5-rail switching power. Analyzer handles hierarchical design well but has significant false-positive level-shifter warnings for DDR3L and ULPI (from incomplete FPGA power domain tracking), misses Ethernet PHY and eMMC due to custom lib_ids.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Zynq_SoM.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- All five power regulators correctly detected with accurate feedback divider analysis
- DDR3L memory interface correctly identified: U1 MT41K256M16TW with 25 shared signal nets to U2 XC7Z020
- W25Q128JVS SPI flash correctly detected with 5 shared nets to Zynq
- DDR CK, DQS0, DQS1 differential pairs correctly identified with series impedance matching
- Power sequencing correctly detected: STM32 controls EN for all regulators with power-good feedback
- I2C, eMMC/SDIO buses correctly detected
- Ethernet MDI differential pairs correctly identified between RTL8211F and J1
- JTAG debug nets correctly classified

### Incorrect
- X3 (CMOS_OSC, 4-pin SMD oscillator) classified as 'crystal' instead of 'oscillator'.
  (statistics.component_types)
- 56 of 64 cross_domain_signals flagged as needs_level_shifter including all DDR3L signals. Zynq PS DDR controller natively drives DDR3L at 1.35V — no level shifter needed. Root cause: U2 power_domains only shows '+3V3'.
  (design_analysis.cross_domain_signals)
- 10 ULPI signals falsely flagged as needs_level_shifter between Zynq and USB3318 — both operate at 1.8V.
  (design_analysis.cross_domain_signals)
- RGMII Ethernet signals misclassified as 'uart' in test_coverage. SDIO signals misclassified as 'spi'.
  (test_coverage)

### Missed
- RTL8211F (U3) not detected as Ethernet PHY — uses custom MyLibrary: lib_id.
  (signal_analysis.ethernet_interfaces)
- IS21ES08G eMMC (U7) not detected in memory_interfaces — uses custom MyLibrary: lib_id.
  (signal_analysis.memory_interfaces)
- U2 XC7Z020 power domain detection severely incomplete: only '+3V3' tracked despite VCCINT (1.0V), VCCAUX (1.8V) etc.
  (design_analysis.power_domains)
- QSPI interface not detected in bus_analysis.spi despite QSPI_CLK/D0-D3/CS nets.
  (design_analysis.bus_analysis.spi)

### Suggestions
- Match Ethernet PHY by value field (RTL8211F, KSZ9031, etc.) in addition to lib prefix.
- Match eMMC by value/description keywords in addition to Memory_Flash: lib prefix.
- Fix cross_domain_signals: exclude DDR signals from level-shifter check; track all FPGA power rails across multi-unit components.
- Fix test_coverage net categorization for RGMII/SDIO signals.

---
