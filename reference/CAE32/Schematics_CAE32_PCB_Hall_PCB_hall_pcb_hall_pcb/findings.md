# Findings: CAE32 / Schematics_CAE32_PCB_Hall_PCB_hall_pcb_hall_pcb

## FND-00000418: Local signal label 'Vout' incorrectly listed as a power rail

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Schematics_CAE32_PCB_Hall_PCB_hall_pcb_hall_pcb.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The schematic uses a local label 'Vout' to connect U1's OUTPUT pin (Hall sensor digital output) to J1 pin 2 and C1. It is a signal net, not a power rail. The analyzer includes it in statistics.power_rails alongside '+3V3' and 'GNDREF', which is wrong. Only nets driven by power symbols or PWR_FLAG should appear in power_rails.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000419: D5 (SMF5V0A TVS diode on VBUS) missing from protection_devices; HX711 units (U5, U6, U7) misclassified as having an internal voltage regulator topology; SCLK net of SPI bus misclassified as I2C in ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Schematics_CAE32_PCB_Pedals_Pedals.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The HX711 is a 24-bit ADC specifically designed for weigh scales and load cell interfaces. Its VFB pin is the feedback pin for its built-in excitation voltage regulator for the load cell bridge supply — not a general-purpose power regulator. Classifying U5, U6, and U7 under power_regulators with topology 'ic_with_internal_regulator' is technically triggered by the VFB feedback divider pattern but is misleading: these are ADC/amplifier ICs, not regulators. The estimated_vout of 2.063V attributed to HX711 is a heuristic misread of the ADC bridge excitation circuit.
  (signal_analysis)
- The net '/0187334c-67e7-4c37-9e56-a2c4a9ea8c19/SCLK' is the SPI clock signal connecting U1 (STM32F072) to U3 (ADC128S102). The bus_analysis.spi section correctly identifies this as a SPI SCK signal. However, in the net_classification cross-domain signals section, this same net is categorized as 'i2c' rather than 'spi'. The net name contains 'SCLK' which is SPI terminology (I2C uses SCL), and the SPI bus detection itself correctly identifies it — the mismatch in net_classification is an inconsistency.
  (design_analysis)

### Missed
- D5 is a SMF5V0A unidirectional TVS diode (SOD-123) placed on the USB VBUS line for overvoltage/ESD protection. The schematic shows it connected between the VBUS net and ground. The protection_devices list only contains D4 (VCAN26A2-03GHE3 ESD IC on D+/D-) and F2 (fuse). D5, which is explicitly a protection diode on a power rail, should also appear in protection_devices.
  (signal_analysis)

### Suggestions
- Fix: HX711 units (U5, U6, U7) misclassified as having an internal voltage regulator topology
- Fix: SCLK net of SPI bus misclassified as I2C in net_classification

---
