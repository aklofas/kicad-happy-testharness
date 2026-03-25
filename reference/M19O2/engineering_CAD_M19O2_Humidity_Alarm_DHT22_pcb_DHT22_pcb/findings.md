# Findings: M19O2 / engineering_CAD_M19O2_Humidity_Alarm_DHT22_pcb_DHT22_pcb

## FND-00000837: Output file does not exist — RFSOC project has not been analyzed

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_Schaltplan_RFSOC_RFSOC.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The M19O2 repo in the test harness is a robotics/pneumatics project (humidity alarm DHT22, pneumatic wiring). It contains no PCB_Schaltplan_RFSOC_* files. The RFSOC schematic outputs requested do not exist anywhere in results/outputs/schematic/M19O2/ or any other results directory. The repo hosting the RFSOC project is either not in repos.md or not yet checked out and analyzed.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000838: Output file does not exist — RFSOC MCU sheet not analyzed

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_Schaltplan_RFSOC_RFSOC_MCU.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause as above. No RFSOC hierarchy sheets present in M19O2 results.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000839: Output file does not exist — RFSOC RF-Frontend sheet not analyzed

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_Schaltplan_RFSOC_RFSOC_RF-Frontend.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause as above.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000840: Output file does not exist — RFSOC Supply sheet not analyzed

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: PCB_Schaltplan_RFSOC_RFSOC_Supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause as above.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000841: Output file does not exist — RFSOC PCB not analyzed

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: PCB_Schaltplan_RFSOC_RFSOC.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The M19O2 PCB outputs that do exist are for DHT22_pcb and M19O2_Wiring_Simplified. No RFSOC PCB output is present.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000842: Output file does not exist — no gerber outputs exist at all for M19O2

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: PCB_Schaltplan_RFSOC_Gerber_v1.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The gerber results directory for M19O2 does not exist. No RFSOC gerber outputs are present.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000843: Output file does not exist — no gerber outputs exist at all for M19O2

- **Status**: promoted
- **Analyzer**: gerber
- **Source**: PCB_Schaltplan_RFSOC_Gerber_v2.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same root cause as above.
  (signal_analysis)

### Suggestions
(none)

---
