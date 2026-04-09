# Findings: transistorfet/retroverse / components_backplane_6-Slot-Backplane_6-Slot-Backplane

## ?: 6-slot VME64 backplane with ATX power, active bus termination (TCA0372 + 4610X divider networks), and 74ACT32 daisy-chain logic. Analyzer correctly identifies hierarchical design, VME connectors, voltage dividers, and bus topology but misclassifies graphic logo as switch, labels opamp buffers as comparators, and misses VME bus protocol detection.

- **Status**: new
- **Analyzer**: schematic
- **Source**: components_backplane_6-Slot-Backplane_6-Slot-Backplane.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- 163 unique components correctly counted across 9 sheets (root + 6 slots + 2 termination sheets)
- 6 VME-J1-4R-NS DIN41612 slot connectors (J1-J6) correctly identified as 4-unit multi-unit connectors
- ATX-24 power connector (J101) correctly identified with Intel datasheet link
- 5 power rails correctly detected: +12V, +5V, +5VStdby, -12V, GND
- 4 voltage dividers (330/470 ohm, ratio 0.5875 giving ~2.94V) correctly detected feeding TCA0372 inverting inputs for active termination reference
- Bus topology correctly detects A[0..31] (32-bit address), D[0..31] (32-bit data), and AM[0..5] (6-bit address modifier) buses
- 24 resistor networks (4610X-104-331/471L dual terminator divider SIP) correctly identified as resistor_network type
- 7 74ACT32 quad OR gates (U3-U9) correctly identified for bus grant and IACK daisy chain routing
- 25 DNP jumpers correctly identified (JP14-JP38 are per-slot bus grant bypass jumpers marked DNP)
- 3 decoupling groups correctly analyzed: +12V (10.1uF), -12V (10.1uF), +5V (11.2uF with 13 caps)
- IRQ1-IRQ7 nets correctly classified as 'interrupt' type
- SYSCLK and ~{SERCLK} correctly classified as 'clock' nets
- ~{SYSRESET} correctly classified as 'control' net
- 82k pull-down resistors on OR gate inputs correctly detected in ic_pin_analysis for bus grant chain weak pull-downs
- Hierarchical design correctly flattened: 9 sheets listed (root + Slot1-6 + TerminationLeft + TerminationRight)

### Incorrect
- S1 (Logo_Open_Hardware_Small from Graphic:Logo_Open_Hardware_Small) misclassified as 'switch'. It is a PCB silkscreen logo graphic, not an electrical component. The 'S' reference prefix triggers incorrect switch classification.
  (statistics.component_types.switch)
- TCA0372 opamp circuits classified as 'comparator_or_open_loop' but they are actually configured as voltage followers/buffers with positive feedback (output tied to non-inverting input) providing a regulated termination voltage. The TCA0372 is a high-current dual power opamp specifically designed for active bus termination. While the positive feedback connection could be interpreted as comparator-like, the intent is a unity-gain buffer driving the termination reference rail through a decoupling capacitor.
  (signal_analysis.opamp_circuits)
- VME bus control signals (~{AS}, ~{DS0}, ~{DS1}, ~{DTACK}, ~{BERR}, ~{WRITE}, ~{BBSY}, ~{BCLR}, ~{RETRY}) are classified as generic 'signal' rather than 'control'. These are well-known VME bus control strobes that should be classified as control signals.
  (design_analysis.net_classification)
- ~{SYSFAIL} and ~{ACFAIL} classified as 'signal' rather than 'control' or 'interrupt'. These are VME system failure indicators that function as control/status signals.
  (design_analysis.net_classification)

### Missed
- VME bus protocol not detected. This is a VME64 backplane with all standard VME bus signals (A[0..31], D[0..31], AM[0..5], IRQ1-7, BR0-3, BG0-3, IACK, DTACK, AS, DS0, DS1, BERR, SYSRESET, SYSCLK, BBSY, BCLR, etc.). The bus topology section detects address/data bus widths but does not identify this as a VME bus system.
  (signal_analysis)
- Active bus termination circuit not identified as a distinct pattern. The TCA0372 opamps (U1, U2) with voltage dividers (330/470 ohm) providing ~2.94V reference, feeding through PASSIVE/ACTIVE jumpers (JP1-JP8) to 4610X resistor divider networks (RN1-RN24), is a classic VME active termination circuit. This is a well-known bus termination topology that should be recognized.
  (signal_analysis)
- Bus grant daisy chain topology not identified. The 74ACT32 OR gates (U3-U9) implement the VME bus grant and IACK daisy chain, where each slot's BG0OUT/BG1OUT/BG2OUT/BG3OUT/IACKOUT connects through an OR gate (with bypass jumpers) to the next slot's BGIN/IACKIN. This is a key VME backplane topology pattern.
  (subcircuits)
- SYSTEM MONITOR connector (J107, 5-pin) not characterized. It provides monitoring access to the backplane - likely for power good, reset, and status signals.
  (ic_pin_analysis)

### Suggestions
- Add VME bus protocol detection based on characteristic signal names (AS, DS, DTACK, BERR, BR0-3, BG0-3, IACK, IRQ1-7, AM0-5, SYSCLK, SYSRESET) and DIN41612 connectors
- Add active bus termination pattern detection: opamp voltage reference + resistor divider networks + passive/active selection jumpers
- Recognize graphic/logo symbols (Graphic:Logo_Open_Hardware_Small, etc.) as non-electrical components rather than classifying by reference designator prefix
- Detect daisy-chain bus grant topology: OR gate chains connecting slot-to-slot with bypass jumpers
- Classify known bus control signals (~{AS}, ~{DS*}, ~{DTACK}, ~{BERR}, ~{WRITE}, ~{BBSY}, ~{BCLR}) as 'control' rather than generic 'signal'

---

## FND-00002530: VME 6-slot backplane with ATX power input, 6 DIN41612 slot connectors, 7 74ACT32 OR gates for BG/IACK daisy-chains, 2 TCA0372 comparators for power monitoring, and 24 Bourns 4610X terminator SIPs. Component identification correct but S1 (OSHW logo) misclassified as switch, duplicate pin entries for multi-unit ICs inflate ERC warnings, and 98 unnamed single-pin nets for terminator taps not flagged.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: components_backplane_6-Slot-Backplane_6-Slot-Backplane.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- All 163 components correctly typed: 7 74ACT32 as ic, 2 TCA0372 as ic, 6 DIN41612 connectors, 24 4610X as resistor_network
- All 4 comparator voltage-divider references correctly detected: R19/R20, R3/R4, R21/R22, R7/R8 producing 2.94V
- All 4 TCA0372 units correctly classified as comparator_or_open_loop with hysteresis feedback
- VME bus topology correctly detects A[1..31], D[0..31], AM[0..5] from 536 bus wires across 9 sheets
- All 12 dual-terminator connections correctly merged to named bus signals

### Incorrect
- S1 (Graphic:Logo_Open_Hardware_Small, OSHW silkscreen logo) classified as type='switch'. Should be 'graphic' or excluded from BOM.
  (statistics.component_types)
- 15 nets have duplicated pin entries for multi-unit 74ACT32 ICs, inflating ERC output_conflict counts from 5 to 10 per net.
  (connectivity_issues.multi_driver_nets)
- 5 output_conflict ERC warnings inflated by duplicate-pin issue. Each net legitimately has 5 OR-gate outputs (VME daisy-chain), but reports 10.
  (design_analysis.erc_warnings)

### Missed
- 98 unnamed single-component nets for RN1-RN12 terminator tap pins (pins 3-9) not reported as connectivity issues. 7 of 8 bus terminations per SIP appear unconnected.
  (connectivity_issues.single_pin_nets)
- TERM_L1_LOW net shows only JP2 pin 2 connected — asymmetric label resolution failure vs TERM_L1_HIGH which correctly merges with 14 components.
  (connectivity_issues.single_pin_nets)

### Suggestions
- Add 'Graphic:' library prefix to classify as 'graphic' instead of 'switch'.
- Deduplicate pin-to-net entries by (reference, pin_number) for multi-unit ICs.
- Extend single_pin_net detection to include unnamed nets with exactly one non-#PWR pin.

---
