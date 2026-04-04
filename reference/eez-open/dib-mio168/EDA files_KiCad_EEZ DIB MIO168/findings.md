# Findings: dib-mio168 / EDA files_KiCad_EEZ DIB MIO168

## FND-00000291: EEZ DIB MIO168 mixed I/O module (279 components). Negative isolated rails (-15V_ISO, -5V_ISO) omitted from isolation_barriers. Phantom per-chip SPI bus entries for IC12/IC13 (already on main MIO bus). Duplicate reset_pin observation for IC8 (3x). OPA376 buffer has spurious input_resistor from neighboring opamp's feedback network.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: EDA files_KiCad_EEZ DIB MIO168.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- Voltage dividers correctly detected: R13/R14 (1.25V reference), DIN level-shift networks (2K7+27K), PE-to-GND divider
- 14 RC filters correctly detected including DAC output post-filters and ADIB connector filters
- LP5907, L78L15, L79L15 regulators correctly identified
- OPA2196 inverting amplifiers with gain -0.121 correctly identified
- W9812G6KH-6 SDRAM memory interface correctly detected
- Q1-Q5 2N7002PS digital output switches and Q9/Q11 IRLML2246 P-FET power switches correct
- SI8641 digital isolator and WE-750315371 transformer correctly in isolation_barriers

### Incorrect
- isolation_barriers isolated_power_rails lists [+3V3_ISO, +15V_ISO, +5V_ISO] but omits -15V_ISO and -5V_ISO — both exist as isolated negative rails through rectifier/regulator chain
  (signal_analysis.isolation_barriers)
- Phantom SPI bus entries 'pin_IC12' and 'pin_IC13' — artifact entries with MIO_MISO labeled as MOSI and no chip selects, for chips already on main MIO bus
  (design_analysis.bus_analysis.spi)
- Duplicate reset_pin observation for IC8 STM32F446 NRST emitted 3 times identically
  (signal_analysis.design_observations)
- OPA376 (IC16) buffer has spurious input_resistor R17 (9K09) — R17 belongs to IC19's feedback path on shared 1V25_REF net
  (signal_analysis.opamp_circuits)

### Missed
(none)

### Suggestions
- Isolation detector should include negative rails (-15V_ISO, -5V_ISO) in isolated_power_rails
- SPI bus grouping should not create per-chip entries for ICs already assigned to a bus
- Deduplicate design_observations by component reference
- Opamp input_resistor attribution should verify the resistor connects to the specific opamp's input, not just a shared net

---
