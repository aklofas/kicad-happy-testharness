# Findings: kicad_devboard_f070 / dev_f070

## FND-00002355: total_components reports 7 but 24 components are present in the components list; AMS1117-3.3 linear voltage regulator not detected in power_regulators; Decoupling analysis misidentifies all C? caps...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad_devboard_f070_dev_f070.sch.json.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- statistics.total_components=7 and statistics.component_types shows one entry per type (ic:1, connector:1, capacitor:1, etc.) but the components array has 24 entries: ic:3, connector:8, capacitor:6, resistor:4, crystal:1, led:1, switch:1. The bug is that the statistics deduplicate by reference prefix — all 'C?' collapse to one count, all 'J?' to one, etc. — rather than counting each component instance. This affects total_components, unique_parts, and component_types counts.
  (components)
- signal_analysis.decoupling_analysis for +3.3V shows 4 caps all valued 100pF, but the schematic has 2x 10uF capacitors on +3.3V (in addition to 100pF decoupling caps). Because all capacitors share the duplicate reference 'C?', BOM deduplication collapses them to a single entry retaining only one value. When the decoupling analysis looks up cap values, all C? instances resolve to the same value, causing 10uF caps to be misidentified as 100pF. The analysis then incorrectly reports has_bulk=false and has_bypass=false for the +3.3V rail.
  (signal_analysis)

### Missed
- The schematic contains an AMS1117-3.3 (SOT-223) linear LDO regulator converting +5V USB to +3.3V. signal_analysis.power_regulators is empty. The regulator is correctly placed in a subcircuit (center_ic U? AMS1117-3.3) but the detector fails to classify it. This likely fails because the component reference is 'U?' (unannotated) rather than a numbered ref like 'U2', confusing the regulator recognition heuristic.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002356: Correctly handles dummy PCB stub file with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: pcb_kicad_devboard_f070_dev_f070.kicad_pcb.json.json
- **Created**: 2026-03-24

### Correct
- The .kicad_pcb file contains only '(kicad_pcb (version 4) (host kicad "dummy file") )' — 51 bytes with no actual content. The analyzer correctly returns all-zero statistics (footprint_count=0, track_segments=0, etc.) without crashing. The file_version=4 is parsed accurately from the minimal header.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
