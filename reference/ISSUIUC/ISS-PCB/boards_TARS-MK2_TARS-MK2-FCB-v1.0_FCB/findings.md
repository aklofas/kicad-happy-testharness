# Findings: ISS-PCB / boards_TARS-MK2_TARS-MK2-FCB-v1.0_FCB

## FND-00000153: Flight computer with OSD3358 SiP, MIMXRT1062, sensors, LoRa, GPS. Good basic parsing but SPI-as-I2C false positives, LDO inverting flag errors, and TVS IC detection gaps.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: boards_TARS-MK2_TARS-MK2-FCB-v1.0_FCB.kicad_sch.json
- **Related**: KH-082
- **Created**: 2026-03-15

### Correct
- Crystal Y101 40MHz with load caps correctly detected
- CAN bus detection with MCP2518FDT and TCAN337G correct
- USB differential pair detection correct

### Incorrect
- TLV75733PDRV LDOs (U305, U505) marked as inverting=true -- TLV757xx is a standard positive fixed-output LDO
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Add Power_Protection library components to protection_devices detection
- Fix LDO inverting flag -- TLV757xx and similar fixed-output LDOs should not be marked inverting

---
