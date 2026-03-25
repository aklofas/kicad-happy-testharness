# Findings: Dual-pos-neg-5V-Supply-from-USB-power / KiCAD_files_LT193n_+-5V_Supply

## FND-00000484: Component references correctly resolved from sheet instance table (C1→C201, U1→U201, etc.); U201 (LT1930ES5-TRMPBF) pin mapping fully correct: SW pin 1, GND pin 2, FB pin 3, *SHDN pin 4, VIN pin 5;...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCAD_files_LT1930_+5V_supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The source file uses local annotation (C1, C2, ... U1, R1, R2, ...) in its symbol_instances section, but the hierarchical parent (LT193n_+-5V_Supply.kicad_sch) remaps these to the 200-series sheet namespace (C201, C202, U201, R201, etc.). The analyzer correctly reads the symbol_instances table and reports all references with their sheet-qualified numbers (C201–C205, D201–D202, J202, L201–L202, R201–R204, U201). All 15 components are correctly enumerated with matching values.
- The ic_pin_analysis for U201 correctly maps all five pins. Pin 1 (SW) connects to L201 pin 2 and C203 pin 1 (switch node). Pin 2 (GND) to Earth rail with decoupling caps C201/C202/C204/C205. Pin 3 (FB) connects to R201 pin 2 and R202 pin 1 (feedback divider between +5V_unfiltered_output and Earth). Pin 4 (*SHDN) connects to C205, D202, R204. Pin 5 (VIN) connects to +5V_input_+side with L201 pin 3, D202 pin 1 (K), R204. All net assignments verified against source wiring.
- The power_regulators detector identifies U201 as a 'switching' topology regulator using L201 (CLS62NP-100NC) as the coupled inductor, with input_rail '+5V_input_+side' and output_rail '__unnamed_0' (the switch node net connecting D201 anode, L201 pin 1, C203 pin 2). This is correct: the LT1930 is a boost converter and the CLS62NP-100NC is a coupled inductor (EMI filter + inductor combined). L202 (10uH) is the output filter choke between +5V_unfiltered_output and +5V_filtered_output.

### Incorrect
- The rc_filters detector reports R204 (30k) + C205 (68nF) as an RC network with cutoff 78.02 Hz. In the LT1930 circuit, R204 (30k) is a pull-up from VIN (+5V_input_+side) to the *SHDN pin, and C205 (68nF) is the soft-start/enable capacitor on *SHDN. D202 (1N4148) completes the soft-start reset path. This RC combination controls the soft-start timing (τ ≈ 2.04 ms), not a signal filter. The 'input_net' and 'output_net' assignments ('__unnamed_3' and '+5V_input_+side') are also misleading — the RC charges the *SHDN pin from 0V to VSHDN_thresh. The detection is not technically wrong (it is an RC circuit) but the functional classification as a 'filter' is misleading for a regulator enable/soft-start network.
  (signal_analysis)
- The 'regulator_caps' observation reports missing_caps for both input ('+5V_input_+side') and output ('__unnamed_0'). In reality, C201 (2.2uF) is on +5V_input_+side (VIN, pin 5) to Earth — this is the VIN decoupling cap and is correctly identified in the decoupling_caps for VIN. The 'output' cap is reported missing on '__unnamed_0' (the switch node), but the actual output cap C202 (10uF) is on +5V_unfiltered_output, not the switch node. The analyzer is checking the wrong net for the output cap — the switch node (__unnamed_0) is not the output rail; +5V_unfiltered_output is the boost output. This is a systematic error in how the regulator output net is assigned.
  (signal_analysis)
- In signal_analysis.power_regulators, U201's output_rail is listed as '__unnamed_0'. This is the anode side of the Schottky diode D201 (D201 pin 2 / A, L201 pin 1, C203 pin 2) — the inductor switching node, not the regulator output. The true DC output of the boost converter is '+5V_unfiltered_output' (D201 cathode / K). The analyzer is identifying the inductor-adjacent net as the 'output' rather than tracing through the rectifying diode to the actual output rail.
  (signal_analysis)

### Missed
- L202 (10uH) connects between +5V_unfiltered_output (L202 pin 1) and +5V_filtered_output (L202 pin 2). C204 (30uF) is on +5V_filtered_output (C204 pin 1) to Earth (C204 pin 2). This forms a classic LC post-filter on the boost converter output. The lc_filters list in signal_analysis is empty for this file. The analyzer found LC filters in LT1931_-5V_supply.kicad_sch (L302+C303 and L302+C306) but missed the equivalent L202+C204 in LT1930_+5V_supply.kicad_sch. This is because L202 (Device:L style, 2-pin) shares no net directly with C204 — they share '+5V_filtered_output' — and the LC filter detector may require a shared net between the inductor output pin and capacitor pin 1, which is satisfied here. The failure may relate to how the Inductor_SMD L_Taiyo-Yuden part's pin type ('input') differs from CLS62NP-100NC's 'unspecified' pins.
  (signal_analysis)
- R201 (243K) connects from +5V_unfiltered_output (pin 1) to the FB node (pin 2). R202 (82.5K) connects from the FB node (pin 1) to Earth (pin 2). This is a classic resistive feedback divider setting the output voltage of U201. The voltage_dividers list is empty. The analyzer does detect these resistors in the ic_pin_analysis for U201 pin 3 (FB), correctly noting R201 as 'pull-up' to '+5V_unfiltered_output' and R202 as 'series' to Earth, but does not synthesize this into a voltage_divider signal_analysis entry. The feedback_networks list is also empty.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000485: Component references correctly resolved from sheet instance table (C1→C301, U1→U301, R6→R306, C6→C306, etc.); U301 (LT1931E) pin mapping correct: SW pin 1, GND pin 2, NFB pin 3, *SHDN pin 4, VIN pi...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCAD_files_LT1931_-5V_supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The source file uses local annotations (C1–C4, C6, D1, D2, J1–J3, L1, L2, R1–R3, R6, U1) in symbol_instances. The hierarchical parent remaps these to 300-series references (C301–C304, C306, D301, D302, J302, L301, L302, R301–R303, R306, U301). Note C5 is absent from the local list (only C6 is present for 30uF), which the analyzer handles correctly by including C306 in the output. All 15 components are enumerated with correct values.
- The ic_pin_analysis for U301 correctly resolves all pins. Pin 1 (SW) → L301 pin 2 and C302 pin 1 (switch node). Pin 2 (GND) → Earth with capacitors C301/C303/C304/C306. Pin 3 (NFB) → R301 pin 2 and R302 pin 1 (feedback divider). Pin 4 (*SHDN) → R303 pin 2, D302 pin 2 (A), C304 pin 1. Pin 5 (VIN) → +5V_input_-side with L301 pin 3, D302 pin 1 (K), C301 pin 1. The LT1931 uses 'NFB' (negative feedback) instead of 'FB', which the analyzer correctly reports from the symbol definition.
- power_regulators correctly identifies U301 (LT1931E) as 'switching' topology with L301 (CLS62NP-100NC) as the inductor, input_rail '+5V_input_-side', and output_rail '__unnamed_0'. This matches the Cuk/inverting topology of the LT1931 which takes positive input and produces negative output. The output_rail assignment has the same issue as U201 (switch node rather than -5V output rail) but is internally consistent.
- The lc_filters list correctly finds two LC pairs both involving L302 (10uH): one with C303 (22uF) sharing net '-5V_unfiltered_output' (resonant at 10.73 kHz), and one with C306 (30uF) sharing net '-5V_out_filtered' (resonant at 9.19 kHz). L302 is the output filter inductor (L302 pin 1 on -5V_unfiltered_output, pin 2 on -5V_out_filtered), and both capacitors connect to the respective nets. This is accurate.
- The LT1931 source has a title_block with title 'lT1391 -5v Supply' and company 'M C Nelson, PhD'. The analyzer correctly extracts both fields. Note the title contains a typo ('lT1391' vs LT1931) which the analyzer faithfully reproduces from the source.

### Incorrect
- The rc_filters entry shows R301 (29.4k) + C303 (22uF) as an RC network with 0.25 Hz cutoff. R301 is actually the upper resistor in the NFB feedback voltage divider (R301 from -5V_unfiltered_output to the NFB node, R302 10k from NFB to Earth). C303 is the output decoupling capacitor on -5V_unfiltered_output. These do share the '-5V_unfiltered_output' net, but their pairing as an RC filter is spurious. The actual feedback network consists of R301 and R302 around the NFB pin, which the analyzer captures in the ic_pin_analysis but not in a feedback_networks entry.
  (signal_analysis)
- Same issue as LT1930: U301's output_rail in power_regulators is '__unnamed_0' (the net connecting D301 anode / L301 pin 1 / C302 pin 2 — the inductor switch node), not '-5V_unfiltered_output' (D301 cathode, which is the DC output of the Cuk/inverting converter). The true output is on the D301 cathode side. Note: in the LT1931 Cuk topology the diode D301 (MBR0520 Schottky) rectifies the switching node to produce -5V at its cathode (which connects to Earth) — wait, on closer inspection the topology is: D301 cathode (K) is on Earth, D301 anode (A) is on __unnamed_0 (the switching node). This means the Cuk converter's energy transfer capacitor node is __unnamed_0, and the negative output is drawn from -5V_unfiltered_output via L301 pin 4. This is an unusual topology readout and the output_rail assignment as '__unnamed_0' is still not the regulated -5V output net.
  (signal_analysis)

### Missed
- R301 (29.4k) from -5V_unfiltered_output to NFB node, R302 (10k) from NFB node to Earth forms the output voltage setting divider for the LT1931 negative regulator. The voltage_dividers and feedback_networks lists are both empty. The ic_pin_analysis for U301 pin 3 (NFB) does report R301 and R302 as connected resistors, but no voltage_divider or feedback_network signal_analysis entry is generated. This mirrors the missed feedback divider detection in LT1930.
  (signal_analysis)
- The statistics.power_rails for LT1931_-5V_supply.kicad_sch lists only ['+5V_input_-side', 'Earth']. The nets '-5V_unfiltered_output' and '-5V_out_filtered' are named nets carrying the actual negative output voltage and appear in the nets section, but are classified as 'signal' in net_classification rather than 'power'. The global_label '-5V_filtered_output' (shape input) is present in the labels section. These should be recognized as power rails given the global_label declarations and named net conventions (they carry regulated supply voltages). The +5V side correctly lists '+5V_unfiltered_output' and '+5V_filtered_output' as power rails in LT1930.
  (signal_analysis)

### Suggestions
(none)

---

## FND-00000486: Top-level sheet aggregates all 34 components from both sub-sheets and 4 root-level connectors (J101, J102, JP101, JP102); JP101 and JP102 correctly classified as 'jumper' type, and power rails from...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: KiCAD_files_LT193n_+-5V_Supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
- The root sheet LT193n_+-5V_Supply.kicad_sch has J101 (705430001, 2-pin input connector), J102 (70543-0002, 3-pin output connector), JP101 and JP102 (Jumper_2_Open — selectability jumpers on the +5V and -5V sides), plus all 30 components from the two sub-sheets. The analyzer reports total_components=34 (4 root + 15 from LT1930 sheet + 15 from LT1931 sheet), which matches. BOM correctly aggregates duplicate values across sub-sheets (e.g. C203 and C302 both 1uF are listed together with quantity 2).
- JP101 and JP102 (Jumper:Jumper_2_Open) are correctly typed as 'jumper' in component_types (count 2). The statistics.power_rails correctly includes all 6 named power rails from the combined hierarchy: '+4_6.5V_input' (local label on J101/J102 input), '+5V_filtered_output', '+5V_input_+side', '+5V_input_-side', '+5V_unfiltered_output', and 'Earth'. JP101 pin 2 ('B') connects to +5V_input_+side and JP102 pin 2 ('B') connects to +5V_input_-side, acting as optional isolation jumpers for the two supply rails.
- The top-level aggregated output correctly identifies both U201 and U301 in the power_regulators list, each with their respective inductors (L201 and L301), input rails, and output rails. The two subcircuits are also correctly enumerated with their neighbor components.

### Incorrect
(none)

### Missed
- The global_label '-5V_filtered_output' (shape input) appears in the labels section of the LT1931 sub-sheet output and is also connected in the top-level via J102 pin 1 (the 3-pin output connector). The top-level power_rails list does not include '-5V_filtered_output' or '-5V_unfiltered_output'. These are active supply nets that exit the design to the output connector J102. This is consistent with the same omission in LT1931_-5V_supply.kicad_sch, confirming the analyzer does not classify negative voltage nets as power rails.
  (signal_analysis)

### Suggestions
(none)

---
