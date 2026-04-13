# Findings: Jarins/Solder-Paste-Dispenser-with-DCMotor / Hardware_SPD_DC_MotorHBridge

## FND-00001409: T0 and T1 (MountingHole_Pad footprints) misclassified as 'transformer'; Crystal oscillator circuit (Y1 + STM32F103) not detected — crystal_circuits empty

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: SPD_DC_MotorHBridge.sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- statistics.component_types shows 'transformer': 2 for components T0 and T1, but both have lib_id='archive:Mechanical_MountingHole_Pad' and value='MountingHole_Pad'. The 'T' prefix is being interpreted as transformer when these are clearly padded mounting holes. The 5 correctly-classified mounting holes (MP1, MP2, MP3, VM1, IM1) use the same lib_id but have 'M'-prefix or 'V'/'I'-prefix refs. The component type classifier is using reference prefix 'T' → transformer heuristic which collides with non-standard pad mounting hole designators.
  (statistics)

### Missed
- The design has Y1 (TSX-3225 16MHz crystal, lib_id='archive:Device_Crystal_GND24_Small', type=crystal) connected to the STM32F103C8Tx MCU (U2). Despite the type field being correctly set to 'crystal' and the crystal being present, signal_analysis.crystal_circuits=[] — no crystal circuit was extracted. This is likely a failure to match the GND24_Small footprint variant or the archive-prefixed lib_id against the detector's crystal template patterns.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001410: via_count=141 in PCB significantly overstates actual routed vias (gerber shows 91); Board dimensions (70.04 × 20.07 mm), 2-layer stackup, and DFM tier accurately reported

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: SPD_DC_MotorHBridge.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Board outline correctly parsed as 4-segment rectangle, 70.04 × 20.066 mm (matching the gerber edge-cuts extents of 70.04 × 20.07 mm to 3 decimal places). DFM tier 'challenging' is appropriate: minimum annular ring = 0.075 mm is below both the 0.125 mm standard and 0.1 mm advanced thresholds. The DFM violation message is accurate.

### Incorrect
- The PCB analyzer reports via_count=141 (121 × 0.45/0.3mm + 20 × 0.8/0.5mm through vias). The Gerber drill file contains only 91 holes classified as vias (all 0.3mm) and 45 component holes; total 136 drilled holes. The 20 PCB vias sized 0.8/0.5mm likely correspond to drilled component pad holes that the PCB analyzer is counting as vias due to the size ambiguity between large vias (0.5mm drill) and small THT pads (also 0.5mm). The gerber-based classification (91 vias) is more accurate since it uses actual fabrication output.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001411: 7-file gerber set correctly validated: layers complete, all 7 required/recommended layers found, alignment confirmed; Drill classification correctly identifies 91 vias (0.3mm) and 45 component hole...

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerber
- **Created**: 2026-03-24

### Correct
- Gerber set contains B.Cu, B.Mask, B.SilkS, Edge.Cuts, F.Cu, F.Mask, F.SilkS — all required 2-layer layers present (missing_required=[]). F.Paste correctly flagged as missing_recommended since the PCB file marks F.Paste layer as hidden. Alignment check passes (all layer extents fit within the 70.04×20.07 mm board outline). Generator correctly identified as KiCad Pcbnew 5.1.9.
- Drill file has 136 total holes: 91×0.3mm (classified as vias), 20×0.5mm + 2×0.8mm + 19×1.0mm + 4×1.2mm (45 total, classified as component holes). The 0-count mounting holes is consistent with the PCB mounting holes being padded (PTH) rather than NPTH — no NPTH drill file was exported. All tool diameters, counts, and the PTH-only classification are consistent with a mixed SMD/THT board having no unpaded mounting holes.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
