# Findings: nica-f/Bangle-JS2-SWD / Bangle-USB-SWD

## FND-00000385: Single-pin nets not flagged in connectivity_issues; SWD debug connector not detected in test_coverage; All connectors classified as SMD; should be THT; VbusA net classified as 'signal' instead of '...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Bangle-USB-SWD.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- assembly_complexity reports smd_count=3 and tht_count=0. All three connectors use through-hole footprints: J1 uses USB_A_Molex_67643_Horizontal (THT), J2 uses PinHeader_2x05_P2.54mm_Vertical (THT), J3 uses PinHeader_1x02_P2.54mm_Vertical (THT). None are SMD. The SMD/THT classification is incorrect.
  (assembly_complexity)
- design_analysis.net_classification classifies VbusA as 'signal'. VbusA is the USB VBUS power rail delivered to the target device through the SWD 10-pin header (J2 pin 10). It is connected to J3 pin 2 (the other end of the power jumper). This is a power distribution net and should be classified as 'power', consistent with how the related 'Vbus' net is classified.
  (design_analysis)

### Missed
- J2 pins 1, 5, 7, 8, 9 are each on isolated unnamed nets (__unnamed_0 through __unnamed_4) with no connections. These five single-pin nets appear in the nets section but connectivity_issues.single_pin_nets is an empty list. They should all be reported there as connectivity issues.
  (connectivity_issues)
- The design is explicitly a SWD breakout adapter. J2 (Conn_02x05_Odd_Even) carries nets named SWD and SWCLK — the canonical 10-pin ARM SWD/JTAG header pinout. The test_coverage.observations incorrectly states 'No debug connectors (SWD/JTAG/UART) identified'. A connector with SWD and SWCLK signals on a 2x5 header should be recognised as a debug/SWD connector.
  (test_coverage)

### Suggestions
- Fix: VbusA net classified as 'signal' instead of 'power'

---
