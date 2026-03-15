# Testing Status

Operational log of batch testing progress, corpus maintenance, and open issues.

Last updated: 2026-03-15

---

## Corpus summary

| Metric | Count |
|--------|------:|
| Total repos in repos.md | 1,052 |
| Checked out in repos/ | 1,044 |
| Layer 1-3 tested (reference/) | 186 |
| Remaining to test | 858 |
| Total assertions seeded | 2,449+ |
| Assertion errors | 0 |

---

## Completed batches

### Batch 1 — Well-known hardware projects (10 repos)

All tested with reference data, assertions, and/or findings:
hackrf, splitflap, ubertooth, bitaxe, moteus, Voron-Hardware, OnBoard,
HadesFCS, icebreaker, OtterCastAudioV2

### Batch 2 — High-quality designs (6 of 10 tested)

Tested: ESP32-POE, OSHW-reCamera-Series, tomu-hardware, Otter-Iron-PRO,
greatfet-hardware, analog-toolkit

Not yet tested: modular-psu, bms-c1, Ventilator, acorn-robot-electronics

### Batch 3 — Broad corpus (96 repos, 2026-03-15)

96 repos from `0x42` through `Capitulo118` processed with Layer 1-3 testing.
2,449 assertions seeded, 0 errors.

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

7 open issues remain (all MEDIUM/LOW). See ISSUES.md for details.
- **KH-078** (MEDIUM) — `build_net_map()` unhashable list crash
- **KH-080** (MEDIUM) — Power symbol despite in_bom=yes
- **KH-081** (MEDIUM) — Current sense FPs on Ethernet termination
- **KH-082** (MEDIUM) — TVS IC protection devices not detected
- **KH-085** (MEDIUM) — RF chain keyword lists too narrow
- **KH-087** (MEDIUM) — Switching regulator output_rail missing
- **KH-090** (LOW) — LDO inverting flag incorrect

---

## Issue fix history

58 analyzer issues fixed across 6 batches. Full details in FIXED.md.

| Batch | Date | Issues fixed | Highlights |
|------:|------|-------------:|------------|
| 1 | 2026-03-13 | 14 | Initial triage — component classification, net building, power detection |
| 2 | 2026-03-13 | 13 | Signal detectors — voltage dividers, regulators, filters, bus protocols |
| 3 | 2026-03-14 | 11 | Legacy format — KiCad 5 .sch parsing, wire-to-pin matching |
| 4 | 2026-03-14 | 6 | Edge cases — hierarchical sheets, multi-instance sub-sheets |
| 5 | 2026-03-15 | 8 | Crystal detection, Ethernet linkage, over-fitting fixes |
| 6 | 2026-03-15 | 6 | Eagle import, lib_name mismatch, regulator FPs, SPI/I2C confusion |
