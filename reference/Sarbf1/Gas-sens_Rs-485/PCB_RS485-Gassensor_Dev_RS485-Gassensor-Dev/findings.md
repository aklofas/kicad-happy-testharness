# Findings: Sarbf1/Gas-sens_Rs-485 / PCB_RS485-Gassensor_Dev_RS485-Gassensor-Dev

## FND-00000203: Development version of the RS485 gas sensor board, nearly identical to the production version with same dual-MCU design, opamp signal conditioning, and RS485 interface. Minor differences include extra connectors (J10-J12) and one fewer capacitor. Same analysis issues as the production board.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: PCB_RS485-Gassensor_Dev_RS485-Gassensor-Dev_RS485-Gassensor-Dev.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- 6 opamp circuits correctly identified matching the production board: U3 (MCP6002) for CO, U6 (MCP6002) for NO, U9 (AD8676) for output buffering
- U6 unit 2 correctly identified as comparator_or_open_loop for NO2 output (slight difference from production board where it was transimpedance_or_buffer)
- Voltage dividers R14/R9 and R27/R28 correctly detected identically to production board
- RC filters R17/C8 and R15/C4 (1k/470nF, fc=338.6Hz) correctly detected for PWM smoothing
- U4 (OKI-78SR-5) and U5 (AP2127N-3.3) correctly identified as power regulator chain
- 12 connectors correctly counted (2 more than production board: J10, J11, J12 for development headers)

### Incorrect
- Same false current_sense detection: R12 (R220) with U7 (LT1785) is RS485 bus resistor, not current shunt
  (signal_analysis.current_sense)
- Same OKI-78SR voltage estimation error: estimated_vout=1.5V instead of 5V
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Same fixes needed as production board variant - RS485 transceiver exclusion from current sense, OKI-78SR part number parsing, and hierarchical net decoupling resolution

---
