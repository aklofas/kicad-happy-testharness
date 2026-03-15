# Testing Status

Operational log of batch testing progress, corpus maintenance, and open issues.

Last updated: 2026-03-15

---

## Corpus summary

| Metric | Count |
|--------|------:|
| Total repos in repos.md | 1,052 |
| Checked out in repos/ | 1,044 |
| Repos with baselines | 1,034 |
| Repos with assertions | 952 |
| Total assertion files | 5,437 |
| Total assertions | 55,272 |
| Assertion pass rate | 98.6% |
| Layer 3 reviewed | 60+ |

---

## Completed batches

### Batch 1 — Well-known hardware projects (10 repos)

All tested with reference data, assertions, and/or findings:
hackrf, splitflap, ubertooth, bitaxe, moteus, Voron-Hardware, OnBoard,
HadesFCS, icebreaker, OtterCastAudioV2

### Batch 2 — High-quality designs (6 of 10 tested)

Tested: ESP32-POE, OSHW-reCamera-Series, tomu-hardware, Otter-Iron-PRO,
greatfet-hardware, analog-toolkit

Not yet tested: acorn-robot-electronics

### Batch 3 — Broad corpus (96 repos, 2026-03-15)

96 repos from `0x42` through `Capitulo118` processed with Layer 1-3 testing.
2,449 assertions seeded, 0 errors.

### Batch 4 — Priority top 50 (2026-03-15)

50 repos from priority.md top 50 processed with Layer 1-2 testing:
tb303_vcf_kicad_project_gerbers, modular-psu, KiDiff, slab-pcb,
NUS-CPU-03-Nintendo-64-Motherboard, Duplicanator-Scart-Duplicator,
SparkFun_XRP_Controller, hw_projects, commodorelcd, Neo6502pc,
Castor_and_Pollux, ESP32-SBC-FabGL, KICAD, OtterCam-s3,
ESP32-S3-DevKit-LiPo, keyboard, PCB-Design, iMX8MP-SOM-EVB,
Cosmos-Keyboard-PCBs, SparkFun_IoT_RedBoard-RP2350, kuro65,
TPA3255_ClassD_PBTL, explorer, LAEMP-Prism, HandAssemble_Pmod,
pcb, Sichergo, kicad, geiger-counter, PCB-Modular-Multi-Protocol-Hub,
bms-c1, ms60, Gas-sens_Rs-485, Ventilator, STAN, DATALOGGER02,
KevinbotV3-KiCAD, DIN_41612_Backplane, ESP32-PRO, dib-mio-afe3,
FunBox, robocup-pcb, SparkFun_IoT_Node_LoRaWAN, fidget,
Mechanical-Keyboard-PCBs, RISCBoy, SparkFun_GNSS_Flex_Breakout,
psylink, DIY-LAPTOP, + 15 more SparkFun/misc repos.
Layer 3 reviews in progress on 19 repos (27 files).

---

## Purge log

### 2026-03-15 — Removed 87 repos

Repos removed from repos.md and all local data after audit:

- **18 Eagle-only** — Adafruit, SparkFun, and others in Eagle XML format
  misidentified as KiCad (discover.py filters these via header check)
- **14 Tools/libraries** — KiCad parsers, generators, plugins with example
  PCBs but no real designs (CopperForge, KiParse, PcbDraw, etc.)
- **22 PCB-only** — Repos with `.kicad_pcb` but no schematics
  (keyboard plates, templates, footprint-only repos)
- **33 Tiny** — Schematics with <3 components (templates, art pieces,
  rulers, test patterns)

---

## Open issues

11 open issues (0 HIGH, 9 MEDIUM, 2 LOW). See ISSUES.md for details.

### MEDIUM (pre-existing)
- **KH-078** — `build_net_map()` unhashable list crash
- **KH-080** — Power symbol despite in_bom=yes
- **KH-081** — Current sense FPs on Ethernet termination
- **KH-082** — TVS IC protection devices not detected
- **KH-085** — RF chain keyword lists too narrow
- **KH-087** — Switching regulator output_rail missing
- **KH-097** — CSYNC nets classified as chip_select
- **KH-098** — Flyback diode drain-to-supply not detected
- **KH-099** — I2S audio bus misidentified as I2C

### LOW
- **KH-090** — LDO inverting flag incorrect
- **KH-100** — WiFi modules classified as power regulators

---

## Issue fix history

64 analyzer issues fixed across 7 batches. Full details in FIXED.md.

| Batch | Date | Issues fixed | Highlights |
|------:|------|-------------:|------------|
| 1 | 2026-03-13 | 14 | Initial triage — component classification, net building, power detection |
| 2 | 2026-03-13 | 13 | Signal detectors — voltage dividers, regulators, filters, bus protocols |
| 3 | 2026-03-14 | 11 | Legacy format — KiCad 5 .sch parsing, wire-to-pin matching |
| 4 | 2026-03-14 | 6 | Edge cases — hierarchical sheets, multi-instance sub-sheets |
| 5 | 2026-03-15 | 8 | Crystal detection, Ethernet linkage, over-fitting fixes |
| 6 | 2026-03-15 | 6 | Eagle import, lib_name mismatch, regulator FPs, SPI/I2C confusion |
| 7 | 2026-03-15 | 6 | Component classification prefix bugs — CR/T/VR/RV/FIL overrides, LED substring fix |
