# Findings: LibreSolar/data-manager / kicad_data-manager

## FND-00002310: SI8621AB-B-ISR digital isolator (U2) not detected in isolation_barriers; ERC false positives: TX_EXT/RX_EXT reported as no-driver nets, but pin context is wrong; TX_EXT/RX_EXT on J2 (RJ12 connector...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_data-manager_kicad_data-manager.sch.json
- **Created**: 2026-03-24

### Correct
- bus_analysis.can correctly identifies CAN_TX and CAN_RX nets between U1 (ESP32-WROOM-32D) and U5 (TCAN334 CAN transceiver), plus the physical CANH/CANL differential lines on U5. The 120-ohm termination resistor R6 is present in the BOM, and the overall CAN topology is correctly captured.

### Incorrect
- The ERC warnings report TX_EXT and RX_EXT as 'no_driver' nets and incorrectly associate them with GND1 (power_in) and VCC1 (power_in) pins on U2. These net-to-pin associations are wrong: TX_EXT and RX_EXT are the external-side signal pins of the SI8621AB isolator (pins 1 and 4), not the GND1/VCC1 supply pins. The analyzer is mis-mapping nets to pins due to the multi-unit or pin-order parsing of the SI8621AB.
  (signal_analysis)
- bus_analysis.uart includes nets TX_EXT and RX_EXT with J2 (6P6C RJ12 connector) as the only device. These are external RS-232/UART lines carried on the RJ12 connector going to an external device, routed through the SI8621AB isolator. While the net names happen to match UART patterns, the single-device entries (devices: []) represent only the connector, not a true UART bus between two ICs. This clutters the UART bus list with pass-through connector signals.
  (signal_analysis)

### Missed
- The design uses a Silicon Labs SI8621AB-B-ISR (U2), which is a 2-channel digital isolator creating an isolation boundary between the 3.3V domain and the VCC_EXT domain. The signal_analysis.isolation_barriers array is empty despite the part being clearly an isolation IC. The analyzer correctly observes the cross-domain VCC_EXT rail on U2 under design_observations (decoupling category), but fails to classify U2 as an isolation barrier.
  (signal_analysis)

### Suggestions
(none)

---
