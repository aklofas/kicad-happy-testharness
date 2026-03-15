# Findings: ESP32-DevKit-LiPo / HARDWARE_ESP32-DevKit-LiPo-Rev.D_ESP32-DevKit-Lipo_Rev_D

## FND-00000121: OLIMEX ESP32 dev board with LiPo, CH340X USB-UART, and HX6211A LDO. Same empty power domains issue as C3 variant. Auto-program transistor circuit detected but missing relay to USB-UART bridge function.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/ESP32-DevKit-LiPo/HARDWARE/ESP32-DevKit-LiPo-Rev.D/ESP32-DevKit-Lipo_Rev_D.sch
- **Created**: 2026-03-14

### Correct
- Component classification accurate - 50 components with ICs, transistors, diodes properly typed
- Power rails correctly identified: +3.3V, +5V, +5V_USB, VBAT, GND
- Two BJT auto-program circuits (Q2, Q3 BC817-40) correctly detected as transistor_circuits
- UART TX/RX on GPIO1/GPIO3 correctly detected
- BOM accurately lists CH340X USB-UART, HX6211A LDO, BL4054B charger, ESP32-WROOM-32D

### Incorrect
- Power domains ic_power_rails and domain_groups completely empty despite 4 ICs present
  (design_analysis.power_domains)
- All 4 subcircuits have empty neighbor lists
  (subcircuits)
- TESTPAD components (D_Com1, GND1) misclassified as diodes in BOM
  (bom)

### Missed
- HX6211A LDO regulator not detected in power_regulators
  (signal_analysis.power_regulators)
- BL4054B LiPo charger circuit not analyzed
  (signal_analysis)
- CH340X USB-UART bridge function not identified
  (signal_analysis)
- BAT54C dual Schottky diode (D3) power OR-ing function not detected
  (signal_analysis)
- No decoupling analysis despite capacitors present
  (signal_analysis.decoupling_analysis)
- Auto-program circuit (Q2/Q3 DTR/RTS to GPIO0/EN) not linked to its USB-UART function
  (signal_analysis.transistor_circuits)

### Suggestions
- Fix test pad / fiducial classification - TESTPAD should not be typed as diode
- Same power domain detection issue as C3 variant - likely KiCad 5 legacy format parsing
- Detect USB-UART bridge chips (CH340, CP210x, FT232) and their auto-program circuits

---
