# Findings: greatscottgadgets/hackrf-pro / praline

## FND-00000117: KiCad 9 value parsing completely broken: capacitor/inductor farads/henries fields contain raw numeric values without SI prefix conversion (e.g. 18 pF parsed as 18.0 farads, 10 nH as 10.0 henries), causing all derived calculations (resonant freq, cutoff freq, effective load, time constant, total_uF) to be orders of magnitude wrong

- **Status**: promoted
- **Analyzer**: schematic
- **Source**: repos/hackrf-pro/hardware/praline/praline.kicad_sch
- **Created**: 2026-03-14

### Correct
- Component count (577), net count (518), and component type classification are correct
- RF chain correctly identifies RFFC5072 mixer, MAX2831 transceiver, 4 baluns (2x IF_BALUN, 2x RF_BALUN), and their interconnections
- I2C bus detection correctly finds SDA/SCL with pullups R27/R28 to VCC
- SPI bus detection correctly identifies SPIFI and SSP1 buses
- USB-C compliance correctly flags cc1/cc2_pulldown_5k1 as fail (R106/R103 are 4.7k, not 5.1k per spec)
- Voltage divider detection is structurally correct (10 dividers found with proper topology)
- Differential pairs correctly detected: USB D+/D-, RXIF+/-, TXIF+/-, RXIF_BALUN+/-, TXIF_BALUN+/-
- Power domain analysis correctly maps ICs to their supply rails
- Crystal circuits correctly identify X1 TCXO and SI5351C as active oscillators

### Incorrect
- All capacitor farads values are raw numbers without SI prefix conversion: 18 pF stored as farads=18.0 instead of 1.8e-11, 100 pF as 100.0 instead of 1e-10, 1 uF as 1.0 instead of 1e-6
  (signal_analysis.rc_filters, signal_analysis.lc_filters, signal_analysis.crystal_circuits, signal_analysis.decoupling_analysis)
- All inductor henries values are raw numbers without SI prefix conversion: 10 nH stored as henries=10.0 instead of 1e-8, 2.2 uH as 2.2 instead of 2.2e-6
  (signal_analysis.lc_filters)
- Crystal effective_load_pF calculated as 9000000000003.0 instead of ~12 pF due to farads=18.0 for 18pF caps
  (signal_analysis.crystal_circuits)
- All RC filter cutoff frequencies are 0.00 Hz and time constants are thousands of seconds due to wrong farads values
  (signal_analysis.rc_filters)
- All LC filter resonant frequencies are 0.01-0.11 Hz instead of MHz/GHz range for RF filters due to wrong farads/henries
  (signal_analysis.lc_filters)
- Decoupling total_capacitance_uF values are millions (e.g. 55000000.0 uF for VCC rail) instead of tens of uF
  (signal_analysis.decoupling_analysis)
- BGB741L7ESD (U38, U40) are RF LNAs but misclassified as power_regulators with topology=unknown
  (signal_analysis.power_regulators)
- RF chain amplifiers list is empty despite BGB741L7ESD (LNA), TRF37C73 (RF amp), MGA-81563 being present
  (signal_analysis.rf_chains)
- RF chain switches list is empty despite MXD8546F (U1, U2) and MXD8638C (U9, U12, U14) RF switches being present
  (signal_analysis.rf_chains)
- RF matching list is empty despite extensive matching networks around baluns and mixer
  (signal_analysis.rf_matching)
- I2S0_RX_SDA and I2S0_TX_SDA nets misidentified as I2C SDA lines (these are I2S audio data lines)
  (design_analysis.bus_analysis.i2c)
- MIXER.SDATA net misidentified as I2C SDA (this is a SPI-like serial data line for RFFC5072)
  (design_analysis.bus_analysis.i2c)
- Decoupling has_bypass and has_high_freq are both false for all rails despite 100nF and smaller caps being present
  (signal_analysis.design_observations)

### Missed
- No detection of PLL loop filter (R25/R26/C44/C45/C47 form RFFC5072 charge pump filter)
  (signal_analysis)
- No RF switch detection for MXD8546F (SPDT) and MXD8638C (SP4T) RF switches critical to the signal routing
  (signal_analysis.rf_chains)
- No identification of the complete RF signal path: antenna -> balun -> switch -> mixer -> IF balun -> transceiver -> baseband
  (signal_analysis.rf_chains)
- FM8625H/BGS12P2L6 (U5, U6, U7) are RF amplifier switches but not detected in any RF analysis
  (signal_analysis.rf_chains)
- Power sequencing between multiple domains (VCC, VAA, 2V5RF, 1V2FPGA, etc.) not analyzed despite being critical for FPGA+RF design
  (signal_analysis)

### Suggestions
- CRITICAL: Fix SI prefix parsing for KiCad 9 format - the value string parser fails to convert pF/nF/uF/nH/uH to base SI units
- Add RF switch detection for common RF switch ICs (MXD, SKY, PE42, HMC, etc.)
- Add RF amplifier/LNA detection for common RF amp ICs (BGB, MGA, TRF, SKY, HMC, etc.) instead of misclassifying them as regulators
- Distinguish I2S data lines from I2C SDA by checking net name patterns (I2S, I2S0, etc.)
- Fix decoupling has_bypass/has_high_freq classification - likely broken by the same unit parsing bug

---

## FND-00002510: Praline is a wideband SDR (1MHz-6GHz) with RFFC5072 mixer/synthesizer, MAX2831 transceiver, MAX5865 40MSPS ADC/DAC, ICE40UP5K FPGA, and LPC4330 MCU. Analyzer correctly identifies major RF ICs and chain topology, but has 35 RF signal nets falsely detected as UART, misses RF impedance matching networks, omits FL2/FL3 bandpass filters and MAX5865 from RF chain, and misclassifies AP22652 load switches as LDOs.

- **Status**: confirmed
- **Analyzer**: schematic
- **Source**: praline.kicad_sch.json
- **Created**: 2026-03-30

### Correct
- RFFC5072 (U4) correctly identified as mixer with proper connections to T1/T2 RF baluns on MIX_IN+/- and MIX_OUT+/-
- BGB741L7ESD/TRF37C73 amplifiers correctly placed in RF chain
- T1-T4 baluns correctly identified in rf_chains
- MAX2831 (U17) correctly identified as RF transceiver with differential pairs RXIF+/-, TXIF+/-, RXBB.I/Q+/-
- RF switches FM8625H/MXD8546F/MXD8638C correctly classified as RF IC
- SI5351C clock generator correctly typed as oscillator; TCXO X1 (25MHz) identified
- ICE40UP5K correctly classified as FPGA (Lattice)
- RF-frequency LC filters correctly computed: L6/C114 at 3.88GHz, L9/C111 at 767MHz
- All I/Q baseband differential pairs correctly detected
- TPS62410 (U21) correctly identified as switching regulator with feedback divider R38/R39
- 577 total components correctly counted: 157 resistors, 211 caps, 32 inductors, 4 transformers, 3 filters, 66 test points

### Incorrect
- AP22652 (U28) classified as LDO but it is a current-limiting load switch. Passes VCC directly to 3V3AUX under enable control, no internal voltage reference.
  (signal_analysis.power_regulators)
- 35 of 42 UART detections are false positives from RF signal net names containing RX/TX: RXIF+/-, TXIF+/-, RXBB.I/Q+/-, TXBB.I/Q+/-, RX_AMP_IN/OUT, TX_AMP_IN/OUT, etc. Only U0_RXD/U0_TXD are real UART.
  (design_analysis.bus_analysis.uart)

### Missed
- rf_matching is empty despite clear RF impedance matching networks: L6/C114/R124 pi-network on MIX_OUT+ at GHz resonance, L30/C198 on MIX_OUT-, and matching around U1/U9 bypass paths.
  (signal_analysis.rf_matching)
- FL2 and FL3 (BFCN-1445/BPF1608LM02R2400A 2.45GHz bandpass filters) absent from rf_chains.filters despite being in the mixer signal path.
  (signal_analysis.rf_chains)
- MAX5865 (U18, 40MSPS dual ADC+DAC) absent from rf_chains and has no function label. It is the core data converter connected via SPI alongside MAX2831 and ICE40.
  (signal_analysis.rf_chains)
- RFFC5072 PLL/synthesizer function not captured — classified only as 'mixer' but it is a mixer+synthesizer+VCO. MIXER.LD (lock detect) not noted.
  (signal_analysis.rf_chains)
- GT4227 (U3/U8/U34/U35) classified as 'USB IC' but used as differential 2:1 muxes for baseband I/Q signal routing, not USB switching.
  (ic_pin_analysis)

### Suggestions
- Require UART detection to check pin type or exclude nets already in RF chain context.
- Add filter-type components (RF_Filter lib_id) to rf_chains builder.
- Include ADC/DAC components on same SPI bus as transceiver in rf_chains.
- Add 'synthesizer' role for ICs with VCO/synthesizer in description.
- Classify AP22652/BD2243G as 'load_switch' topology, not 'LDO'.

---
