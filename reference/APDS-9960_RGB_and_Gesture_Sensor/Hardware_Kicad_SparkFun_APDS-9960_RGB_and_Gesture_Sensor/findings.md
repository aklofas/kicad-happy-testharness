# Findings: APDS-9960_RGB_and_Gesture_Sensor / Hardware_Kicad_SparkFun_APDS-9960_RGB_and_Gesture_Sensor

## FND-00000339: I2C pull-ups R2 and R3 not detected — both SDA and SCL report has_pullup: false; U1 SDA (pin 1) and SCL (pin 7) both land in the same unnamed net __unnamed_4 — net tracing error merges two distinct...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Hardware_Kicad_SparkFun_APDS-9960_RGB_and_Gesture_Sensor.sch.json
- **Created**: 2026-03-23

### Correct
- The nets output shows __unnamed_4 containing both U1 pin 1 (SDA) and U1 pin 7 (SCL). These are two separate I2C signals that cannot share a net. Additionally, the named 'SDA' net incorrectly shows U1 pin 4 (LEDK) and the named 'SCL' net shows U1 pin 3 (LDR) — these are IR LED pins, not I2C pins. The label-to-pin resolution for U1 is wrong in legacy KiCad 5 format.
- Both STANDOFF1 and STANDOFF2 have lib_id 'sparkfun_apds_9960:STAND-OFF' and value 'STAND-OFF'. They are mechanical PCB standoffs, not switches. The BOM also classifies them as 'switch'. This is a type classification heuristic error in the legacy KiCad 5 parser.
- JP1 has lib_id 'sparkfun_apds_9960:Conn_01x06' and value 'M06SIP' (6-pin male SIP header). It is a board-edge I/O connector carrying VCC, GND, SCL, SDA, INT, and VL signals. It should be classified as a connector, not a jumper. The jumper classification is likely triggered by the 'JP' prefix heuristic.

### Incorrect
- bus_analysis.i2c contains three entries: one for SDA, one for SCL, and a third for __unnamed_4 which incorrectly shows both U1 and U1 as 'devices' (duplicating U1 twice). This phantom net entry is a direct consequence of the net tracing error that merges U1 SDA/SCL pins into one unnamed net.
  (design_analysis)

### Missed
- R2 (4.7k) pulls SDA to VCC via solder jumper SJ1 (pin 1→pin 2), and R3 (4.7k) pulls SCL to VCC via SJ1 (pin 3→pin 2). The analyzer fails to trace pull-up topology through the jumper, leaving both I2C lines reporting no pull-up. The pull-ups are architecturally present and switchable via SJ1.
  (design_analysis)
- C1 (100uF polarized, c_2917 footprint) and C2 (1uF 0603) are both connected to the VL net which is U1's VDD supply pin. These are the primary bulk and bypass decoupling caps for the APDS-9960 sensor. The decoupling_analysis section only reports C3 (1uF) on VCC; the VL rail is completely absent. C3 is on the VCC rail (LED supply side), not VDD.
  (signal_analysis)

### Suggestions
(none)

---
