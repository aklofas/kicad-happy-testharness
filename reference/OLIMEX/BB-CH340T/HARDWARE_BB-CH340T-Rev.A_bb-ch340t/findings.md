# Findings: OLIMEX/BB-CH340T / HARDWARE_BB-CH340T-Rev.A_bb-ch340t

## FND-00000400: UART detected on RXD/TXD nets but U1's actual serial pins are floating; U1 GND pin (pin 8) is not on the GND power net — isolated in an unnamed net

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_BB-CH340T-Rev.A_bb-ch340t.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The analyzer detects UART on the named nets RXD and TXD. However, U1's actual TXD pin (pin 3) is on an isolated unnamed net (__unnamed_0) and U1's actual RXD pin (pin 4) is on another isolated unnamed net (__unnamed_1). Neither is connected to the labeled RXD or TXD nets. The RXD net contains U1.pin20 (NOS#, a modem-control signal) and a connector pin; the TXD net contains R1 and D1 passive pins but no IC UART output. The UART detection is triggered by net name pattern matching, not by tracing actual IC UART pin connectivity.
  (design_analysis)

### Missed
- U1's GND pin (pin 8, at schematic coordinate y=4450) is placed on net __unnamed_4 rather than the named GND net. The wire at y=4450 connects from USB1.D+ (pin 3) to U1.GND (pin 8). As a result, the CH340T GND pin is not detected as connected to the board ground plane. This may be an unusual schematic connection or a design error, but it means the power rail detection misses U1's ground connection. The GND net's power_rails list is present but U1 has no ground rail in its ic_power_rails entry.
  (design_analysis)

### Suggestions
(none)

---

## FND-00000401: Net count drops from 26 to 8 versus identical schematic due to failed pin extraction from cache library; U1 subcircuit has no neighbor components due to empty pin lists

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_BB-CH340T-Rev.A_rescue-backup_bb-ch340t-2020-04-29-09-36-51.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The rescue-backup schematic is byte-for-byte identical in component layout to the Rev.A main schematic, yet the analyzer extracts only 8 nets instead of 26. U1 (CH340H/T), USB1, D1 (Schottky diode), and 3.3/5V1 (JUMPER3) all have empty 'pins' arrays in the rescue-backup output. This is because the rescue-backup file uses only the project-local 'bb-ch340t-cache' library and the analyzer cannot resolve pin positions for components defined solely in that cache. The consequence is that all U1, USB1, D1, and jumper pin connections are invisible to the net tracer, collapsing the net graph from 26 to 8 entries.
  (statistics)

### Missed
- Because U1, USB1, D1, and the voltage-select jumper all have empty pin arrays (cache library lookup failure), the subcircuit detection for U1 finds zero neighbor components. The actual circuit has C1, C2, C3, C4, C5, Y1, USB1, and POUT1 all connected to or near U1. The subcircuits entry shows neighbor_components: [] when it should list at least the crystal, load capacitors, and USB connector.
  (subcircuits)

### Suggestions
(none)

---

## FND-00000402: Modem control nets RTS/CTS/DSR/DCD are single-pin; CON1 and CON2 pins are unnamed — net-tracing incomplete; UART detected on TX net via U1 pin RS232 (pin 18) — this is not a UART data line

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_BB-CH340T-Rev.B_bb-ch340t.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The bus_analysis UART section lists net TX as a UART signal containing U1.pin18 (named RS232 in the cache library). In the CH340T, pin 18 is a mode-select or 3.3V supply pin; it is not a standard UART TXD or RXD data line. The true UART TXD (U1 pin 3) is on an unnamed net (__unnamed_3, connected to SJ2), and the true RXD (U1 pin 4) is on the NOS net (connected to SJ1). The analyzer is matching the net label 'TX' by name pattern rather than by IC UART pin identification, leading to a false UART detection on a non-data signal.
  (design_analysis)

### Missed
- In the Rev.B schematic the modem control signals from U1 (CTS#, DSR#, DCD#, RTS#) are labeled RTS, CTS, DSR, and DCD respectively and routed via multi-segment wires to connector CON1 (3-pin) and CON2 (3-pin). The analyzer correctly traces DTR (which connects U1.DTR# to CON1.pin1) but fails to trace the other four nets across their diagonal wire segments. As a result: (a) nets RTS, CTS, DSR, and DCD each contain only one pin (single-pin dangling), and (b) CON1.pin2, CON1.pin3, CON2.pin1 land in unnamed isolated nets instead of on DSR, CTS, and RTS respectively. This is a net-tracing failure for wire segments that change direction before reaching a connector pin.
  (nets)

### Suggestions
(none)

---
