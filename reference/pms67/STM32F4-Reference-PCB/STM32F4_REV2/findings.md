# Findings: STM32F4-Reference-PCB / STM32F4_REV2

## FND-00001306: rf_matching detector false-positives on buck converter components; Buck converter detected with correct feedback network (R3/R5, BUCK_FB); STM32F405 crystal load capacitance correctly computed; KiC...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: STM32F4_REV2.sch.json
- **Created**: 2026-03-24

### Correct
- Feedback network correctly identified: R3=47k, R5=270 with output ratio 0.0057 into BUCK_FB pin of MP2359. Power regulator topology correctly identified as switching with input on unnamed net.
- Y1 (16MHz) with C15/C16 (12pF each) gives effective CL = 9pF — correctly computed as (12p*12p)/(12p+12p) + stray.

### Incorrect
- C4 (10n) and D2 (B5819W Schottky) are misidentified as RF matching network components. These are clearly part of the MP2359 buck converter bootstrap/diode circuit (BUCK_BST net), not an RF chain. L1 (10u, 503kHz LC resonance) is also flagged as RF matching. The rf_matching detector is triggering on any L+C/D combination regardless of context.
  (signal_analysis)

### Missed
- No ic_pin_analysis, connectivity_issues, pwr_flag_warnings, footprint_filter_warnings, label_shape_warnings, ground_domains, sourcing_audit, pdn_impedance, assembly_complexity, test_coverage, usb_compliance sections present. This is a systematic gap for legacy .sch files — the legacy parser produces a reduced output.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001307: 4-layer board correctly identified with GND plane on In1.Cu and +3V3 plane on In2.Cu; Tombstoning risk correctly flagged for 0402 decoupling caps between GND pour and signal; kicad_version reported...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: STM32F4_REV2.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Both inner layers typed as 'power' with correct zone fills. GND zone at 2264mm² (79% fill), +3V3 zone full-board on In2.Cu.
- C10 and C11 (0402, bridging GND pour and +3V3/+3.3VA) correctly identified as medium tombstoning risk due to thermal asymmetry.

### Incorrect
- file_version 20171130 is a KiCad 5 format. The analyzer should identify this as KiCad 5, not 'unknown'. The schematic correctly reports '5 (legacy)' but the PCB analyzer doesn't map the file version to a KiCad version string.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001308: 4-layer board correctly identified with all 11 layers present and complete; Alignment issue correctly detected — copper extent smaller than board edge; Drill file lacks X2 FileFunction attribute — ...

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: gerber.json
- **Created**: 2026-03-24

### Correct
- In1.Cu and In2.Cu correctly detected, all required layers found, no missing_required entries.
- Width varies 4.5mm and height 4.1mm across copper vs edge layers; this is expected for a design with keepout margins but correctly flagged as aligned=false.

### Incorrect
- STM32F4_REV2.drl has no FileFunction X2 attribute, so type is reported as 'PTH'. Tools T4 (1.0mm, 0 holes) and T5 (1.1mm, 0 holes) are defined but have 0 holes — these zero-count tools clutter the drill_tools output.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
