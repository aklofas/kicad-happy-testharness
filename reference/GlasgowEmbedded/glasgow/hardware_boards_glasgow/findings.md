# Findings: glasgow / hardware_boards_glasgow_glasgow

## FND-00000001: current_sense detector produces 68 false positives in glasgow.kicad_sch by pairing R49 (0.15 ohm shunt) with every IC sharing GND net

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: KH-007
- **Created**: 2026-03-13

### Correct
- R49 (0R15) + INA233 current sense IC is correctly detected

### Incorrect
- 67 of 68 current_sense detections are false positives — R49 paired with unrelated ICs (SN74LVC1T45, CAT24M01X, etc.) that merely share GND net
  (signal_analysis.current_sense)

### Missed
(none)

### Suggestions
- Detector should require shunt resistor to be in series path (not shunt to GND) or check sense IC has current sense pins (INP/INM)

---

## FND-00000006: Voltage divider false positives: R30/R48 and R56/R48 on ISNS_H net are current sense network components, not dividers. R5/R4 on ~{CY_RESET} is a pull-up/pull-down pair, not a sensing divider.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: KH-012
- **Created**: 2026-03-13

### Correct
- R33/R28 (49k9/59k) feedback divider for VDAC→VFB correctly detected with is_feedback=True
- R34/R35 on VIO→VFB also appears to be a legitimate feedback divider

### Incorrect
- R30 (4R7) / R48 (0R15) on ISNS_H → GND detected as divider but these are current sense shunt resistors
  (signal_analysis.voltage_dividers)
- R56 (0R33) / R48 (0R15) on ISNS_H → GND same issue — current sense, not divider
  (signal_analysis.voltage_dividers)
- R5/R4 (100k/100k) on ~{CY_RESET} → GND is a pull-up/pull-down pair on a digital reset line, not a voltage sensing divider
  (signal_analysis.voltage_dividers)

### Missed
(none)

### Suggestions
- Filter out sub-1-ohm resistor pairs (these are current sense). Filter out equal-value resistor pairs on digital signal names. Require mid-point connection to an analog input or feedback pin.

---

## FND-00000018: CRITICAL: +3V3 power rail completely missing from nets dict despite 52 power symbols in main sheet + 33 in io_banks (85 total). GND (133 symbols), +5V (10), +1V2 (5) all work correctly. This means ALL +3V3 connections are invisible — signal analysis for anything on the 3.3V rail will fail.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Related**: NEW - not yet in issue tracker
- **Created**: 2026-03-13

### Correct
- GND, +5V, +1V2, VCCPLL0, VCCPLL1, GNDPLL0, GNDPLL1 all correctly appear in nets

### Incorrect
(none)

### Missed
(none)

### Suggestions
- Debug build_net_map() for +3V3 specifically. May be a naming collision, coordinate issue, or power symbol lib_id resolution problem. Check if +3V3 power symbols have correct pin positions.

---

## FND-00000025: 73 capacitors with value "u1" (European notation for 0.1uF) have no parsed_value. Parser handles "4u7" but fails when unit prefix precedes digit.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_boards_glasgow_glasgow.kicad_sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- "u1" = 0.1uF not parsed. Pattern: unit prefix before digit (u1, n47, p33). Parser only handles digit-first like "4u7".
  (components[*].parsed_value)

### Suggestions
- Add parsing for prefix-first notation: u1=0.1u, n47=0.47n, p33=0.33p

---

## FND-00000303: Gerber review: 6 revisions (revA-C3) of 4-layer FPGA board. Cross-revision progression correctly tracked

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: hardware/boards/glasgow/
- **Related**: KH-177, KH-184, KH-186
- **Created**: 2026-03-18

### Correct
- All 6 revisions correctly 4-layer. Alignment progression accurate: revA-C1 misaligned, revC2-C3 aligned. Via evolution (0.3mm-only to 0.3+0.2mm BGA escape) captured
- revC3 correctly uses X2 classification (KiCad 7) while revA-C2 use diameter heuristic (KiCad 5.x). Correctly adapts across versions
- Growing file count handled: 11 (revA) to 15 (revC3, adds Fab+Courtyard). Extra layers not false-flagged

### Incorrect
- smd_ratio=0.0 for all 6 revisions. Wrong for FPGA board (revC3: 812 front paste flashes)
  (pad_summary)
- revC3: 3.5mm mounting holes misclassified as component_holes via X2 ComponentDrill. Same holes correctly classified in revC1/C2 via diameter heuristic
  (drill_classification.mounting_holes)
- has_pth_drill=false for revA-C2 (5 revisions) despite 189-560 vias. Only revC3 with explicit MixedPlating gets true
  (completeness)

### Missed
(none)

### Suggestions
- Override X2 ComponentDrill for NPTH >= 2.5mm as mounting holes

---

## FND-00002098: TPS73101 feedback divider uses wrong resistor refs for second instance (U14 gets R34/R35 instead of R28/R29)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_glasgow_hardware_boards_glasgow_io_banks.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The glasgow io_banks sheet instantiates io_buffer.kicad_sch twice (IO_Buffer_A and IO_Buffer_B). Each instance contains a TPS73101 adjustable LDO: U31 in IO_Buffer_A and U14 in IO_Buffer_B. The physical feedback divider resistor in io_buffer is tagged as R34 (59k) in instance A and R28 (59k) in instance B, and R35 (24k3) in instance A / R29 (24k3) in instance B. The analyzer reports both U31 and U14 using R34/R35 as their feedback divider — it always picks the IO_Buffer_A instance reference and applies it to both regulators. The estimated_vout of 2.057V is only valid for one of the two instance interpretations; the actual VIO output depends on which R28/R29 values are correct. This is a hierarchical multi-instance ref resolution bug.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002099: USB-C compliance check correctly identifies VBUS ESD and decoupling failures; Memory interfaces correctly detect dual EEPROMs connected to both USB MCU and FPGA

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_glasgow_hardware_boards_glasgow_glasgow.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The analyzer detects J1 (USB_C_USB2.0) and runs 7 compliance checks. CC1/CC2 5.1k pull-downs pass, USB ESD IC passes, but vbus_esd_protection and vbus_decoupling fail. DP/DM series resistors are informational. The summary reports 3 pass, 2 fail, 2 info. This is an accurate characterization of a USB-C device-only (sink) implementation that has ESD protection IC but lacks a dedicated VBUS ESD TVS diode and bulk decoupling on the VBUS rail at the connector.
- The analyzer detects U2 (CAT24M01X, 1Mbit EEPROM) and U3 (BL24C256A, 256kbit EEPROM) as memory interfaces. Both are correctly identified as connected to both U1 (CY7C68013A USB MCU) and U30 (ICE40HX8K FPGA) via 2 shared signal nets (I2C SDA/SCL). This is the Glasgow debug tool's I2C bus architecture where the MCU and FPGA share access to both configuration EEPROMs.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002100: Mounting holes misclassified as component holes in revC3 due to X2 attribute tagging

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_glasgow_hardware_boards_glasgow_revC3.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- RevC3 gerbers use X2 attributes (classification_method: x2_attributes) and report 0 mounting holes. However the drill file contains 4 holes at 3.5mm diameter tagged as PTH,ComponentDrill rather than MountingHole. Earlier revisions (revA–revC2) use diameter_heuristic classification and correctly report 4-6 mounting holes. The 3.5mm PTH holes are almost certainly board mounting holes (consistent with M3 screws), but KiCad tagged them as ComponentDrill in the X2 attributes. The analyzer faithfully follows the X2 attribute classification, resulting in zero mounting holes shown for revC3 while revC2 (identical board with heuristic classification) shows 4 mounting holes.
  (drill_classification)

### Missed
(none)

### Suggestions
(none)

---
