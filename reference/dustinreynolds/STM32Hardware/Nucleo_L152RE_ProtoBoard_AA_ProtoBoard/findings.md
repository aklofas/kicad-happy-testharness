# Findings: dustinreynolds/STM32Hardware / Nucleo_L152RE_ProtoBoard_AA_ProtoBoard

## FND-00001272: Multi-sheet hierarchy parsed correctly across 5 sheets

- **Status**: new
- **Analyzer**: schematic
- **Source**: Nucleo_L152RE_ProtoBoard_AB_ProtoBoard.sch
- **Created**: 2026-03-24

### Correct
- AB ProtoBoard.sch correctly identifies all 5 sub-sheets (Power, NucleoPins, Sensors, Modules) and aggregates 158 components, 154 nets, and 24 no-connects. Component types (switch, connector, ic, capacitor, resistor, led, test_point, jumper, transistor, relay) are all correctly classified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001273: Sub-sheet Modules.sch correctly included in Sensors.sch parse

- **Status**: new
- **Analyzer**: schematic
- **Source**: Nucleo_L152RE_ProtoBoard_AB_Sensors.sch
- **Created**: 2026-03-24

### Correct
- Sensors.sch includes Modules.sch as a sub-sheet (2 sheets parsed total). Component count of 104 includes the 21 components from Modules.sch — correct hierarchical behavior. ICs U4 (S25FL127S flash), U5 (MT3329 GPS), U6 (RFM69HW), U7 (ATSHA204A) correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001274: LDS3985 LDO regulator not detected as power_regulator; Voltage dividers from +15V rail correctly detected

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Nucleo_L152RE_ProtoBoard_AB_Power.sch
- **Created**: 2026-03-24

### Correct
- Two voltage dividers detected: R9+R8 (0-ohm in series) + R10 from +15V to GND (ratio 0.213), and R14+R12 from unnamed net to GND (ratio 0.746). The chain resistor handling for R8=0 ohm in series with R9 is correct. RC filters (R13+C5 at 4.79Hz, R4+C3 at 159Hz) also correctly identified.

### Incorrect
(none)

### Missed
- U1 is an LDS3985 (STMicro 150mA 3.3V LDO regulator in SOT23-5) but power_regulators array is empty. The IC is only listed in subcircuits with empty neighbor_components. The analyzer appears to miss LDO recognition for this custom lib_id 'LDS3985', likely needing a keyword or pin-name match for LDO detection.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001275: SPI bus nets correctly classified, ICs correctly typed; Many ICs have empty pins[] due to KiCad 5 custom library symbol parsing

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Nucleo_L152RE_ProtoBoard_AB_Modules.sch
- **Created**: 2026-03-24

### Correct
- SPI2_NSS, SPI2_MOSI, SPI2_MISO, SPI2_SCK nets correctly classified as chip_select/data/clock. USART1_RX/TX detected in UART bus_analysis. RFM69HW (RF module), S25FL127S (SPI flash), MT3329 (GPS), ATSHA204A (crypto IC) all classified as 'ic' type.

### Incorrect
- U4 (S25FL127S), U6 (RFM69HW), U5 (MT3329), U7 (ATSHA204A) all have pins=[] in their component entries, and neighbor_components=[] in subcircuits. These are custom library symbols in KiCad 5 legacy format whose pin data is not extracted, so subcircuit analysis is empty. This is a known limitation for KiCad 5 custom libs but results in missed SPI/I2C bus membership detection for these ICs.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001276: PMOS transistor (SI2323DS) correctly characterized as load switch; I2C bus missing pullup detected on I2C_SDA1/SCL1 despite pullup resistors being present

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ProtoBoard.sch
- **Created**: 2026-03-24

### Correct
- Q1 (SI2323DS PMOS) correctly identified as mosfet, is_pchannel=true, gate_resistors include R1 (10K) and R2 (2.20k), gate_pulldown=R2. The voltage divider R2+R3 on the VIN_Meas net is also correctly detected.

### Incorrect
- design_observations report has_pullup=false for I2C_SDA1, I2C_SCL1, I2C_SDA2, I2C_SCL2. However the Modules.sch sheet contains R43 (100k) connected to FLASH_nCS (chip select, not I2C). Looking at the AA schematic, the I2C nets terminate at global labels with no pullups visible on the local schematic — the pullups may be on the Nucleo board itself. The 'no pullup' observation is factually correct for what is visible on this ProtoBoard schematic, so this is correct behavior rather than an error.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001277: PCB AA: 116 footprints, 2-layer, fully routed, board dimensions correct; kicad_version reported as 'unknown' for KiCad 5 legacy PCB format

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: ProtoBoard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- footprint_count=116 matches schematic component count. Board 68.58x80.518mm, 1294 track segments, 215 vias, 4 zones, 108 nets, routing_complete=true. GND zone stitching correctly identified across both copper layers with 29 stitching vias.

### Incorrect
- The PCB file is version 4 (KiCad 5 legacy .kicad_pcb format) but kicad_version is 'unknown' rather than '5 (legacy)'. The schematic files correctly report '5 (legacy)'. This inconsistency means the PCB analyzer doesn't extract the application version string from KiCad 5 PCB headers the way the schematic analyzer does.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001278: Autosave file analyzed redundantly alongside the real PCB

- **Status**: new
- **Analyzer**: pcb
- **Source**: _autosave-ProtoBoard.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The autosave file _autosave-ProtoBoard.kicad_pcb produces identical results to the main ProtoBoard.kicad_pcb (same stats: 116 footprints, 1294 tracks, 215 vias). Analyzing autosave files adds noise without value. The discover.py script should exclude _autosave-* files.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001279: PCB AB: 158 footprints, 2-layer, fully routed, correct revision delta

- **Status**: new
- **Analyzer**: pcb
- **Source**: Nucleo_L152RE_ProtoBoard_AB_ProtoBoard.kicad_pcb
- **Created**: 2026-03-24

### Correct
- AB revision has 158 footprints vs AA's 116 (adds sensors/modules), 1354 track segments, 184 vias, 2 zones (vs 4 in AA), 98 nets. Board slightly wider at 69.596mm. routing_complete=true, unrouted=0. All consistent with an expanded revision.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001280: Missing Edge.Cuts correctly flagged; layer set complete otherwise; Gerber layer alignment reported as clean despite F.SilkS overhanging board slightly; No NPTH drill file present — not flagged as a...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Gerber_ProtoBoardAA_04_smartprototyping
- **Created**: 2026-03-24

### Correct
- The gerber set has 8 files (B.Cu, B.Mask, B.Paste, B.SilkS, F.Cu, F.Mask, F.Paste, F.SilkS) plus 1 drill file. No outline/Edge.Cuts file is present — correctly flagged as complete=false with missing_required=['Edge.Cuts']. Drill classification: 215 via holes (0.381mm), 167 component holes (1.016mm, 0.9906mm), 10 mounting holes (1.5748mm, 2.9972mm) all correctly categorized.
- F.SilkS extents (68.708mm wide) slightly exceed the PCB board width (68.58mm) but alignment is reported as aligned=true with no issues. This is correct — silkscreen legends slightly outside the board edge is normal and expected, not a misalignment.

### Incorrect
(none)

### Missed
- has_npth_drill=false and no note is raised. For a board with mounting holes (10 holes at 1.5748mm and 2.9972mm classified as PTH mounting holes), it would be worth noting the mounting holes are in the PTH file rather than a separate NPTH file. This is not necessarily wrong but could be flagged as an observation.
  (signal_analysis)

### Suggestions
(none)

---
