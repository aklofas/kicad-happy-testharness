# Findings: Seeed-Studio/OSHW-reCamera-Series / reCamera_Sensor_Board_S1_OV5647_PCB_V1.1_reCamera S101 v1.1

## FND-00000147: reCamera S101 v1.1 is a camera sensor board with OV5647 image sensor (connected via FPC), NS4150B Class-D audio amplifier, and two SGM2036S LDO regulators (2.8V for sensor analog, 1.5V for sensor core). 92 components, 92 nets. The analyzer correctly identifies the LDOs, 5 transistor circuits, 7 RC filters, and the crystal circuit. However, the OV5647 camera sensor interface (MIPI CSI-2) is completely missed.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: repos/OSHW-reCamera-Series/reCamera_Sensor_Board_S1_OV5647/PCB_V1.1/reCamera S101 v1.1.kicad_sch
- **Related**: KH-047
- **Created**: 2026-03-14

### Correct
- Two SGM2036S LDO regulators correctly identified: 2.8V variant for camera analog supply (CAM_2V8) and 1.5V variant for camera core supply (CAM_1V5)
- 5 transistor circuits detected - likely level shifters and power switches for camera module control
- 7 RC filters detected - some are likely camera clock/data line filtering
- Crystal circuit detected (likely the camera reference clock oscillator)
- 4 decoupling groups correctly identified for the multiple power domains (1V8, 3V3, CAM_1V5, CAM_2V8)
- Power rails correctly enumerate the camera power domains: 1V8, 3V3, CAM_1V5, CAM_2V8, VIN
- NS4150B correctly identified as Class-D audio amplifier in subcircuit analysis

### Incorrect
- All 92 components have category=None despite correct component_types in statistics
  (components[*].category)

### Missed
- MIPI CSI-2 camera interface not detected. The OV5647 connects via MIPI CSI-2 differential data lanes (at least 2 lanes + clock) which are a critical high-speed interface. No bus analysis identifies this.
  (design_analysis.bus_analysis)
- Camera sensor power sequencing not identified. OV5647 requires specific power-up order (DOVDD->AVDD->DVDD) controlled by the transistor switches and LDOs.
  (signal_analysis)
- I2C SCCB interface for camera sensor configuration not explicitly detected (OV5647 uses SCCB which is I2C-compatible)
  (design_analysis.bus_analysis)
- FPC connector interface to main board not characterized as a board-to-board connection carrying MIPI, I2C, power, and control signals
  (design_analysis)

### Suggestions
- MIPI CSI-2 detection could look for differential pair patterns with names containing CSI, MIPI, CAM, or D0P/D0N lane naming
- Camera sensor power domain analysis could identify multi-rail designs with sequencing requirements
- SCCB/I2C detection on camera sensor boards is a common pattern worth identifying

---
