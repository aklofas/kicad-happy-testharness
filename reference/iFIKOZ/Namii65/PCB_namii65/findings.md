# Findings: iFIKOZ/Namii65 / PCB_namii65

## FND-00000984: Key matrix correctly detected as 8x10 with 73 estimated keys; assembly_complexity reports unique_footprints=1 but there are 12 unique footprints; pwr_flag_warnings for VCC and GND are false positiv...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: namii65.kicad_sch
- **Created**: 2026-03-23

### Correct
- signal_analysis.key_matrices reports 8 rows, 10 columns, 73 switches on matrix using net_name detection method. Stats show 79 switches total (73 matrix keys + stabilizers S1-S5 + reset RST1), which is consistent.
- Row0-Row7 and Col0-Col9 nets use input-shaped global labels routed to ProMicro I/O pins. The KiCad ERC would flag these in isolation. Warnings are technically accurate per the label type.

### Incorrect
- assembly_complexity.unique_footprints is 1 and package_breakdown shows only 'other_SMD': 148. In reality there are 12 distinct footprints (Kailh hotswap at various sizes, stabilizers, ProMicro, SOD123, PinHeader, logo). The counting logic appears to be collapsing all into one entry. This also causes tht_count=0 despite RST1 using PinHeader_1x02 (THT) — consistent with PCB reporting tht_count=2.
  (signal_analysis)
- The ProMicro provides power via its own USB connector, so VCC and GND are driven by the module itself. The analyzer warns that VCC and GND have no power_out or PWR_FLAG, but this is expected for connector-powered designs where the ProMicro is the power source. These warnings are noise for this design pattern.
  (signal_analysis)
- All D1-D67 1N4148W diodes use footprint 'Cipulot:D_SOD123' from a custom library. The filter pattern 'D*SOD?123*' doesn't match 'D_SOD123' (no wildcard at start), generating 67 warnings. The footprint is functionally correct for 1N4148W SOD-123. This is a false positive caused by the regex not accounting for the prefix-less footprint name in a custom library.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000985: Board size DFM violation correctly identified for 304.8x95.25mm keyboard PCB; courtyard_overlaps for SW70/SW61 and similar switch pairs are false positives for ISO-layout keys

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: namii65.kicad_pcb
- **Created**: 2026-03-23

### Correct
- JLCPCB pricing tier violation at 304.8mm x 95.25mm (exceeds 100x100mm threshold) is a real and accurate observation for this full-size 65% keyboard.

### Incorrect
- 6 courtyard overlaps are reported between regular switch footprints (SW70 L-ctrl, SW61 L-alt, SW64/SW72 R-ctrl, etc.). These are ISO or bottom-row modifier keys that intentionally share courtyard space in keyboard PCB designs. The footprint names show these are all 'L ctrl', 'L alt', 'R ctrl' type keys using standard MX hotswap footprints. This is normal for angled/offset key layouts.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
