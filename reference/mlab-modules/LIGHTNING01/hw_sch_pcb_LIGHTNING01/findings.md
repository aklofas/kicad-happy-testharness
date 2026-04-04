# Findings: LIGHTNING01 / hw_sch_pcb_LIGHTNING01

## FND-00000803: I2C bus detection for AS3935 via SCL/SDA_MOSI labels with 10k pullup resistors correct; Mounting holes (M1-M4) classified as 'other' rather than 'mounting_hole'; PWR_FLAG warnings for GND and VCC c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_LIGHTNING01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- AS3935 supports both I2C and SPI. The schematic uses SCL and SDA_MOSI net labels; analyzer correctly detects I2C bus with R5 as pullup. I2C is the primary protocol signaled by the label naming.
- The LIGHTNING01 schematic powers VCC/GND through connectors without PWR_FLAG symbols. The analyzer correctly flags both rails as lacking power_out or PWR_FLAG, which would cause ERC errors in KiCad.

### Incorrect
- The four HOLE footprint components (M1-M4) with lib_id containing 'HOLE-MLAB_MECHANICAL' are classified as type='other'. They should be 'mounting_hole'. The classifier likely misses custom/library-specific hole symbols that don't match the standard KiCad mounting hole library names.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000804: Alignment warning 'width varies by 4.9mm' is a false positive caused by copper/silk asymmetry; NPTH drill file with 0 holes correctly parsed and not counted as missing

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr.json
- **Created**: 2026-03-23

### Correct
- The LIGHTNING01A-NPTH_drill.drl file has hole_count=0, which is correctly handled. The NPTH drill file exists (possibly required by the CAM profile) but contains no actual holes, and this does not cause has_npth_drill=false incorrectly.

### Incorrect
- The warning compares B.Cu (36.4mm) vs Edge.Cuts (40.1mm), a 3.7mm difference, which is normal board-edge clearance. However B.SilkS at 40.593mm genuinely exceeds Edge.Cuts by 0.46mm. The bulk alignment failure is triggered by comparing all layer widths together rather than identifying that copper-to-edge-cuts clearance is expected while silk-beyond-board-edge is the real issue.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
