# Findings: PCB-Mini-Environmental-Sensor / Kicad Files_Mini_Environmental_Sensor

## FND-00001084: USB-C CC1/CC2 pull-down resistor failure correctly detected: 10k instead of 5.1k; PWR_FLAG warnings for +3V3, GND, VBUS are legitimate ERC issues; I2C buses (BME280 and SGP40) and all sensor ICs co...

- **Status**: new
- **Analyzer**: schematic
- **Source**: Mini_Environmental_Sensor.kicad_sch
- **Created**: 2026-03-23

### Correct
- J2 USB_C_PowerOnly requires 5.1k pull-downs on CC1 and CC2 pins for UFP (device) identification per USB-C spec. R3 (10k) on CC1 and R4 (10k) on CC2 are confirmed in the net data. The analyzer correctly flags cc1_pulldown_5k1 and cc2_pulldown_5k1 as fail. This is a real compliance issue that may prevent proper USB-C power delivery negotiation.
- TPS62203 (U5) outputs +3V3 via inductor L1 (passive pin), so there is no power_out typed pin on +3V3 net — KiCad ERC would flag this. VBUS comes from J2 USB connector (passive pins only). GND has no PWR_FLAG. All three warnings are valid per KiCad ERC rules. Not false positives.
- Subcircuits correctly identify U3 (BME280), U4 (SGP40-D-R4), U1 (ESP32-C3-WROOM-02), U2 (MCP73831 charger), U5 (TPS62203 switcher). Net classification correctly identifies BME280_SCL, SGP40_SCL as clock; BME280_SDA, SGP40_SDA as data. Two separate I2C buses are distinguished.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---

## FND-00001085: Tombstoning risk on 0402 caps C3, C4 correctly identified due to GND pour thermal asymmetry

- **Status**: new
- **Analyzer**: pcb
- **Source**: Mini_Environmental_Sensor.kicad_pcb
- **Created**: 2026-03-23

### Correct
- C3 (0.1uF) and C4 (0.1uF) in 0402 package on B.Cu have one pad on GND zone (thermal asymmetry) and one on a signal net. The analyzer correctly identifies medium tombstoning risk for both components. Real assembly concern for reflow.

### Incorrect
(none)

### Missed
(none)

### Suggestions
(none)

---
