# Findings: Bastardkb/Charybdis-nano-tent-glow / glow

## FND-00000427: Spurious third LED chain detected (D6 alone, chain_length=1) due to parallel chain topology not handled correctly; Chain 1 reports first_led=D5 but the second parallel chain starts at D6; Total est...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: glow_glow.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The schematic has two physically parallel LED chains: Chain A starts at D5 (DIN on net __unnamed_12) and Chain B starts at D6 (DIN also on net __unnamed_12). Both D5 and D6 receive their data input from the same net (fed via R1/R2 from the Din global label at J3 pin 3). The detected Chain 1 is labeled first_led=D5 but its component list (D8, D34, D22, D24, D26, D38, D40, D42, D47, D49, D51, D55, D57, D60) corresponds to the successors of D6 in Chain B — the correct first_led for Chain 1 should be D6. Chain 0 and Chain 1 also each include exactly one LED from each physical pair (cross-selecting between chain A and chain B at each hop), which is an artifact of the greedy path-tracing through ambiguous fork nodes.
- The correct design is two 15-LED chains at 60 mA/LED each = 2 × 900 mA = 1800 mA total. Because a spurious third chain (D6 alone at 60 mA) is generated, the sum of estimated_current_mA across all three detected chains is 900 + 900 + 60 = 1860 mA. This 60 mA overcount equals one extra LED.

### Incorrect
- The schematic contains two 15-LED parallel SK6812MINI chains sharing the same data input net (__unnamed_12). Each inter-LED data net has exactly two DOUT drivers and two DIN receivers (one LED from each chain). The analyzer traces two valid 15-LED chains but then finds D6 unaccounted for (because the chain traces picked up D6's chain-B successors under chain 1's trace rather than tracing from D6), and emits a spurious chain of length 1 for D6. D6 is the head of the second physical chain. The result is 3 chains reported (15+15+1) instead of the correct 2 chains (15+15), and a D6 LED is double-counted: it appears in Chain 2 and implicitly traced in Chain 1's path (D8, D34, D22... are D6's chain-B successors). Total LEDs across chains is 31 instead of 30.
  (signal_analysis)

### Missed
- C1 and C2 are unpolarized 1206 capacitors connected directly across the Vcc/Gnd power rails that supply all 30 SK6812MINI LED VDDs. The ic_pin_analysis correctly identifies has_decoupling_cap=true at the connector J5 and J3 Vcc pins, citing C1 and C2 as decoupling caps. However, the top-level signal_analysis.decoupling_analysis array is empty — no summary entry is generated for the overall power rail decoupling. A decoupling analysis entry for the Vcc rail with 30 power consumers would be expected.
  (signal_analysis)

### Suggestions
(none)

---
