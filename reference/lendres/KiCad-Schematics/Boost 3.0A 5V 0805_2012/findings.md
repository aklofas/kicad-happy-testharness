# Findings: KiCad-Schematics / Boost 3.0A 5V 0805_2012_Boost 3.0A 5V 0805_2012

## FND-00000701: All MPNs reported missing despite F6 'Manufacturer Part No.' fields being populated in the .sch file; GND net incorrectly contains U? VIN (pin 2) and SW (pin 8) pins; BATT+ net incorrectly contains...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Boost 3.0A 5V 0805_2012_Boost 3.0A 5V 0805_2012.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Every component has MPNs stored in custom field F6 (e.g., VSSAF510-M3/H, MGV06056R8M-10, RK73H2ATTD1002F) but the analyzer shows mpn='' and all refs in missing_mpn. The KiCad 5 legacy parser is not extracting MPNs from non-standard field names.
  (signal_analysis)
- Net tracing assigns U? pin 2 (VIN, power_in) to the GND net and pin 8 (SW) to GND; pin 1 (PGND) and pin 4 (COMP) appear in BATT+. These are definitively wrong — VIN is the supply input, not ground. The SS net label maps to FB pin (pin 6) and FB maps to AGND (pin 5), further indicating systematic pin-offset errors in KiCad 5 legacy net tracing.
  (signal_analysis)

### Missed
- R? 30k and R? 10k form the standard adjustable boost regulator output voltage divider between BOOSTVOUT and GND with the midpoint at U? FB pin. voltage_dividers is empty. The power_regulators entry also has input_rail=null, missing the BATT+ input rail.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000702: Pin-to-net mapping is systematically wrong: ~SD label connects to IN+ pin, IN+ label connects to ~SD pin; R60/C25 falsely detected as 1.59 Hz low-pass RC filter; these are actually a pull-up and by...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Mono Amplifier PAM8302A_Mono Amplifier PAM8302A.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- Net '~SD' maps to U10 pin 3 (IN+) instead of pin 1 (~SD); net 'IN+' maps to U10 pin 1 (~SD) instead of pin 3 (IN+). Similarly POWIN net maps U10 pin 7 (GND/power_in) and GND net maps U10 pin 6 (VDD/power_in). This is the same systematic pin association error as the Boost schematic — nets are connected to the wrong IC pins in KiCad 5 legacy parsing.
  (signal_analysis)
- The rc_filter detector identifies R60 (10k) and C25 (10uF) as a low-pass filter with 1.59 Hz cutoff. However, R60 is the ~SD shutdown pull-up resistor and C25 is the VDD bypass capacitor — they are not in a series-RC filter topology. The spurious topology match is caused by the pin-to-net mapping errors above, which place these components in a false RC path.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000703: PCB files are empty placeholder stubs (version 4, single line); analyzer correctly returns all-zero outputs

- **Status**: new
- **Analyzer**: pcb
- **Source**: Boost 3.0A 5V 0805_2012_Boost 3.0A 5V 0805_2012.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- All eight .kicad_pcb files in this repo are one-line dummy files: '(kicad_pcb (version 4) (host kicad "dummy file") )'. The analyzer outputs footprint_count=0, track_segments=0, etc. — accurate for empty files. No false positives.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
