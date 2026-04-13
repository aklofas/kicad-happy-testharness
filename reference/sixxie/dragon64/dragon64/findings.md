# Findings: sixxie/dragon64 / dragon64

## FND-00002333: Crystal circuits not detected despite 4 active crystals (XL1-XL3, XL5) present in design; Memory interfaces not detected despite full 16-bit address bus (A0-A15) and RAM ICs present; LM348 quad op-...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_dragon64_dragon64.kicad_sch.json.json
- **Created**: 2026-03-24

### Correct
- The dragon64 project uses hierarchical schematics with 4 sub-sheets (pia, ram, video, serial). In KiCad 6+, the top-level .kicad_sch file embeds all component instances from all sub-sheets. The analyzer correctly extracts all 249 unique component references from the root file, matching the PCB footprint count exactly. Sub-sheet files (pia: 74, ram: 19, video: 71, serial: 27 components) are proper subsets of the 249 total. The sheets_parsed=None and sheet_files=[] is correct behavior since KiCad 6 does not require following external sheet links — all data is in the root file.

### Incorrect
- IC3 (LM348 quad op-amp) appears 5 times in signal_analysis.opamp_circuits: units 1, 2, 3, 4, and 5. Unit 5 has configuration 'unknown' with no input/output nets — this corresponds to the power supply unit of the quad op-amp (the V+ / V- pin unit), which should not be classified as an opamp circuit. The power supply unit of a multi-unit op-amp being included as a separate 'unknown' opamp circuit entry is incorrect. The 4 actual amplifier units are correctly identified as comparator_or_open_loop configuration.
  (signal_analysis)

### Missed
- The dragon64 computer has 5 crystal/oscillator components: XL1 (1.8432MHz), XL2 (4.433619MHz colorburst), XL3 (14.218MHz CPU clock), XL4 (CXO_DIP8 oscillator, DNP), and XL5 (1.8432MHz). The signal_analysis.crystal_circuits array is empty. The crystals use lib_ids Device:Crystal_GND3, Device:Crystal_GND3_Small, and Oscillator:CXO_DIP8, and are typed as 'other' in the component list rather than 'crystal'. The detector apparently requires components to be typed as 'crystal' or uses value-based matching that doesn't catch these. Three distinct clock domains are present: system clock (14.218MHz), PAL colorburst (4.433619MHz), and UART baud rate (1.8432MHz).
  (signal_analysis)
- The dragon64 is a full 6809-based home computer with a 16-bit address bus (nets A0-A15 are all present) and 10 RAM ICs in the design (IC15, IC16, IC20-IC22, IC25-IC27, IC32-IC33 from the RAM sheet). The signal_analysis.memory_interfaces array is empty. Additionally the data bus nets are partially missing — only D3, D5, D6 are found in the top-level schematic's net list, while D0-D7 are named differently (possibly prefixed or differently labeled in sub-sheets). This suggests the memory interface detector is not matching on this vintage-computer bus topology where the CPU data bus uses a different naming convention.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002334: 11 keepout zones listed as regular unfilled copper zones without keepout type indication; DFM correctly identifies advanced-tier annular ring violation and large board size flag

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_dragon64_dragon64.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The dragon64 PCB (252.984 x 199.39mm, a full computer motherboard) is correctly classified as 'advanced' DFM tier due to a 0.104mm annular ring (below the 0.125mm standard threshold). The board size flag is also correctly triggered since the board exceeds 100x100mm. The 9 'exclude_from_pos_files' footprints (mounting holes M1,M3,M4,M7,M8 and others) are correctly typed separately from the 240 THT components, avoiding inflation of the SMD/THT component counts.

### Incorrect
- The dragon64 PCB has 11 zones with net=0 and net_name='' that appear in the zones list as regular copper zones with is_filled=False. Inspection of the source .kicad_pcb file confirms these are KiCad keepout zones — they contain 'keepout (copperpour not_allowed)' rules, not empty copper pours. The analyzer does not detect or report the keepout rule attribute, so these zones are indistinguishable in the output from unfilled copper fills. A reviewer would incorrectly interpret them as copper zones that failed to fill. The 4 GND zones (net=143) are correctly identified as filled copper pours on F&B.Cu.
  (statistics)

### Missed
(none)

### Suggestions
(none)

---
