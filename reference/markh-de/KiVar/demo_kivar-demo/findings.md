# Findings: markh-de/KiVar / demo_kivar-demo

## FND-00000726: statistics.dnp_parts reports 0 but 9 components are DNP; bus_topology reports width=6 for prefix 'A' but range is A0..A2 (3 signals); missing_mpn list correctly excludes DNP, not-in-BOM, and compon...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: demo_kivar-demo.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 66 total - 9 DNP - 7 JP (in_bom=False) - 2 with actual MPN (U3, U4) = 48 missing, matching statistics.missing_mpn count exactly.
- Root sheet has 8 subsheet references (examples 1-7 + rule_processing). All are listed in sheets[], components are tagged with _sheet index, and net names include hierarchical path prefixes. Component and net counts agree between schematic and PCB outputs.
- U6 TLV75801PDBV correctly identified as LDO with input=+5V, output=VOUT, feedback divider R35/R36 detected. U3 ISL91127IRNZ detected as buck-boost (topology='ic_with_internal_regulator') with inductor L1, +BATT→+3V3. U5 AP3032 detected as switching with inductor L2. The estimated_vout=1.2V for U6 uses a heuristic Vref=0.6V (actual TLV758P Vref=0.8V gives 1.6V) but this is documented as heuristic.

### Incorrect
- The schematic has 9 DNP components (R1, R9, R11, R17, R18, R21, R29, C5, C6 — KiVar variant-selector resistors/capacitors). Individual component records have dnp=true but statistics.dnp_parts=0. The count is not being aggregated into the top-level stats.
  (signal_analysis)
- detected_bus_signals shows {prefix: 'A', width: 6, range: 'A0..A2'}. A0..A2 implies 3 signals (indices 0,1,2), so width should be 3. The width=6 is inconsistent with the declared range and does not correspond to any actual signal count in the labels (A0, A1, A2, A2{slash}~{RST} are the only A-prefixed labels).
  (signal_analysis)
- GND, +5V, and +BATT are all flagged as missing PWR_FLAG. This is a demo board where +5V and +BATT are connector-supplied power inputs spread across subsheets. The GND flag in particular is likely a false positive as GND is driven by multiple passive pins and is the common return. However, since no connectors or PWR_FLAGs are present in any sheet, these warnings may be technically accurate for ERC purposes.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000727: Unrouted board state correctly detected — 0 tracks, 29 unrouted nets, routing_complete=false; DNP footprints correctly identified — 9 DNP, 16 exclude_from_bom; smd_count=59 and tht_count=0 but 7 JP...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: demo_kivar-demo.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- The PCB is a demo/placement board with no copper traces routed. Statistics correctly report track_segments=0, via_count=0, routing_complete=false, unrouted_net_count=29 out of 57 nets.
- PCB correctly identifies 9 DNP footprints (C5, C6, R1, R9, R11, R17, R18, R21, R29) matching the schematic DNP set. 16 exclude_from_bom footprints also correctly captured. This matches KiVar variant-selector components.

### Incorrect
- footprint_count=66 = 59 smd + 7 'exclude_from_pos_files' (JP*). The tht_count=0 is correct (no THT pads), but the 7 JP footprints are not included in smd_count despite being SMD solder-bridge jumpers. The type classification 'exclude_from_pos_files' is not a pad type — it's a placement attribute. These should be counted as SMD (smd_count should be 66, or the stat should clarify it only counts position-file-eligible parts).
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
