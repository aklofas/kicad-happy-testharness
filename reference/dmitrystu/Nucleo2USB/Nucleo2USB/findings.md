# Findings: dmitrystu/Nucleo2USB / Nucleo2USB

## FND-00000969: USB D+/D- differential pairs on OTG connectors not detected; ESD protection ICs (ESDAxxSC6) correctly detected on both OTG USB buses; PMEG2010EJ Schottky diodes (D1-D3) misclassified as reverse_pol...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Nucleo2USB.sch.json
- **Created**: 2026-03-23

### Correct
- U3 protects OTGFS_DN/OTGFS_DP and U4 protects OTGHS_DN/OTGHS_DP, both detected as esd_ic type protection devices with correct net listings.

### Incorrect
- D1, D2, D3 are PMEG2010EJ Schottky diodes used as power path ORing diodes (common anode on VBUS inputs, cathode to +5V0 bus), not reverse polarity protection. They are forward-biased power-path selectors, not reverse-polarity clamps. The protected_net and clamp_net are both '+5V0' which is wrong for a protection device.
  (signal_analysis)

### Missed
- X1 and X2 are USB-OTG connectors with D+/D- signals routed through 22Ω series resistors to the STM32 USB FS and HS peripherals. differential_pairs[] is empty. The design also has ESD protection (U3/U4 ESDAxxSC6) on both USB buses. The USB buses should be detectable as differential signal paths.
  (signal_analysis)

### Suggestions
(none)

---
