# Findings: 8048-board / 8048board

## FND-00000324: Decoupling analysis undercounts bypass caps: C1, C3, C9 excluded from +5V decoupling; has_bulk=false incorrectly: C9 (1µF electrolytic) is a bulk capacitor on +5V; Memory interface not detected: 80...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 8048board.sch.json
- **Created**: 2026-03-23

### Correct
- The crystal circuit detection reports Y1 (6.144MHz) with load caps C7 and C8. The net data shows Y1 pin 1 on net __unnamed_0 with U1 T0 (test input, pin 1), and Y1 pin 2 on net __unnamed_1 with U1 ~INT~ (interrupt input, pin 6). On the Intel 8048, the crystal pins are X1 (pin 2) and X2 (pin 3), not T0/~INT~. The custom 'Ken:8048' symbol pin assignments differ from standard expectations. The crystal detection still correctly identifies Y1+C7+C8 as a crystal circuit (which it is), but the associated MCU pins flagged in the net data are T0 and ~INT~ rather than X1/X2, suggesting the custom 8048 symbol may have unusual pin numbering or the crystal is connected to non-standard pins in this design.

### Incorrect
- U7 uses a custom 'Ken:Converter' symbol with a daughterboard footprint and has pins named Vin-, Vin+, Vout-, Vout+ — clearly a DC-DC converter module providing the 15V supply (net '15V' on Vout-). It is classified as type 'ic' in the component list and is not detected in power_regulators=[]. A component with Vin/Vout power-named pins should be recognized as a power converter/regulator.
  (signal_analysis)
- The design_observations single_pin_nets entry reports 'U2 pin A7 on net A9'. In the schematic the label 'A9' appears on multiple wires including near U2 pin 24 (named A9 in the EPROM symbol). The observed anomaly — U2's pin named 'A7' (pin 3) being on a net labeled 'A9' — results from the 2764 EPROM symbol having A7 on pin 3 while the schematic routes it to a wire carrying the A9 label. This is actually an error in the schematic (address line mismatch/typo by the designer), but flagging it as a 'single-pin net' (point_count=2 is shown in the net data) is inaccurate — the A9 net has one endpoint from the label side. This is a real design issue but the single_pin_nets category mischaracterizes it.
  (signal_analysis)

### Missed
- The design has nine capacitors total: six 0.1µF bypass (C1–C6) and one 1µF bulk (C9), plus two 22pF crystal load caps (C7, C8). The decoupling_analysis only reports four capacitors (C2, C4, C5, C6) on the +5V rail and reports has_bulk=false with total 0.4µF. C1 and C9 are on the +5V rail but their return side connects to net __unnamed_2 rather than directly to GND, so the analyzer fails to recognize them as decoupling caps. C3 has both pins resolved to the +5V net (a connectivity parsing anomaly), also causing it to be excluded. The correct count should be at least 6 bypass caps (0.6µF) plus C9 (1µF bulk), and has_bulk should be true.
  (signal_analysis)
- C9 is a 1µF electrolytic (CP_Small, radial through-hole) connected to the +5V rail. The design_observations entry for decoupling_coverage reports has_bulk=false, but a 1µF electrolytic is standard bulk decoupling. C9 is excluded because its return side (pin 2) connects to net __unnamed_2 (which is an intermediate GND bus) rather than directly to the named GND net, so the analyzer doesn't classify it as a decoupling cap at all.
  (signal_analysis)
- The board uses a classic 8048 external memory expansion topology: U1 (Intel 8048 MCU) multiplexes its address/data bus on the DB.0–DB.7 pins, U3 (74LS373 octal latch) demultiplexes the lower address byte using the ALE signal, and U2 (2764 27C64-compatible EPROM) provides 8KB of external program memory. This is a textbook multiplexed-bus memory interface, but memory_interfaces=[] in the output. The address signals A0–A7 (through U3), A8–A10 (directly from U1 port 2) and ~RD/~WR control signals to U2 are all present.
  (signal_analysis)

### Suggestions
- Fix: U7 'Converter' (DC-DC power converter) classified as generic IC instead of power_regulator

---
