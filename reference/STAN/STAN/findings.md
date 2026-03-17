# Findings: STAN / STAN

## FND-00000213: STAN (Sentinel Tinkering and Analysis Node) - a retro computer board with STM32F401VCTx MCU, IS61C5128AS SRAM, S29GL064S70TFI040 NOR flash, bus buffers, and USB-C interface. The analyzer correctly identified the LDO regulator, USB ESD protection, crystal circuit, and decoupling. It missed memory interfaces due to bus buffer indirection and incorrectly classified control signals as power rails.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STAN.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U8 TLV76133DCY correctly detected as LDO regulator with input_rail=USB_VBUS and output_rail=+3.3V
- U9 USBLC6-2P6 ESD protection correctly detected on USB_DP, USB_DM, and USB_VBUS nets
- Crystal Y1 (X50328MSB2GI) correctly detected with 2x 20pF load caps (C6, C9) giving effective CL=13pF, flagged as in_typical_range=true
- Low-pass RC filter R5 (47k) / C16 (0.1uF) at 33.86 Hz correctly detected on +3.3V rail
- 13 decoupling caps on +3.3V rail (15.8uF total including C1 4.7uF bulk and C20 10uF) correctly analyzed with has_bulk=true, has_bypass=true
- U1 STM32F401VCTx correctly detected as ic_with_internal_regulator topology in power_regulators
- USB data lines USB_DP and USB_DM correctly flagged with has_esd_protection=true via U9
- Missing input cap warning for U8 TLV76133DCY on USB_VBUS rail correctly flagged in regulator_caps observation

### Incorrect
- PWR_ON and PWR_OK listed as power_rails in statistics, but these are logic control signals from U7 AP22816KC USB load switch (enable output and power-good indicator), not power supply rails
  (statistics.power_rails)
- Decoupling observation flags U7 AP22816KC and U1 STM32F401VCTx as missing caps on PWR_ON and PWR_OK rails, but these are logic signals not power rails requiring decoupling
  (signal_analysis.design_observations)

### Missed
- U4 IS61C5128AS-25TLI (512Kx8 SRAM) and U6 S29GL064S70TFI040 (64Mbit NOR flash) not detected in memory_interfaces. They connect to U1 STM32F401VCTx through bus buffers (U10/U8/U11/U9 74ALVC16245DG, U15/U16 74AHC16373DG) rather than directly, which prevents detection.
  (signal_analysis.memory_interfaces)

### Suggestions
- Detect memory interfaces through bus buffers by tracing signal paths transitively (memory -> buffer -> processor)
- Filter control signals (EN, PG, ON, OK suffixed nets from load switch/regulator ICs) from power_rails list
- Detect USB load switches (AP22816, TPS2051, etc.) as power management devices
- Detect bus buffer arrays (74xx245, 74xx373, 74xx541) as bus topology indicators

---
