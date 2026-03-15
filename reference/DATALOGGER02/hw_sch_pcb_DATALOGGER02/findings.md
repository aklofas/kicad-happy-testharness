# Findings: DATALOGGER02 / hw_sch_pcb_DATALOGGER02

## FND-00000197: Universal battery-powered SD card datalogger (KiCad 9) with ATmega328, LoRa radio (RFM95), GPS, RTC, power management (LTC4041 + dual TPS631000 buck-boost), and extensive sensor support across multiple sheets. Excellent detection of feedback dividers, switching regulators, crystal circuits, and RF matching. Component count and sheet parsing are thorough.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_DATALOGGER02.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- Voltage divider R38/R39 (523k/100k) correctly detected feeding IC3 (LTC4041) RSTFB/BSTFB pin, ratio=0.161
- Voltage divider R44/R45 (511k/91k) correctly detected feeding U10 (TPS631000) FB pin, ratio=0.151
- Voltage divider R40/R41 (220k/100k) correctly detected feeding IC3 CAPFB pin, ratio=0.313
- U8 (MIC5504-1.8YM5-TR) correctly identified as LDO with input=+3.3V, output=+1V8, vout=1.8V
- U9 (TPS631000) correctly identified as switching regulator with inductor L3, feedback via R42/R43, estimated_vout=5.9V (close to 5V target)
- U10 (TPS631000) correctly identified as switching regulator with inductor L4, feedback via R44/R45
- Crystal Y6 (8MHz) correctly detected with load caps C3/C4 (15pF each), effective CL=10.5pF for ATmega328
- Crystal Y3 (32MHz) detected for LoRa radio module
- RC filter R2/C5 (4k7/100nF, fc=338.6Hz) on AREF correctly detected as analog reference filter
- RC filter R47/C56 (100R/1nF, fc=1.59MHz) correctly detected as anti-aliasing/EMI filter on DIO2
- 12 LC filters detected around LoRa radio matching network (L11 9n1 with C58/C59 3p3, resonant ~918MHz) - consistent with 868/915MHz ISM band operation
- Q2 (DMTH3002LPS) NMOS correctly identified as power switch driven by IC3 (LTC4041 battery backup manager)
- 4 feedback networks correctly identified connecting to IC3 and U10 feedback pins with is_feedback=true
- Decoupling on +3.3V rail correctly tallied at 48.1uF across C27 (1uF), C38 (100nF), C13 (47uF)

### Incorrect
- U9 (TPS631000) estimated_vout is 5.914V but the output rail is correctly labeled +5V. The vout estimate is slightly off from the nominal 5V, likely due to heuristic Vref=0.6V vs actual TPS631000 Vref=0.5V
  (signal_analysis.power_regulators)
- U10 (TPS631000) estimated_vout is 3.969V on the +3.3V rail; same Vref heuristic issue. With actual Vref=0.5V, output would be 0.5/0.151=3.31V which matches the +3.3V rail exactly
  (signal_analysis.power_regulators)
- RC filter R3/C8 (10k/4u7) classified as 'RC-network' with ground_net='+3.3V' which is wrong - this is a reset RC delay circuit, not a ground-referenced filter
  (signal_analysis.rc_filters)

### Missed
(none)

### Suggestions
- Add TPS631000 to known regulator Vref table (Vref=0.5V per datasheet) to improve voltage estimation accuracy
- Distinguish reset RC delay circuits (where both ends connect to power/signal, not ground) from standard RC filters

---

## FND-00000198: Power management sub-sheet of DATALOGGER02 with LTC4041 backup power manager, dual TPS631000 buck-boost converters, and MIC5504 LDO. Analyzer correctly parses this as a standalone sheet with all power regulators, feedback networks, and MOSFET switches detected consistently with the parent sheet analysis.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: hw_sch_pcb_Power_management.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- All 3 power regulators (U8 MIC5504, U9 TPS631000, U10 TPS631000) detected identically to parent sheet analysis
- 4 feedback networks correctly identified for IC3 (LTC4041) and U10 (TPS631000)
- Q2 (DMTH3002LPS) gate driven by IC3 correctly identified
- Decoupling on +3.3V (48.1uF), +1V8 (1uF), +5V (47.1uF) correctly tallied

### Incorrect
- U9/U10 estimated_vout values are off due to assumed Vref=0.6V instead of TPS631000's actual 0.5V
  (signal_analysis.power_regulators)
- Missing caps observation for U9/U10 claims Vdc input rail lacks decoupling, but input capacitors may be on the parent schematic or connected via hierarchical labels
  (signal_analysis.design_observations)

### Missed
(none)

### Suggestions
- When analyzing sub-sheets, consider that capacitors on shared power nets may be placed on sibling sheets

---
