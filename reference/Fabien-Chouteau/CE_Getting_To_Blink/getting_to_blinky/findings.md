# Findings: Fabien-Chouteau/CE_Getting_To_Blink / getting_to_blinky

## FND-00000420: U1 pin 1 (GND) not resolved to GND net; U1 pin 8 (VDD) not resolved to VDD net; power domain incorrect; U1 timing and control pins (2,4,5,6,7) all isolated in single-pin unnamed nets; R2/C1 timing ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: getting_to_blinky.sch.json
- **Created**: 2026-03-23

### Correct
- U1's GND pin (pin 1) is placed in an isolated unnamed net '__unnamed_0' with only one pin rather than being connected to the GND net. In the 555 circuit, pin 1 is ground and should share the GND net with BT1 pin 1, C1 pin 1, D1 anode, and the power symbols. This is a net-resolution failure in the KiCad 5 legacy parser for U1's pin connections.
- U1's VDD supply pin (pin 8) is isolated in '__unnamed_7' instead of being connected to the VDD net. The schematic shows wires from the VDD label line (at y=2650) going to U1's VDD pin (5675,2825 → U1 at 5800,3600 area). As a result, design_analysis.power_domains.ic_power_rails.U1.power_rails lists '__unnamed_7' instead of 'VDD', which is incorrect.
- Pins 2 (TRIG), 3 (OUT), 4 (RESET), 5 (CTRL), 6 (THRESHOLD), 7 (DISCHARGE) of U1 are each placed in isolated single-pin unnamed nets (__unnamed_1 through __unnamed_6) rather than being connected to the RC timing network and output circuit. For a 555 astable oscillator: TRIG and THRESHOLD should share the R2/C1 junction net; DISCHARGE should share the R1/R2 junction net; OUT should connect to R3; RESET should tie to VDD; CTRL is often left open or bypassed. This is a systematic net-connectivity failure for all U1 signal pins.
- The statistics report 14 total nets. Of these, 8 (__unnamed_0 through __unnamed_7) each contain exactly one pin from U1, resulting from the net-resolution failure on U1's pins. If U1's pins were correctly connected to their respective nets (VDD, GND, timing nets, output net), the real net count would be around 6: VDD, GND, R1/R2 junction, R2/C1 junction, U1_OUT/R3 junction, R3/D1 junction. The inflated count of 14 directly reflects the connectivity bug.

### Incorrect
- The analyzer detected R2 (470K) and C1 (1u) as a low-pass filter with fc=0.34 Hz. In reality this is the timing RC network of a 555 astable oscillator — the resistor and capacitor set the oscillation period (~0.47s time constant), not a signal filtering function. Classifying it as a low-pass filter is a functional misclassification; the correct category would be an oscillator timing network.
  (signal_analysis)

### Missed
- The 7555 CMOS timer (U1) with R1 (1K), R2 (470K), and C1 (1u) forms a classic astable oscillator (LED blinker). The subcircuits entry for U1 has empty neighbor_components and no description, indicating the analyzer failed to identify U1's surrounding oscillator topology. A 555 in astable mode is a well-known, detectable circuit pattern (discharge resistor R1 from VDD to DISCHARGE, timing resistor R2 from DISCHARGE to THRESHOLD/TRIG, timing capacitor C1 from THRESHOLD to GND). This should appear in design_observations or a dedicated oscillator detector.
  (subcircuits)
- R3 (1K) and D1 (LED) form an LED current-limiting driver circuit on the output of U1 (555 timer, pin 3). This is a standard LED driver topology where a series resistor limits current to the LED. The signal_analysis section has no detection of this LED driver circuit, and D1 does not appear in any signal analysis entry.
  (signal_analysis)

### Suggestions
- Fix: R2/C1 timing network misclassified as a low-pass RC filter

---
