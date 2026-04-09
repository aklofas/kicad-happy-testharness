# Findings: Sierra-Lobo/mainboard-hardware / revC-fm_mainboard

## FND-00002518: 632-component PyCubed satellite mainboard (ATSAMD51, 4x LoRa, LT3652HV solar chargers, TPS63070 buck-boost, INA230 current monitors). Good structural parsing. Issues: TPS63070 classified as LDO, LT3652 chargers missed by battery_chargers, 5 INA230 current monitors undetected, addressable LEDs missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: revC-fm_mainboard.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- 632 components, 654 nets, 8 sub-sheets correctly parsed
- Y1 (32.768kHz) crystal with load caps correctly detected
- R11/R12 battery voltage divider correctly found with ratio 0.258
- LT3652HV feedback dividers correctly identified as feedback networks
- SWD debug interfaces on P2/P3 correctly detected
- USB ESD protection (ESD321, TVS0500) correctly identified
- 4 LoRa transceivers correctly found in rf_chains
- Level shifters U2/U3 (SN74LVCH245A) correctly identified

### Incorrect
- U20/U17 (TPS630701, buck-boost) classified as LDO — have external inductors L5/L6 not detected
  (signal_analysis.power_regulators)
- U11/U13 (LT3652HV) estimated_vout=1.523V wrong — LT3652 is battery charger with Vref=3.3V not 0.6V
  (signal_analysis.power_regulators)
- U20 compensation_capacitors contains 30+ unrelated caps (MCU decoupling, crystal loads)
  (signal_analysis.power_regulators)

### Missed
- battery_chargers empty but U11/U13 (LT3652HV) and U15 (BQ25883) are charger ICs
  (signal_analysis.battery_chargers)
- 5 INA230 current monitors (U9/U10/U16/U19/U23) not detected
  (signal_analysis.current_sense)
- U6 (MAX708) voltage supervisor IC missed — only RC reset detected
  (signal_analysis.reset_supervisors)
- LED12-15 (SK68xx NeoPixel) addressable LEDs missed
  (signal_analysis.addressable_led_chains)
- U22 (TPS54226) feedback divider not found, estimated_vout=None
  (signal_analysis.power_regulators)
- 4 MCP9700A temperature sensors missed
  (signal_analysis.sensor_interfaces)

### Suggestions
- Detect battery charger ICs by BOM description ('BAT CHG') and known part families (LT3652, BQ25883)
- Recognize INA230/219/226 as current sense monitors
- Classify TPS63070 as buck-boost based on inductor pin connections, not LDO
- Detect supervisor ICs (MAX708/MAX809) by pin names (~RESET, ~WDI, PFI)

---
