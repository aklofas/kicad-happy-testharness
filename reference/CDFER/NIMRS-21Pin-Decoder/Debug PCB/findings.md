# Findings: CDFER/NIMRS-21Pin-Decoder / Debug PCB

## FND-00000960: Empty Debug PCB schematic correctly produces all-zero output

- **Status**: new
- **Analyzer**: schematic
- **Source**: Debug PCB.kicad_sch
- **Created**: 2026-03-23

### Correct
- The Debug PCB schematic appears to be a blank/placeholder KiCad 9.0 file. Analyzer correctly returns zero components, nets, wires, and empty signal analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000961: Component counts correct: 85 total, correct type breakdown; Power regulator fb_net incorrectly reported as 'GND' for both TPS63070 instances; Differential pair detector misidentifies U2 (MAX98357A ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Decoder PCB_NIMRS-21Pin-Decoder.kicad_sch
- **Created**: 2026-03-23

### Correct
- 28C, 23R, 2Q, 3J, 10TP, 4H, 4L, 5D, 5IC, 1X = 85 total. The 3 connectors includes PN1 (panel number component) in addition to J1 and J2. Counts are accurate.
- The 2.7nH inductor (L1) and two 1.5pF capacitors (C12, C13) form a pi-match network between ESP32-S3 (U1) and the U.FL antenna connector (J2). Resonant frequency 2.50 GHz matches the 2.4 GHz WiFi band. Topology and target IC are correctly identified.
- R61/R62 (510k/51k) for U60 and R71/R72 (75k/24k) for U70 are correctly flagged as feedback networks with is_feedback=true, connected to the respective FB pins.
- 40MHz crystal with C10 and C8 (both 20pF) gives effective load of 13pF including stray. Correct computation and in-typical-range flag.
- All components have LCSC numbers populated but the mpn field is empty. The analyzer correctly reports 0/68 MPN coverage. The missing_mpn list correctly enumerates all 68 BOM components.

### Incorrect
- U60 and U70 (TPS63070 buck-boost converters) show fb_net='GND' in power_regulators section. The actual feedback nets are 'Net-(U60-FB)' and 'Net-(U70-FB)' per the schematic nets data. The analyzer is mapping the wrong pin to fb_net, missing the actual feedback resistor network node.
  (signal_analysis)
- differential_pairs reports Speaker+/Speaker- with esd_protection=['U2']. U2 is the MAX98357A I2S power amplifier—it drives the Speaker+/- outputs. It is not an ESD protection device. The detector appears to classify any IC sharing both differential nets as ESD protection.
  (signal_analysis)
- MOTOR_1, MOTOR_2, MOTOR_GAIN_SEL are flagged needs_level_shifter=true because U1 (+3V3 domain) and U4 (VMOTOR domain) differ. However the DRV8213DSGR accepts 3.3V logic inputs while powered from VMOTOR, so no level shifter is needed by design. The flag reflects domain mismatch but not actual electrical risk.
  (signal_analysis)

### Missed
- bus_analysis.i2c and bus_analysis.spi are empty, and UART only catches ESP32_TX/RX. The I2S audio signals (AMP_DIN, AMP_BCLK, AMP_LRCLK) connecting ESP32-S3 (U1) to MAX98357A (U2) are not identified as an I2S bus. These signal names clearly indicate I2S protocol.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000962: Empty/blank Debug PCB correctly yields all-zero analysis with copper warning

- **Status**: new
- **Analyzer**: pcb
- **Source**: Debug PCB.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Zero footprints, tracks, vias, zones on the blank debug board. Appropriate copper_presence warning about unfilled zones. Silkscreen warnings for missing board name and revision are reasonable for an empty board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000963: 4-layer stackup correctly parsed: F.Cu/In1.Cu(power)/In2.Cu/B.Cu with full stackup details; DFM 'challenging' tier correctly identified due to 0.1mm tracks and 0.09mm spacing; Polarity reminder inc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Decoder PCB_NIMRS-21Pin-Decoder.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Board correctly identified as 4-layer with 30x23.5mm dimensions, 197 vias, 1366 tracks, 89 footprints (77 front, 12 back), routing complete. Stackup material/thickness data accurately captured from the design.
- Track width 0.1mm is below standard 0.127mm minimum and the 0.09mm spacing falls below advanced process minimum (0.1mm). This is a dense 30x23.5mm 4-layer decoder board designed for JLCPCB advanced process, so the DFM warnings are accurate.
- Non-standard thickness (between 1.0mm and 1.6mm standard options) is faithfully captured. The stackup matches JLC04101H-7628 as noted in board comments. HAL lead-free finish and dielectric constraints are correctly extracted.

### Incorrect
- The polarity_reminder lists C1, C10, C11, C12, C13, etc. (all 0402/0603/0805 MLCCs) as polarized components requiring polarity marker verification. MLCCs are not polarized. Only D1-D5 (Schottky/Zener diodes) truly require polarity checking. The warning is correct for diodes but wrong for all the ceramic capacitors.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
