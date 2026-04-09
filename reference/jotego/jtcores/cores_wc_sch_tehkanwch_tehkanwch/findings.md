# Findings: jotego/jtcores / cores_wc_sch_tehkanwch_tehkanwch

## FND-00002609: Tehkan World Cup arcade PCB reverse-engineering schematic by JOTEGO, featuring Z80 CPUs, 74LS logic, YM2149 sound, OKI-M5205 ADPCM, and 27128/27256 EPROMs. The analyzer correctly identifies crystals, RC filters, and the LM324 voltage-divider reference, but massively misclassifies component types because this board uses a positional grid reference scheme (C=column, D=row, F=row, V=row, etc.) rather than type-based designators, causing 187+ IC instances to be classified as capacitor, diode, fuse, varistor, mounting_hole, or relay.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: cores_wc_sch_tehkanwch_tehkanwch.kicad_sch.json

### Correct
- Crystal circuits detected for all three oscillators: Y1 (18.432 MHz clock), Y2 (400kHz resonator), Y3 (4.0 MHz CPU clock) with load caps CX15/CX16 for Y3 and C13/C14 for Y2
- Voltage divider R23/R24 (4.7k/4.7k, VCC-REF-GND, ratio 0.5) correctly identified feeding the LM324 (C15) non-inverting inputs at pins 3 and 5
- RC debounce/filter network RZ31/C24, R28/C16, RZ30/C23, RD1/C27 (each 100R + 220pF, fc=7.23 MHz) correctly detected as low-pass filters on joystick input lines
- Bus topology correctly identifies large A* (address), D* (data), and other bus signals with 1368 bus wires and 1200 bus entries in the multi-sheet schematic
- Decoupling analysis correctly identifies only CF1/CF2 (104 = 100nF) tied to VCC, and flags that no bulk capacitance is present

### Incorrect
- 139 logic IC instances (74LS153, 74LS86, 74LS161, 74LS298, 74LS175, 74LS30, 74LS10, 74LS27, 74LS20, 74LS393, 74LS107, 4069, 64K DRAM, etc.) classified as varistor because their reference designators start with V (positional grid row, not a type indicator).
  (statistics.component_types)
- ICs with C-prefix refs (4066/C12, LM324/C15, 27128/C4+C1+C2, 74LS138/C5, 74LS139/C6, 74LS157/C7-C10) classified as capacitor due to reference prefix heuristic. This is a positional reference scheme.
  (statistics.component_types)
- ICs with D-prefix refs (74LS174/D12, OKI-M5205/D17, 74LS244/D7-D10, 74LS00/DA1-DA3, 74LS373/DC2+DB2) classified as diode. None are actual diodes.
  (statistics.component_types)
- ICs with F-prefix refs (YM2149/F12+F15, 74LS02/F16, 74LS32/F4, SW_DIP_x08/F5+F6, 74LS273/F7-F9) classified as fuse. None are actual fuses.
  (statistics.component_types)
- Spurious RC-network filter detected as R17 (100k) + C12 (4066 analog switch). C12 is a 4066 Quad Analog Switch IC, not a capacitor; its value 4066 is parsed as 4.066nF, generating a fictitious 391 Hz filter.
  (signal_analysis.rc_filters)

### Missed
- LM324 (C15) operational amplifier circuit not detected in opamp_circuits. C15 has a VCC/GND supply, a voltage reference on the non-inverting inputs (from R23/R24 divider), and is part of the audio mixing/output stage.
  (signal_analysis.opamp_circuits)
- Y1 crystal has value 18.432 with no unit — the analyzer stores frequency as 18.432 Hz instead of 18.432 MHz.
  (signal_analysis.crystal_circuits)

### Suggestions
- The root cause is that the component-type classifier uses the reference designator first letter as a type hint. This heuristic breaks for arcade/positional reference schemes. The classifier must prioritize the KiCad library symbol name (lib_id) and component value/description over the reference prefix.
- The RC-filter detector must verify that the capacitor component actually has a capacitive lib_id before computing RC cutoff.
- Crystal frequency parsing: when a crystal value has no unit suffix and the number is between 1 and 50, assume MHz.

---
