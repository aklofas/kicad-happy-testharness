# Findings: TU-Darmstadt-APQ/MTS-module_80MHz_200MHz / KiCad_MTS_module

## FND-00000887: LT3045xMSE (U2, U3) falsely flagged as 'inverting: true' in MTS_module top-level; Cross-domain signal false positive: __unnamed_4 flagged as needing level shifter between U10/U12; Regulator cap war...

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad_power_supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- All six power regulators are correctly identified with correct lib_id, input/output rails, and topology classification. The LT3094/LM7908 negative regulators are correctly identified.
- D4 and D3 (D_TVS) on +15V and -15V rails correctly detected as protection_devices with proper protected_net and clamp_net.

### Incorrect
- In the MTS_module flat view, U2 and U3 (LT3045xMSE, positive linear regulator) have 'inverting: true' in power_regulators. The LT3045 is a non-inverting positive LDO — only the LT3094 (U1, negative LDO) should be inverting. The issue appears to be output_rail resolution using UUIDs (e.g. '/00000000-0000-0000-0000-000061c36f5e/V+') when the output is a hierarchical net, which may confuse the topology classifier.
  (signal_analysis)
- __unnamed_4 is the intermediate voltage node between LM7812 (U10, +12V output) and LM7808 (U12, +8V from +12V input) — it is simply a chained linear regulator node, not a cross-domain signal-level interface. Flagging 'needs_level_shifter: true' on a power supply rail passing through regulators is a false positive.
  (signal_analysis)
- design_observations flags missing_caps for U10 output (__unnamed_4), U12 input (__unnamed_4), U11 input/output (-15V/-8V), and U1. The PCB decoupling_placement shows nearby caps correctly associated with these regulators. The issue is that unnamed/intermediate power nets break the cap-association logic, not that caps are actually missing.
  (signal_analysis)

### Missed
- R2 has value '33k', type 'resistor', but footprint 'Capacitor_SMD:C_0603_1608Metric'. This is a footprint/symbol mismatch that should be flagged in property_issues or footprint_filter_warnings, but property_issues is empty and footprint_filter_warnings does not catch this. This is a real design data anomaly worth detecting.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000888: Hierarchical sheet structure correctly resolved — 4 sheets detected, all 146 components aggregated; 8 hierarchical labels flagged as unconnected but are legitimately sheet-internal power rail exports

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad_MTS_module.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The top-level MTS_module correctly lists all 4 sheets (MTS_module, power_supply, PLL_VCO, error_signal), aggregates 146 total components across subsheets, and correctly identifies hierarchical labels with 38 hierarchical and 15 global labels.

### Incorrect
- Labels like '+12V', '+3.3V', '+5V', '-12V', '-5V', 'V+_OPA', 'V-_OPA', 'Vcc_VCO' are hierarchical outputs from subsheets. These are not 'unconnected' — they export power domain nets to the top level and drive other subsheets. The analyzer appears to flag them because it cannot resolve the cross-sheet connection at the top level hierarchy.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000889: Opamp and RC filter detection correct for PLL loop filter circuitry; ERC warnings for missing negative supply drivers (V-_ADA, V-_OPA) are valid

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad_PLL_VCO.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- ADA4898-2 (U8) transimpedance/buffer configurations correctly detected; OPA695 units detected; PLL loop filter RC components (R8/C17, R7/C17+C18) with correct low-pass cutoffs (25 kHz, 3.4 kHz) properly identified. These match typical PLL loop filter topology.
- V-_ADA and V-_OPA negative supply nets have no driver in the PLL_VCO sheet because they are driven from the power_supply sheet via hierarchical labels — correctly identified as ERC concern at sheet level.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000890: OPA695 inverting amplifier gain calculation correct (-0.78, -2.2 dB) with RV1 potentiometer as input resistor; V- net (negative supply) flagged as ERC 'no_driver' — but this is a hierarchical sheet...

- **Status**: new
- **Analyzer**: schematic
- **Source**: KiCad_error_signal.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- U14 detected as inverting configuration with feedback R25=390Ω and input RV1=500Ω, giving gain=-390/500=-0.78. This is a valid detection of an inverting amplifier using a potentiometer for variable gain.

### Incorrect
- The V- net in error_signal.kicad_sch is fed from the power_supply sheet via hierarchical labels. Reporting it as 'no_driver' is expected at the individual sheet level, but should be suppressed or marked as 'sheet-level only' when the design has a proper hierarchical structure.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000891: PCB statistics, routing, and board dimensions correctly extracted; J6 (RF_Shield_One_Piece, Laird BMI-S-107) generates 30+ false courtyard overlaps; Thermal pad via adequacy correctly identified as...

- **Status**: new
- **Analyzer**: pcb
- **Source**: KiCad_MTS_module.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- 145 footprints (143F/2B), 2 copper layers, 872 track segments, 523 vias, 21 zones, 160x100mm board, routing_complete=true all correctly reported.
- U1 (LT3094, 2 vias), U2 (LT3045, 3 vias), U3 (LT3045, 3 vias) all flagged 'insufficient' against recommended 5+ vias. U7/U8 (ADA4898-2 SOIC-8-EP) with disconnected thermal pads (unconnected-(U7C-EP-Pad9)) correctly flagged as 'none'. These are real concerns worth noting.
- GND fill on both F.Cu and B.Cu with 27,700 mm² area and 454 stitching vias at 1.6/cm² is correctly detected. Secondary power fills (V+, V-, +8V, etc.) on F.Cu also correctly enumerated.

### Incorrect
- J6 is an RF shielding can with footprint Laird_Technologies_BMI-S-107 (44.37x44.37mm). Its courtyard deliberately encloses all components inside it (U15, U7, U16, U14, U17, and numerous passives). All 30+ overlaps involving J6 are intentional by design — the shield encloses those parts. This is a known limitation of courtyard overlap checking for RF/EMI shielding cans.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
