# Findings: RISCBoy / board_riscboy_reva0_fpgaboy

## ?: RISCBoy Rev A0 (fpgaboy) is the earlier revision with iCE40-HX4K FPGA, GS74116 SRAM, NCP1532 dual switching regulator, BQ21040 charger, CP2102N USB-UART, and W25Q16 SPI flash. Analyzer produced good results on regulators and protection but missed memory interfaces and had many single-pin net false positives.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: board_riscboy_reva0_fpgaboy.sch.json

### Correct
- NCP1532 (U5) correctly detected as switching regulator with input_rail=PWR_EN
- Voltage divider R17/R18 (450k/100k) at ratio 0.182 correctly detected as feedback divider for NCP1532 SW2 output (3.3V rail)
- Voltage divider R19/R20 (100k/100k) at ratio 0.5 correctly detected as feedback divider for NCP1532 SW1 output (1.2V rail)
- Audio voltage divider R15/R14 (680/220) at ratio 0.244 on AUDIO_PWM net feeding P4 headphone jack is correct
- ESD protection D3, D4 (DF2B7AFS) on USB_DP and USB_DM correctly detected, plus D5 on +5V rail
- RC-networks R8/C5 and R7/C3 at ~16 kHz on +1V2 rail correctly detected as PLL supply filters
- DSC60XX (U2) correctly identified as active oscillator
- USB data nets USB_DP/USB_DM correctly flagged with ESD protection present (D3/D4)
- Decoupling coverage across 4 rails (+BATT, +5V, +3V3, +1V2) correctly tallied

### Incorrect
- Single-pin nets reports 38 nets, but many are SRAM address/data bus signals (SRAM_A13, SRAM_~WE, etc.) which connect U1 (iCE40) to U3 (GS74116) across hierarchical sheets. These are legitimate multi-pin nets that appear single-pin due to cross-sheet connectivity parsing issues
  (signal_analysis.design_observations)
- NCP1532 regulator detected with input_rail=PWR_EN, but PWR_EN is actually the enable control signal, not the power input. The actual input is +BATT
  (signal_analysis.power_regulators)
- Decoupling observations repeatedly flag U8 (74LVC2G04) as missing caps on PWR_EN rail. PWR_EN is a logic signal, not a power rail, so decoupling is not expected
  (signal_analysis.design_observations)

### Missed
- BQ21040 (U4) is a LiPo battery charger IC not detected in bms_systems
  (signal_analysis.bms_systems)
- W25Q16 (U6) SPI flash connected to iCE40 FPGA (U1) not detected in memory_interfaces
  (signal_analysis.memory_interfaces)
- GS74116 (U3) 4Mbit SRAM connected to iCE40 FPGA (U1) via parallel address/data bus not detected in memory_interfaces
  (signal_analysis.memory_interfaces)
- CP2102N (U7) USB-UART bridge not classified or noted in design_observations
  (signal_analysis.design_observations)

### Suggestions
- Fix single-pin net detection to properly handle cross-sheet hierarchical connections in KiCad 5 legacy format
- NCP1532 pin mapping: distinguish VIN/PVIN power inputs from EN enable inputs
- Add BQ21040 to bms_systems/charger detection

---
