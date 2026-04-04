# Findings: STEPUPDC02 / hw_sch_pcb_STEPUPDC02

## FND-00001336: Component counts and topology extraction correct for TPS61041 boost converter; TPS61041 Vout estimated at ~14V but actual Vout is ~28.8V; power_regulator output_rail and input_rail both reported as...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STEPUPDC02.kicad_sch
- **Created**: 2026-03-24

### Correct
- 18 components (1 IC, 4 capacitors, 1 inductor, 2 diodes, 3 resistors, 4 mounting holes, 3 connectors) correctly parsed. Voltage divider R2/R4 at FB pin and feedback_network detected. Boost switching topology with L1, D1 (Schottky) correctly identified.
- D1 is the rectifier diode in the boost output path; D2 is a 5.6V Zener on the input clamping the enable network. Both correctly typed as diodes, though the Zener is not specifically identified as a protection_device or zener clamp.
- The schematic includes 4 single-pin nets for M1-M4 mounting holes (__unnamed_2 through __unnamed_5), which are not electrical nets in the PCB. The PCB's 6 nets (GND, /Power, /PowerOUT, /ENABLE, Net-(D1-Pad2), Net-(C1-Pad2)) correspond accurately to the actual circuit connections.

### Incorrect
- The analyzer uses a heuristic Vref=0.6V and calculates Vout = 0.6 * (1 + 1.8M/80.6k) = ~14V. The TPS61041 datasheet specifies Vref = 1.233V, giving Vout = 1.233 * (1 + 1.8M/80.6k) = ~28.8V. The STEPUPDC02A.json confirms the module is rated 'Vout up to 28V.' The error is 2x, caused by the generic 0.6V Vref heuristic being wrong for this specific IC.
  (signal_analysis)
- The TPS61041 is a boost converter: input is 'Power' (Vin), output is 'PowerOUT'. The analyzer reports both output_rail and input_rail as 'Power'. This happens because the SW pin feeds into the same 'Power' net label tracking rather than tracing through L1/D1 to 'PowerOUT'. This misidentification makes the switching regulator entry misleading.
  (signal_analysis)

### Missed
- D2 (ZSMD-5V6, a 5.6V Zener on the Power/input net alongside R1 and J1) is an input overvoltage clamp but appears in protection_devices: []. The analyzer sees it as a plain diode in the neighbor list.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001337: Legacy KiCad 5 rescue backup parsed correctly with 13 components

- **Status**: new
- **Analyzer**: schematic
- **Source**: rescue-backup_STEPUPDC02A-2019-04-08-08-40-05.sch
- **Created**: 2026-03-24

### Correct
- KiCad 5 format parsed, version 4 file, 13 components (versus 18 in the current KiCad 6 schematic — the rescue backup is an older revision without J2, J4, C2, R1, and D2). Power rails +BATT and GND correctly extracted.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001338: PCB statistics accurate: 18 footprints, 2-layer, split front/back placement

- **Status**: new
- **Analyzer**: pcb
- **Source**: STEPUPDC02.kicad_pcb
- **Created**: 2026-03-24

### Correct
- 7 front / 11 back footprints, 10 SMD / 8 THT, 56 tracks, 26 vias, 5 zones, 19.8 x 40.1mm board. Fully routed. GND zone stitching with 26 vias at 1.2 via/cm2 correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001339: Gerber set is complete with all expected layers; Drill classification: 26 vias + 20 component holes correctly separated; F.Paste extent reported as 0x0mm — likely a false alarm or all SMD on back

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hw_cam_profi_gbr
- **Created**: 2026-03-24

### Correct
- 9 gerber files covering F.Cu, B.Cu, F/B Mask, F/B Paste, F/B Silk, Edge.Cuts; plus PTH and NPTH drill files. No missing or extra layers. Dimensions 19.96 x 40.28mm consistent with PCB (19.8 x 40.1mm).
- Via holes (0.4mm dia, 26 count) and component holes (0.889mm x16, 3.0mm x4 for mounting holes) correctly classified via X2 attributes. 4 mounting holes at 3mm matches M1-M4 in schematic.

### Incorrect
- F.Paste layer extents are 0x0mm (empty), while B.Paste covers 8.7 x 21.1mm. This is consistent with the PCB having 7 front / 11 back components and all front-side components being THT (no front SMD paste needed). This is actually correct behavior — front side has THT components only. The analyzer reports it without flagging it as an issue, which is acceptable.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
