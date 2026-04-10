# Findings: Pong-1976 / pong_pong

## FND-00001116: Crystal circuit detection correct: Y1 2MHz with 30pF load caps, CL_eff=18pF; LM7805 classified as 'LDO' topology — it is a standard linear regulator; VCC PWR_FLAG warning correct — VCC is external ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: pong.kicad_sch
- **Created**: 2026-03-23

### Correct
- Correctly identifies Y1 with C1 and C4 (both 30pF) as crystal load caps, calculates effective load capacitance of 18pF and reports it is within typical range.
- VCC connects directly to the battery connector J3 and LM7805 input. No PWR_FLAG symbol present. Warning is accurate for ERC purposes.
- R7 (330Ω), R8 (220Ω), R9 (1.2kΩ) form a resistor mixing network for video signal output. Two divider relationships correctly identified with ratios 0.40 and 0.155.
- 4 ICs on VCC rail identified; +5V has LM7805 output regulator. Decoupling coverage observations (has bulk 100µF + bypass 0.1µF on VCC, only bypass on +5V) are accurate.

### Incorrect
- LM7805 is a fixed positive linear regulator with ~2V dropout (not an LDO, which typically has <0.5V dropout). The analyzer categorizes it as 'LDO' which is technically incorrect. Should be 'linear' or 'series_linear'.
  (signal_analysis)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001117: PCB stats correct: 51 footprints (46 THT components + 4 mounting holes + 1 logo), 48 nets, fully routed

- **Status**: new
- **Analyzer**: pcb
- **Source**: pong.kicad_pcb
- **Created**: 2026-03-23

### Correct
- tht_count=46 matches schematic exactly. Extra 5 footprints are HOLE1-4 (MountingHole_3.2mm_M3) + REFLOGO (OSHW logo). GND copper fill on B.Cu correctly identified. Net count 48 matches schematic.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
