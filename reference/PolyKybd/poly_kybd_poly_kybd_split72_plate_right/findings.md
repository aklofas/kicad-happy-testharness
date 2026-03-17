# Findings: PolyKybd / poly_kybd_poly_kybd_split72_plate_right

## FND-00000292: PolyKybd keyboard mainboard (KiCad 5, 83 components). K_P/K_N key signals falsely detected as differential pair. MCU U2 falsely listed as USB ESD protection. Level-shifter false alarms for shift register signals (same 3.3V domain). WS2812B LED chain count severely undercounted (2 chains of 1 instead of ~100+).

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: backup_poly_kb_mainboard_poly_kb.sch.json
- **Created**: 2026-03-16

### Correct
- XC6206P332MR LDO (U1) input +5V, output +3.3V correctly identified
- Crystal Y1 16MHz with 12pF load caps, effective 9pF correct
- 3 I2C buses correctly flagged as missing pullup resistors
- RC filter R2+C1 (10k/1u, 15.92Hz) on NRST correct
- Polyfuse F1 (2A) correctly identified on VCC rail
- SPI buses with W25N01G NAND flash correctly detected
- ERC no_driver warnings for misrouted pins (FLASH_NHOLD on VREF+, FLASH_NWP on VCAP_2) are genuine schematic errors

### Incorrect
- K_P/K_N (individual keyboard key signals P and N) falsely detected as differential pair — single-character _P/_N suffix match too aggressive
  (design_analysis.differential_pairs)
- U2 (STM32F407 MCU) falsely listed as USB ESD protection device — no actual TVS/ESD array on USB lines
  (design_analysis.differential_pairs)
- SHIFTR_CLK/DATA/LATCH_CLK falsely flagged as needing level shifters — STM32 VDD pins resolve to unnamed nets instead of +3.3V, creating false cross-domain appearance vs 74HCT595 on same 3.3V rail
  (design_analysis.cross_domain_signals)
- Spurious RC filter R9(22ohm)+C1(1u) at 7.23kHz — R9 is SWD debug header series protection, C1 is shared NRST cap
  (signal_analysis.rc_filters)

### Missed
- Key matrix not detected — KRow0-7/KCol0-20 GPIO matrix exists but switch components are on keyboard daughterboard, not in parsed sheets
  (signal_analysis.key_matrices)

### Suggestions
- Differential pair matching: require longer common prefix, not single-character _P/_N
- Don't attribute ESD protection to MCU on USB nets — require dedicated TVS/diode lib_id
- Resolve unnamed MCU VDD nets to named supply rail before cross-domain analysis
- When sub-sheet file has multiple AR Path instances, multiply LED chain length by instance count

---
