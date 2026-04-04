# Findings: bb-parallel-port-cape / bbb-parallel-cape

## FND-00001967: Multi-sheet schematic correctly parsed: 2 sheets, 54 components, 256 nets; Multiple ground domains correctly detected as isolation barrier; Decoupling cap warnings correctly issued for all 5 GTL200...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: bbb-parallel-cape.sch.json
- **Created**: 2026-03-24

### Correct
- The design has a top-level sheet (bbb-parallel-cape.sch) and a sub-sheet (voltage_translators.sch). Both are parsed, yielding 54 total components, 256 nets, 401 wires, and 53 no-connects. GTL2003PW voltage translators (5 ICs) in the sub-sheet are correctly included.
- The design has separate ground domains: GNDD (digital), GNDA_ADC (analog ADC), and GND_OR_5V, correctly detected in signal_analysis.isolation_barriers with distinct domain keys. No explicit isolation components are listed (correct — there is no galvanic isolator, just separate ground planes). PWR_BUT is correctly flagged as an isolated power rail.
- All five GTL2003PW level-translator ICs (IC201-IC205) are flagged in design_observations with rails_without_caps=['+3V3'] and rails_with_caps=[]. The 5 decoupling caps C201-C205 exist in the schematic but the analyzer correctly notes they are not close enough or not directly tied to the IC supply pins in the net topology.
- The STATUS_LED net connects to Q101 gate (input) and BBB connector pin P103.22 (passive), with no explicit output driver. The analyzer's erc_warnings correctly flags this as 'no_driver', which is accurate — the LED control signal comes from the BeagleBone GPIO, which the schematic does not assign a driver pin type to.
- Q101 is a 2N7002K N-channel MOSFET driving an LED (classified as JFET due to lib_id 'Q_NJFET_GDS' but functionally correct for the switching circuit). load_type='led' is correct as the drain connects to the LED current path. The detection of gate/drain/source nets and load type is accurate.

### Incorrect
- Q101 uses lib_id 'Q_NJFET_GDS' which is a JFET symbol, but the actual component is a 2N7002K — an N-channel enhancement MOSFET in SOT-23. The analyzer reports type='jfet' which is incorrect. The 2N7002K is a MOSFET, not a JFET. This is a schematic symbol selection error in the original design (using a JFET symbol for a MOSFET), but the analyzer should ideally use the MPN to determine the correct type or flag the discrepancy.
  (signal_analysis)

### Missed
- Five GTL2003PW bidirectional voltage-level translators (IC201-IC205) translate 8 I/O lines each between the BeagleBone Black (3.3V GPIO) and the DB25 parallel port. These should be detected as voltage translation/bus interface circuits. The signal_analysis has no category for voltage translators, and none appears in any existing category. This is a missed opportunity to flag the 3.3V-to-5V translation topology.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001968: PCB statistics correctly parsed: 46 footprints (43 SMD, 3 THT), 268 vias, 2 ground domains; DFM correctly escalated to 'advanced' tier due to 0.1mm annular ring; Three separate ground domains corre...

- **Status**: new
- **Analyzer**: pcb
- **Source**: bbb-parallel-cape.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- footprint_count=46 (less than the 54 schematic components because 9 components have no footprint — off-board connectors like J101/J102 DB25 and Z-series blocks). 43 SMD components plus 3 THT (the BBB headers and DB25 connectors). 268 vias and 1727 track segments are consistent with a dense 2-layer board with multiple voltage translators routing 40 parallel I/O signals.
- minimum annular ring of 0.1mm is below the standard process limit of 0.125mm, correctly triggering dfm_tier='advanced' with one violation. The 0.1mm minimum drill (0.4mm) also meets advanced process requirements. This is accurate for the design's small via sizes.
- ground_domains.domain_count=3 with GNDA_ADC, GNDD, and a third domain. This matches the schematic's separate ground plane strategy (digital ground GNDD, analog ADC ground GNDA_ADC, GND_OR_5V). The PCB correctly identifies these as separate domains with different component memberships.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
