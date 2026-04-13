# Findings: Nxe5/Modular_Macropad_Hardware_Kicad / Macropad_Dial_Mini_Module_Macropad Dial Module

## FND-00001776: Key matrix correctly detected: 5x5 grid with 19 switches and 19 diodes; SK6812MINI addressable LED chain correctly detected: 17 LEDs chained on LED_GPIO; LTC3536 switching regulator correctly detec...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Macropad_Mini_Module_Macropad_Mini_Module.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identified Row0-Row4 and Col0-Col4 nets forming a sparse 5x5 matrix. Source confirms 18 SW_MEC_5G switches plus 1 RotaryEncoder_Switch (SW21) with 19 plain-diode column diodes, all matching the output exactly.
- Source contains exactly 17 SK6812MINI LEDs (D7, D9-D24). The analyzer correctly found chain_length=17, protocol='single-wire (WS2812)', data_in_net='LED_GPIO', and estimated_current_mA=1020 (17 x 60mA).
- U7 (LTC3536EMSE-PBF) correctly identified as a switching regulator with inductor L1, input_rail=BAT+, output_rail=+3V3, estimated_vout=3.315V from R17/R16 feedback divider (1000k/221k).
- Analyzer reports 107 total_components. Source file contains this many placed, non-power symbol instances (including test points and connectors), which is consistent with the large Mini Module design.

### Incorrect
- The analyzer detects 4 RC filters but filters [0], [1], and [2] all involve the same 4 components (R14, R15, C8, C9) that form a single Type-II compensation network for the LTC3536 switching regulator. Specifically, RC filter [2] (R15+C9, 111kHz) uses the feedback mid-node as both input and ground reference, which is topologically invalid as an independent RC filter. Only filter [3] (R18+C11, 159Hz, ESP32 EN pull-down) is an independent low-pass filter.
  (signal_analysis)
- Q1 is an FS8205A dual N-channel MOSFET used in a battery protection circuit driven by the DW01A (U6). Its drain_net and source_net both resolve to 'GND' which is wrong — the FS8205A is placed in series with the battery path (between B- and GND), not driving an LED load. The 'led' load_type is incorrect; the correct classification would be 'battery_protection' or similar. The drain_is_power=True and source_is_ground=True flags are also inconsistent for this topology.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: Q1 (FS8205A) load_type='led' is incorrect; it is a battery protection MOSFET

---

## FND-00001777: Key matrix correctly not detected in Dial Module (rotary encoders, no key matrix); Addressable LED chains correctly not detected in Dial Module (uses plain LEDs only); BMS chain (TP4056 + DW01A + F...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Macropad_Dial_Module_Macropad_Dial_Module.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The Dial Module has 4 RotaryEncoder switches (SW1, SW2, SW8, SW9) with no Row/Col matrix nets. The analyzer correctly reports key_matrices=[] (empty). There are no SW_MEC_5G key switches in this module.
- Source confirms D1, D2, D3 are all LED_Small (non-addressable), not SK6812MINI. The analyzer correctly reports addressable_led_chains=[] for this module.

### Incorrect
(none)

### Missed
- The Dial Module has a classic 1S LiPo battery management chain: U3=TP4056 (charger from VBUS), U6=DW01A (protection IC), Q1=FS8205A (dual protection MOSFET), and U7=LTC3536 (boost regulator from BAT+ to +3V3). The bms_systems detector returns [] despite all four components being present and interconnected. The TP4056 charger is not recognized as a charging IC, and the overall BMS topology is missed.
  (signal_analysis)
- U1=AS5600L-ASOM is a magnetic rotary position encoder that provides the core functionality for the dial input. It communicates via I2C. The analyzer does not classify it in any signal analysis category — it appears only in the raw components list. The design's key sensor (the angle encoder that makes this a 'Dial Module') goes entirely undetected in signal analysis.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001778: SK6812MINI LED chain correctly detected: 4 LEDs (D5, D6, D7, D8); 5 slide potentiometers (PTA4543) not detected as voltage dividers or ADC inputs

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Macropad_Slider_Module_Macropad_Slider_Module.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Source confirms exactly 4 SK6812MINI instances (D5, D6, D7, D8) in the Slider Module. The analyzer correctly reports chain_length=4 with data_in_net='LED_GPIO'.

### Incorrect
(none)

### Missed
- The Slider Module has 5 Bourns PTA4543 linear slide potentiometers (R19, R20, R21, R22, R23) connected between +3V3 and GND with their wipers feeding ESP32 ADC pins. These function as analog position sensors (voltage dividers). The analyzer finds only 1 voltage_divider (the regulator feedback network) and does not recognize the 3-terminal potentiometers as ADC input voltage dividers.
  (statistics)

### Suggestions
(none)

---

## FND-00001779: SK6812MINI LED chain correctly detected: 10 LEDs in Dial Mini Module

- **Status**: new
- **Analyzer**: schematic
- **Source**: Macropad_Dial_Mini_Module.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Source confirms exactly 10 SK6812MINI instances (D9-D16, D22, D23) in the Dial Mini Module. The analyzer correctly reports chain_length=10, data_in_net='LED_GPIO', with the correct component list.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001780: SK6812MINI LED chain correctly detected: 4 LEDs in Slider Mini Module

- **Status**: new
- **Analyzer**: schematic
- **Source**: Macropad_Slider_Mini_Module_Macropad_Slider_Mini_Module.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- Source confirms exactly 4 SK6812MINI instances (D5, D6, D7, D8) in the Slider Mini Module. The analyzer correctly reports chain_length=4.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001781: PCB statistics correct: 95 footprints, 4-layer board, 102x99mm, routing complete; DFM board size violation correctly flagged: 102x99mm exceeds JLCPCB 100x100mm threshold; Edge clearance of -21.1mm ...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Macropad_Mini_Module_Macropad_Mini_Module.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- PCB analysis correctly reports footprint_count=95, copper_layers_used=4 (F.Cu, B.Cu, In1.Cu, In2.Cu), board_width_mm=102, board_height_mm=99, routing_complete=True, via_count=174. These match the physical .kicad_pcb source file.
- The Mini Module PCB is 102x99mm which correctly exceeds the standard 100x100mm tier at JLCPCB. The analyzer correctly identifies this as a pricing-tier DFM issue. The Dial and Slider Module PCBs at 100x100mm have 0 violations, which is also correct.

### Incorrect
- U4 (ESP32-S3-MINI-1) is placed at (186.9, 132.7) with -135 degree rotation on a 102x99mm board. A clearance of -21.1mm implies the component extends 21.1mm outside the board edge, which is impossible for a placed module. The same module in the Dial Module PCB at 90 degree rotation shows -3.65mm. The severity correlates with rotation angle, strongly indicating a bounding-box calculation bug for rotated footprints in the edge clearance analysis. The Dial Module also shows J2 (-0.08mm) and J3 (-0.21mm) which are edge-mounted connectors intentionally placed at the board perimeter — those negative values are plausible, but U4 at -21.1mm is not.
  (placement_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001782: Unfinished PCB correctly detected: routing_complete=False, 33 unrouted nets, no track segments; Board dimensions correct for Slider Mini Module: 52x100mm

- **Status**: new
- **Analyzer**: pcb
- **Source**: Macropad_Slider_Mini_Module_Macropad_Slider_Mini_Module.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The Slider Mini Module PCB is in an early design stage with 0 track segments and 33 unrouted nets. The copper_layers_used reports only In1.Cu and In2.Cu (no F.Cu/B.Cu traces), and routing_complete=False. The analyzer correctly captures this incomplete state. The DFM metrics section is appropriately minimal (no track widths to report).
- The Slider Mini Module is a narrower half-width board (52mm x 100mm) compared to the full-width 100x100mm modules. The analyzer correctly reports board_width_mm=52.0 and board_height_mm=100.0.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001783: Gerber layer completeness correctly verified: all 11 layers present for 4-layer board; Layer alignment flagged as misaligned due to paste/silk extent differences — this is expected behavior

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Macropad_Mini_Module_Manufacturing.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly identifies all required layers (F.Cu, B.Cu, In1.Cu, In2.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts) as present, with PTH and NPTH drill files, and reports complete=True.

### Incorrect
- The analyzer reports aligned=False with 'Width varies by 6.0mm across copper/edge layers'. This is because paste layers (F.Paste width=45.2mm) only cover SMD pad areas, and inner copper layers have slightly smaller extents than Edge.Cuts. These differences are normal and expected in professional PCB designs — the Edge.Cuts layer always defines the true board boundary, and other layers need not extend to all edges. F.SilkS (98.7mm) exceeding Edge.Cuts (102mm) by the analyzer's measurement suggests a measurement artifact. The board is correctly fabricated.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001784: Dial Module gerber analysis used wrong Manufacturing folder (Mini Module gerbers instead of Dial Module gerbers)

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Macropad_Dial_Module_Manufacturing.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Dial Module's Manufacturing/ folder contains files named 'Modular MacroPad-*.gbr' (from the full Mini Module design), not Dial-Module-specific gerbers. The analyzer processed these wrong gerbers, reporting 97 component_refs (which match the Mini Module's ~95 footprints), while the Dial Module PCB has only 49 footprints. The gerber board_dimensions (102.2x99.2mm) also match the Mini Module (102x99mm), not the Dial Module (100x100mm). This is a repo organization issue (developer stored wrong gerbers in the Dial Module folder), but it results in the gerber output being entirely mismatched to the Dial Module PCB/schematic.
  (board_dimensions)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001785: Dial Mini Module gerber analysis also used the Mini Module's Manufacturing folder gerbers

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Manufacturing.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The Dial Mini Module manufacturing output also analyzed 'Modular MacroPad-*.gbr' files (the full Mini Module gerbers), reporting 97 components and 102.2x99.2mm dimensions. The Dial Mini Module PCB is 52x100mm with 49 footprints. Both the Dial Module and Dial Mini Module directories contain the same wrong gerber set. This is a repo organization issue — no Dial-Module-specific gerbers were ever generated and committed by the designer.
  (layer_count)

### Missed
(none)

### Suggestions
(none)

---
