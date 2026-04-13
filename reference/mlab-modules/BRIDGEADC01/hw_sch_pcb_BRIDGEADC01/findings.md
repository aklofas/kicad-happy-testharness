# Findings: mlab-modules/BRIDGEADC01 / hw_sch_pcb_BRIDGEADC01

## FND-00000396: RF matching network falsely detected on reverse-protection diode D2 and ferrite bead L2; Multi-driver net false positives on __unnamed_21 and __unnamed_22 due to MIC4426 multi-unit symbol pin role ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_BRIDGEADC01.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer detected D2 (value 'M4', footprint SMA_Standard) as an antenna with L2 (BLM21PG300SN1D ferrite bead) as a matching network component. D2 is a reverse-polarity protection diode on the VAA analog supply; its value 'M4' is a package/footprint designation (SMA diode), not an RF component identifier. L2 is a ferrite bead used for EMI filtering between the +5V supply input and the VAA analog rail. Neither component has anything to do with RF or antenna matching. The detection was likely triggered by the diode value string 'M4' matching some pattern heuristic.
  (signal_analysis)
- The MIC4426 dual MOSFET gate driver is placed as two units (unit 1 at y=58.42, unit 2 at y=78.74). The symbol library defines pin 4 with different roles across sub-symbol configurations: in MIC4426_1_2 (unit 1 alternate) it is a non-inverting output, but in MIC4426_2_1 (unit 2 primary) it is a non-inverting input. The analyzer resolves pin 4 of the unit 2 instance as 'output' type because one of the symbol unit configurations lists it as output, and erroneously adds it to nets __unnamed_21 and __unnamed_22 as a second driver alongside pin 7 (real output of unit 1) and pin 5 (real output of unit 2) respectively. In reality there is only one driver per net. The net __unnamed_7 (ACX) also shows U1 pin 2 duplicated twice, and net __unnamed_8 (~ACX) incorrectly shows both pin 4 and pin 2 of U1 — pin 2 from MIC4426_2_2 alternative sub-symbol configuration bleeding into the unit 2 instance.
  (connectivity_issues)
- The analyzer flags nets __unnamed_7 (ACX) and __unnamed_8 (~ACX) as cross-domain signals requiring a level shifter, based on U2 (AD7730) having io_rails=['VCC'] and U1 (MIC4426) having power_rails=['VAA']. However, ACX and ~ACX are analog clock output signals from the AD7730 that drive the bridge excitation. These pins operate on the AD7730's AVDD rail (VAA), not on DVDD (VCC). The MIC4426 is powered from VAA. Both endpoints of the ACX and ~ACX signals are in the VAA domain — no level shifter is needed. The incorrect io_rail assignment (VCC rather than VAA) for U2's ACX/~ACX outputs causes this spurious warning.
  (design_analysis)

### Missed
- The AD7730 bridge ADC (U2) communicates via an SPI-like serial interface with pins SCLK (pin 1), ~CS (pin 19), DIN (pin 22, MOSI), and DOUT (pin 21, MISO). These are broken out to connectors J15 (SCLK), J14 (~CS), J16 (DIN), and J17 (DOUT). The analyzer correctly identifies these nets as signal nets but bus_analysis.spi is empty — the SPI interface is not detected despite the textbook SPI pin naming (SCLK, DIN, DOUT, ~CS).
  (design_analysis)

### Suggestions
(none)

---
