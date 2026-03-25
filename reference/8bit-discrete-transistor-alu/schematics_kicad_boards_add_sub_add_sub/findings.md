# Findings: 8bit-discrete-transistor-alu / schematics_kicad_boards_add_sub_add_sub

## ?: 8-bit adder/subtractor built from discrete CMOS transistors (178 NMOS/PMOS) plus 74HC86 XOR and 74HC157 mux ICs; bridge detector misclassifies transmission gates as motor bridges; no discrete logic gate detection

- **Status**: new
- **Analyzer**: schematic
- **Source**: schematics_kicad_boards_add_sub_add_sub.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- Total transistor count of 178 (89 PMOS + 89 NMOS) is correct, matching all discrete MOSFET instances across hierarchical sheets
- Correctly identified 12 IC packages: 6x 74HC86 quad XOR and 6x 74HC157 quad 2:1 mux
- Correctly identified VCC and GND as the only two power rails
- Decoupling analysis correctly found 6x 100nF caps on VCC rail
- Bus topology correctly detected A[0..7], B[0..7], and SUM[0..7] 8-bit buses
- Correctly identified 4 connectors (J101-J104): 3x Conn_01x12 and 1x Conn_01x34
- 140 transistor circuits correctly identified with MOSFET type, gate/drain/source nets, and power connection analysis
- Correctly traversed 58 hierarchical sheets including deeply nested structures (root -> adder8 -> adder2 -> gate_and/or/nand)
- BOM correctly grouped 8 unique part values with accurate quantities
- Connectivity issues correctly flagged 16 single-pin nets including U801/U802 I0 inputs that appear unconnected at the mux level

### Incorrect
- Bridge circuit detection classified 19 complementary NMOS pairs as a '19_phase' motor bridge. These are actually CMOS transmission gates implementing discrete multiplexer/pass-transistor logic in the adder carry chain, not H-bridges or motor drivers. The 38 transistors (Q36xx-Q57xx) form paired NMOS pass gates, not power-stage half-bridges.
  (signal_analysis.bridge_circuits)
- Bridge circuit lists 74HC86 XOR gates as 'driver_ics' for the bridge. XOR gates serve as conditional inverters for the subtraction mode (A XOR M), not as gate drivers for a motor bridge.
  (signal_analysis.bridge_circuits[0].driver_ics)
- All FETs in the bridge classification show as NMOS only, but the actual transmission gates use complementary NMOS/PMOS pairs. The PMOS counterparts (Q3601, Q3604, Q3701, Q3704, etc.) are in transistor_circuits but their paired NMOS are in bridge_circuits, splitting what are actually complementary pairs across two different detection categories.
  (signal_analysis.bridge_circuits[0].fet_values)

### Missed
- No detection of discrete CMOS logic gates. The design's core innovation is implementing AND, OR, NAND, NOT, and XOR functions from complementary MOSFET pairs. The 140 transistors in transistor_circuits form recognizable CMOS gate topologies (e.g., Q5005+Q5006 form an AND gate, Q903-Q906 form an OR gate, Q5105+Q5106 form an inverter) that should be classified as digital logic gates rather than generic transistor circuits.
  (signal_analysis.transistor_circuits)
- No detection of the adder/subtractor functional block. The hierarchical sheet structure (adder8 containing 4x adder2, each containing full-adder logic) implements an 8-bit ripple-carry adder with XOR-based conditional inversion for subtraction mode. This is a recognizable arithmetic circuit topology.
  (signal_analysis)
- No detection of CMOS transmission gates / pass-transistor logic. The 38 transistors classified as bridge circuits are actually CMOS pass gates used in the multiplexer selection logic, a fundamental analog switch topology distinct from both bridges and simple switching transistors.
  (signal_analysis.transistor_circuits)

### Suggestions
- Add a discrete CMOS logic gate detector that recognizes complementary NMOS/PMOS pairs with shared drain nodes as inverters, series/parallel PMOS+NMOS networks as NAND/NOR gates, and cascaded stages as AND/OR gates
- Add a CMOS transmission gate / pass-gate detector for complementary NMOS/PMOS pairs with shared source and drain (not power/ground) that act as analog switches
- The bridge circuit detector should distinguish power-stage half-bridges (where the output drives a load between VCC and GND) from signal-level pass-transistor logic (where the 'power' net is actually a signal input). A key distinguishing feature: in real bridges, the high-side FET is typically PMOS and the supply net is a power rail, whereas here both FETs are NMOS and the 'supply' is a logic signal
- Consider detecting arithmetic circuit patterns (ripple-carry adder, carry chain) from the hierarchical sheet names and connectivity patterns

---
