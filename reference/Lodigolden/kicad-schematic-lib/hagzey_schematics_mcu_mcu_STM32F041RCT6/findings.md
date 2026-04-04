# Findings: kicad-schematic-lib / hagzey_schematics_mcu_mcu_STM32F041RCT6

## FND-00002264: STM32F041RCT6 MCU schematic parsed as empty (0 components, 0 nets)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematic-lib_hagzey_schematics_mcu_mcu_STM32F041RCT6.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The analyzer produced zero components, zero nets, and zero wires for this schematic. The file is a KiCad 9.0 (.kicad_sch) format schematic that contains an STM32F041RCT6 MCU with supporting circuitry. This is most likely a schematic that uses a custom symbol library (hagzey_symbols) and the analyzer failed to extract any components from it. The STM32 MCU, its decoupling caps, crystal, and connectors should all be present but nothing was captured.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002265: M24C02 EEPROM (CR1) misclassified as 'diode' due to 'CR' reference prefix; I2C bus not detected despite explicit I2C.SCL and I2C.SDA net names

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematic-lib_hagzey_schematics_memory_eeprom_eeprom_M24C02_WMN6TP.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The M24C02-WMN6TP 8-pin I2C EEPROM is assigned reference 'CR1' by the designer and is classified as type 'diode' throughout the output (component_types shows 'diode: 1', BOM type is 'diode', category is 'diode'). The component is clearly an EEPROM IC with 8 pins (VCC, GND, SCL, SDA, E0-E2, WC). The 'CR' prefix is non-standard but the device is categorically an integrated circuit or memory device, not a diode. The misclassification propagates to the assembly_complexity section which counts it as 'other_SMD' and simulation_readiness which treats it as simulatable. The component type should be determined by the symbol's pin structure and lib_id ('hagzey_symbols:eeprom_M24C02-WMN6TP') rather than just the reference prefix.
  (statistics)

### Missed
- The nets 'I2C.SCL' and 'I2C.SDA' are present and correctly identified in net_classification (as 'clock' and 'data' respectively). The M24C02 EEPROM's SCL and SDA pins are connected to these nets. However, design_analysis.bus_analysis.i2c is empty — no I2C bus was detected. The analyzer should recognize this as an I2C bus based on the net names and the device's pin names. The single_pin_nets warning for I2C.SCL and I2C.SDA is correct (they're hierarchical labels connecting outward), but the I2C interface itself should still be detected.
  (design_analysis)

### Suggestions
(none)

---

## FND-00002266: LDO output rail reported as '__unnamed_0' rather than '+3V3' due to ferrite bead on output

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-schematic-lib_hagzey_schematics_power_ldo_ldo_3v3_TCR2EF33_LMCT.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The TCR2EF33 LDO VOUT pin connects to an unnamed internal net (the junction between VOUT, C2, and FB1 pin 1). The named '+3V3' power rail is on the other side of FB1. The analyzer correctly identifies the LDO topology and estimates Vout=3.3V from the part suffix, but reports output_rail as '__unnamed_0' in power_regulators. The design_observations also flag a missing output cap because C2 is on the unnamed net, not on '+3V3'. In reality C2 is the output decoupling cap — just separated from the '+3V3' label by the ferrite bead. The analyzer should trace through ferrite beads to associate the output rail with the named net.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
