# Findings: JINISHAM/Breadboard-power-supply_KiCad / Breadboard power supply

## FND-00000416: R1+C3 incorrectly detected as RC low-pass filter; they are LM317 feedback and output bypass components; Design observation incorrectly reports U1 (LM7805) is missing input and output capacitors; Po...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: Breadboard power supply.kicad_sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- R1 (330Ω) is the LM317 feedback resistor between the output rail (3.3V) and the ADJ node (__unnamed_0). C3 (1µF) is a bypass capacitor from the 3.3V output rail to GND. They are not in a series RC filter topology. The RC filter detector identified the path ADJ→3.3V through R1 with C3 on 3.3V-to-GND as a low-pass filter (482 Hz), but this is a voltage regulator feedback network, not an RC filter. The cutoff frequency calculation is also meaningless in this context.
  (signal_analysis)
- The design_observations section reports U1 (LM7805) as missing caps on its input rail '12V' and output rail '5V'. However, C1 (10µF) is connected between the 12V rail and GND (decoupling the LM7805 input), and C2 (0.1µF) is connected between the 5V rail and GND (decoupling the LM7805 output). The inrush_analysis section correctly identifies both caps. The design_observations detector is incorrectly ignoring these caps when generating the missing_caps warning for U1.
  (signal_analysis)
- In the net_classification section under design_analysis, the nets '3.3 V', '5V', '12 V', and '12V' are all classified as 'signal'. These are voltage regulator output/input rails — named power nets that should be classified as 'power'. Only GND and PWR_OUT_* nets are correctly classified. The named voltage nets (3.3 V, 5V, 12 V, 12V) are power supply rails driven by linear regulators.
  (design_analysis)
- The pwr_flag_warnings array reports that GND has 'power_in pins but no power_out or PWR_FLAG'. However, the schematic contains 4 GND power symbols (power:GND) which connect to GND via their power_in pin. More critically, there are 3 PWR_FLAG symbols (at positions y=66.04, y=93.98, y=41.91) all on nets that connect to GND through the power network. The PWR_FLAG symbols in the schematic explicitly exist to silence ERC on GND. The warning should not be generated.
  (pwr_flag_warnings)
- The assembly_complexity section reports 8 SMD components and 9 THT components. All passives (C1/C2/C3 as C_Disc, R1/R2/R3 as R_Axial DIN0204), LED (D1 as LED_D5.0mm), regulators (U1/U2 as TO-220-3_Vertical), and connectors (PinHeaders, TerminalBlocks, BarrelJack) use THT footprints. The switch S1 uses a digikey SMD-style footprint. At most 1 component could be classified as SMD. The SMD count of 8 is a significant miscount likely caused by the footprint pattern matcher incorrectly flagging connector and other THT footprints as SMD.
  (assembly_complexity)
- The design_observations reports U2 (LM317) as missing a cap on input rail '12 V'. While the output cap (C3 on 3.3V) is acknowledged in the inrush section, the input cap for '12 V' is genuinely absent in the schematic. The input bypass cap for the LM317 is correctly missing — however the design_observations also flags the output ('3.3 V') as missing a cap, which is wrong since C3 (1µF) is on the 3.3V rail. This is a partial false positive: the input cap warning for U2 is correct, but reporting the output ('3.3 V') as missing a cap is incorrect given C3 exists.
  (signal_analysis)

### Missed
(none)

### Suggestions
- Fix: Power rails '3.3 V', '5V', '12 V', '12V' are classified as 'signal' nets instead of 'power' in net_classification

---
