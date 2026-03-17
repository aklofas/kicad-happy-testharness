# Findings: zx-sizif-512 / pcb_rev.B_sizif512

## FND-00000265: ZX Spectrum clone/expansion rev.B (KiCad 5, 216 components). Y-flip transform causes collector/emitter pin swap on BJTs. False LED driver detection for Q1/D12 with no shared nets. DC-DC converter not detected as regulator.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pcb_rev.B_sizif512.sch.json
- **Created**: 2026-03-16

### Correct
- Digital logic ICs (buffers, latches, memory) correctly classified
- Voltage dividers for biasing correctly detected

### Incorrect
- NPN transistors with (1,0,0,-1) Y-flip transform have collector/emitter pins swapped — Q2 reports emitter=+5V (should be collector), Q1 reports collector=GND (should be emitter), Q3 has both C/E on same net
  (signal_analysis.transistor_circuits)
- Q1 falsely identified as LED driver for D12/R13 — no shared nets, ~142mm apart on schematic
  (signal_analysis.transistor_circuits)

### Missed
(none)

### Suggestions
- Fix Y-flip (1,0,0,-1) transform matrix handling for Q_NPN_CBE in KiCad 5 legacy
- LED driver detection should require net connectivity between transistor and LED
- Recognize isolated DC-DC converter modules as power regulators

---
