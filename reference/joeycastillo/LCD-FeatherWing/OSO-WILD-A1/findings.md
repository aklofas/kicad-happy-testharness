# Findings: joeycastillo/LCD-FeatherWing / OSO-WILD-A1

## FND-00000766: A3 kicad_sch correctly reports zero components — file is a blank shell

- **Status**: new
- **Analyzer**: schematic
- **Source**: OSO-WILD-A3_OSO-WILD-A3.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- OSO-WILD-A3.kicad_sch is only 21 lines and contains no symbols (lib_symbols is empty). The real design is in OSO-WILD-A3.sch (legacy format). The analyzer correctly produces zero components/nets for the KiCad 6 file.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000767: A1 kicad_sch correctly identifies 9 components, I2C bus with pull-ups on BU9796A LCD driver; single_pin_net warnings for SCL, SDA, ~{RST}, A0 are false positives for label-driven nets; PWR_FLAG war...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: OSO-WILD-A1_OSO-WILD-A1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Correctly finds U1 (BU9796AMUV-E2 LCD segment driver), 2x 10K I2C pull-ups (R1/R2) on SCL_LCD/SDA_LCD nets, 3 solder jumpers for I2C address/signal routing, LCD connector (LCD1, 16-pin), decoupling cap C1 (0.1uF on +3V3). Bus analysis correctly identifies I2C with pull-ups present. Net connectivity for all COM/SEG signals to LCD connector is correct.
- GND and +3V3 rails have no PWR_FLAG symbols and no power_out driver in the kicad_sch (power comes from the Feather connector, modeled in the legacy .sch). The ERC warning is technically valid for this file in isolation. This is the known KH-160 pattern (connector-powered designs triggering PWR_FLAG warnings).

### Incorrect
- Nets SCL, SDA, A0, and ~{RST} each have one pin (jumper/switch pads) but are connected to net labels that route to the Feather connector. The kicad_sch file is a standalone design where these labels are intentional stubs (the Feather header is in the companion .sch legacy file). The analyzer flags them as single_pin_nets which is misleading — they are label terminations, not floating nets. However since the .kicad_sch is indeed standalone (no hierarchical sheets), this is borderline correct. Still, reporting 4 single_pin_net warnings on a clean design is noisy.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000768: A1 legacy .sch correctly parses Feather connector pinout (J1/J2) with all 28 net labels

- **Status**: new
- **Analyzer**: schematic
- **Source**: OSO-WILD-A1_OSO-WILD-A1.sch.json
- **Created**: 2026-03-23

### Correct
- The legacy KiCad 5 schematic for A1 is a Feather connector breakout: J1 (1x16 long) and J2 (1x12 short). 28 nets parsed correctly including SCK/MOSI/MISO/SPI, SCL/SDA/I2C, RX/TX/UART, A0-A5 analog, VBAT/VUSB power. All pins have empty pin lists (expected for KiCad 5 legacy format where component-net association is not extracted from wire connections). Bus analysis correctly identifies UART (RX/TX).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000769: A3 legacy .sch output is identical to A1 legacy .sch — same Feather connector file

- **Status**: new
- **Analyzer**: schematic
- **Source**: OSO-WILD-A3_OSO-WILD-A3.sch.json
- **Created**: 2026-03-23

### Correct
- OSO-WILD-A3.sch is the same Feather connector schematic as OSO-WILD-A1.sch (same UUIDs, identical net list, identical components J1/J2). Both correctly parsed. No issues.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000770: A1 PCB correctly identifies 2-layer 50.8x22.86mm board with BU9796A QFN and GND pour; smd_count=5 is suspicious — only 3 real SMD parts (U1 QFN, C1 0603, R1/R2 0603 = 4 total)

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: OSO-WILD-A1_OSO-WILD-A1.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 18 footprints (9 real components + 4 REF** markers + 3 G*** graphics + J1/J2 feather headers), 136 tracks, 18 vias, 4 zones, routing complete. Thermal pad on U1 (EPAD 2.15x2.15mm on GND) correctly detected with 0 thermal vias in the footprint-via-pad count (the GND zone stitching provides 5 stitching vias nearby). Board dimensions and net count (47) are reasonable.

### Incorrect
- The PCB reports smd_count=5, tht_count=3. The design has: U1 (QFN, SMD), C1 (0603, SMD), R1 (0603, SMD), R2 (0603, SMD) = 4 SMD, and SW1 (SMD pushbutton), J1/J2 (THT Feather headers), JP1/JP2/JP3 (solder jumpers). So smd_count=5 likely includes SW1, which is correct. tht_count=3 plausibly covers J1, J2, and LCD1 (which is a header). Count may be correct but front_side=6 vs back_side=12 is surprising for a design where most SMD is on the back — this bears verification.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000771: A3 PCB reports duplicate footprint references (J1,J1,J2,J2,LCD1,LCD1) without flagging them; A3 PCB correctly identifies 50.8x76.2mm board with no zones and routing complete; Duplicate footprint re...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: OSO-WILD-A3_OSO-WILD-A3.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The A3 board is a larger test/breakout board (76.2mm = 3 inches tall vs A1's 22.86mm). No copper pours, no vias, 132 tracks at 1163mm total length. No SMD components — all footprints are THT connectors and mounting holes. This matches the design intent (A3 is the larger carrier/demo board).

### Incorrect
- The A3 PCB footprint list contains J1 twice, J2 twice, and LCD1 twice — 15 footprints total (8 REF**/mounting holes + 1 logo + 6 real footprints with duplicates). The analyzer silently accepts duplicate references without any warning in design_observations or dfm_analysis. Duplicate refs on a PCB are an ERC/DRC issue that should be flagged.
  (signal_analysis)

### Missed
- The A3 PCB has 6 footprints with real component references, but J1, J2, and LCD1 each appear exactly twice. The analyzer's design_observations, dfm_analysis, and connectivity sections are all empty — no duplicate reference warning is emitted. A DFM or ERC check for duplicate refs would catch this and help identify a likely PCB design issue.
  (signal_analysis)

### Suggestions
(none)

---
