# Findings: racerxdl/kicad-board-collection / AS5600

## FND-00002238: I2C bus not detected despite MPU-9250 + BMP280 with named SDA/SCL nets and 4k7 pull-up resistors

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-board-collection_CJMCU-925x_CJMCU_CJMCU.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The CJMCU-925x board has two I2C sensor ICs (U1=MPU-9250, U2=BMP280) with explicit SDA and SCL net names, and 4.7k pull-up resistors R2 and R4. This is a textbook I2C bus configuration, but no i2c_bus or pull_up_resistor detector fired. The lib_id for the ICs is 'Sensor_Motion:MPU-9250' and 'Sensor_Pressure:BMP280', both well-known I2C devices. The +3.3V power rail is also present but no voltage_regulator or power_supply detector fired.
  (statistics)

### Suggestions
(none)

---

## FND-00002239: No I2C bus, LDO regulator, or LED indicator detected for MPU-6050 breakout with TC2185 LDO and 4 resistors on SCL/SDA

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-board-collection_MPU6050_MPU6050.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The MPU6050 schematic has U1=MPU-6050 (I2C IMU), U2=TC2185-3.3VxCTTR (explicit 3.3V LDO regulator with lib_id 'Regulator_Linear:TC2185-3.3VxCTTR'), D1=LED, and 4 resistors. Named nets include SDA, SCL, AD0, INT, XDA, XCL, +3.3V, and VCC. No i2c_bus, voltage_regulator, or led_indicator detector fired. The TC2185 lib_id directly encodes the regulator family and the 3.3V output voltage, making it a clear missed detection for both the regulator and the downstream I2C bus it powers.
  (statistics)

### Suggestions
(none)

---

## FND-00002240: I2C bus not detected for AS5600 magnetic encoder breakout with named SDA/SCL nets

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: schematic_kicad-board-collection_AS5600_AS5600.kicad_sch.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The AS5600 schematic has U1=AS5600 (magnetic angle encoder with I2C interface), with named nets SDA, SCL, VCC, VDD3v3, GND, OUT, DIR, and PGO. Two 10k pull-up resistors R2 and R3 are present. No i2c_bus or pull_up_resistor detector fired. The VDD3v3 net suggests an internal 3.3V domain separate from VCC, which is also undetected as a voltage domain.
  (statistics)

### Suggestions
(none)

---

## FND-00002241: +3.3V power net absent from power_net_routing despite being the primary supply net

- **Status**: promoted
- **Analyzer**: pcb
- **Source**: pcb_kicad-board-collection_CJMCU-925x_CJMCU_CJMCU.kicad_pcb.json
- **Created**: 2026-03-24

### Correct
(none)

### Incorrect
(none)

### Missed
- The CJMCU-925x PCB net list contains only GND, SCL, SDA, AD0, and various unconnected stubs — the +3.3V supply net from the schematic does not appear in the PCB nets at all. The power_net_routing analysis only reports GND. This suggests the +3.3V net is implemented entirely via copper zone fill (both layers have GND zones; +3.3V may be distributed through pads without a named net in the PCB file), or the +3.3V net was not transferred to the PCB. The power_net_routing section is therefore incomplete for the primary supply.
  (connectivity)

### Suggestions
(none)

---
