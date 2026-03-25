# Findings: LED-cube-programmable / LED-Cube_MK3

## FND-00000800: Net connectivity broken for Q3, Q2, Q4 FET source pins in legacy KiCad5 schematic; Transistor drain/source swapped for Q3/Q4/Q1/Q2: drain_net=GND is topologically inverted for low-side switches; ER...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: LED-Cube_MK3.sch.json
- **Created**: 2026-03-23

### Correct
- The scrclk net drives ~OE (active-low output enable) of both 74HC595s. A dedicated GPIO should drive this pin rather than leaving it with no explicit driver source. The ERC correctly identifies this.
- Arduino Nano runs at 3.3V logic, 74HC595s run at 5V. The sr_latch net crosses domains correctly identified as needing a level shifter.

### Incorrect
- Q3, Q2, Q4 source nets each contain only a single pin (the FET source itself), meaning the net tracing failed to connect source pins to their downstream loads. Q1 source correctly resolves to R13/R20 (LED rows), but Q2/Q3/Q4 source nets are isolated. This is a wire-tracing bug in the legacy .sch parser affecting some transistors in the same schematic.
  (signal_analysis)
- All four 2N7002 FETs are analyzed with drain=GND and source=load. For a low-side switch, drain should connect to load (LED cathode rows) and source to GND. Because source-pin nets are broken (only 1 pin), the analyzer correctly picks up that drain=GND, but the downstream load topology is wrong. The drain_is_power=True (GND is technically a power rail) flag makes this appear as an anomaly when it is actually a net-tracing artifact.
  (signal_analysis)

### Missed
- The Arduino drives U1/U2 (74HC595) via mosi, scrclk, sr_latch signals which form an SPI-like interface. The bus_analysis shows spi=[] even though MOSI-equivalent data and clock signals are present. The non-standard net names (not labeled MOSI/SCK) likely prevent SPI detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000801: G*** logo/decorative footprint (Kitchen_LOGO) correctly parsed in PCB without causing errors

- **Status**: new
- **Analyzer**: pcb
- **Source**: LED-Cube_MK3.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The PCB contains a logo footprint with reference G*** and 0 pads. It is correctly extracted with pad_count=0 and does not affect routing or net analysis.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000802: 2-layer KiCad5 gerber set correctly parsed; missing F.Paste flagged as recommended (not required)

- **Status**: new
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-23

### Correct
- 7 gerber files + 1 drill file. All required layers present (F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts). Missing F.Paste listed as missing_recommended (not missing_required). This is appropriate as F.Paste is optional for THT-dominant boards.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
