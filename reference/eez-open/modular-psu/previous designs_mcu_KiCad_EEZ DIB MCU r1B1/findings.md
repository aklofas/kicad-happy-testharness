# Findings: eez-open/modular-psu / previous designs_mcu_KiCad_EEZ DIB MCU r1B1

## FND-00000186: EEZ DIB MCU r1B2 (189 components, 6 hierarchical sheets). Correct: STM32F769 176 pins, Ethernet PHY, SDRAM, LD1117 LDO, TPS61169, ESD protection, USB pairs. Incorrect: STM32F769 power pins mapped to wrong signal nets (systematic multi-unit pin-swap bug), SPEED1/TOUCH1/VBUS1 LEDs misclassified (switch/transformer/varistor), ZD1/ZD2 TVS as other, IC4 duplicated 4x in power_regulators, crystal feedback R/C detected as RC filter, VLED+/- as differential pair. Missed: crystal load caps, SPI/SDMMC/JTAG buses, voltage dividers.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: EEZ_DIB_MCU_r1B2.sch.json
- **Created**: 2026-03-15

### Correct
- IC4 STM32F769 correctly identified with 176 pins across 4 units
- IC17 DP83848 Ethernet PHY detected
- IC5 LD1117 correctly detected as LDO

### Incorrect
- IC4 STM32F769 power pins grossly misassigned to FMC/LTDC signal nets
  (nets)
- SPEED1 LED classified as switch, LCD1 as inductor, TOUCH1 as transformer, VBUS1 as varistor
  (components)
- IC4 listed 4x in power_regulators (once per unit)
  (signal_analysis.power_regulators)

### Missed
- Crystal Y1 load caps C8/C9 not detected
  (signal_analysis.crystal_circuits)
- SPI/SDMMC/JTAG buses not detected
  (design_analysis.bus_analysis)

### Suggestions
- Fix multi-unit pin-to-net mapping for legacy KiCad 5 with Eagle-imported libraries
- Deduplicate multi-unit IC entries in power_regulators
- Detect LEDs by lib_id/footprint patterns not just reference prefix

---

## FND-00000187: EEZ DIB MCU r1B1 — all 189 components extracted but ALL have 0 pins and ALL 181 nets have empty pin lists. Root cause: r1B1-cache.lib prefix mismatch with sub-sheets referencing r1B2-eagle-import. Signal analysis almost completely empty. Same component misclassifications as r1B2.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: EEZ_DIB_MCU_r1B1.sch.json
- **Created**: 2026-03-15

### Correct
- All 189 unique components extracted with correct references and values
- IC17 Ethernet PHY detected even without pin data

### Incorrect
- All 284 component instances have 0 pins (cache library prefix mismatch)
  (components)
- All 181 nets have empty pins arrays
  (nets)
- Same LED misclassifications as r1B2
  (components)

### Missed
- All signal analysis empty due to missing pin connectivity
  (signal_analysis)

### Suggestions
- Fall back to fuzzy matching when cache library prefix does not match lib_id prefix
- Attempt bus detection from net name patterns even without pin data

---
