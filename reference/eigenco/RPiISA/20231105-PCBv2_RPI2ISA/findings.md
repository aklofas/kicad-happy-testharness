# Findings: eigenco/RPiISA / 20231105-PCBv2_RPI2ISA

## FND-00001201: RPiISA v2 schematic parsed correctly: 4 components, ISA bus + RPi + crystal oscillator; Crystal oscillator Y1 not detected in crystal_circuits; single_pin_nets correctly reported for unconnected IS...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: RPI2ISA.kicad_sch
- **Created**: 2026-03-23

### Correct
- Simple adapter board with Bus_ISA_8bit (J1), Raspberry_Pi_2_3 (J2), DIP-20 connector (J3), and 14.318MHz crystal oscillator (Y1). Component types, power rails (GND/VCC), and 23 no-connects are correct for a minimal ISA bus adapter.
- The connectivity_issues.single_pin_nets section correctly flags ISA bus signals that are exported from J1 but not connected to other components in this minimal schematic.

### Incorrect
(none)

### Missed
- Y1 is a 14.318MHz clock oscillator (ACH-14.31818MHZ-EK, 4-pin oscillator module). The signal_analysis.crystal_circuits array is empty, even though there is a crystal/oscillator component. The ACH part is a 4-pin CMOS oscillator, not a 2-pin crystal, but it should still be detected as a clock source.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001202: ISARPiv2 legacy schematic parsed with 12 components: ISA bus, RPi connector, 8 pull-up resistors, crystal oscillator; Crystal oscillator Y1 not detected in crystal_circuits for ISARPiv2

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: ISARPiv2_ISARPiv2.sch
- **Created**: 2026-03-23

### Correct
- Component count and types (3 connectors, 8 resistors, 1 crystal) are correct. The 8 resistors (R10-R17, value 100 ohm) are bus termination/pull-up resistors consistent with ISA bus design.

### Incorrect
(none)

### Missed
- Same issue as the v2 schematic — 14.318MHz crystal oscillator Y1 is present but crystal_circuits is empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001203: ISAMEM schematic parsed correctly: 3 components (ISA bus connector, AS6C4008 SRAM, 10uF cap); ERC warning for V5 net correctly flagged as no_driver (power rail without a PWR_FLAG); AS6C4008 SRAM no...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: MEMv1_ISAMEM.sch
- **Created**: 2026-03-23

### Correct
- AS6C4008-55PCN CMOS SRAM correctly identified as IC. ISA bus connector correct. Only GND power rail (no VCC power symbol, only through ISA connector pins) is accurately reflected.
- V5 connects ISA VCC pins to SRAM VCC but has no power symbol driver — the ERC correctly identifies this as a net with power_in pins but no power source symbol.

### Incorrect
(none)

### Missed
- IC3 is an AS6C4008-55PCN, a 512K x 8 CMOS SRAM with a standard parallel address/data bus interface. memory_interfaces is empty. The SRAM's 20-bit address bus (A0-A19) and 8-bit data bus (D0-D7) connecting to the ISA bus should be detectable as a memory interface.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001204: PCB v2 correctly parsed: 4 THT footprints, 2-layer, 81.3x33.8mm ISA card form factor

- **Status**: new
- **Analyzer**: pcb
- **Source**: RPI2ISA.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 4 through-hole components, 62 nets, 319 track segments, 12 vias, fully routed. The board dimensions match a standard ISA card form factor.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001205: ISARPiv2 PCB correctly parsed: 12 footprints (9 SMD + 3 THT), 2-layer, same ISA form factor; Edge clearance warnings for J2 and J3 correctly flagged (negative clearance = outside board outline)

- **Status**: new
- **Analyzer**: pcb
- **Source**: ISARPiv2_ISARPiv2.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 12 components matching schematic count, mixed SMD/THT, 45 nets, fully routed. Courtyard overlap between Y1 and J3 (98.6mm²) is a real DFM issue that the PCB analyzer correctly flags.
- J2 (RPi header, -19.4mm) and J3 (DIP socket, -3.8mm) have negative edge clearance, meaning their courtyards extend beyond the board edge. This is intentional for an ISA slot connector that overhangs the board edge, but the flagging is correct.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001206: ISAMEM PCB correctly parsed: 3 footprints, 2-layer, 81.28x39.37mm, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: MEMv1_ISAMEM.kicad_pcb
- **Created**: 2026-03-23

### Correct
- 3 components (SRAM DIP-32, ISA connector, decoupling cap), 32 nets, 208 tracks, 16 vias, fully routed. Matches the simple SRAM card design.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
