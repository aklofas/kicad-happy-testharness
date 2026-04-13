# Findings: mobilinkd/NucleoTNC / Enclosure_KiCAD_BackPanel

## FND-00000993: Logo_Open_Hardware_Large graphic classified as a power rail; LED_TX net falsely detected as UART interface; I2C bus not detected despite I2C_SCL and I2C_SDA nets with a 24LC32 EEPROM; Transistor ci...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_KiCAD_Nucleo32TNC.sch
- **Created**: 2026-03-23

### Correct
- 9 RC filters detected including the audio path filters: 32.88 Hz output coupling cap (R4/C2), 5.31 kHz anti-aliasing filters (R7/C6, R16/C7), 9.18 kHz (R14 with parallel C6+C8). These match the audio TNC use case.
- 52 components correctly counted with correct breakdown: 3 ICs, 2 transistors, 22 resistors, 13 capacitors, 4 LEDs, 2 diodes, 1 connector, 4 mounting holes, 1 switch. BOM values and footprints correctly extracted.

### Incorrect
- The Graphic:Logo_Open_Hardware_Large symbol (#LOGO1) is listed in statistics.power_rails alongside +3.3V and GND. It is a decorative graphic element, not a power rail. The parser is treating the lib_id value field as a net name for non-power graphic symbols.
  (signal_analysis)
- bus_analysis.uart reports LED_TX as a UART signal (pin_count=1, no devices). LED_TX is a GPIO signal driving an LED indicator (D4 anode), not a UART TX line. The analyzer is pattern-matching on the '_TX' suffix without verifying connectivity to UART-capable IC pins.
  (signal_analysis)
- U1 is an MCP6004 quad op-amp. All 5 units (including power unit 5) are reported with configuration='unknown'. The 4 active signal-processing units are in inverting, non-inverting, and active filter configurations based on the surrounding R/C components. Opamp configuration detection fails because op-amp pin connections are empty in the KiCad 5 parser.
  (signal_analysis)
- SW1 (a tactile push button, user/boot button) is listed as having a pin on the I2C_SCL net, which is incorrect. SW1 pin 2 goes to GND. This appears to be a wire-tracing error in the KiCad 5 parser placing nearby wires on wrong nets.
  (signal_analysis)

### Missed
- The schematic has a 24LC32 I2C EEPROM (U2) with I2C_SCL and I2C_SDA nets and 2K2 pull-up resistors (R17, R18), but bus_analysis.i2c is empty. Root cause: U2 has pins:[] in the output (KiCad 5 .sch IC pin connections not parsed), so the I2C bus detector finds no IC pins on the I2C nets.
  (signal_analysis)
- Q1 and Q2 are 2N7000 N-channel MOSFETs used as PTT (push-to-talk) switches. transistor_circuits in signal_analysis is empty. The transistor detector is missing these, likely because pin connections to the FET are not parsed (same KiCad 5 pin extraction issue).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000994: PCB statistics correctly extracted: 54 footprints, 187 tracks, 3 vias, 2-layer board; LEDs (D3-D6) flagged with -4.95mm edge clearance are likely intentional panel-mount overhangs; 20 courtyard ove...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCB_KiCAD_Nucleo32TNC.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Board is 66x99mm, 2-layer (F.Cu + B.Cu), fully routed with 52 nets, 1012mm total track length. All correct for a THT-dominant TNC board on a Nucleo32 carrier.
- The board is a THT-dominant design (48 THT, 1 SMD, 5 virtual) packed in 66x99mm. Overlapping courtyards are expected when manually placing THT components tightly. The overlaps reported (U1/R16, C12/C13, etc.) are consistent with a hand-designed amateur radio TNC.
- The thermal analysis correctly finds the +3V3 zone on F.Cu with 5640mm2 area and 1 stitching via. Board metadata (title, revision, company) all correctly extracted.

### Incorrect
- D3, D4, D5, D6 all show -4.95mm edge_clearance_mm. For a TNC in an enclosure, horizontal LED_D3.0mm THT LEDs are commonly placed to protrude through panel holes — their leads overhang the PCB edge intentionally. The warning is technically accurate but likely not a real defect for this board style. The board metadata confirms this is a PCB Rev B (Mobilinkd LLC) with '67mm width' note.
  (signal_analysis)
- The statistics report smd_count=1 which is the LOGO footprint (library=KiCAD:LOGO, reference=G1). This inflates the SMD count by counting a graphic element as an SMD component. The board is effectively all-THT.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000995: Older KiCAD/Nucleo32TNC.sch (breadboard version) correctly parsed with 41 components

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCAD_Nucleo32TNC.sch
- **Created**: 2026-03-23

### Correct
- The older design iteration has 41 components (vs 52 in the PCB version), 32 nets, and no LEDs for DCD/TX status indicators, consistent with an earlier breadboard design. The output matches the source schematic accurately.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000996: Enclosure panel schematics correctly identified as mounting-hole-only with no signal analysis

- **Status**: new
- **Analyzer**: schematic
- **Source**: Enclosure_KiCAD_FrontPanel_FrontPanel.sch
- **Created**: 2026-03-23

### Correct
- FrontPanel (8 mounting holes) and BackPanel (6 mounting holes) are mechanical-only boards. The analyzer correctly extracts these as mounting_hole type components with no signal analysis detectors triggered.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000997: No gerber files present in repo — gerber analysis not applicable

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: 
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The review prompt referenced 4 gerber output files (NucleoTNC-gerbers, NucleoTNC_r3-gerbers, NucleoTNC_r4-gerbers, NucleoTNC_r5-gerbers), but the NucleoTNC repo contains no gerber files. The checked-out repo only has .sch and .kicad_pcb files. These outputs do not exist and cannot be reviewed.
  (signal_analysis)

### Suggestions
(none)

---
