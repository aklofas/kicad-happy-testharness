# Findings: RISCBoy / board_riscboy_revb0_riscboy

## ?: RISCBoy Rev B0 is an FPGA handheld game console with RP2040, iCE40-HX8k FPGA, CY7C1041 SRAM, two W25Q16JV SPI flash chips, stereo audio, MIC23050 switching regulators, and NCP115 LDO. Analyzer produced excellent results across nearly all detection categories.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: board_riscboy_revb0_riscboy.kicad_sch.json

### Correct
- Two MIC23050 switching regulators correctly detected: U2 (MIC23050-4YML) with L1 outputting +1V2 from +BATT, and U5 (MIC23050-SYML) with L2 outputting +3V3 from +BATT
- U7 (NCP115ASN330) correctly detected as LDO with input +BATT and output +3.3VA
- Voltage dividers R7/R11 (330/100 ohm, ratio 0.23) and R8/R12 (330/100 ohm) correctly detected on STEREO_L_DC and STEREO_R_DC audio bias nets
- Crystal Y1 (12M) with load caps C14 (10p) and C16 (10p) giving effective 8pF load correctly calculated
- High-pass RC filters R14/C24 and R15/C25 at 15.39 Hz correctly detected - these are audio coupling/DC-blocking for stereo channels
- RC-networks R18/C36+C39 and R21/C42+C43 at 331.57 Hz on VPLL0/VPLL1 to +1V2 correctly detected as PLL supply filters for the FPGA
- Memory interfaces correctly detected: U3 (W25Q16JV) connected to U1 (RP2040) with 6 shared signals, and U11 (W25Q16JV) connected to both U10 (iCE40) and U1 (RP2040)
- Speaker circuit LS1 correctly detected with series resistor R9 (27 ohm) and driver IC U8 (74LVC2G04)
- Decoupling analysis correctly shows 6 rails with appropriate cap counts: +3V3 has 16 caps (6.2uF total), +1V2 has 7 caps (5.3uF)
- USB data lines USB_D+/USB_D- correctly flagged as lacking ESD protection
- 12 switches (SW1-SW12) correctly classified as gamepad buttons

### Incorrect
- U4 (MCP73831-SOT-23-5) is a LiPo battery charger IC but not detected in bms_systems or power_regulators. The charger manages the +BATT rail
  (signal_analysis.bms_systems)

### Missed
- CY7C1041CV33 (U9) is a 4Mbit async SRAM connected to the iCE40 FPGA (U10) - should appear in memory_interfaces but is absent, likely because it uses parallel bus (not SPI) which the detector may not handle
  (signal_analysis.memory_interfaces)
- U4 (MCP73831) LiPo charger with PROG resistor for charge current setting is a common battery management circuit worth detecting
  (signal_analysis.bms_systems)

### Suggestions
- Add MCP73831/MCP73832 to bms_systems or charger IC detection
- Consider detecting parallel SRAM interfaces (address/data bus pattern) in memory_interfaces

---
