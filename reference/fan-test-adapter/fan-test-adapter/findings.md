# Findings: fan-test-adapter / fan-test-adapter

## FND-00002063: Logo_Open_Hardware_Small graphic incorrectly listed as a power rail; Capacitors with value 'DNF' not detected as Do-Not-Fit/DNP parts

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_fan-test-adapter_fan-test-adapter.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- In the KiCad 5 .sch source, the open-hardware logo is placed as symbol '#LOGO1' with value 'Logo_Open_Hardware_Small'. Because KiCad 5 power components start with '#', the KiCad 5 parser misidentifies this as a power component and adds 'Logo_Open_Hardware_Small' to the power_rails list. The net is also incorrectly classified as 'control' in design_analysis.net_classification. This is a false positive — the logo is purely graphical with no electrical connections. It should be filtered out the same way KiCad 6 'Graphic:' library symbols are handled.
  (statistics)

### Missed
- Four capacitors (C1, C3, C5, C7) use the component value 'DNF' (Do Not Fit) as the conventional KiCad 5 way to mark non-populated parts, since KiCad 5 has no formal DNP property. The analyzer reports dnp_parts=0, missing the 4 DNF capacitors. These are radial electrolytic caps in a THT footprint (CP_Radial_D10.0mm) that the designer chose to leave unpopulated. Detecting value=='DNF' (case-insensitive) as a DNP indicator would improve BOM accuracy for KiCad 5 designs.
  (statistics)

### Suggestions
(none)

---
