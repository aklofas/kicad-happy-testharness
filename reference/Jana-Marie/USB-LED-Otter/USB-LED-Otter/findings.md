# Findings: USB-LED-Otter / USB-LED-Otter

## FND-00001647: Component count: 14 total components correctly parsed from KiCad 5 legacy schematic; USB differential pair (USB_P/USB_N) correctly detected; MCP1700 LDO regulator topology not resolved — input/outp...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-LED-Otter.sch.json.json
- **Created**: 2026-03-24

### Correct
- The analyzer correctly extracted 14 components: U1 (MCP1700 LDO), U2 (STM32F072), 5 capacitors, 1 resistor, 1 switch, 5 connectors (J1-J5). The legacy .sch parsing is accurate.
- The analyzer correctly identified USB_P and USB_N as a USB differential pair connected to J1. The pair is detected with has_esd: false, which is correct since there is no ESD protection IC on this board.
- The three power rails are correctly extracted from the schematic. Decoupling analysis shows +5V has 1 cap (C1, 100nF) and +3.3V has 4 caps (C2-C5, 100nF each, total 0.4µF).

### Incorrect
(none)

### Missed
- U1 is an MCP1700-3302E LDO regulator. Its lib_id is 'Regulator_Linear:MCP1700-3302E_SOT23'. The schematic shows it powered from +5V and outputting +3.3V, but the analyzer reports input_rail: null, output_rail: null, topology: 'unknown'. The MCP1700 pin connections (IN→+5V, GND→GND, OUT→+3.3V) are traceable from the net data but the regulator pin mapping was not resolved.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001648: PCB footprint count 14 matches schematic component count; Board dimensions 12×15mm correctly extracted

- **Status**: new
- **Analyzer**: pcb
- **Source**: USB-LED-Otter.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The PCB has 14 SMD footprints (2 front, 12 back), matching the schematic's 14 components. All 14 are SMD (0 THT), routing complete with 0 unrouted nets.
- The PCB dimensions are reported as 12.0×15.0mm, matching the gerber Edge.Cuts extent of 12×15mm exactly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001924: Component count, types, BOM, and net classification all correct; MCP1700-3302E LDO: topology=unknown, input_rail=None, output_rail=None, estimated_vout=None; Pin/net linkage missing for complex com...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_USB-LED-Otter_USB-LED-Otter.sch.json
- **Created**: 2026-03-24

### Correct
- 14 components correctly parsed (2 ICs, 5 caps, 1 resistor, 1 switch, 5 connectors). Power rails +3.3V/+5V/GND identified. Decoupling analysis correctly shows 1 cap on +5V (C1) and 4 caps on +3.3V (C2/C3/C4/C5). USB differential pair USB_P/USB_N correctly detected. SCL/SDA/SCK net classifications correct.

### Incorrect
- U1 is from lib 'Regulator_Linear:MCP1700-3302E_SOT23', a fixed 3.3V LDO. Topology should be 'LDO' (same lib as AZ1117-3.3 which correctly gets topology='LDO' in UDVBM-1). estimated_vout should be 3.3 (deducible from part suffix '3302E' = 3.3V, 2E = SOT-23). The input (+5V) and output (+3.3V) rails cannot be resolved because U1.pins=[] in the legacy KiCad5 parser — the pin/net linkage for complex components is incomplete. This is consistent with the regulator having no neighbors in the subcircuit.
  (signal_analysis)

### Missed
- In the legacy KiCad5 .sch format, complex components (ICs and multi-pin connectors) have pins=[] in the output. Simpler 2-pin passives (C1-C5, R1, SW1) do have their pins. Nets for USB_P, USB_N, LED, SCL, SDA, SCK, SWDIO, SWCLK have 0 connected component-pins in the nets dict, though they have correct point_counts. This means the STM32F072CBUx (U2) signal analysis cannot identify which signals connect to which STM32 pins.
  (components)

### Suggestions
(none)

---

## FND-00001925: PCB statistics, layer detection, routing completeness, and thermal analysis all correct; PCB net count difference from schematic is expected and correctly handled

- **Status**: new
- **Analyzer**: pcb
- **Source**: repos_USB-LED-Otter_USB-LED-Otter.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- 14 footprints, all SMD (correct — board is fully SMD). 2-layer board (F.Cu + B.Cu). 168 track segments, 17 vias, 2 zones. Board dimensions 12×15mm correct. Routing complete (0 unrouted). Thermal pad on U2 (QFN-48 EP, pad 49, 2.6×2.6mm, GND) correctly identified. GND zone stitching detected with 7 vias.
- PCB reports 39 nets vs schematic 13. The difference is 27 anonymous 'Net-(U2-Pad##)' nets from the STM32F072CBUx QFN-48 unconnected pads. Named PCB nets (GND, +3V3, +5V, USB_P, USB_N, LED, SCL, SDA, SCK, SWDIO, SWCLK) match the schematic named nets (note: PCB uses '+3V3' while schematic uses '+3.3V', which is the same net). This difference is correct behavior.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001926: Layer completeness, board dimensions, and drill classification all correct; smd_apertures count derived from paste layer flashes correctly labeled

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_USB-LED-Otter_gerber.json
- **Created**: 2026-03-24

### Correct
- All 9 required layers found (F.Cu, B.Cu, F.Mask, B.Mask, F.Paste, B.Paste, F.SilkS, B.SilkS, Edge.Cuts). Board dimensions 12×15mm match PCB. PTH drill: 17 holes total (16 at 0.300mm, 1 at 0.399mm) — correctly classified as all vias (fully SMD board, no component THT holes). NPTH file present with 0 holes. Complete=true. KiCad 5.1.4 generator identified from X2 attributes.
- smd_apertures=81 is the sum of B.Paste flashes (74) + F.Paste flashes (7). smd_ratio=1.0 is correct (all-SMD board). The source label 'paste_layer_flashes' accurately describes the methodology. The 74 B.Paste flashes for U2 QFN-48 (49 pads) plus other back-side components is plausible.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
