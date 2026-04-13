# Findings: mlab-modules/VCAI2C01 / hw_sch_pcb_VCAI2C01

## FND-00001762: 74 components and 31 nets correctly counted; Four symmetrical voltage dividers correctly detected for differential input channels; I2C bus detected on SDA/SCL with pull-up resistors R23/R24; Opamp ...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: VCAI2C01.kicad_sch.json
- **Created**: 2026-03-24

### Correct
- The schematic has 74 components (diodes 9, capacitors 12, resistors 24, connectors 21, ICs 3, inductor 1, other 4) and 31 nets. These match the KiCad source file and the PCB/gerber data.
- The board has four identical 180K/33K voltage dividers (R4/R7, R6/R8, R14/R17, R16/R18), one per differential input channel, each feeding the positive input of a TLC27L2ID opamp. All four are detected with correct ratios (0.155) and mid-point connections.
- The design_observations correctly identify the SDA and SCL lines with pull-up resistors R23 and R24 on the VCC rail, serving U3 (MCP3424 ADC).

### Incorrect
- The four detected RC networks (R3/C6, R5/C7, R13/C10, R15/C11) each have ground_net=OUT1, OUT2, OUT3, OUT4 respectively. These are opamp output signals, not ground. The topology is a feedback integrator (R in series with the negative input, C from input to opamp output), not a standard low-pass RC to GND. The filter type should not be 'RC-network' classified as a frequency filter; it is a feedback path element.
  (signal_analysis)

### Missed
- U1 and U2 are TLC27L2ID dual opamps (4 opamp units total) used as instrumentation amplifier stages. They are stored under the rescue library (VCAI2C01A-rescue:TLC27L2ID) rather than a standard Amplifier_Operational:* lib_id. The opamp_circuits detector returns an empty list, missing all four opamp circuit instances.
  (signal_analysis)

### Suggestions
- Fix: RC filters have ground_net pointing to opamp output nets (OUT1-4), not GND

---

## FND-00001763: PCB footprint count (74), net count (31), and via count (162) all correct

- **Status**: new
- **Analyzer**: pcb
- **Source**: VCAI2C01.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
- The PCB analysis matches the schematic and gerber data: 74 footprints (25 front/49 back), 31 nets, 162 vias (all 0.4 mm), 2-layer board 60.45 x 40.13 mm, routing complete.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
