# Findings: Mechanical-Keyboard-PCBs / 60% Pcb_60_Pcb

## ?: 60% mechanical keyboard switch matrix with 68 keys across 5 rows and 15 columns, using Cherry MX-compatible switches with per-key diodes and LED resistors. Analyzer correctly detected the key matrix but misclassified MX switch components as relays.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: 60% Pcb_matrix.kicad_sch.json

### Correct
- Key matrix correctly detected as 5 rows x 15 columns with 68 estimated keys, matching the 68 diodes in the schematic
- Row nets ROW0-ROW4 and column nets COL0-COL14 correctly identified by net name pattern
- 68 diodes (D1-D68) correctly classified as diode type for anti-ghosting
- 68 resistors (R1-R68) correctly classified - these are per-key LED current-limiting resistors
- +5V power rail correctly identified as the only power rail (for LED supply)

### Incorrect
- 91 MX key switches (K_ESC1, K_#1, K_TAB1, K_CAPS1, K_ENTER1, etc.) are classified as 'relay' type. These are MX_Alps_Hybrids library symbols representing Cherry MX mechanical keyboard switches, not relays. They should be classified as 'switch' or 'key_switch'
  (statistics.component_types)
- key_matrices shows switches_on_matrix=0 despite 91 switch symbols being present. The MX switches are the matrix switches but are not recognized because they are classified as relays instead of switches
  (signal_analysis.key_matrices)

### Missed
(none)

### Suggestions
- Add MX_Alps_Hybrids library symbols (MX-1U, MX-1.25U, MX-1.5U, MX-1.75U, MX-2U, MX-2.25U, MX-2.75U, MX-6.25U, MX-7U, MX-ISO) to the switch/key_switch classification instead of relay
- When key_matrices detection finds row/col nets, cross-reference with components on those nets to populate switches_on_matrix

---
