# Findings: koalo/KiCad_PCBmerge / example_led_led

## FND-00000746: KiCad 5 legacy schematic parsed correctly: 4 components (LED, R, 2 connectors), 5 nets

- **Status**: new
- **Analyzer**: schematic
- **Source**: example_led_led.sch.json
- **Created**: 2026-03-23

### Correct
- file_version=4, kicad_version='5 (legacy)', sheets_parsed=1. Components and types correct. Power rail 'Earth' (legacy GND symbol name) correctly identified.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000747: KiCad 5 legacy PCB correctly parsed: 4 footprints, 1 copper layer used, 6 tracks; kicad_version reported as 'unknown' for KiCad 5 PCB files

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: example_led_led.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- kicad_version='unknown' for KiCad5 format (file_version=4) is reasonable. Component split (2 SMD, 2 THT) and routing completeness accurate.

### Incorrect
- The file_version is 4 (KiCad 5 legacy format), but kicad_version is 'unknown' instead of '5 (legacy)'. The schematic analyzer correctly reports '5 (legacy)' for .sch files, but the PCB analyzer does not apply the same version inference for .kicad_pcb with file_version=4.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000748: Power supply schematic: 5 components (LDO U1, 2 caps, barrel jack, pin header) correctly extracted

- **Status**: new
- **Analyzer**: schematic
- **Source**: example_power_power.sch.json
- **Created**: 2026-03-23

### Correct
- Component types: 2 connectors, 2 capacitors, 1 IC. Power rail 'Earth' detected. All 4 nets extracted correctly.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00000749: Power PCB: 5 footprints (3 SMD, 2 THT), 1 copper layer, 12 tracks, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: example_power_power.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
- Statistics match the schematic component count. Single-layer routing with zone is consistent with a simple power supply board.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
