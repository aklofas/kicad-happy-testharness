# Findings: esp32bb / bottom_pcb_bottom_pcb

## FND-00002051: NCP1117ST33T3G LDO (U2) not detected as power regulator; RC filter input/output direction swapped for R3+C1 reset timing circuit on EN pin; RC filter type labeled 'RC-network' instead of 'low-pass'...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32bb_main_pcb_esp32bb.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- U2 is an NCP1117ST33T3G 3.3V LDO regulator — one of the most common linear regulators — but it does not appear in signal_analysis.power_regulators. The component uses a local rescue library ('esp32bb-rescue:NCP1117ST33T3G') and pin names VI/VO/GND rather than the standard IN/OUT naming, which prevents the regulator detector from recognizing it. power_regulators is empty despite a clear LDO being present.
  (signal_analysis)
- The RC filter (R3=10K, C1=1nF) is reported with input_net='EN' and output_net='+3.3V', but the actual topology is the reverse: +3.3V feeds through R3, the mid-node (EN rail) is the filtered output, and C1 connects from EN to GND. The analyzer used the resistor's pin1 net as 'input_net', but R3 pin1 connects to EN (the output node) while R3 pin2 connects to +3.3V (the source). The direction assignment is wrong.
  (signal_analysis)
- The same reset timing circuit topology (R to EN, C to GND, power rail as source) is labeled 'low-pass' in esp32-s3-testboard but 'RC-network' in esp32bb. Both use 10K resistor and microfarad-range capacitor on the EN pin of an ESP32 module. The inconsistency suggests the type classification depends on secondary factors (net classification, power rail detection) rather than topology, and may produce non-deterministic results.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002052: Thermal pad analysis reports duplicate entries: P3 pad 6 appears 4 times, U3 pad 29 appears 4 times; Duplicate P3 reference in PCB file not flagged

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_esp32bb_main_pcb_esp32bb.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The thermal_analysis.thermal_pads list contains 9 entries for only 3 unique component+pad combinations: P3/pad6 appears 4 times (with varying nearby_thermal_vias: 0,1,0,0), U3/pad29 appears 4 times (all with nearby_thermal_vias=1), and U1/pad39 appears once. This is a bug in the thermal pad detection — the same pad is being reported multiple times, likely because the search algorithm iterates over multiple search radii or footprint instances and collects duplicates without deduplication.
  (thermal_analysis)

### Missed
- The PCB file contains two footprints with reference 'P3' (the USB OTG connector), visible in both the footprint reference list and the silkscreen values_visible_on_silk list which shows 'P3' twice. The PCB connector P3 is likely a through-hole USB connector with a mechanical mounting footprint duplicated. The analyzer does not flag this duplicate reference anywhere — not in DFM, placement, connectivity, or any other section. A duplicate reference check should be part of PCB validation.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002053: Gerber alignment flagged as failed due to copper-to-edge-cuts height variation, but it is not an alignment error; Missing F.Paste gerber correctly flagged as missing_recommended

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_esp32bb_main_pcb_plots.json
- **Created**: 2026-03-24

### Correct
- The main_pcb gerber set (7 files) is missing F.Paste and B.Paste layers. The analyzer correctly identifies F.Paste in missing_recommended. Given the board has SMD components (27 SMD of 30 total footprints), the paste layer should have been exported for solder stencil production. This is a real omission in the exported gerber set.

### Incorrect
- The alignment check reports aligned=false with 'Height varies by 9.3mm across copper/edge layers' because the copper layers (B.Cu: 51.68mm, F.Cu: 51.68mm) are shorter in height than the Edge.Cuts outline (60.96mm). This is not a misalignment — the copper simply does not extend to the top portion of the board outline, which is a common and intentional design choice (e.g., a connector zone or mechanical margin). The alignment algorithm incorrectly treats this as an error rather than a routing boundary.
  (alignment)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002054: bottom_pcb marked complete=false because it has only NPTH drill holes, but it is a valid mechanical PCB

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber_esp32bb_bottom_pcb_gerbers.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- The bottom_pcb is a pure mechanical PCB (0 electronic components, 4 NPTH mounting holes, no SMD or THT components). The completeness check sets complete=false because has_pth_drill=false. For mechanical or panel PCBs with only mounting holes, NPTH-only drill files are expected and correct. The completeness algorithm should not require PTH drill when the board has no electronic components.
  (completeness)

### Missed
(none)

### Suggestions
(none)

---

## FND-00002055: Empty schematics (bottom_pcb, spacer_pcb) handled gracefully with zero-count stats

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_esp32bb_bottom_pcb_bottom_pcb.sch.json
- **Created**: 2026-03-24

### Correct
- The bottom_pcb and spacer_pcb schematics are stub files (72 bytes each, no components). The analyzer correctly handles them without errors, returning all zero counts for components, nets, wires, and no_connects. No false detections occur on empty files.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
