# Findings: Otter-Iron-PRO / v1.1_OtterIron_Devkit

## FND-00000141: USB-C soldering iron with STM32: power MOSFET heater drive and USB PD detected, but missing temperature sensing circuit and PID control loop identification

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/Otter-Iron-PRO/v1.1/OtterIron_Devkit.sch
- **Created**: 2026-03-14

### Correct
- AP2204R-3.3 LDO correctly identified for VBUS to 3.3V regulation
- USB differential pair (USB_P/USB_N) detected with ESD protection
- P-channel MOSFET Q2 (DMP3017SFG) identified as high-side heater power switch
- I2C bus detected for OLED display (OLED_SDA/OLED_SCL) with 2.37k pull-ups to 3.3V
- Voltage divider R1/R2 (560k/100k) on VBUS to UIN for input voltage monitoring correctly identified
- BJT transistors Q1 (SS8050) and Q3/Q4 (SS8050/BC807) identified as signal switching circuits

### Incorrect
(none)

### Missed
- Thermocouple/temperature sensing circuit for soldering tip not identified - critical for PID temperature control
  (signal_analysis)
- PWM heater control circuit (MCU -> gate driver -> P-MOSFET -> heating element) not identified as a thermal control loop
  (signal_analysis)
- USB Power Delivery (PD) negotiation IC not identified despite USB-C connector and VBUS power path
  (signal_analysis)
- Complementary pair Q3 (NPN SS8050) + Q4 (PNP BC807) forms a push-pull output stage, not identified as such
  (signal_analysis.transistor_circuits)
- OLED display driver communication not linked to user interface / display subsystem
  (design_analysis)

### Suggestions
- Detect thermocouple amplifier circuits (op-amp + cold junction compensation) as temperature sensing
- Identify PWM-controlled MOSFET circuits driving resistive heating loads as thermal control
- Recognize complementary BJT pairs (NPN+PNP with shared base) as push-pull output stages
- Detect USB PD controllers as power negotiation components

---
