# Findings: Stulinaz/STM32F103RB_USB_to_UART_SPI_I2C / KICAD_STM32_MULTIPROTOCOL

## FND-00001303: Footprint filter warnings correctly flagged for LEDs using R-footprint; PWR_FLAG warning correctly raised for +3V3 rail; Annotation issue C0 (zero-indexed ref) correctly detected; USB compliance vb...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32_MULTIPROTOCOL.kicad_sch
- **Created**: 2026-03-24

### Correct
- STNDBY1, TX1, RX1 and other LEDs use Resistor_SMD footprint — analyzer correctly identifies the footprint doesn't match LED filter patterns on all 9 LED components.
- +3V3 rail has power_in pins but no PWR_FLAG or power_out driver; only one warning is raised (correctly, since +3.3V is a separate alias rail with its own PWR_FLAG power symbol present).
- C0 is correctly flagged as a zero-indexed reference in annotation_issues.
- Subcircuit correctly identifies U2 as center IC with CF1-CF4 crystal caps and bypass capacitors as neighbors.

### Incorrect
- USB1 (USB_B_Mini) is flagged for missing VBUS ESD protection, but ESD1 (USBLC6-2SC6) is present on the USB D+/D- lines. The check appears to test for VBUS-specific ESD rather than D-line ESD protection. Whether this is truly missing VBUS ESD depends on design intent; calling it 'fail' may be overly strict if the design relies on upstream protection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001304: Courtyard overlaps correctly detected for multiple components; Via fanout pattern correctly identified for LQFP-64 STM32

- **Status**: new
- **Analyzer**: pcb
- **Source**: STM32_MULTIPROTOCOL.kicad_pcb
- **Created**: 2026-03-24

### Correct
- PWR1/USB1 overlap (15.5mm²) and U2/Y2 overlap (11.3mm²) are flagged — these are real DRC violations in the design.
- U2 (LQFP-64) correctly identified with 25 fanout vias across 18 unique nets.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001305: SMD ratio 0.0 despite board having 60 SMD components; 2 NPTH 1.0mm holes misclassified as component_holes instead of mounting_holes; Missing F.Paste layer correctly flagged as missing_recommended

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: production_PCB
- **Created**: 2026-03-24

### Correct
- F.Paste absent from gerber set; correctly listed in missing_recommended (not missing_required), appropriate since paste is optional for wave-soldered or hand-assembled boards.

### Incorrect
- pad_summary shows smd_apertures=0 and smd_ratio=0.0. This is because F.Paste is missing from the gerber set and SMD detection relies on X2 aperture function data. The board has 60 SMD components in the PCB but the gerber set lacks paste and the copper gerbers use older X2 attributes. This is a known limitation but smd_ratio=0.0 is misleading.
  (signal_analysis)
- The two NPTH 1.0mm holes are classified under component_holes (diameter_heuristic path). NPTH holes at 1.0mm are too small for standard M2.5+ mounting hardware but could be standoff holes; however, since they are explicitly NPTH (no pad), they are more likely mounting/fiducial holes than component holes. The classification_method is diameter_heuristic which lacks the NPTH-aware logic.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
