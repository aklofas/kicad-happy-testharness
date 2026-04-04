# Findings: SOICbite / adaptors_SOICbite_SWD_SOICbite_SWD

## FND-00001250: VCC/GND net assignment swapped for J1/J4 ARM SWD connector pins; SWO and SWDCLK net labels are swapped relative to actual pin assignments

- **Status**: new
- **Analyzer**: schematic
- **Source**: SOICbite_SWD.sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The GND pins (3, 5) of J1 and J4 are listed under the VCC net, and VTref pin (1) is listed under GND net. This is a net-name collision or pin assignment error in the legacy KiCad 5 parser — the connector symbol's pin named 'GND' is being placed in the VCC net. The ERC output_conflict/no_driver warnings on SWO/SWDCLK are likely artifacts of this same misparse.
  (signal_analysis)
- Net 'SWO' contains J1/J4 pin 4 (SWDCLK/TCK output pins) while net 'SWDCLK' contains J1/J4 pin 6 (SWO/TDO input pins). The net names are derived from schematic labels but the underlying pin-to-net mapping is crossed. This causes spurious ERC warnings (dual output drivers on SWO, no driver on SWDCLK).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001251: USB_ID net contains VBUS pin instead of ID pin; GND pin of USB connector isolated; USB_ID net misclassified as 'high_speed'; USB differential pair (USB+/USB-) correctly detected with shared ICs J1/...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: adaptors_SOICbite_USB_SOICbite_USB.sch
- **Created**: 2026-03-24

### Correct
- The differential_pairs section correctly identifies the USB D+/D- pair and notes has_esd=false, which is accurate for this simple breakout adapter.

### Incorrect
- J1 pin 1 (VBUS, power_out) is placed in the USB_ID net instead of the +5V power rail. J1 pin 4 (ID) also appears in USB_ID — the VBUS/+5V assignment is wrong. Additionally J1 pin 5 (GND) becomes unnamed_0 rather than joining the GND net, suggesting a net continuity issue in the legacy .sch parser for this connector.
  (signal_analysis)
- The net_classification labels USB_ID as 'high_speed', but USB_ID is the OTG mode-detect line, not a high-speed differential data net. Only USB+ and USB- should be classified high_speed.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001252: False positive: missing_connector_labels warning despite extensive silkscreen pin labels

- **Status**: new
- **Analyzer**: pcb
- **Source**: SOICbite_SWD.kicad_pcb
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The PCB has clearly labeled silkscreen text: DIO, CLK, VCC, GND, 'Cortex Debug', 'SOICbite', and pin numbers. The missing_connector_labels check flags all 4 connectors anyway, indicating the check doesn't correlate nearby silk text with connector footprints.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001253: False positive: missing_revision warning despite 'rev2' silkscreen text present; False positive: missing_connector_labels warning despite signal-labeled silkscreen (5V, D+, D-, ID, GND, NC); USB la...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: adaptors_SOICbite_USB_SOICbite_USB.kicad_pcb
- **Created**: 2026-03-24

### Correct
- The USB differential traces run on both F.Cu and B.Cu without vias (routed through pads), which is accurately captured. This is a THT-only board with no vias, correctly shown.

### Incorrect
- The silkscreen contains the text 'rev2' at (107.3, 84.7) on F.SilkS, but the documentation_warnings still fires missing_revision. The check likely uses a regex that requires 'Rev' (capital R) or 'V1.0' format and misses lowercase 'rev2'.
  (signal_analysis)
- The board has 5V, D+, D-, ID, GND, and NC silk labels near all connectors, yet missing_connector_labels fires for J1, J2, J3. Same root cause as SWD PCB: the check doesn't spatially associate nearby text with connector footprint extents.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001254: KiCad USB gerber set correctly analyzed: all layers found, aligned, complete

- **Status**: new
- **Analyzer**: gerber
- **Source**: adaptors_SOICbite_USB_gerbers
- **Created**: 2026-03-24

### Correct
- All 9 gerber layers and 2 drill files correctly parsed. Layer completeness, drill classification (vias vs component holes), and alignment all accurate. The 7 'vias' detected from small drill sizes (0.35/0.44mm) are consistent with PCB output showing 0 vias — these are actually USB Micro-B mounting/shield holes, a minor via-vs-pad classification ambiguity.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001255: gEDA-format gerber filenames all classified as 'unknown' layer_type; all required layers reported missing; No drill file detected for gEDA gerbers despite SOICbite being a THT design

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gEDA_gerbers
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The gerber directory uses gEDA naming conventions (.top, .bottom, .topmask, .bottommask, .outline, .fab, .topsilk, .toppaste, .bottompaste). The analyzer only recognizes KiCad-style filenames and X2 FileFunction attributes. Since these legacy gerbers lack X2 attributes, all 9 files get layer_type='unknown' and the completeness check reports F.Cu, B.Cu, F.Mask, B.Mask, Edge.Cuts as missing — but they are actually present under different names. The complete=false verdict is a false negative.
  (signal_analysis)

### Missed
- The gEDA gerber set has no .drl file alongside the .gbr files — the drill data may be embedded or missing. The analyzer correctly reports has_pth_drill=false but does not flag this as a potential issue for a THT board. A warning about missing drill file for what appears to be a THT design would be useful.
  (signal_analysis)

### Suggestions
(none)

---
