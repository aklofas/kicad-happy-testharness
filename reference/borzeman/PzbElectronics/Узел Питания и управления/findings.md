# Findings: borzeman/PzbElectronics / Узел Питания и управления

## FND-00002517: Industrial food processing machine power/control unit (363 components, 25 sub-sheets, 12 IRF4905 MOSFET circuits). Major classification issue: lib_id ignored in favor of reference prefix, causing 29 LED-strip connectors as LEDs, 6 circuit breakers as capacitors, 2 DS18B20 sensors as transformers, 1 AC motor as capacitor.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: Узел Питания и управления_Узел Питания и управления.kicad_sch.json
- **Created**: 2026-04-09

### Correct
- 12 IRF4905 P-channel MOSFETs correctly identified with is_pchannel=true
- 24 TVS diodes and 25 fuses correctly identified as protection_devices
- 363 components and 669 nets correctly extracted across 25+ sheets
- K1 relay correctly classified

### Incorrect
- T1/T2 (DS18B20, lib_id Sensor_Temperature:DS18B20) misclassified as transformer due to T prefix
  (components)
- 29 LED-strip connectors (lib_id Connector:Conn_01x01_Pin) misclassified as LED due to LED prefix in reference
  (components)
- 6 circuit breakers CB1-CB6 (lib_id Device:CircuitBreaker) misclassified as capacitor due to CB prefix
  (components)
- COMPR (lib_id Motor:Motor_AC, compressor) misclassified as capacitor due to C prefix
  (components)
- QF1 (lib_id Device:Residual_current_device, RCD/GFCI) misclassified as transistor due to Q prefix
  (components)
- V_SATA_SSD (lib_id Connector:Conn_01x01_Pin) misclassified as varistor due to V prefix
  (components)

### Missed
- 12 SB560 flyback diodes across lock solenoids not detected (has_flyback_diode=false on all MOSFETs)
  (signal_analysis.transistor_circuits)
- R1-R12 gate resistors not detected for MOSFET circuits due to hierarchical net tracing gaps
  (signal_analysis.transistor_circuits)
- RS-485 bus protocol not detected despite RS485 nets and dedicated sub-sheet
  (signal_analysis)

### Suggestions
- Prioritize lib_id over reference prefix for type classification — Connector:* should always be connector, Sensor_Temperature:* not transformer, Device:CircuitBreaker not capacitor, Motor:* not capacitor
- Fix net tracing in hierarchical sheets to detect flyback diodes and gate resistors for MOSFET switches

---
