# Findings: Caffeinated-AFTONSPARV / Caffeinated-AFTONSPARV

## FND-00000424: Capacitor count wrong: reports 2 capacitors, actual count is 10; DNP count reports 0, but J4 (USB connector) is marked DNP; Multi-project schematic: analyzer reads wrong-project Reference property ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Caffeinated-AFTONSPARV.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic file is shared between two KiCad projects: 'JugendHackt-Badge-Display' and 'Caffeinated-AFTONSPARV'. KiCad stores per-project component references in `instances` blocks keyed by project UUID. The analyzer reads the top-level `Reference` property (e.g., 'C5', 'C22', '#PWR0129') rather than the project-specific reference from the instance matching the file's own UUID (4a7e3c1c-0963-4185-9d61-8867e6f8dfa5). This causes systematic wrong references throughout: e.g., UUID 1626f54a should be C2 (not C22), UUID 37f45d72 should be C3 (not C5), UUID 995234e8 should be C1 (not C5). The GND net also incorrectly references '#PWR0129' three times (correct refs are #PWR019, #PWR020, #PWR023 for this project).
- The SY8201 buck converter (U2) output filter consists of L1 (10uH) and a single 4.7uF capacitor on the LX switching node (__unnamed_5). Because the wrong-project reference collision makes nine distinct capacitors all appear as 'C5', the LC filter detector combines them as '9 caps parallel' (total 900nF) and uses ref 'C5' throughout. The actual single output filter capacitor is the component with UUID 37f45d72, which has Caffeinated-AFTONSPARV instance reference C3 (4.7uF). The resonant frequency and impedance calculations (53.05 kHz, 3.33Ω) are therefore wrong; the correct single-cap values would be ~75.7 kHz and 1.63Ω.

### Incorrect
- This schematic was reused across two KiCad projects. Component references in the file are project-specific and stored in `instances` blocks, not in the top-level `Reference` property. The analyzer reads the top-level property (which reflects the other project 'JugendHackt-Badge-Display') instead of the 'Caffeinated-AFTONSPARV' instance reference. As a result, nine distinct capacitors (C1, C3, C4, C6, C7, C9, C10, C11 + one legitimately named C5) all appear as 'C5'. The statistics section reports capacitor count=2 (seeing C5 and C22), when the correct count is 10 (C1=100nF, C2=100µF, C3=4.7uF, C4=100nF, C5=22pF, C6=4.7uF, C7=100nF, C9=4.7uF, C10=4.7uF, C11=100nF).
  (statistics)
- The component J4 (a 4-pin USB connector) has `dnp yes` set in the schematic source and the analyzer correctly marks J4's `dnp` field as true in the components list. However, `statistics.dnp_parts` reports 0 instead of 1.
  (statistics)
- The voltage_dividers list contains an entry with r_top=R5 (20Ω) and r_bottom=R1 (10kΩ), top_net='__unnamed_0', mid_net='LED-B'. This is not a voltage divider. R5 is a gate series resistor for Q3 (N-channel MOSFET, AO3400A) limiting gate current, and R1 is a gate pull-down resistor to GND. The mid-point net 'LED-B' connects to U1 GPIO6 which drives the MOSFET gate. A 20Ω:10kΩ ratio would produce a 0.998 division ratio, which makes no sense as a voltage divider but is correct for a GPIO-driven gate drive where the pull-down holds the gate low when the GPIO is tristated. The transistor_circuits section already correctly identifies Q3 with gate_resistors=[R5], confirming R5's true role.
  (signal_analysis)
- The BOM section shows only two capacitor entries: one 'C22' (100µF 35V, qty 1) and one 'C5' (100nF, qty 1). Because eight additional distinct capacitors all received the wrong reference 'C5' from the other project's data, the BOM deduplication consolidates them into a single C5 entry of qty=1. The correct BOM should show: 100nF ×4 (C1, C4, C7, C11), 100µF 35V ×1 (C2), 4.7uF ×4 (C3, C6, C9, C10), 22pF ×1 (C5) — four distinct capacitor line items totalling 10 units.
  (statistics)

### Missed
- The schematic has four 100nF bypass capacitors on +3.3V (C4, C7, C11 on various 3.3V sub-rails) and one on +24V (C1). All appear as duplicate 'C5' references due to the multi-project reference resolution bug, so the decoupling analyzer cannot associate them with the correct power rails. The decoupling_analysis section only finds C22 (100µF on +24V) and misses: (1) C1/100nF bypass on +24V, (2) all three 100nF bypass caps on +3.3V. The design observation for U1 correctly notes '+3.3V' is without caps, but this is because the caps exist and are wired correctly — they just have wrong references in the output.
  (signal_analysis)

### Suggestions
(none)

---
