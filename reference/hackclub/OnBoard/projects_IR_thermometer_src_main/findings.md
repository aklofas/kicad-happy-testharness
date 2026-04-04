# Findings: OnBoard / projects_IR_thermometer_src_main

## FND-00000100: IR thermometer with MLX90614 sensor, SEEED XIAO MCU, SPX2920 LDO regulator, and SSD1306 OLED. Good overall detection.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/OnBoard/projects/IR_thermometer/src/main.kicad_sch
- **Created**: 2026-03-14

### Correct
- SPX2920M3-3.3 correctly identified as LDO regulator with input from battery switch and output to 3v3 rail
- I2C bus correctly detected between SEEED XIAO (U2) and MLX90614 (U1) on mlx scl/mlx sda nets
- MLX90614ESF-BCF-000-TU correctly identified as IC type
- Battery input and external switch connectors correctly identified

### Incorrect
(none)

### Missed
- OLED display (J2, labeled oled, Conn_01x04_Pin) is a 4-pin I2C OLED module but not detected as an I2C device in bus analysis since it uses generic connector symbols
  (design_analysis.bus_analysis)

### Suggestions
- The I2C pull-up resistor detection shows has_pull_up: false. Should verify whether the MLX90614 or XIAO module has internal pull-ups, or if external pull-ups are needed.

---
