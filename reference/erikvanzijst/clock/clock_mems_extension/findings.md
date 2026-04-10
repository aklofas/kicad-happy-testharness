# Findings: clock / clock_mems_extension_clock_mems_extension

## FND-00002013: XTAL1 (32.768kHz crystal) misclassified as type 'other' instead of 'crystal'; XTAL1 32.768kHz crystal circuit not detected in crystal_circuits; NE555P (U11) crystal_circuit entry has output_net='VC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_clock_kicad_clock.sch
- **Created**: 2026-03-24

### Correct
- 82 components (13R, 24C, 22 IC, 10 resistor networks, 6 diodes, 3 switches, 1 transistor, 1 oscillator, 1 other) match the source schematic exactly. Power rails GND/VCC/PWR_FLAG are correct. LDO U2 (LD1117V) detected with input_rail=5V / output_rail=VCC. Four RC filters detected (two at crystal pins of XTAL1, two NE555 timing networks). The decoupling observation for VCC rail (5 caps, 10.4uF total with bulk) is accurate. Schematic-to-PCB component count matches at 82.

### Incorrect
- XTAL1 has reference prefix 'XTAL' which is not in type_map and doesn't reach the X-prefix crystal handler (line 432 of kicad_utils.py, which only fires when prefix == 'X'). The lib_id 'dk_Crystals:ECS-_327-12_5-34B-TR' contains 'crystal' in lowercase but the generic lib-based fallback section (lines 462+) has no crystal detection — only the X-prefix block does. As a result XTAL1 falls through to 'other', preventing crystal_circuits detection from finding it (the detector only processes type=='crystal' components). The IC-pin detection also misses it because U1 (74HC4060) uses 'RTC'/'CTC' pin names rather than XTAL/OSC/XI/XO patterns.
  (statistics)
- The analyzer reports U11 (NE555P) with output_net='VCC' in crystal_circuits. This is technically accurate: U11 pin 3 (OUT) is literally on net VCC and pin 8 (VCC) is on net GND in the source schematic — the power pins are wired backwards. The analyzer faithfully reports what the schematic says. The source design has a wiring error (the NE555 is powered with VCC/GND swapped), but the analyzer output is not incorrect — it reflects the source accurately. No fix needed in the analyzer; this is a correct detection of a broken source design.
  (signal_analysis)

### Missed
- Because XTAL1 is typed 'other', detect_crystal_circuits() skips it. The crystal_circuits list contains only the NE555P (U11) as an active_oscillator, missing the actual passive crystal. A correct output should include XTAL1 with its two connected RC components (R3/R4 feedback resistors, C1/C2 load caps at 22pF) as a crystal circuit associated with U1 (74HC4060 ripple counter/oscillator).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002014: SIT1630AI MEMS oscillator (U1) not detected in crystal_circuits

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos_clock_clock_mems_extension_clock_mems_extension.sch
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- U1 is a Silicon Labs SIT1630AI MEMS oscillator in SOT-23-5. The active oscillator detection in detect_crystal_circuits() scans for keywords including 'sit2' and 'sit8' (for SIT2xxx/SIT8xxx series) but not 'sit1' for the SIT1xxx series. Value 'SIT1630AI' and lib_id 'clock_extension:SIT1630AI' produce no keyword matches, so U1 is not added to crystal_circuits. The component is classified as type 'ic' (correct — U-prefix), and none of the oscillator keyword patterns match SIT1xxx. The crystal_circuits list is empty for this design when it should contain U1 as an active_oscillator.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002015: F.Paste layer correctly flagged as missing for SMD board

- **Status**: new
- **Analyzer**: gerber
- **Source**: repos_clock_clock_mems_extension_gerbers_
- **Created**: 2026-03-24

### Correct
- The MEMS extension PCB has 2 SMD components (U1 SOT-23-5 and C1 0603) but no F.Paste gerber file was exported. The gerber analyzer correctly identifies this: found_layers omits F.Paste and missing_recommended=['F.Paste']. The smd_apertures=0 is because no X2 ApertureFunction attribute marks SMD pads in these gerbers, but the missing-layer detection is independent and correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
