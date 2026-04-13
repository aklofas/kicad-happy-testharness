# Findings: TU-Darmstadt-APQ/PDH-module / KiCad_PDH_module

## FND-00001077: Hierarchical schematic correctly aggregates all 4 sheets (3 sub-sheets + root), 85 components total including 3 logo graphics; label_shape_warnings incorrectly flags global_label input/output shape...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PDH_module.kicad_sch
- **Created**: 2026-03-23

### Correct
- Main sheet has 3 logo symbols (LOGO1, LOGO2, LOGO5). Sub-sheets contribute 82 components (power_supply=30, error_signal=39, Mod_out=13). Total 85 matches PCB footprint count exactly. Correct.

### Incorrect
- The analyzer warns that nets +8V, -8V, +15V, -15V have 'inconsistent shapes' (input+output). In KiCad, global_labels intentionally use shape=output on the driving sheet and shape=input on consuming sheets — this is standard practice, not an error. These are false positive warnings for well-formed hierarchical designs.
  (signal_analysis)
- File version 20230121 corresponds to KiCad 7.x. Both schematics (20230121) and PCB (20221018) return kicad_version='unknown'. This is a lookup gap — these version stamps should be mapped to KiCad 6/7 releases.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001078: pwr_flag_warning incorrectly reports GND missing PWR_FLAG when PWR_FLAG is present; Negative power rails -15V, -8V, -5V classified as 'signal' instead of 'power'; Power regulators correctly identif...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: power_supply.kicad_sch
- **Created**: 2026-03-23

### Correct
- All 5 regulators detected with correct topologies. LT3045 (+8V→+5V), LT3094 (-8V→-5V), LM7812 (+15V→intermediate), LM7808 (intermediate→+8V), LM7908 (-15V→-8V). Regulator chain fully traced.

### Incorrect
- The power_supply.kicad_sch has three PWR_FLAG instances (on +15V, -15V, and another rail). The analyzer still warns 'GND has power_in pins but no power_out or PWR_FLAG'. This is a false positive — the PWR_FLAG exists in the schematic but is apparently not being recognized correctly.
  (signal_analysis)
- This is a bipolar ±15V / ±8V supply. The nets -15V, -8V, and -5V are power supply rails that feed op-amps, yet the analyzer classifies them as 'signal'. Only nets named with '+' prefix or matching common positive patterns get classified as 'power'. Negative supply rails should also be classified as 'power'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001079: R18 with value 'DNF(200)' not detected as DNP — dnp_parts reports 0; Undriven input label warning for V+ and V- is a false positive in hierarchical sub-sheets; Op-amp subcircuits correctly identifi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: error_signal.kicad_sch
- **Created**: 2026-03-23

### Correct
- 7 subcircuits detected including all key analog signal processing ICs. OPA695 as inverting amplifiers, ADA4898-2 in buffer and transimpedance configurations, LT1568 active lowpass filter, SYPD-1 RF mixer. This is a PDH laser locking circuit and all functional blocks are present.

### Incorrect
- R18 has value 'DNF(200)' which is a common convention for 'Do Not Fit'. The KiCad DNP flag is not set (so dnp=False is technically correct for the attribute), but the value-based DNF convention is not detected. dnp_parts=0 is misleading — the design intends R18 to not be populated. Analyzer should detect DNF/DNP/NF in value strings.
  (signal_analysis)
- V+ and V- are hierarchical_labels with shape=input in error_signal.kicad_sch. The analyzer warns they are 'undriven'. In hierarchical KiCad design, these are driven by the parent sheet (PDH_module.kicad_sch) via sheet pins — the sub-sheet is analyzed in isolation so they appear undriven, but they are not. This is a false positive for any hierarchical sub-sheet analyzed standalone.
  (signal_analysis)

### Missed
- The SYPD-1 is a Mini-Circuits RF double-balanced mixer used in the PDH error signal demodulation path. rf_chains=0 and rf_matching=0, meaning the RF signal path (photodetector → mixer → lowpass filter → error signal) is not detected as an RF chain. Given the SMA connectors and mixer IC, this design has a clear RF signal path that should be captured.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001080: PCB statistics accurate: 85 footprints, 160x100mm board, 2 layers, 98 nets, fully routed; connectivity reports 'routed_nets: 39' vs 'total_nets_with_pads: 98' but routing is complete; Courtyard ove...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PDH_module.kicad_pcb
- **Created**: 2026-03-23

### Correct
- Footprint count (85) exactly matches schematic component count. Board dimensions, layer count, via count (189), track count (458), and zone count (14) all correctly extracted. routing_complete=True with 0 unrouted nets is accurate.
- 8 courtyard overlaps detected. J1 (DIN41612 2x32 connector) overlapping D4 (TVS diode) by 32.85mm² is a significant issue. U13 (OPA695) overlapping J9 (SMA connector) by 22.9mm² is also real. These appear to be genuine PCB layout issues in the design.
- 5 thermal pad via entries detected for exposed-pad SOIC/MSOP packages. ADA4898-2 SOIC-8-1EP and the two MSOP-12-1EP LDO regulators all have thermal pads with via stitching identified. Correct for these package types.
- The 160mm width exceeds the 100mm standard JLCPCB threshold, correctly flagging it as a higher fabrication cost tier. Min track 0.2mm, min drill 0.3mm, min annular ring 0.15mm are all within standard DFM tolerances.

### Incorrect
- 39 of 98 nets have explicit track segments; the remaining 59 nets are connected via copper pour zones. The field name 'routed_nets' is misleading — these 59 nets are fully connected but only via zones, not explicit tracks. This metric is confusing since routing_complete=True and unrouted_count=0 contradict the apparent implication that 59 nets are unrouted.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
