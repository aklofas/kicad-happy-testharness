# Findings: SparkFun_Ambient_Light_Sensor-VEML7700 / Hardware_SparkFun_VEML7700

## FND-00001412: I2C pull-up resistors R2 and R6 not detected as pull-ups on SCL/SDA; Component count and types correctly identified: 25 total, 1 IC (VEML7700-TT), 4 resistors, 2 caps, 2 Qwiic connectors; I2C bus c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_VEML7700.kicad_sch
- **Created**: 2026-03-24

### Correct
- statistics.total_components=25, with correct breakdown: 1 ic (VEML7700-TT), 4 resistors (R1 4.7, R2 2.2k, R3 4.7k, R6 2.2k), 2 capacitors (C1 2.2uF, C2 0.1uF), 1 LED (D1), 2 Qwiic JST connectors (J3, J5), 1 PTH I2C header (J4), 4 fiducials, 4 mounting holes, 2 jumpers, 3 graphic logos. The BOM entries match the actual component list and quantities. Power rails 3.3V and GND correctly identified.
- bus_analysis.i2c correctly enumerates two entries (SCL and SDA nets), each listing U1 as the connected device. Net classification correctly labels SCL as 'clock' and SDA as 'data'. The 13 total nets match the schematic.

### Incorrect
- R2 (2.2k) is on the SCL net (pin 1) with its other end (pin 2) connected through JP2 to the 3.3V rail. R6 (2.2k) mirrors this on SDA. These are the on-board I2C pull-ups (switchable via JP2). The analyzer reports has_pullup: false and pullup_resistor: null for both SCL and SDA in design_observations. The pull-up resistors feed through a 3-pin solder jumper (JP2) which has a middle tap connected to 3.3V — the analyzer fails to trace through the jumper to find the power rail connection, so the pull-up topology goes undetected.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001413: GKO (Edge.Cuts) gerber file misclassified as layer_type 'B.Mask'; Drill classification correctly identifies 32 vias (0.3mm), 4 PTH component holes (1.016mm), and 4 NPTH mounting holes (3.1mm)

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Production
- **Created**: 2026-03-24

### Correct
- drill_classification shows vias.count=32 with 0.3mm tool (matching PCB via_count=32), component_holes.count=4 with 1.016mm (matching the 4 PTH standoffs in the BOM), and mounting_holes.count=4 with 3.1mm NPTH (matching the 4 mounting holes ST1-ST4). Total 40 holes matches drill file hole_count=40. Classification method is x2_attributes which is authoritative.

### Incorrect
- SparkFun_VEML7700.GKO has FileFunction 'Soldermask,Bot' in the x2_attributes but the GKO extension conventionally denotes Edge.Cuts (board outline). Examining the x2_attributes shows FileFunction='Soldermask,Bot' — but this appears to be a KiCad export anomaly or the analyzer is using the x2 FileFunction attribute, which in this case is wrong (GKO is normally Edge.Cuts). The file does contain a Profile aperture function aperture (by_function.Profile=1), which is the correct Edge.Cuts indicator, but the layer_type is still assigned as B.Mask. The completeness check reports missing_required=['Edge.Cuts'] even though the GKO board outline file is present — this is a direct consequence of the misclassification.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001414: PCB dimensions (25.4x25.4mm), 2-layer stackup, 43 footprints, and routing status correctly reported

- **Status**: new
- **Analyzer**: pcb
- **Source**: SparkFun_VEML7700.kicad_pcb
- **Created**: 2026-03-24

### Correct
- board_width_mm=25.4, board_height_mm=25.4 is correct for a standard 1-inch square SparkFun Qwiic breakout. copper_layers_used=2 (F.Cu and B.Cu) matches the gerber's layer_count=2. footprint_count=43 includes 37 circuit/mechanical footprints plus kibuzzard graphic items visible in component_analysis. routing_complete=true with unrouted_net_count=0 is correct. Track count 80 segments and 32 vias are plausible for a simple sensor breakout.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
