# Findings: 0101shift/Project_OAK / Design_LLD_Design_V0.1_Project_OAK_MAIN_BRD_V0.1_RTC_Change_Project_OAK_MAIN_BRD_V0.1

## FND-00001720: Component counts correctly parsed for V0.1 main board (112 total); I2C bus detected with pull-ups on RTC_SCL and RTC_SDA; RV-8263 RTC correctly classified as ic, not crystal; 37 LEDs and 7 BJT tran...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Project_OAK_MAIN_BRD_V0.1.sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 112 components: 1 battery, 3 switches, 2 ICs (ATmega328PB-MU + RV-8263-C7 RTC), 16 capacitors, 33 resistors, 13 test points, 37 LEDs, 7 BC547 transistors. All component types are correctly classified.
- The analyzer correctly identifies the I2C bus between U1 (ATmega328PB) and U2 (RV-8263 RTC) with 4.7K pull-up resistors on both SCL (R10) and SDA (R11) to +3V0. The primary i2c nets RTC_SCL and RTC_SDA are correctly captured.
- Despite the RV-8263-C7-32.768KHZ-20PPM-TA-QC being in the Crystal footprint library and having 'crystal' in its name, the analyzer correctly classifies it as type 'ic' (it is an integrated RTC module with I2C interface, not a passive crystal). crystal_circuits is correctly empty.
- All 37 LEDs (D1–D37) and all 7 BC547 NPN transistors (Q1–Q7) are identified. Transistor circuit analysis correctly shows 6 transistors with LED loads (Q2–Q7) and Q1 with a resistive load. emitter_is_ground=False is correct because emitter nets connect through 120E/1K resistors to +3V0, not GND directly.
- The analyzer correctly identifies 4 RC low-pass filters: R4/C3 (DWN_BTN), R3/C2 (UP_BTN), R2/C1 (LGT_ON_BTN), and R17/C13 (MCU_RSTn), all with 10k resistors and 0.1uF capacitors giving ~159 Hz cutoff. These are correct debounce/reset filter identifications.
- The 50% voltage divider (R14=10k top, R15=10k bottom) feeding the +3V0_VOL_MON net is correctly identified. This is used for battery voltage monitoring on an analog ADC pin of the ATmega328PB.
- The ICSP SPI programming interface (MISO, MOSI, SCK) on U1 is correctly detected as a full-duplex SPI bus with chip_select_count=3, consistent with the ATmega's ICSP header.

### Incorrect
- The analyzer reports three I2C nets: RTC_SCL (U1+U2), RTC_SDA (U1 only), and __unnamed_27 (U2 SDA pin only). This third entry is caused by U2's SDA pin (pin 8) being disconnected from the RTC_SDA net label in the V0.1 schematic — U2's SDA wire was not labeled. The analyzer is faithfully reporting the source connectivity, but presenting it as a third I2C bus segment without a pull-up is misleading. The real I2C bus has both SCL and SDA, but the SDA analysis is split incorrectly into two entries.
  (design_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001721: V0 main board correctly identifies 114 components including 18 capacitors; V0 RTC_SCL I2C net incorrectly includes U2 /IRQ pin as a bus device; Voltage divider mid-point incorrectly lists U2 GND pi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Design_LLD_Design_V0_Project_OAK_MAIN_BRD_V0_Project_OAK_MAIN_BRD_V0.sch.json
- **Created**: 2026-03-24

### Correct
- The V0 board has 2 more capacitors than V0.1 (C10 = 0.1uF and C11 = 1uF, which were part of the original RX8130CE RTC decoupling). The total of 114 components and unique_parts=18 is correct.

### Incorrect
- The RTC_SCL net in the V0 schematic includes both U2 pin 2 (SCL, correct) and U2 pin 6 (/IRQ, incorrect) due to a net routing collision in the source schematic — the SCL wire and the /IRQ wire overlap at the same coordinate. The analyzer faithfully captures this but reports U2 twice in the RTC_SCL device list and includes the /IRQ output as if it were an I2C device, which will confuse bus topology analysis. This is a source schematic bug, but the analyzer should ideally filter output-type pins from I2C device lists.
  (design_analysis)
- The voltage divider R14/R15 feeding +3V0_VOL_MON has mid_point_connections that includes U2 (RX8130CE) pin 7 (GND, type=power_in). This is because the RX8130CE's GND pin happens to be connected to the +3V0_VOL_MON net (likely a schematic routing error in the source). The analyzer correctly reports the net connection, but listing a GND-type power pin as a mid-point load is misleading. A proper mid-point load should be a signal or input type pin.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001722: Mechanical PCB schematic correctly parsed as empty (0 components)

- **Status**: new
- **Analyzer**: schematic
- **Source**: Design_LLD_Design_V0_Project_OAK_BOT_CAVITY_V0_Project_OAK_BOT_CAVITY_V0.sch.json
- **Created**: 2026-03-24

### Correct
- BOT_CAVITY_V0 is a mechanical outline PCB with no schematic components. The analyzer correctly returns 0 total_components, empty BOM, no nets, and no signal detections. The same is true for BOT_STRAP, HEX_COVER_INNER, HEX_COVER_OUTER, TOP_LED_CAVITY, and WATCH_DIAL.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001723: V0.1 PCB correctly identified as 6-layer board with 125 footprints; DFM tier correctly classified as 'challenging' due to small annular rings

- **Status**: new
- **Analyzer**: pcb
- **Source**: Project_OAK_MAIN_BRD_V0.1.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies 6 copper layers (F.Cu, In1.Cu–In4.Cu, B.Cu), 125 footprints (112 schematic components + 5 logo G*** + 8 REF** mounting holes), 158 vias, 992 track segments, and a complete routing. The board is 42.61 x 42.61mm.
- The analyzer correctly identifies the board as DFM 'challenging' due to 0.075mm annular rings (below the 0.1mm advanced process minimum). The minimum trace width of 0.142mm and 6-layer construction are consistent with an advanced PCB design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001724: V0 PCB copper_layers_used=2 but board actually uses 6 copper layers; V0 PCB routing complete with 145 footprints and 993 track segments

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Design_LLD_Design_V0_Project_OAK_MAIN_BRD_V0_Project_OAK_MAIN_BRD_V0.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The V0 board is correctly identified as fully routed (routing_complete=true, unrouted_net_count=0), with 145 footprints (more than V0.1 because C10/C11 and additional RTC-related components are present), 993 track segments, and 157 vias. The board dimensions match V0.1 at 42.61×42.61mm.

### Incorrect
- The V0 PCB has inner layers defined with alias=hide: In2.GND, In3.SIG, In4.GND, In5.PWR. These layers contain actual copper: tracks on In3.SIG, zone fills on In2.GND, In4.GND, In5.PWR (confirmed via layer_transitions and thermal_analysis zone_stitching). The analyzer reports copper_layers_used=2 and copper_layer_names=['B.Cu','F.Cu'] because it filters layers with alias='hide'. The correct answer is 6 copper layers (same as V0.1, since both share the same PCB stack-up, only the layer naming/visibility differs).
  (statistics)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001725: Mechanical PCB correctly shows 0 tracks and 0 copper layers used

- **Status**: new
- **Analyzer**: pcb
- **Source**: Design_LLD_Design_V0_Project_OAK_BOT_CAVITY_V0_Project_OAK_BOT_CAVITY_V0.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- BOT_CAVITY is a mechanical outline board containing only mounting holes (MountingHole_2.1mm, REF** references) and no electrical components. The analyzer correctly reports 0 track_segments, 0 vias, 0 zone_count, 0 copper_layers_used, and routing_complete=true. All 6 mechanical PCBs (BOT_CAVITY, BOT_STRAP, HEX_COVER_INNER, HEX_COVER_OUTER, TOP_LED_CAVITY, WATCH_DIAL) are correctly handled.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001726: V0.1 gerber correctly identified as 6-layer with complete layer set; Gerber completeness check correctly passes for V0.1 main board

- **Status**: new
- **Analyzer**: gerber
- **Source**: Project_OAK_MAIN_BRD_V0.1_gerber.json
- **Created**: 2026-03-24

### Correct
- The gerber output correctly identifies 6 copper layers (F.Cu, B.Cu, In1.Cu–In4.Cu), 12 gerber files total, complete=true with no missing or extra layers per the .gbrjob file. Via count of 158 matches the PCB output exactly. The 114 unique component references in the gerber match 112 schematic components plus 2 additional G*** logo pads counted separately.
- All 12 expected layers from the .gbrjob file are present in the gerber set: F.Cu, B.Cu, In1.Cu–In4.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, Edge.Cuts, F.Paste. No missing or extra layers. PTH drill file present with 166 holes (158 vias + 8 mounting holes).

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001727: Mechanical PCB gerbers correctly show 2-layer board with mounting holes only; Gerber alignment reported as failed for mechanical PCBs due to empty copper layers

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Design_LLD_Design_V0_Project_OAK_BOT_CAVITY_V0_Project_OAK_BOT_CAVITY_Gerber.json
- **Created**: 2026-03-24

### Correct
- The BOT_CAVITY gerbers are correctly parsed as a 2-layer board with 7 gerber files (complete per .gbrjob), 8 mounting holes (2.1mm diameter), 0 via count, 0 component holes, and 0 SMD apertures. F.Cu and F.SilkS are empty (all copper is on B.Cu for the mounting ring pads). All 5 other mechanical PCBs have the same correct structure.

### Incorrect
- All 6 mechanical PCBs report aligned=False with large dimension mismatches (e.g. 'Width varies by 36mm across copper/edge layers'). This is caused by F.Cu having 0x0 extents (no copper on top layer) while Edge.Cuts spans the full 42.61mm board outline, creating an artificial mismatch. For mechanical boards where copper is minimal (only mounting hole pads on B.Cu), empty-layer extent comparisons against Edge.Cuts will always produce false alignment failures. The alignment check should exclude layers with zero-extent copper.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---
