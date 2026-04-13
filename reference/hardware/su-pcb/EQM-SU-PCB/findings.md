# Findings: hardware/su-pcb / EQM-SU-PCB

## FND-00000288: AcubeSAT satellite payload PCB (371 components). I2C SDA lines (TWD0/TWD1) misclassified as SCL. OP484 quad opamps (8 thermistor channels) missed due to +IN_A/-IN_A pin naming. INA228 current sense high/low nets reversed. Opamp feedback T-network resistors falsely detected as voltage dividers. DRV8825 stepper driver not in bridge_circuits.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: EQM-SU-PCB.kicad_sch.json
- **Created**: 2026-03-16

### Correct
- SPI bus correctly identified with FGDOS and MCU
- CAN buses correctly identified (CAN0/CAN1 with TCAN337GD)
- I2C pull-ups R107/R108/R106/R109 (4.7k to +3V3) correctly identified
- 7 NTC thermistor bias divider networks correctly identified
- INA228 current sense with R64 (50mohm shunt) correctly identified
- Crystal Y5 (32.768kHz) with C9/C10 load caps correct
- TCXO oscillators Y1-Y4 correctly classified as active_oscillator
- 6 MOSFET transistor circuits correctly identified
- ESD protection D1 on USB_VCC correctly identified
- RC valve coil snubbers (50ohm/100nF) correctly detected
- DACC_USB DAC smoothing filter (R70=1k, C48=3.9u, 40.81Hz) correct

### Incorrect
- I2C SDA lines (I2C_TWD0, I2C_TWD1) both misclassified as line='SCL' — SAM V71 TWD=SDA, TWCK=SCL; all 4 I2C entries report SCL
  (design_analysis.bus_analysis.i2c)
- INA228 current sense high/low nets reversed: high_net=PUMP_VCC_SENSE and low_net=+12V, should be swapped (IN+ connects to +12V side, IN- to load side)
  (signal_analysis.current_sense)
- Voltage dividers falsely detected from opamp feedback T-networks (R156/R148, R158/R150 with ratio ~0.001 from opamp output/inverting-input)
  (signal_analysis.voltage_dividers)
- RC filter duplicate entry: R70+C49 reported in reverse direction alongside correct R70+C48 entry (shared-node bidirectional detection)
  (signal_analysis.rc_filters)
- INA228 (IC3) false missing-decoupling warning for +12V — IC3 supply is +3V3, +12V is only the measured rail
  (signal_analysis.design_observations)
- CAN protected-supply signals falsely flagged as needing level shifters — same 3.3V rail through load switch
  (design_analysis.cross_domain_signals)

### Missed
- MT29F64G NAND flash not detected as memory interface despite full EBI bus
  (signal_analysis.memory_interfaces)
- DRV8825 stepper motor driver not detected in bridge_circuits
  (signal_analysis.bridge_circuits)

### Suggestions
- I2C: TWD pins should map to SDA, TWCK to SCL (SAM/AVR convention)
- Opamp pin detection: also match +IN_x/-IN_x prefix convention
- Current sense: determine high/low from IN+/IN- pin names, not topology heuristics
- Suppress voltage dividers from opamp feedback T-networks (ratio ~0.001)
- Fix decoupling warning: don't flag measured rails, only supply rails

---
