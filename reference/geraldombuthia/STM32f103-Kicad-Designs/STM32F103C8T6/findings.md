# Findings: geraldombuthia/STM32f103-Kicad-Designs / STM32F103C8T6

## FND-00001312: STM32F103C8T6 board correctly identified with AMS1117-3.3 LDO, USB D+/D- differential pair, I2C pull-ups, UART; USB ESD protection incorrectly attributed to U2 (STM32); U2 is the MCU, not ESD devic...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32F103C8T6.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Correct: AMS1117-3.3 as LDO from VBUS→+3.3V, I2C2 SDA/SCL with 1K5 pull-ups, USART1 TX/RX identified on U2, USB differential pair with J4+U2, series resistors R5 on USB, crystal Y1 at 16MHz with load caps C5/C9. Power domain grouping (+3.3V/+3.3VA for U2, VBUS for U1) is correct.
- J4 is USB_B_Micro with footprint='' — correctly reported in missing_footprint list. All other components have valid footprints.
- These nets connect passives and MCU input pins without a PWR/output driver symbol — correctly flagged as no_driver ERC warnings. These are expected in a raw KiCad schematic without explicit power symbols on those lines.

### Incorrect
- esd_protection lists 'U2' (STM32F103C8T6) as ESD protection for USB differential pair. The MCU has internal USB ESD but the analyzer is conflating pin connectivity with dedicated ESD protection. No dedicated ESD protection device (e.g. PRTR5V0U2X) exists in the BOM. The STM32 happens to share the USB net but is not an ESD protector.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001313: STM32 PCB correctly analyzed: 33 footprints, all front-side, 2 layers, full GND plane on B.Cu, +3.3V/VBUS/GND zones on F.Cu; B.Cu layer type reported as 'power' instead of 'signal'; it is a GND pla...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32F103C8T6.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- smd_count=25, tht_count=3 (header pins), 4 copper zones identified correctly (VBUS, GND on F.Cu; two GND on B.Cu — one zone plus fill plane). Via count 24 with 7 fanout vias from U2 LQFP-48 correctly detected. Routing complete confirmed.

### Incorrect
- The B.Cu layer entry shows type='power' (line 37 of PCB JSON). In KiCad, copper layers are always signal type in the layer definition — the 'power' designation is not a standard KiCad layer type for B.Cu. This appears to be an analyzer misclassification; KiCad's layer types are 'signal', 'power', 'mixed', 'jumper' but B.Cu in this file is used as a GND plane via a zone, not declared as power type in the file.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001314: Gerber alignment flagged as misaligned due to mask/paste layer extent differences — this is a false positive for normal SMD boards; Complete 9-layer + drill gerber set correctly identified; layer c...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Manufacturing.json
- **Created**: 2026-03-24

### Correct
- All required layers (F.Cu, B.Cu, F/B Mask, F/B Paste, F/B SilkS, Edge.Cuts) present and correctly classified. Drill file correctly parsed with 44 total holes: 24 vias (0.3mm), 12 PTH component (1.0mm), 2 NPTH (0.8mm), 2 NPTH (0.9mm), 4 NPTH mounting (2.2mm). T2 (0.55mm, 0 holes) and T3 (0.85mm, 0 holes) correctly noted as defined but unused.

### Incorrect
- The alignment checker reports 'Height varies by 2.6mm across copper/edge layers' because B.Paste has 0x0 extents (no paste on back, correct for an all-SMD-front design), B.Mask extents are smaller than Edge.Cuts (mask doesn't extend to full board edge — normal), and silk is smaller still. The Cu layers (35.98×29.98) vs Edge.Cuts (37×31) difference is ~1mm per side which is normal keepout/clearance behavior. This is a false positive — the gerbers are correctly aligned.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
