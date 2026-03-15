# Findings: ESP32-C3-DevKit-Lipo / HARDWARE_ESP32-C3-DevKit-Lipo_Rev_B_ESP32-C3-DevKit-Lipo_Rev_B

## FND-00000119: OLIMEX ESP32-C3 dev board with LiPo charging. Power domains and IC identification empty despite detecting SY8089 buck and BL4054B charger in BOM. Subcircuit neighbors empty. USB data lines detected but no ESD protection noted.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/ESP32-C3-DevKit-Lipo/HARDWARE/ESP32-C3-DevKit-Lipo_Rev_B/ESP32-C3-DevKit-Lipo_Rev_B.sch
- **Created**: 2026-03-14

### Correct
- Component types correctly classified - 52 components, ICs, caps, resistors, diodes all properly typed
- Power rails correctly identified: +3.3V, +5V, +5V_USB, VBAT, GND
- UART TX/RX correctly detected on GPIO20/GPIO21
- USB D+/D- data lines detected with no ESD protection flag (correct observation)
- BOM entries accurate - BL4054B charger, SY8089 buck, ESP32-C3-MINI-1-N4 all present

### Incorrect
- Power domains ic_power_rails and domain_groups are completely empty despite 3 ICs (U1 BL4054B, U2 SY8089, U3 ESP32-C3) being present and power rails being detected
  (design_analysis.power_domains)
- All 3 subcircuits have empty neighbor lists - neighbor detection failed
  (subcircuits)

### Missed
- SY8089 buck converter not detected in power_regulators despite being in BOM with inductor available
  (signal_analysis.power_regulators)
- BL4054B LiPo charger not detected - charging circuit analysis missing
  (signal_analysis)
- No crystal circuit detection (ESP32-C3 may use internal oscillator)
  (signal_analysis.crystal_circuits)
- No decoupling analysis despite 7 capacitors present
  (signal_analysis.decoupling_analysis)
- USB CC resistors (R4/R2 5.1k) not identified for USB-C current advertisement
  (signal_analysis.design_observations)
- WPM2015-3 P-MOSFET power path switch not detected
  (signal_analysis.transistor_circuits)

### Suggestions
- Investigate why power domain detection failed - may be KiCad 5 legacy pin mapping issue
- Investigate why subcircuit neighbor detection returned empty for all ICs
- Detect USB-C CC pull-down resistors (5.1k to GND on CC pins)

---
