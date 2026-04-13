# Findings: meowmeowahr/KevinbotV3-KiCAD / P2 Kevinbot Board

## FND-00000199: Parallax Propeller 2 based robot controller board with voltage monitoring (TMUX1511 analog mux), DC motor drivers, USB-C, multiple I/O connectors, fuses, and PSU sub-sheet with LM25145 synchronous buck converter. Good voltage divider and RC filter detection; PSU analysis finds the switching regulator. Many connectors and test points correctly classified.

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: P2 Kevinbot Board.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Voltage divider R18/R19 (120K/10K, ratio=0.077) correctly detected for voltage monitoring channel C on VMOUT_C_RAW net
- Voltage divider R14/R15 (180K/10K, ratio=0.053) correctly detected for voltage monitoring channel A on VMOUT_A_RAW net
- RC low-pass filter R55/C20 (887R/10pF, fc=17.9MHz) correctly detected for high-frequency noise filtering
- RC low-pass filters R54/C18 and R53/C18 (20k/2.2uF, fc=3.62Hz) correctly detected as slow analog averaging filters
- Feedback divider R59/R58 (2.15k/3.4k) correctly identified as feedback network for the PSU regulator
- 26 connectors, 7 test points, 4 fuses, 6 LEDs correctly classified
- Decoupling on +5V rail with 20uF across C22/C23 (10uF each) correctly detected
- Power rails +5V, +5VUSB, VBUS, VCCIO, GND all correctly identified
- Buzzer correctly classified as component type 'buzzer'
- Ferrite bead correctly classified as component type 'ferrite_bead'

### Incorrect
- Voltage divider R59/R58 (2.15k/3.4k, ratio=0.613) is actually the feedback divider for the LM25145 buck converter. With Vref=0.6V, Vout=0.6/0.613=0.979V which is clearly wrong. The feedback_divider entry says R56 (18k) connects at the midpoint, suggesting a more complex 3-resistor divider. The estimated_vout of 0.979V is incorrect; the actual output should be 5V.
  (signal_analysis.power_regulators)
- VBUS decoupling shows only C1 (10nF) which seems low but may be correct for the specific design context
  (signal_analysis.decoupling_analysis)

### Missed
(none)

### Suggestions
- When a 3-resistor feedback network is present (R56 in series with R59/R58 divider), calculate Vout considering the full network topology rather than just the bottom two resistors
- The LM25145 Vref is 0.6V; with R56 (18k) + R59 (2.15k) as top and R58 (3.4k) as bottom, Vout = 0.6 * (18k+2.15k+3.4k)/3.4k = 4.15V, closer to 5V target

---

## FND-00000200: PSU sub-sheet for Kevinbot with LM25145 synchronous buck converter, voltage monitoring via TMUX1511 analog mux with precision resistor dividers, and multiple fuses for power distribution. Good detection of all key circuits as standalone sub-sheet.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: psu.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- U15 (LM25145RGYR) correctly identified as switching regulator with inductor L1, bootstrap cap, output=+5V
- 4 voltage dividers correctly detected for the TMUX1511 analog mux channels
- 5 RC filters detected for voltage monitoring averaging and EMI suppression
- 2 feedback networks identified connecting to the LM25145 FB pin
- 18 resistors, 12 capacitors, 3 fuses correctly counted in sub-sheet

### Incorrect
- U15 estimated_vout is 0.979V which is wrong; the LM25145 output is +5V. The 3-resistor feedback network (R56+R59 top, R58 bottom) is not correctly analyzed
  (signal_analysis.power_regulators)

### Missed
(none)

### Suggestions
- Handle multi-resistor feedback networks where series resistors (R56 18k in series with R59 2.15k) form the upper arm of the divider

---
