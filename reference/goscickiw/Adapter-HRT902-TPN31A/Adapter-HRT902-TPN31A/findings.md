# Findings: goscickiw/Adapter-HRT902-TPN31A / Adapter-HRT902-TPN31A

## FND-00000543: Component count and BOM correct; Net topology correctly traced; assembly_complexity misclassifies all components as SMD; kicad_version reported as 'unknown' despite parseable version field; P1 NC p...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Adapter-HRT902-TPN31A_Adapter-HRT902-TPN31A.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 9 total symbols, 5 BOM parts (excluding non-BOM AC_Symbol ~1 and H1/H2/H3 grouped), all refs and types match source.
- 4 nets extracted; J1->P1.D, J2->P1.M, J3->JP1->P1.P, and mounting holes + NC pins on shared net all match wire connections in source.
- Pins 3-6 of P1 (type 'free', name 'NC') share __unnamed_0 with H1/H2/H3 and JP1 pin A, consistent with the wire routing in the schematic.
- P1 has value '~' (blank) in source; flagging it in annotation_issues.missing_value is correct.

### Incorrect
- Reports smd_count=9, tht_count=0. SolderWire footprints (J1/J2/J3) and MountingHole pads (H1/H2/H3) are not SMD components; the custom HRT902 footprint (P1) is also ambiguous. No component here is a conventional SMD part.
  (signal_analysis)
- File has (version 20230121) which corresponds to KiCad 7.x. The output reports kicad_version: 'unknown' instead of resolving the date-format version number to a KiCad release.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
