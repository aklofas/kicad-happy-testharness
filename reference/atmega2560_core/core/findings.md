# Findings: atmega2560_core / core

## FND-00001984: Unannotated schematic correctly handled — 8 unique references collapsed from 21 instances; Crystal Y? detected at 16MHz with correct frequency; Crystal load capacitors missed — load_caps=[] despite...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: core.sch.json
- **Created**: 2026-03-24

### Correct
- The source core.sch has 21 physical component instances but all references end in '?' (unannotated). The analyzer correctly reports 8 total_components corresponding to 8 unique reference prefixes: IC?, Y?, C?, R?, SW?, D?, P?, CON?. This is the expected behavior for an unannotated legacy KiCad 5 schematic.
- The 16MHz crystal is detected and its frequency correctly parsed at 16000000.0 Hz. The crystal is a standard HC-49S type for the ATmega2560.
- The design_observations correctly identifies SCL and SDA nets on IC? (ATmega2560) and correctly reports has_pullup=false. The schematic has no I2C pull-up resistors, which is a real design gap for a minimal ATmega2560 core schematic.

### Incorrect
- The source schematic has two 22pF capacitors (C?) connected as crystal load caps for the Y? crystal. However load_caps=[] is reported. Because the schematic is unannotated (all refs are '?'), the analyzer cannot reliably trace net connectivity from the crystal pins to the load capacitors, since all C? instances share a collapsed reference. This is an inherent limitation with unannotated schematics, but the result is a missed detection.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001985: KiCad 5 legacy PCB file (file_version=4) correctly parsed with zero footprints

- **Status**: new
- **Analyzer**: pcb
- **Source**: core.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The core.kicad_pcb is a KiCad 5 format PCB. The analyzer reports 0 footprints, 0 tracks, 0 vias — this appears to be a schematic-only project where the PCB layout was never started. The file is valid but empty. The kicad_version='unknown' for file_version=4 is expected as this is a very old format.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
