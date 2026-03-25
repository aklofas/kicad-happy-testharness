# Findings: UBW32 / Hardware_Kicad_UBW32_MX460_v262

## FND-00001619: LM317-type regulator U2 Vref estimated as 0.6 V; should be 1.25 V, causing Vout to be reported as 0.969 V instead of ~3.3 V; LM317-type regulators U2 and U3 (V_REG_317SMD) classified as topology 'L...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: UBW32_MX460_v262.kicad_sch
- **Created**: 2026-03-24

### Correct
- In Eagle-imported designs, quartz crystals use the 'Q' reference prefix (not 'Y' as in KiCad convention). The analyzer correctly resolves Q1 (SchmalzHaus CRYSTAL5X3) and Q2 (SchmalzHaus_CRYSTAL32-SMD) as type 'crystal' and includes them in crystal_circuits analysis with appropriate load cap detection (C14/C15 for Q1, C16/C17 for Q2). Load capacitance calculations are in typical range for both oscillators.

### Incorrect
- U2 uses lib_id 'V_REG_317SMD', an LM317-type adjustable linear regulator whose reference voltage is 1.25 V. The analyzer uses assumed_vref=0.6 V (heuristic) and computes estimated_vout = 0.6 × (1 + R13/R14) = 0.6 × (1 + 390/240) = 1.57 V, but reports 0.969 V (ratio math differs). The correct calculation is Vout = 1.25 × (1 + 390/240) = 3.28 V, matching the net name '3.3V' and component value label. The analyzer itself flags a 70.6% vout_net_mismatch, confirming the wrong Vref. The assumed_vref heuristic of 0.6 V should not be applied to LM317-family devices.
  (signal_analysis)
- Both U2 ('3.3V', V_REG_317SMD) and U3 ('5V', V_REG_317SMD) are reported with topology='LDO'. The LM317 requires a minimum 3 V input-to-output differential and is an adjustable linear regulator, not a low-dropout device. The correct topology is 'linear_adjustable'. This misclassification also flows into the power_budget and design_observations sections.
  (signal_analysis)
- For U2: C12 (10 µF) is on the 5V input rail and C6–C13 (seven 0.1 µF/1 µF caps) are on the 3.3V output rail — well-decoupled. For U3: C1 (10 µF) is on the __unnamed_9 input rail and C2 (10 µF) plus C5 (10 µF) are on the 5V_ALT output rail. Both regulators have adequate decoupling. The false positive likely occurs because the input rails are unnamed or non-standard ('__unnamed_9' for U3 input, and caps on '5V_ALT' vs the expected '5V' label for U3's output).
  (signal_analysis)
- These are non-electrical Eagle-import artifacts: U$4 is a SparkFun logo silkscreen symbol, U$6 and U$7 are mechanical standoffs. All three are classified as type 'ic' because their reference prefix 'U' triggers the IC classifier. They should be classified as 'mechanical', 'graphic', or 'other'. This inflates the IC count (8 reported, but only U1, U2, U3 are actual ICs among the U-prefix group) and pollutes ic_pin_analysis.
  (statistics)

### Missed
(none)

### Suggestions
- Fix: LM317-type regulators U2 and U3 (V_REG_317SMD) classified as topology 'LDO'; LM317 is an adjustable linear regulator with ~3 V dropout
- Fix: U$4 (LOGO-SFENEW), U$6 (STAND-OFF), and U$7 (STAND-OFF) classified as type 'ic'

---

## FND-00001917: Component count, types, and power rails correctly extracted from Eagle-imported KiCad 8 schematic; USB0 and PWR0 classified as 'connector' instead of 'led'; LM317 regulator voltage estimation uses ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: UBW32_Hardware_Kicad_UBW32_MX460_v262.kicad_sch
- **Created**: 2026-03-24

### Correct
- 62 components reported (source has 62 named refs including #FRAME2 and M01PTH pads). Power rails [3.3V, 5V, GND, VBUS] correct. Crystal circuits (8MHz, 32.768KHz) with load cap analysis correct. Switches PROGRAM0/RESET0/USER0 correctly classified as 'switch'. Fuse F1, diode D1, LEDs LED1/LED2/LED3 correctly classified.
- J7 (USB-A-S) and J8 (USB-MINIB) correctly identified. vbus_decoupling=pass (C3 1uF on VBUS). vbus_esd_protection=fail is accurate — there is no TVS on VBUS. D+/D- differential pair detected. Annotation issues correctly flag Eagle-style zero-indexed refs (GND0, PROGRAM0, PWR0, RESET0, USB0, USER0).

### Incorrect
- Both USB0 and PWR0 have lib_id 'UBW32_MX460_v262-eagle-import:LED0603' and are clearly LED footprints, but the type field is 'connector'. LED1/LED2/LED3 with the same lib_id are correctly classified as 'led'. The component_types count reports led=3 but there are 5 LEDs. GND0 (M01PTH) is 'other' but UNK3.3 and UNK5 (same M01PTH lib_id) are classified as 'ic' — inconsistent classification of the same lib_id.
  (statistics)
- U2 (V_REG_317SMD, 3.3V output) is an LM317-type regulator with Vref=1.25V. With R13=390Ω and R14=240Ω, correct Vout = 1.25*(1+390/240) = 3.28V which matches the 3.3V net. But the analyzer uses assumed_vref=0.6 (heuristic) giving estimated_vout=0.969V and reports a 70.6% vout_net_mismatch — a false positive. Same issue applies to U3 (5V LM317 with R15=715Ω, R16=240Ω → Vout=4.97V, correct). The 'regulator_caps missing' observation for U2 and U3 is also suspect since both have multiple decoupling caps nearby.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001918: PCB statistics accurately match source: 63 footprints, 100 nets, 1233 tracks (1231 segments + 2 arcs), 96 vias, 2 copper layers; Ground domain correctly identifies single GND domain with copper zon...

- **Status**: new
- **Analyzer**: pcb
- **Source**: UBW32_Hardware_Kicad_UBW32_MX460_v262.kicad_pcb
- **Created**: 2026-03-24

### Correct
- Source confirms: 63 footprints, 101 unique nets in file (100 excluding unconnected net 0), 1231 segments + 2 arcs = 1233 track_segments in analyzer, 96 vias. Board dimensions 111.5×26.4mm correct. routing_complete=True, unrouted=0 correct. DFM correctly flags board size exceeding 100×100mm (one dimension is 111.5mm).
- Single GND domain with has_zone=True on F.Cu is accurate. The GND copper pour covers the underside of the PIC32 area as confirmed by zone_count=2 in statistics.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
