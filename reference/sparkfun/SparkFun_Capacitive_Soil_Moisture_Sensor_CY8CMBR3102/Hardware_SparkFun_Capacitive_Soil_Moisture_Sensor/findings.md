# Findings: sparkfun/SparkFun_Capacitive_Soil_Moisture_Sensor_CY8CMBR3102 / Hardware_SparkFun_Capacitive_Soil_Moisture_Sensor

## FND-00001418: I2C pull-up resistors on SCL/SDA not detected (same jumper-traced pull-up miss as VEML7700); Component count (30), IC U1 (CY8CMBR3102 capacitive touch sensor), and I2C bus topology correctly identi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SparkFun_Capacitive_Soil_Moisture_Sensor.kicad_sch
- **Created**: 2026-03-24

### Correct
- total_components=30 matches the BOM: 4 caps, 2 LEDs, 4 fiducials, 2 logos, 2 connectors (J1/J2 Qwiic RA), 2 jumpers, 5 resistors, 2 mounting holes (ST2/ST4), 4 test points (TP4-TP7), 1 IC (U1 CY8CMBR3102). The CY8CMBR3102 is an 8-input capacitive sensing IC correctly typed as 'ic'. The TO_CAP_PLATE net is visible in the net_classification, correctly identified as a signal net (this is the electrode connection to the capacitive sensor plate).

### Incorrect
- This design has R1 (4.7k) on SCL and R2 (2.2k) on SDA as I2C pull-ups, both switchable via JP2 (I2C solder jumper). The analyzer reports has_pullup=false, pullup_resistor=null for both SCL and SDA bus lines. The net data confirms R1 pin 2 connects to SCL, and R2 pin 2 to SDA, with the other ends of R1/R2 going through JP2 to 3.3V. This is the same failure mode as VEML7700 — the analyzer fails to trace pull-up topology through a 3-pin solder jumper to the power rail.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001419: Board dimensions reported as null despite the gerber showing measurable extents (~15x76mm elongated sensor probe shape)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SparkFun_Capacitive_Soil_Moisture_Sensor.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- board_width_mm=null, board_height_mm=null in the PCB statistics. The gerber analysis reports F.Cu extents of 15.087x75.948mm, and B.Cu extents of 15.087x25.14mm, consistent with a narrow elongated PCB with a ~76mm tall probe and a ~25mm circuit section. The board outline likely uses a non-rectangular or curved shape for the probe, which the PCB analyzer fails to parse into bounding dimensions. This is a real data gap — the null dimensions prevent automated size checks.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001420: GKO (Edge.Cuts) file misclassified as layer_type 'B.Mask', causing false 'Edge.Cuts missing' completeness warning; Drill classification correctly identifies 20 vias (0.3mm) and 2 NPTH mounting hole...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Hardware
- **Created**: 2026-03-24

### Correct
- drill_classification shows vias.count=20 with 0.3mm diameter (matching PCB via_count=21 — within 1, likely one via is at a panel edge), component_holes.count=0 (correct — the CY8CMBR3102 is SMD, as is all other circuitry), and mounting_holes.count=2 with 3.1mm NPTH (matching ST2/ST4 from schematic). The smd_ratio=1.0 in pad_summary confirms all component pads are SMD. Total hole_count=22 in drill file matches vias(20)+mounting(2).

### Incorrect
- SparkFun_Capacitive_Soil_Moisture_Sensor.GKO is assigned layer_type='B.Mask' and carries FileFunction='Soldermask,Bot' in its x2_attributes, but it contains 163 draw_count segments (vs 12 for the actual B.Mask GBS file) and has a Profile aperture function (by_function.Profile=1) — the hallmarks of an Edge.Cuts file. The completeness check reports missing_required=['Edge.Cuts'] as a result. This is the same GKO misclassification bug seen in the VEML7700 gerbers — the x2 FileFunction attribute on the .GKO file is incorrect or absent, causing the layer to be misidentified. The alignment warning ('Height varies by 50.8mm') is a downstream consequence, since the actual board outline is not being used to validate layer extents.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---
