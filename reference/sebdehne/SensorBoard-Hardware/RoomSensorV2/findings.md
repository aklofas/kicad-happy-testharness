# Findings: sebdehne/SensorBoard-Hardware / RoomSensorV2

## FND-00001405: 3V3 power net omitted from power_rails despite being a primary supply; I2C pullup resistors R2/R3 not detected — has_pullup incorrectly false; Voltage divider (R6+R7 on V_Bat_READ) correctly identi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RoomSensorV2.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies the battery voltage monitoring divider: R6 (10k) on top from VSwitched, R7 (10k) to GND, midpoint V_Bat_READ feeding ATSAMD21 ADC pin PA22. Ratio = 0.5 is correct for equal-value resistors. The midpoint connection to U3 (ATSAMD21) is correctly noted.
- The analyzer correctly identifies R11 (100k) + C11 (100n) as a low-pass RC filter on the RESET net (supervisory reset hold-low filter). Cutoff frequency 15.92 Hz and time constant 0.01 s are mathematically correct for those values. The topology (3V3 → R11 → RESET → C11 → GND) is consistent with a reset supervisory circuit.

### Incorrect
- The schematic has a prominent 3V3 net that powers the MCU (ATSAMD21G18A-A), RTC (DS3231SN), humidity sensor, and decoupling capacitors. The power_symbols list contains only GND symbols, so the analyzer excludes 3V3 from statistics.power_rails — reporting ['GND'] only. However, 3V3 is clearly a power net (it supplies VDD to multiple ICs and has 28+ connections). This cascades into the I2C pullup detection failure (see next finding): because 3V3 is not recognized as a power rail, the pullup resistors R2 and R3 (both 4k7, connecting I2C_SDA/I2C_SCL to 3V3) are not identified as valid pullups.
  (statistics)
- signal_analysis.design_observations reports the I2C bus (I2C_SCL and I2C_SDA) with has_pullup=false. In reality, R2 (4k7) connects I2C_SDA to 3V3, and R3 (4k7) connects I2C_SCL to 3V3 — these are textbook I2C pullups. The failure is caused by 3V3 not being recognized as a power rail (see previous finding). The net path is confirmed: net 3V3 contains R2 pin 2 and R3 pin 2; nets I2C_SDA/I2C_SCL contain R2 pin 1 and R3 pin 1 respectively.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001406: Board dimensions (73 x 101 mm), 2-layer stackup, and routing status reported correctly

- **Status**: new
- **Analyzer**: pcb
- **Source**: RoomSensorV2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Board outline has 12 segments forming a non-rectangular (tabbed) outline; bounding box is correctly computed as 73.0 x 101.0 mm. 2-layer copper (F.Cu + B.Cu), 1.6 mm FR4, fully routed (routing_complete=true, unrouted=0). Net count of 81 in PCB vs 123 in the legacy .sch is expected since KiCad 5 schematic net counting includes every unnamed wire node.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
