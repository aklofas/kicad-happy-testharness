# Findings: labtroll/KiCad-Simulations / 555-bipolar_555bip

## FND-00002272: Discrete boost converter topology (L+NMOS+D+C) not detected in power_regulators; Simulation voltage sources (VPULSE, VDC, VSIN) misclassified as varistor, causing false protection_devices entries; ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Simulations_Boost_Boost2.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- Components V1 and V3 use lib_id 'Simulation_SPICE:VPULSE' and are classified as type='varistor' by the analyzer. This triggers two false entries in signal_analysis.protection_devices, where V3 is reported as protecting net 'in' and V1 as protecting net 'gg' — both are purely simulation stimuli with no physical protection function. The same pattern occurs in the 741 schematic where VDC and VSIN sources are also typed as varistor. Simulation_SPICE library components should be classified as a distinct 'simulation_source' type, not matched against physical component heuristics.
  (signal_analysis)
- The schematic has PWR_FLAG (#FLG02) at position (135.89, 134.62) connected via wire to (130.81, 134.62), which continues to (130.81, 138.43) where a GND power symbol sits. This forms a valid electrical connection to the GND net. However, the analyzer shows both PWR_FLAG symbols with net_name='PWR_FLAG' (a floating net with no pins) rather than resolving them to the nets they connect to, and then fires a pwr_flag_warning claiming GND has no PWR_FLAG. This is a false positive caused by the analyzer not tracing wire connectivity from PWR_FLAG symbol pins to their actual nets.
  (pwr_flag_warnings)

### Missed
- The Boost2 schematic contains a textbook boost converter: inductor L1 connects input to the switching node, NMOS Q1 switches the node to GND, diode D1 rectifies to output capacitor C2. The transistor_circuit entry correctly identifies Q1 with load_type='inductive', but power_regulators remains empty. The same issue applies to the Buck3 schematic where an IRF540N high-side MOSFET with L, D, and C forms a classic synchronous buck. The analyzer only detects IC-based regulators, completely missing discrete switching converter topologies.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00002273: 741 op-amp transistor-level model: 20 BJTs detected individually but no differential pair or opamp topology recognized

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_KiCad-Simulations_741_741.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The schematic is a transistor-level model of the 741 op-amp, containing a differential input pair (Q7/Q8 using BCV61/BCV62 dual transistors), current mirror, and output stage — all standard analog building blocks. The analyzer correctly counts 20 transistor_circuits but opamp_circuits=0 and feedback_networks=0. A differential pair would require two BJTs sharing the same emitter node with opposing base inputs, which is a detectable structural pattern. Additionally, the 13 DNP components (simulation-use only) are included in the 38 total component count and assembly_complexity analysis, potentially inflating assembly scores for simulation-only schematics.
  (signal_analysis)

### Suggestions
(none)

---
