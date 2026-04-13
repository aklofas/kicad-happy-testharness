# Findings: greatscottgadgets/hackrf / hardware_marzipan

## FND-00000030: "Description" custom field not captured in legacy parser

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_marzipan_marzipan.sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
(none)

### Missed
- Legacy parser has no case for "DESCRIPTION" field. Custom "Description" fields present on components are not extracted.
  (components[*].description)

### Suggestions
- Add "DESCRIPTION" to the field extraction logic in the legacy parser

---

## FND-00000032: U15 LXES1TBCC2-004 ESD suppressor misclassified as IC (U prefix)

- **Status**: new
- **Analyzer**: schematic
- **Source**: hardware_marzipan_marzipan.sch.json
- **Created**: 2026-03-13

### Correct
(none)

### Incorrect
- U15 LXES1TBCC2-004 is an ESD suppressor but classified as IC due to U reference prefix.
  (components)

### Missed
(none)

### Suggestions
- Consider library name or component keywords for ESD/TVS classification rather than relying solely on reference prefix

---
