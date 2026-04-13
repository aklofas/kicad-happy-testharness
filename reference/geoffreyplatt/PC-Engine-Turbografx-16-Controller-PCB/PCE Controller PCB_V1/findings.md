# Findings: geoffreyplatt/PC-Engine-Turbografx-16-Controller-PCB / PCE Controller PCB_V1

## FND-00000973: Capacitor C2 value '0.1f' parsed as 0.1 farads instead of 0.1uF; ERC 'no_driver' false positive on 5V net — connector-powered design has no PWR_FLAG; Component counts, types, and net topology corre...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCE Controller PCB_V1.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 26 components correctly identified (9R, 10SW, 2IC, 1connector, 1resistor_network, 3C). All 30 nets present with correct pin assignments. SN74HC157N and SN74HC163N correctly typed as ICs.
- Single GND domain detected, correctly not flagging multiple domains. Power rail 5V identified as the only supply rail.

### Incorrect
- C2 has value '0.1f' which is almost certainly a typo for '0.1uF'. The analyzer reports parsed_value=0.1 (treating 'f' as farads), which is a 1,000,000x error. C1 has the same issue. The analyzer should flag this as a suspicious value or parsing ambiguity.
  (signal_analysis)
- Net '5V' is flagged as having no driver (11 total ERC warnings of this type). Power comes from J1 connector (pin 1 = 5V), not a power symbol. This is the same KH-160 class issue: connector-powered designs without PWR_FLAG generate spurious no_driver warnings. The net is clearly driven by the connector.
  (signal_analysis)
- The ground_domains.ground_nets.GND.components list has 13 entries but the GND net has 18 pin connections across more components. SW1, SW2, SW3, SW4, and RN1 are all on GND but not listed in the ground domain component set.
  (signal_analysis)

### Missed
- U2 (SN74HC163N) pins QD (pad 11), QA (pad 14), and RCO (pad 15) are unconnected outputs that end up on single-pin unnamed nets. The connectivity_issues section shows empty unconnected_pins, but these outputs are floating. These should be flagged as potentially unintended unconnected outputs.
  (signal_analysis)
- This is a classic digital controller: RN1 (8x47k resistor network) pulls up 8 button lines to 5V, and individual buttons (SW5-8 + SW1-4 via mux) pull them to GND. No pull-up or button topology was detected in signal_analysis. The design_observations list is empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000974: Zone fill_ratio > 1.0 (1.397) — filled area larger than outline area, impossible value; Routing completeness, board dimensions, and layer stack correctly reported; missing_switch_labels warning inc...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCE Controller PCB_V1.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- routing_complete=true with 0 unrouted nets, 2-layer board (F.Cu + B.Cu), board 132.02x47.08mm, 27 footprints, 30 nets all correctly extracted.
- The PCB has footprints with designators I, II, RUN, SEL (used as physical labels for buttons instead of SW_N). The PCB analyzer correctly lists them as footprints and includes them in component_groups. This is unusual design practice but handled correctly.
- Board is 132x47mm, exceeding JLCPCB standard tier 100x100mm limit. The DFM violation is correctly identified with accurate dimensions.

### Incorrect
- zones[0] shows outline_area_mm2=7011.08 but filled_area_mm2=9794.32, giving fill_ratio=1.397. Filled copper cannot exceed the outline area. This is a calculation bug — likely the outline_area calculation is using only the rectangular outline bbox while the actual board outline is smaller, or the fill regions include overlapping fills across B.Cu and F.Cu being summed.
  (signal_analysis)
- The PCB silkscreen warning flags SW5/SW6/SW7/SW8/SW9/SW10 as missing function labels. However, these switches have their function encoded in component value fields (UP/DOWN/LEFT/RIGHT) and likely have text near them on silkscreen. The warning fires because the refs themselves aren't visible on silk, but the board uses value-based labeling. This is a borderline false positive for a consumer product controller.
  (signal_analysis)

### Missed
- U2 SN74HC163N has pins A(3), B(4), C(5), D(6) all tied to GND, meaning the counter always loads 0. This is a valid functional choice for a counter that only counts, but is worth noting. The PCB pad_nets show this correctly but no design_observation flags it.
  (signal_analysis)

### Suggestions
(none)

---
