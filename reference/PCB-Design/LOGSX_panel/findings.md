# Findings: PCB-Design / LOGSX_panel

## ?: LOGSX is an earlier revision of the same GPS/LoRa tracker design (LOGSX v2). Same schematic structure with STM32F103, SX1273, TESEO-LIV3. Analyzer output is essentially identical to LOGSX v2 with the same correct detections and same errors.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: LOGSX_ArmTrax.sch.json

### Correct
- Correctly parsed 4-sheet hierarchy with 93 components matching LOGSX v2
- Crystal circuits Y1, Y2, Y3 with load caps correctly detected
- I2C bus with pullups R2, R3 correctly detected on SCL/SDA
- LC filters in radio section correctly identified

### Incorrect
- U2 (LT1129-3.3) regulator shows input_rail=GND and output_rail=GND, same error as LOGSX v2
  (signal_analysis.power_regulators)
- Same spurious RC filter detections (R7/C19, R4/C19, R4/C16) as LOGSX v2 - components not actually forming filter networks
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Same regulator and RC filter issues as LOGSX v2 - see that finding for details

---
