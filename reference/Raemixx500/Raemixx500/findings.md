# Findings: Raemixx500 / Raemixx500

## FND-00001207: TC9 (Device:C_Variable, variable capacitor) misclassified as 'transformer'; Y9 (32768 Hz RTC crystal) not detected in crystal_circuits for rtc.sch standalone analysis

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: rtc.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- TC9 is a 6.8-45pF trimmer capacitor with lib_id Device:C_Variable. The analyzer classifies it as 'transformer', inflating the transformer count to 1 in rtc.sch and in the top-level Raemixx500.sch.json statistics. It should be classified as 'capacitor'.
  (signal_analysis)

### Missed
- Y9 (Device:Crystal_GND2, 32768 Hz) has empty pins[] in the standalone rtc.sch output, so crystal circuit detection fails. The hierarchical analysis (Raemixx500.sch.json) does detect Y9 correctly with 3 pins. This is a KiCad5 legacy sub-sheet pin-loading bug affecting detectors in per-sheet analysis.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001208: CN8 (Amiga power connector, lib amipower:Amiga_Power_Conn) misclassified as 'capacitor'; power.sch sub-sheet contains 13 duplicate component refs from other sheets (CPU, clock)

- **Status**: new
- **Analyzer**: schematic
- **Source**: power.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
- CN8 has value 'POWER' and footprint 'Raemixx500:DS215+DIN8_COMBO'. Its lib_id is 'amipower:Amiga_Power_Conn' — a connector — but it is typed 'capacitor' in both BOM and component list. Should be 'connector'.
  (signal_analysis)
- When analyzed standalone, power.sch reports U1 (68000D CPU), U2 (FAT AGNUS), U5 (GARY), U10-U13 (bus buffers), X1 (oscillator), etc. These belong to the CPU/clock sheets and appear in power.sch only because of KiCad 5 legacy flat-file cross-reference. This causes inflated component counts (51 vs ~25 real power components) and wrong crystal/IC type reporting in that sheet.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001209: V0/V1/V2 logo/silkscreen symbols (void:Void) misclassified as 'varistor'; DRAM memory interface (RAS/CAS, 8x XX4256 chips) not detected in memory_interfaces; RF T-match false positive: EMI filter c...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Raemixx500.sch.json
- **Created**: 2026-03-24

### Correct
- The main Raemixx500.sch.json correctly parses 14 sheets, identifies all 14 sheet files, and aggregates 372 unique components with correct power rails (+12V, -12V, VCC, GND, GNDA, VDDA, VAC, VDC). The hierarchical output is authoritative and accurate.
- Both crystal circuits are found in the main output with correct load cap associations. Y9 frequency parsed as 32768 Hz. X1 frequency is null (oscillator module, not raw crystal — acceptable).

### Incorrect
- V0 (OSHW_LOGO), V1 (KICAD_LOGO), V2 (PROJ_LOGO) are graphical logos placed with 'void:Void' library symbols. They are classified as 'varistor' and appear in the BOM, inflating the component count by 3. They should be excluded from BOM or typed as 'mechanical'.
  (signal_analysis)
- rf_matching reports C800 (10n decoupling cap) with CN8 (power connector) and LF1/LF99 (line filters) as a T-match antenna network. This is clearly a false positive — the L-C topology heuristic is triggered by an AC line filter, not an RF matching circuit.
  (signal_analysis)

### Missed
- The RAM sheet has 8x XX4256 DRAM chips with RAS/CAS control signals (~RAS0, ~RAS1, ~CASL, ~CASU). The memory_interfaces array is empty in all outputs, including the hierarchical analysis. The analyzer does not identify DRAM interfaces on this design.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001210: 5 JFET/BJT transistors present but transistor_circuits[] is empty in audio.sch

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: audio.sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- audio.sch has 5 transistors: Q321/Q331 (MPF102 NJFET), Q931/Q921 (MMBFJ113 NJFET), Q301 (2N3906 PNP BJT). The transistor_circuits detector finds 0 entries. Likely due to empty pins on some of these components in the sub-sheet parse (12 components have empty pins in audio.sch).
  (signal_analysis)

### Suggestions
(none)

---

## FND-00001211: PCB statistics correctly parsed: 372 footprints, 340 THT, 10 SMD, 2-layer, fully routed; 189 courtyard overlaps reported — mostly false positives for a THT retro board with intentional tight placem...

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: Raemixx500.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- Board dimensions 365.76x254mm, 11735 track segments, 902 vias, 37 zones, 0 unrouted nets. GND and GNDA copper pours detected with via stitching. Power net class 'Power1.5mm' (1.5mm trace width) correctly identified.
- HY1 (-46mm), U40 (-15mm), P1 (-8.65mm), CN3/CN4 (-7.9mm), CN10 (-7.64mm) all have negative clearance, correctly indicating connectors designed to overhang the board edge (e.g., Amiga bus expansion slot connector). This is intentional and correctly flagged.

### Incorrect
- The Amiga 500 PCB is a dense THT design. Large overlap areas (up to 199mm²) between standard DIP ICs and their neighboring decoupling caps are expected and intentional. KiCad 5 courtyard definitions for THT footprints are often very conservative or rectangular, producing false overlaps for non-conflicting placements. The overlap count of 189 is likely substantially inflated.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---
