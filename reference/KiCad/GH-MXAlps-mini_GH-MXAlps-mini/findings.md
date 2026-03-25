# Findings: KiCad / GH-MXAlps-mini_GH-MXAlps-mini

## FND-00000681: Source file and output both missing — project not in test harness

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: 555_555.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- The repos/KiCad/ directory contains only keyboard-related projects (GH60-Alps, Matt3o, etc.). The projects 555, USB-C-PD, charge-controller, esp32-devkit, servo-driver, and wireless-speaker are not listed in repos.md and have never been checked out. No analyzer output exists to review.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000682: Source file and output both missing — project not in test harness

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: USB-C-PD_USB-C-PD.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- Same as above — this KiCad org project (likely from kicad.com demo library) is absent from repos.md. The path pattern repos/KiCad/<project> implies a GitHub org named 'KiCad' but no such repos are tracked.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000683: Source file and output both missing — project not in test harness

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: USB-C-PD_USB-C-PD.kicad_pcb.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
(none)

### Missed
- All 12 requested file pairs (6 schematics + 6 PCBs) are absent. The repos/KiCad directory exists but contains only keyboard PCBs from a different 'KiCad' folder that happens to share the name. None of the requested projects (555, USB-C-PD, charge-controller, esp32-devkit, servo-driver, wireless-speaker) are present anywhere on the filesystem.
  (signal_analysis)

### Suggestions
(none)

---
