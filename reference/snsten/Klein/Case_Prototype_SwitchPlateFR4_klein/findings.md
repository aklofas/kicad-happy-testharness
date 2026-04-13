# Findings: snsten/Klein / Case_Prototype_SwitchPlateFR4_klein

## FND-00000760: T1 (Trackpad_Mount) misclassified as 'transformer'; U3 (TRRS AudioJack4) misclassified as 'ic'; Key matrix detected as 4x4 (COL 1 missing); should be 4x5; VCC_3{slash}5 global labels present in lab...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_klein.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- design_observations reports two i2c_bus entries for SDA and SCL, each identifying the pull-up resistor (R1, R2) and rail (VCC_3V3). SCL and SDA nets are correctly classified as 'clock' and 'data' in net_classification.
- key_matrices detector finds 4 rows, 19 estimated keys, 19 diodes on matrix — consistent with the 19 keyboard switch diodes in the BOM. Matrix detection method 'net_name' works for ROW/COL labelled nets.
- buzzer_speaker_circuits reports BZ1 is directly driven by GPIO (direct_gpio_drive=true, driver_ic=U2). This is correct — there is no transistor or driver between the MCU and buzzer.

### Incorrect
- T1 has lib_id 'kbrev-kicad-symbols:Trackpad_Mount' and value 'Trackpad_Mount'. It is a mechanical mounting placeholder footprint, but the analyzer classifies it as type 'transformer' (likely due to 'T' reference prefix). Should be 'mechanical' or 'other'.
  (signal_analysis)
- U3 has lib_id 'Connector:AudioJack4' and value 'TRRS' — it is a 4-pole audio connector, not an IC. The analyzer assigns type 'ic' due to 'U' prefix, but should classify it as 'connector'.
  (signal_analysis)
- The schematic has 5 column nets (COL 0–4) but the key_matrix detector reports only 4 col_nets (COL 0, 2, 3, 4). COL 1 is absent because the net resolution algorithm names that net 'SW16A' (another label connected to the same wire) instead of 'COL 1', so the matrix detector doesn't recognise it as a column. This also causes switches_on_matrix=15 instead of the expected ~19.
  (signal_analysis)
- 8 global_label entries named 'VCC_3{slash}5' appear in the labels array but the net is absent from the nets dict. These labels likely connect to a real power net (the ProMicro's 3.3V/5V input rail for the alternative controller U2). The net goes unnamed (__unnamed_*), meaning any analysis depending on net names (power budget, connectivity) silently drops this rail.
  (signal_analysis)
- pwr_flag_warnings flags GND as having 'no power_out or PWR_FLAG'. However GND is properly driven (U1/U2/U3 all connect GND, battery negative rail connects through B2). The warning fires because GND power symbols are all of lib_id 'power:GND' with power_in type, and the analyzer doesn't recognise the battery/USB path as a power source for GND. This is consistent with the known KH-160-class over-aggressive PWR_FLAG check.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000761: Courtyard overlaps with T1 (Trackpad_Mount) are likely false positives; Board size DFM violation correctly identified (147.9x104.8mm > 100x100mm threshold); Routing completeness and 2-layer stackup...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCB_klein.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- DFM tier 'standard' with one violation: board size exceeds the JLCPCB 100x100mm pricing tier. The Klein is a full split-keyboard half at ~148x105mm, so this is an accurate finding.
- routing_complete=true, unrouted_count=0, copper_layers_used=2 (F.Cu, B.Cu) with standard 1.6mm FR4 stackup. 127 vias, 2004 track segments, 60 nets — all consistent with a fully routed keyboard PCB.

### Incorrect
- T1 is a mechanical mounting/placeholder footprint with a large courtyard (34x32mm) and no connected pads. The placement_analysis reports 4 courtyard overlaps involving T1 (with B2, RSW1, S1, J3). Because T1 is a region-marker footprint (pad_count=4 but connected_nets=[]), these overlaps are not real DFM violations — the components in question are intentionally placed inside the trackpad mounting area.
  (signal_analysis)

### Missed
- The PCB has zone_count=1 but the ground_domains analysis reports has_zone=false for GND. Power net routing shows GND uses only 0.25mm tracks with no pour. The zone may be a keepout or is unfilled — the analyzer should flag absence of GND pour on a keyboard PCB as a potential DFM/EMI note.
  (signal_analysis)

### Suggestions
(none)

---
