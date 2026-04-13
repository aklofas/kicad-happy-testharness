# Findings: Fescron/2ch-4-20mA-converter / hardware_1ch-4-20mA

## FND-00000313: Current-sense amplifier circuit not detected for U1 (LMP8640) with shunt R2; Decoupling observation incorrectly reports VDDA has no bypass capacitor

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: hardware_1ch-4-20mA_1ch-4-20mA.sch.json
- **Created**: 2026-03-23

### Correct
(none)

### Incorrect
- The design_observations entry for U1 (LMP8640) lists VDDA in rails_without_caps and rails_with_caps as empty. However, C1 (100nF) is present and its pin 2 is connected to VDDA (confirmed in the nets section: VDDA net includes C1 pin 2). R3 (0Ω jumper) is placed in series between C1 and GNDA, so C1 is effectively bypassing VDDA to GNDA. The analyzer failed to recognize C1 as a decoupling capacitor on VDDA, likely because the intermediate unnamed net (__unnamed_3) connecting C1 pin 1 through R3 to GNDA breaks the direct VDDA→cap→GND topology the detector expects.
  (signal_analysis)

### Missed
- U1 is a TI LMP8640 high-side current shunt monitor (lib: Amplifier_Current:LMP8640). R2 (4.99Ω) is the shunt resistor connected across U1's + (pin 3) and - (pin 4) differential inputs. This is a canonical current-sense circuit — the IC is explicitly classed as a current amplifier and the shunt is directly across its sense inputs. The analyzer reports 0 current_sense detections. The subcircuits section correctly identifies U1 with neighbors R1, R2, JP1, J2 but does not classify the function. A current_sense detection should be generated for U1/R2.
  (signal_analysis)

### Suggestions
(none)

---
