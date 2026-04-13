# Findings: deebot/MorphWatch-STM32 / MorphWatch-Hardware_MorphWatch-STM32

## FND-00000954: RC filter false positive: R1(10k)+C1(4.7uF) classified as 3.39 Hz high-pass filter, but R1 is Q2's gate pull-down and C1 is a gate bypass cap (both on GDR net); IC1 (ME6211C33M5G-N LDO) VSS pin sho...

- **Status**: new
- **Analyzer**: schematic
- **Source**: MorphWatch-Hardware_MorphWatch-STM32.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- C1 pin1 is on GDR net (Q2 MOSFET gate), C1 pin2 is on +3.3V. R1 pin1 is on GDR, R1 pin2 is on GND. The actual function is: R1 pulls Q2 gate low (pull-down), C1 decouples gate-to-3V3. This is not an RC filter in any conventional sense. The high-pass filter classification is wrong.
  (signal_analysis)
- Source schematic has a GND power symbol at (2200,3150) directly below IC1 at (2200,3050), which should connect to the VSS pin. The analyzer returns VSS on __unnamed_44 (a single-pin isolated net). Similarly CE (pin 3) and VOUT (pin 5) are on unnamed single-pin nets, suggesting the legacy parser fails to resolve pin coordinates for this custom watchcomponent library symbol.
  (signal_analysis)

### Missed
- Q1 is typed as 'transistor' in components but not detected in signal_analysis.transistor_circuits (only Q2 DMN3042L and Q3 S8050 detected). The custom watchcomponent symbol uses generic passive pin types rather than labeling pins as gate/drain/source, so the transistor circuit detector can't classify it.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000955: Alignment flagged as false positive: 11mm height mismatch between Edge.Cuts (45.96mm) and copper layers (~35mm) is due to a USB notch/tab cutout in the watch PCB outline, not a misalignment; 4-laye...

- **Status**: new
- **Analyzer**: gerber
- **Source**: MorphWatch-Hardware_Gerber.json
- **Created**: 2026-03-23

### Correct
- All 11 gerber files + 2 drill files present. Inner copper planes In1.Cu (GND) and In2.Cu (+3V3) correctly identified from net_analysis. 76 vias at 0.3/0.4mm, 15 component holes at 0.5-0.8mm correctly classified. Zip archive dated 2021 vs loose files from 2026 correctly noted.

### Incorrect
- The PCB has a complex non-rectangular outline (24 edges including arcs) with a USB charging port cutout at the bottom. Copper layers don't extend into the cutout region, making their bounding box smaller than Edge.Cuts. The alignment checker compares bounding boxes and incorrectly flags this as misalignment. The layers are properly aligned — the asymmetry is intentional board geometry.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
