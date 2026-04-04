# Findings: TPA3255_ClassD_PBTL / TPA3255PBTL

## FND-00000207: 48V-powered Class-D audio amplifier using TPA3255DDV in PBTL (parallel bridge-tied load) configuration with XL7015 buck converter, XLR audio I/O, LC output filters, and analog input signal conditioning. Analyzer performs well on opamp circuits and LC filters but has a significant voltage estimation error on the XL7015.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: TPA3255PBTL.kicad_sch.json
- **Created**: 2026-03-15

### Correct
- L78L12_SOT89 (U2) correctly identified as LDO producing +12V from +15V
- L78L33_SO8 (U3) correctly identified as LDO producing +3.3V from +12V
- XL7015 (U5) correctly identified as switching regulator with L1=100uH inductor and feedback divider R18=30k/R19=2.7k
- R18=30k/R19=2.7k voltage divider from +15V to FB correctly detected as feedback network for U5 XL7015
- 6 opamp circuits using AD8512 (U4, U6, U7) correctly detected with accurate gain calculations: U4.2 inverting gain=-1, U6.1 buffer, U4.1 inverting with variable gain via RV1
- R37=10k/R36=1k and R38=10k/R39=1k voltage dividers on Load1/Load2 feeding U7 comparator inputs correctly detected for speaker load monitoring
- R9=10k/R20=4.7k voltage divider from +12V feeding U6 non-inverting input correctly detected as reference voltage generator
- 14 LC filters correctly detected on Class-D output stage including L4=22uH/L5=22uH with various output capacitors
- 13 RC filters correctly detected in the audio signal path including input filtering and anti-aliasing
- Q1 DMP4015SK3 P-channel MOSFET correctly identified as reverse-polarity protection switch on 48V input with R1=10k/R2=10k gate resistors
- Q2, Q3 DMN10H220L N-channel MOSFETs correctly identified as LED drivers with load_type='led'
- Q4, Q5 DMN10H220L correctly identified as reset timing circuit (Q4 drives Q5 gate which pulls RST_ low)
- D1 TVS diode correctly identified as protection device on Power_IN
- D2 6.3V Zener diode correctly classified
- D4 Schottky diode correctly classified (flyback/catch diode for XL7015)
- Design observation correctly flags vout_net_mismatch: net name +15V implies 15V but estimated Vout is 7.267V

### Incorrect
- XL7015 (U5) estimated Vout=7.267V using assumed Vref=0.6V (heuristic), but XL7015 datasheet specifies Vref=1.25V. Correct calculation: Vout = 1.25 * (1 + 30k/2.7k) = 15.14V, which matches the +15V output net name.
  (signal_analysis.power_regulators)

### Missed
- TPA3255DDV (U1) Class-D audio amplifier speaker outputs through LC filters to J3 screw terminal and Load1/Load2 nets not detected as speaker/buzzer circuits
  (signal_analysis.buzzer_speaker_circuits)
- XLR audio input (J2 AC3FAH2-XLR) and output (J7 AC3FAH2-XLR, J6 AC3MAH-AU-PRE) connectors not detected as audio interface connectors
  (signal_analysis.bus_interfaces)
- No current sense detection despite R6=3.3ohm, R7=3.3ohm, R8=3R3, R10=3R3 likely being Class-D output sense resistors for overcurrent protection on TPA3255
  (signal_analysis.current_sense)

### Suggestions
- Add XL7015 to the Vref lookup table with Vref=1.25V to fix voltage estimation
- Detect TPA3255/TPA3250 as Class-D amplifiers and flag LC-filtered outputs as speaker circuits
- Recognize low-value resistors (< 10 ohm) in amplifier output paths as sense resistors
- Consider XLR connectors (AC3FAH2-XLR, AC3MAH) as audio interface indicators

---
