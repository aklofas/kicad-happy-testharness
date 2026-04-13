# Findings: EanNewton/Awesome-Keebs / pcb files_torn-master_torn_left

## FND-00000389: LEDs L1, L2, L3 classified as 'inductor' instead of 'led'; QR1 (Graphic:SYM_Arrow45_Small) classified as 'transistor'; GND net falsely detected as I2C SDA bus line for MCP23017; Key matrix estimate...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb files_torn-master_torn_right_torn_right.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Components L1, L2, L3 use the KiCad library symbol Device:LED with value 'LED' and footprint footprints:LED_D3.0mm. These are clearly indicator LEDs. The analyzer incorrectly maps the reference prefix 'L' to the inductor type, ignoring that the lib_id is Device:LED. This results in component_types reporting 'inductor: 3' instead of a proper LED count. LEDs are diodes in the signal sense but the misclassification causes them to appear in the inductor category.
  (statistics)
- QR1 uses the symbol Graphic:SYM_Arrow45_Small with footprint footprints:torn_qr_code — it is a purely graphical/mechanical element representing a QR code silkscreen. The analyzer classifies it as 'transistor', which is incorrect. It should be 'mechanical', 'graphic', or 'other'. Note that PUCK1 uses the same lib_id (Graphic:SYM_Arrow45_Small) but is classified as 'connector', showing inconsistency — two instances of the same lib_id get different type classifications.
  (bom)
- The bus_analysis.i2c array contains a third entry with net='GND', line='SDA', devices=['U2','U2','U2']. GND is the ground power rail, not an I2C signal line. The MCP23017 (U2) has address pins A0/A1/A2 that are tied to GND in the schematic, but GND should never be reported as an I2C SDA bus net. This is a false positive caused by the analyzer matching GND pins of U2 against I2C SDA detection logic.
  (design_analysis)
- The schematic has 19 SW_Push switches and 3 Rotary_Encoder_Switch devices (SW28, SW41, SW44), giving 22 total matrix switches. The analyzer reports switches_on_matrix=24 and estimated_keys=24. The overcount by 2 occurs because rotary encoders SW41 and SW44 each have both their B and C encoder pins connected to different COL nets (SW41 appears on both COL6 and COL7; SW44 appears twice on COL9). Each such encoder is counted twice in the matrix switch tally instead of once.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: LEDs L1, L2, L3 classified as 'inductor' instead of 'led'
- Fix: QR1 (Graphic:SYM_Arrow45_Small) classified as 'transistor'

---

## FND-00000390: Key matrix estimated_keys overcounted: reports 25, actual matrix keys is 24

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb files_torn-master_torn_left_torn_left.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The left half has 21 SW_Push (including PB1/RESET and PB2/BOOT) and 3 Rotary_Encoder_Switch, for 24 total switches. The key matrix should contain 19 SW_Push + 3 rotary = 22 true keyboard switches, but the analyzer reports switches_on_matrix=25 and estimated_keys=25. The overcount by 1 occurs because PB2 (the BOOT push button) is wired to the same node as the ROW2 net in the schematic (via the GND/boot circuit at coordinates ~3650,6200 connecting through to the ATmega), so the matrix detector counts PB2 as a keyboard matrix switch. PB2 is not a keyboard key.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
