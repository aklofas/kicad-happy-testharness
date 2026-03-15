# Findings: Power_HW / ElonMux_ElonMux

## FND-00000157: Power generation sub-sheet of ElonMux power mux design with LTC3126 buck converter. Vout estimation wrong due to heuristic Vref; BQ25756E feedback divider missed; lib_name/lib_id mismatch causes 0-pin parsing.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ElonMux_Power - Generation.kicad_sch.json
- **Related**: KH-083, KH-084
- **Created**: 2026-03-15

### Correct
- LTC3126 detected as switching regulator

### Incorrect
- LTC3126 estimated_vout=2.41V using assumed Vref=0.6V -- actual Vref=0.8V (VSET pins to GND), correct Vout=3.3V matching +3V3 output rail
  (signal_analysis.power_regulators)
- IC801/IC802 LTC7000EMSE gate drivers have 0 pins parsed due to lib_name/lib_id mismatch -- lib_symbols keyed by local name but lookup uses lib_id
  (ic_pin_analysis)
- Bootstrap cap + power inductor misidentified as RF matching network in GEODE power_auxiliary
  (signal_analysis.rf_matching)

### Missed
- BQ25756E feedback divider R711 (249k) / R713 (14k) from +VCHARGE_O to FB to FBG missed -- divider detector expects GND as bottom net, not dedicated FBG pin
  (signal_analysis.voltage_dividers)
- R701/R702 (5 milliohm, 1W) current sense resistors on ACP/ACN and SRP/SRN pins not detected
  (signal_analysis.current_sense)
- TPS3701DDCR (IC803) function not classified -- should be 'voltage supervisor' or 'voltage detector'
  (ic_pin_analysis)
- Regulator output_rail is null despite FB pin connecting through divider to +3V3 net
  (signal_analysis.power_regulators)

### Suggestions
- Voltage divider detector should accept dedicated feedback ground pins (FBG, AGND, etc.) as bottom reference
- Fix lib_name/lib_id mismatch: try lib_name first, then lib_id for lib_symbol lookup
- Add TPS370x to voltage supervisor/detector classification

---
