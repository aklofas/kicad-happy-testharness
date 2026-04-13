# Findings: goblinrieur/Analog_Battery_Regulator / 00-kicad_Regulateur_SI_V3.3.0_RegulatorV2

## FND-00000369: Legacy parser detects zero opamp circuits for 3x LM358 dual opamps (6 total units); Legacy parser misses one RC filter (R2/C8 low-pass at 7.23 Hz); Legacy parser inverts drain/source nets for IRFB4...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 00-kicad_Regulateur_SI_V3.3.0_RegulatorV2.sch.json
- **Created**: 2026-03-23

### Correct
- For Q2, Q3, Q4, Q5 (IRFB4321 N-channel MOSFETs in dump load configuration), the KiCad 5 legacy parser reports drain_net=GND and source_net=Vdump with drain_is_power=true. The KiCad 8 parser reports drain_net=Vdump and source_net=GND with source_is_ground=true. Since these are N-channel MOSFETs, drain connects to the load (Vdump) and source connects to GND. The KiCad 8 result is physically correct; the legacy parser has drain and source swapped due to pin numbering differences in the legacy IRLZ44N symbol. Additionally, the legacy parser marks R9 as both base_resistor and base_pulldown for Q1 (double-counting the same resistor), while the KiCad 8 parser correctly only lists it as a base resistor.

### Incorrect
(none)

### Missed
- The schematic has three LM358 dual-opamp ICs (U1, U2, U3) configured as buffers, comparators, and inverting amplifiers. The KiCad 8 parser correctly identifies all 6 opamp circuits. The KiCad 5 legacy parser produces opamp_circuits=[] — a complete miss. The LM358 instances exist in the BOM and component list with all their pins, so the connectivity data is present; the opamp detection logic in the legacy parser is not running or not producing results.
  (signal_analysis)
- The KiCad 8 parser finds 3 RC filters including R2(10k)/C8(2.2uF) forming a 7.23 Hz low-pass filter on the Vcons output net. The KiCad 5 legacy parser only finds 2 (R17/CT1 and R16/C2). Both versions of the schematic are identical in this circuit. The legacy parser misses the R2/C8 filter, likely because the net connectivity around the Vcons node is parsed differently in the legacy format, preventing the RC filter detection algorithm from finding the R-C pair.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000370: KiCad 8 parser misses R23/RV1 voltage divider (Vref → op-amp input)

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 00-kicad_Regulateur_SI_V3.3.0_RegulatorV2.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The KiCad 5 legacy parser correctly identifies a voltage divider formed by R23(10k) and potentiometer RV1(10k) with top_net=Vref feeding the non-inverting input of U1 pin 5. The KiCad 8 parser does not include this divider in its 5 voltage dividers. RV1 is a potentiometer (JST connector footprint) and may be excluded from divider detection because its symbol/lib_id does not match the standard resistor pattern, causing the divider formed with R23 to be dropped.
  (signal_analysis)

### Suggestions
(none)

---
