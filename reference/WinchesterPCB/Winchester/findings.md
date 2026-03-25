# Findings: WinchesterPCB / Winchester

## FND-00001969: Component counts and power rail detection are accurate; USB differential pair DP/DM correctly detected; Crystal Y1 detected in signal_analysis; LM1881 (video sync separator IC) misclassified as 'in...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Winchester.sch.json
- **Created**: 2026-03-24

### Correct
- Total 89 components, 43 unique parts, power rails (+5V, +5VA, +5VB, +12VA, +12VB, +3.3V, -5V, GND) all correctly identified from KiCad 5 legacy format. 13 transistors (MUN5230DW1T1G), 25 capacitors, 22 resistors, and 6 mounting holes all counted correctly.
- The USB D+ and D- lines (nets DP/DM with sub-variants DP1/DM1/DP2/DM2) are correctly identified as a differential pair via the FE1.1s USB hub IC. The pair is flagged as lacking ESD protection, which is accurate.
- The 12 MHz crystal (ECS120, ref Y1) is correctly found in signal_analysis.crystal_circuits. The frequency is null because the value 'ECS120' is a part number rather than a numeric frequency string, which is expected for legacy KiCad 5 parts.

### Incorrect
- LM1881 is Texas Instruments' video sync separator IC, but the analyzer classifies it as type 'inductor'. The reference prefix 'LM' is not a standard KiCad L-prefix for inductors, but the footprint or lib_id lookup falls through and the part gets binned as inductor. It should be 'ic'. This inflates the inductor count to 2 and understates the IC count.
  (statistics)
- THS7376 is a 4-channel video amplifier IC from Texas Instruments, but the analyzer classifies it as 'transformer'. The lib_id 'WinchesterSymbols:THS7376-WinchesterSymbols' is from a custom library not in the standard KiCad library, so the fallback classification picks up the part name pattern incorrectly. It should be 'ic'. The transformer count (1) is entirely a false positive.
  (statistics)
- L1 has value 'Logo' and footprint 'Winchester:v1' — it is a PCB logo/artwork footprint, not an electrical inductor. The analyzer assigns type 'inductor' purely based on the L prefix of the reference designator. It should be classified as 'graphic' or 'other', consistent with LOGO1 which is correctly classified as 'graphic'.
  (statistics)
- COMPONENT1 has value 'PJRAN' and footprint 'Winchester:PJRAN'. PJRAN is a DB25/JAMMA-style arcade joystick connector, not a capacitor. The analyzer assigns type 'capacitor' presumably because the fallback logic matches something in the value or footprint name. It should be 'connector' or 'other'.
  (statistics)

### Missed
- The schematic has two INA260 current/power monitor ICs (INA260-1, INA260-2) connected to SCL and SDA nets, forming a clear I2C bus. The net_classification correctly labels SCL as 'clock' and SDA as 'data'. However, bus_analysis.i2c is empty. The failure is likely because INA260 is in a custom library (WinchesterSymbols) and its pin names are not matched against the I2C detector's known-device list. The Teensy 4.1 (U7) is also an I2C master on this bus.
  (design_analysis)

### Suggestions
(none)

---

## FND-00001970: Board dimensions, layer stack, and routing completeness all correct; DFM board size violation correctly flagged; board_outline.area_cm2 is null — not computed for KiCad 5 board with arc edges

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Winchester.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 2-layer board (F.Cu, B.Cu), 135.05×85.84 mm, 89 footprints, 996 track segments, 248 vias, 2 copper zones, routing complete with 0 unrouted nets. All correctly extracted from KiCad 5 legacy format (file_version 20171130).
- The board is 135.05×85.84 mm which exceeds the 100×100 mm JLCPCB standard tier limit. The DFM analysis correctly identifies this as a 'board_size' violation requiring a higher fabrication pricing tier.

### Incorrect
- The board outline has 13 edges including 4 arcs (rounded corners). The area_cm2 field in board_outline is null, meaning the analyzer did not compute the area. The bounding box is present (135.05×85.84 mm = ~115.9 cm²) but the actual polygon area is not calculated. This is likely a KiCad 5 format issue or an arc-handling limitation in the area computation routine.
  (board_outline)

### Missed
(none)

### Suggestions
(none)

---
