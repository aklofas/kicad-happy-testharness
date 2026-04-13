# Findings: SonOfCheevap/PierogiNixie-PSU / V1.1_PierogiNixiePSU

## FND-00001127: VR1 (TC33X-2-502E Bourns trimpot) misclassified as 'varistor'; RC filter false positive: R1=1.5M feedback divider + output caps detected as low-pass RC; LC filter resonant frequency wrong: C1=100uF...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PierogiNixiePSU.kicad_sch
- **Created**: 2026-03-23

### Correct
- Current sense detection correctly identifies R2=50m as shunt resistor with U1=MAX1771CSAT as the sense IC. This is accurate — R2 is the current sense shunt in the MAX1771 CS-pin feedback loop.

### Incorrect
- TC33X-2-502E is a Bourns TC33X series trimmer potentiometer (variable resistor), not a varistor/TVS. The 'VR' prefix is ambiguous (variable resistor vs varistor), but the part number clearly identifies it as a trimpot. This causes: wrong component_type count (varistor:1 instead of resistor:5), and wrong inclusion in signal_analysis.protection_devices as a clamp device on the FB net.
  (signal_analysis)
- The analyzer detects R1=1.5M (the upper FB divider resistor on the MAX1771 FB net) + C4=4.7uF/C5=0.1uF (output storage capacitors) as an RC low-pass filter with Fc=0.02Hz. While the topology is structurally similar, R1 is part of the feedback divider network, not a filter. C4/C5 are output bulk/bypass caps. This is a semantic misclassification of a feedback network element as a signal filter.
  (signal_analysis)
- V1.1 LC filter detection includes C1=100uF (large output storage cap) in parallel with C2=100nF as the capacitor paired with L1=100uH, giving a resonant freq of 1.59kHz. V1 and V1.2 correctly use only 100nF (50kHz resonant freq). The large output cap should not be included as part of the LC filter — it's a bulk storage cap, not the resonant capacitor.
  (signal_analysis)

### Missed
- MAX1771 is a dedicated step-up (boost) DC-DC controller. The circuit has the classic boost topology: L1 between VIN and MOSFET drain, D1 from drain to output, output cap C1/C4. The topology field in power_regulators is 'unknown' for all three versions. The analyzer should detect this as 'boost' given the characteristic inductor-MOSFET-diode configuration.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001128: VR1 (TC33X-2-502E Bourns trimpot) misclassified as 'varistor'

- **Status**: new
- **Analyzer**: schematic
- **Source**: V1_PierogiNixiePSU.kicad_sch
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Same issue as V1.1: TC33X-2-502E is a Bourns TC33X trimmer potentiometer, not a varistor. The component is the output voltage-setting trimmer in the MAX1771 feedback network.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001129: Boost converter topology not identified for MAX1771xSA (shows 'unknown'); pwr_flag_warnings generated for +12V, VCC, GND despite PWR_FLAG symbols present; Voltage divider, current sense, transistor...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: V1.2_PierogiNixiePSU.kicad_sch
- **Created**: 2026-03-23

### Correct
- V1.2 correctly identifies: RV1+R4 voltage divider on FB net, R1=50m current sense shunt to U2, Q2 MOSFET with inductive load and flyback diode D1, decoupling caps on +12V (110.2uF total) and VCC (4.9uF) rails. These are accurate for the boost PSU design.

### Incorrect
- V1.2 schematic has three PWR_FLAG symbols (confirmed in power_symbols and power_rails lists), yet pwr_flag_warnings fires for +12V, VCC, and GND. The PWR_FLAG symbols are on their own 'PWR_FLAG' net rather than connected to each supply rail, which is a real design concern, but the warning message is misleading — it says 'no power_out or PWR_FLAG' which is not accurate since PWR_FLAG symbols do exist.
  (signal_analysis)

### Missed
- Same issue as V1.1: MAX1771xSA is a boost DC-DC controller but topology='unknown'. V1.2 has the same boost topology (L1, D1, Q2, output cap C2). The transistor circuit correctly identifies gate driver and inductive load but the overall regulator topology is not identified.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001130: 4-layer board, DFM standard tier, thermal pad detected on Q1, zone stitching on GND

- **Status**: new
- **Analyzer**: pcb
- **Source**: PierogiNixiePSU.kicad_pcb
- **Created**: 2026-03-23

### Correct
- V1.1 PCB correctly reports 4-layer stackup, 19 footprints, routing complete, thermal pad on Q1 (TO-263 pad at 101.52mm2), and GND zone stitching with 48 vias across In1.Cu/In2.Cu. All accurate.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001131: 4-layer board with extensive zone fill (12 zones, 251 vias) correctly analyzed

- **Status**: new
- **Analyzer**: pcb
- **Source**: V1.2_PierogiNixiePSU.kicad_pcb
- **Created**: 2026-03-23

### Correct
- V1.2 correctly shows upgraded design: 23 footprints (vs 19), 12 fill zones (vs 1), 251 vias (vs 48), all-front SMD placement. Zone stitching analysis covers GND, +12V, Net-(D1-A), and VCC fills.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001132: Gerber alignment flagged as false — silkscreen extending past board edge is normal

- **Status**: new
- **Analyzer**: gerber
- **Source**: Gerber
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- V1.1 reports aligned=false because F.SilkS height (35.3mm) exceeds Edge.Cuts height (33.3mm) by 2mm. This is common in production PCBs where component values/references near the board edge have silk text that slightly overhangs. The F.Cu and In1/In2 layers are all within the board outline. This is a false positive alignment warning.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001133: Gerber alignment flagged as false — silkscreen and copper extending past Edge.Cuts is common

- **Status**: new
- **Analyzer**: gerber
- **Source**: V1_Gerber
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- V1 reports Width 3.9mm and Height 3.5mm variation. F.SilkS (50.95x36.8mm) extends beyond Edge.Cuts (53.1x33.3mm) in height, and F.Cu (49.25x31.2mm) is smaller. Silk overhang is normal; the flagging of 'aligned=false' is a false positive for normal board designs where silk labels extend outside the board outline.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001134: Complete 4-layer gerber set, aligned=true, 251 vias, V1.2 correctly processed

- **Status**: new
- **Analyzer**: gerber
- **Source**: V1.2_Gerber
- **Created**: 2026-03-23

### Correct
- V1.2 Gerbers correctly report: complete layer set, aligned=true, 4 copper layers, 251 via holes, 9 component THT holes, 2 NPTH mounting holes. Matches PCB analyzer counts accurately.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
