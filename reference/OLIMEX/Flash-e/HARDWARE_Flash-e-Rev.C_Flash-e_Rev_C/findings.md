# Findings: Flash-e / HARDWARE_Flash-e-Rev.C_Flash-e_Rev_C

## FND-00000564: Component counts, types, and BOM parsed correctly; eMMC/SDIO bus detected correctly as 8-bit with devices U1 and U2; U3 VCC (pin 8) incorrectly placed in GND net; SPI bus not detected despite clear...

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: HARDWARE_Flash-e-Rev.C_Flash-e_Rev_C.sch.json
- **Created**: 2026-03-23

### Correct
- 68 total components (13 caps, 16 resistors, 3 ICs, 2 jumpers, 6 fiducials, 1 connector, 27 test points), all BOM groups and values correct. Power rails (+3.3V, GND, VDD, PWR_FLAG) identified correctly.
- SDIO bus detected with bus_id=EMMC, bus_width=8, with CMD/CLK/D0-D7 signals mapped, pullups on CMD and D0 identified. Both the NAND flash (U1) and eMMC (U2) are correctly associated.
- Net classification correctly identifies eMMC-CLK and SPI_CLK as 'clock', NAND-CE0/SPI_CS as 'chip_select', SPI-MOSI/MISO as 'data', +3.3V as 'power', GND as 'ground'. Good heuristic performance on named nets.

### Incorrect
- The W25Q128 SPI flash (U3) pin 8 'VCC' (power_in) appears in the GND net in the output. In the schematic, +3.3V (#PWR045) connects to position 15500,2750 and GND (#PWR046) to 15500,4000. The component is Y-mirrored so pin positions are inverted, but net tracing assigns VCC to GND. This is a net assignment error likely due to mirrored component coordinate handling. The design_observations incorrectly reports U3 as lacking decoupling on +3.3V partly as a consequence.
  (signal_analysis)
- ERC warnings flag that nets NAND-D3\eMMC-D3, NAND-D2\eMMC-D2, NAND-D1\eMMC-D1, NAND-D0\eMMC-D0, NAND-D5\eMMC-D5, NAND-D6\eMMC-D6 have 'power_in' pins (VDDF(VCC) pins E6, F5, J10, K9, K5, etc. of U2 FBGA153 eMMC) but no driver. These VDDF(VCC) and RST_N pins appear to be on the wrong nets — this is a net tracing error stemming from the FBGA153 library symbol having power pins assigned to positions that the parser maps to the wrong schematic nets. The real VDD (1.8V memory core) is on a distinct eMMC-VDDI net, suggesting net assignment errors for this complex BGA component.
  (signal_analysis)
- design_observations flags U1, U2, U3 as missing decoupling caps on +3.3V, but numerous decoupling capacitors exist: C5, C6, C7, C8, C9, C10, C11 are all 100nF/2.2uF caps. However, because U3's VCC is wrongly assigned to GND (see above), and eMMC/NAND power pins are misassigned to data nets, the decoupling checker cannot associate caps on the +3.3V net with these ICs. This is a downstream consequence of the net assignment bugs.
  (signal_analysis)

### Missed
- U3 is a W25Q128 SPI NOR flash with nets explicitly named SPI-MOSI(IO0), SPI-MISO(IO1), SPI-CLK(CLK), SPI-CS(CMD), SPI-WPn(IO2), SPI-HOLD(IO3). bus_analysis.spi is empty. The analyzer should detect this SPI bus.
  (signal_analysis)
- U1 is an MT29F64G08 NAND flash with dedicated NAND bus signals (NAND-D0 through NAND-D7, NAND-CE0, NAND-WE, NAND-RE, NAND-ALE, NAND-CLE, NAND-RB0). signal_analysis.memory_interfaces is empty — the NAND interface is not recognized as a memory interface.
  (signal_analysis)

### Suggestions
(none)

---
