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
- Crystal load caps not found for any of 4 crystals
  (signal_analysis.crystal_circuits)
- TCVCXO (SCO-F998_OSC81_40MHz) classified as crystal -- should be oscillator (lib_id root_2_TCVCXO)
  (signal_analysis.crystal_circuits)

### Suggestions
- Footprint-based override: TP* footprint should force test_point classification regardless of ref prefix
- Lib_id keywords TVSD/TVS should override T->transformer fallback
- Filter out title blocks (no pins, no electrical function) from regulator detection
- Part number Vout parsing should handle 12V suffix as 12V, not as divisor

---
