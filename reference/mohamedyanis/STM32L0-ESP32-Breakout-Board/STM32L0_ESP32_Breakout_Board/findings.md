# Findings: mohamedyanis/STM32L0-ESP32-Breakout-Board / STM32L0_ESP32_Breakout_Board

## FND-00001309: Crystal circuit correctly detected with correct load cap matching; PWR_FLAG warnings correctly raised for +3.3VA and GND rails; Power budget correctly estimates ~250mA for +3.3V rail (ESP32 + STM32...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32L0_ESP32_Breakout_Board.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- X1 (16MHz) with C8/C9 (10pF each) correctly identified; effective load CL computed correctly.
- +3.3VA has passive/power_in pins but no PWR_FLAG or driver; GND missing PWR_FLAG. Both are real ERC issues in this design.
- ESP32-WROOM-32 estimated at 240mA, STM32L031 at 10mA — realistic estimates for WiFi-active operation.

### Incorrect
(none)

### Missed
- UART_TX/UART_RX nets clearly connect STM32L0 (U2) to ESP32 (U3). The signal_analysis section has no UART bus detection or inter-IC communication topology report. The design comment explicitly states 'transmit data from STM32 to ESP32 via UART' but no bus protocol is detected.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001310: ESP32 thermal pad via insufficiency correctly flagged (6 vias vs 12 recommended); Courtyard overlaps for ESP32 module and push buttons correctly detected; Via-in-pad correctly detected on ESP32 the...

- **Status**: new
- **Analyzer**: pcb
- **Source**: STM32L0_ESP32_Breakout_Board.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- U3 (ESP32-WROOM-32) GND pad (5x5mm, 25mm²) has only 6 standalone vias — correctly flagged with recommended_min_vias=12 and recommended_ideal_vias=25.
- SW1, SW2, SW3 each overlap U3 (ESP32-WROOM-32) by 15.84mm² — these are real DRC violations, likely the buttons are placed in the antenna clearance area of the module.
- U3 pad 39 (GND, 5x5mm thermal pad) has 6 vias through it — correctly identified as via-in-pad with same_net=true.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001311: Layer set validated from gbrjob file with all 11 layers correctly matched; 4.3mm mounting holes misclassified as component_holes despite X2 ComponentDrill attribute; Gerber alignment false-positive...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: Manufacturing_Gerber.json
- **Created**: 2026-03-24

### Correct
- expected_files from .gbrjob matches found layers exactly; complete=true with source='gbrjob' — more reliable than defaults-based detection.
- Height varies 3.5mm between edge cuts (50mm) and B.Cu/B.Mask (46.45mm). This is typical for designs where copper/mask doesn't extend to board corners. The flag is technically correct but this pattern is common and not a manufacturing defect.

### Incorrect
- All 4 holes at 4.3mm (M4 mounting holes matching the MountingHole_4.3mm_M4 footprints) are classified as component_holes because the X2 aperture function is 'ComponentDrill'. The x2_attributes classification method correctly reads the Gerber file but the 4.3mm size unambiguously indicates M4 mounting holes. A size threshold (e.g., >3.5mm = mounting_hole) should override the generic ComponentDrill label.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
