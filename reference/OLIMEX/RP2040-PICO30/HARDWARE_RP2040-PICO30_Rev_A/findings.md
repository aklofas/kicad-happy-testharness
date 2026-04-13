# Findings: OLIMEX/RP2040-PICO30 / HARDWARE_RP2040-PICO30_Rev_A

## FND-00001177: Voltage divider R12/R13 detected with mid-point at LX (switching node) instead of FB pin; SY8089 buck regulator feedback network not detected as part of the regulator circuit; Crystal circuit Y1 (1...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RP2040-PICO30_Rev_A.sch
- **Created**: 2026-03-23

### Correct
- Crystal oscillator circuit for RP2040 correctly parsed: 12MHz, two 27pF caps, CL_eff = 16.5pF (series combination plus ~3pF stray). This is consistent with RP2040 datasheet recommendations.
- The +3.3V rail has 22uF (x2) bulk and multiple 100nF bypass caps for the RP2040 IOVDD pins, correctly enumerated. The 1V1 ADC supply also correctly shows separate decoupling.

### Incorrect
- R12 (220k) and R13 (49.9k) form the feedback divider of the SY8089 buck regulator. The divider mid-node (__unnamed_3) is where LX (pin 3, the inductor switching output) and the resistor junction meet in the schematic net. The actual feedback signal goes to FB (pin 5, __unnamed_4). The resistors should be associated with the FB net/feedback network, not reported as a voltage divider with LX as output. This is a schematic wiring artifact causing incorrect classification.
  (signal_analysis)

### Missed
- The power_regulators section detects U3 (SY8089) as 'switching' but the fb_net (__unnamed_4) only has U3 pin 5 (FB) and L1 pin 1, missing the R12/R13 feedback divider. The output voltage set by R12/R13 (ratio 0.185 implies Vout ≈ 0.6V/0.185 ≈ 3.24V, consistent with 3.3V rail) is not reported as part of the regulator output configuration.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001178: False alignment warning: F.Cu reported as 42.6x79.8mm vs board 21x51mm; 4-layer board correctly identified with all required layers present

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerbers
- **Created**: 2026-03-23

### Correct
- Layer set F.Cu/In1.Cu/In2.Cu/B.Cu plus mask, paste, silk, edge, PTH and NPTH drills — complete and correct. 89 vias (0.399mm drill), 86 component holes (1.0mm), 2 mounting holes (2.1mm NPTH) correctly classified.

### Incorrect
- The alignment check reports F.Cu extents of 42.571x79.763mm while Edge.Cuts is 21x51mm, triggering 'Width varies by 21.6mm, Height varies by 29.3mm'. This is almost certainly a gerber parser issue where copper features or aperture flashes that extend to the panel origin or coordinate offset are being included in the bounding box calculation. The gerber file content is almost certainly correct — the board is a legitimate 4-layer 21x51mm design with complete layer set.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
