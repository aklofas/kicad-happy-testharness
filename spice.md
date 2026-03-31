# SPICE Simulation Testing

The test harness validates the kicad-happy SPICE simulation skill (`simulate_subcircuits.py`) against the full 1,035-repo corpus. The SPICE skill reads schematic analyzer JSON outputs, generates ngspice testbenches for detected subcircuits, runs simulations, and produces structured pass/warn/fail/skip results.

## Requirements

- **ngspice** (v39+). Install:
  - Linux: `apt install ngspice`
  - macOS: `brew install ngspice`
  - Windows: download from [ngspice.sourceforge.io](https://ngspice.sourceforge.io), or set `NGSPICE_PATH` to the binary path
- **Schematic outputs** must exist in `results/outputs/schematic/` (run `run/run_schematic.py` first)

## Quick start

```bash
# Run SPICE simulations (reads existing schematic JSON outputs)
python3 run/run_spice.py --repo {repo}       # single repo
python3 run/run_spice.py --jobs 16           # full corpus

# Check aggregate results
cat results/outputs/spice/_aggregate.json | python3 -m json.tool

# Cross-validate SPICE vs analyzer values
python3 validate/validate_spice.py --summary

# Run SPICE regression assertions
python3 regression/run_checks.py --type spice
```

## Subcircuit types (17)

| Type | Count | Simulation | Source |
|------|-------|------------|--------|
| `rc_filter` | 7,820 | AC sweep, measure -3dB cutoff frequency | signal_analysis.rc_filters |
| `decoupling` | 7,296 | AC impedance sweep of parallel cap bank (ESR+ESL model) | signal_analysis.decoupling_analysis |
| `transistor_circuit` | 4,956 | DC sweep, measure Vth and on-state current | signal_analysis.transistor_circuits |
| `voltage_divider` | 3,212 | DC operating point, verify Vout = Vin x ratio | signal_analysis.voltage_dividers |
| `lc_filter` | 1,605 | AC sweep, measure resonant frequency and Q | signal_analysis.lc_filters |
| `inrush` | 1,219 | Transient startup, measure peak inrush current | inrush_analysis.rails |
| `protection_device` | 1,107 | DC sweep, measure clamping onset voltage | signal_analysis.protection_devices |
| `opamp_circuit` | 1,085 | AC sweep, measure gain at 1kHz and bandwidth | signal_analysis.opamp_circuits |
| `crystal_circuit` | 547 | Verify load cap presence and effective CL | signal_analysis.crystal_circuits |
| `current_sense` | 523 | DC sweep, verify I=V/R at 50mV and 100mV | signal_analysis.current_sense |
| `regulator_feedback` | 386 | DC operating point, verify FB voltage = Vref | signal_analysis.power_regulators |
| `feedback_network` | 375 | DC operating point, verify divider ratio | signal_analysis.feedback_networks |
| `rf_matching` | 296 | AC impedance sweep 1kHz-10GHz | signal_analysis.rf_matching |
| `rf_chain` | 94 | Link budget (heuristic gain/loss per stage) | signal_analysis.rf_chains |
| `bridge_circuit` | 93 | DC gate sweep, verify FET turn-on | signal_analysis.bridge_circuits |
| `snubber_circuit` | 26 | AC impedance of RC snubber, verify damping frequency | signal_analysis.transistor_circuits (extracted) |
| `bms_balance` | 6 | DC operating point, verify balance resistor power | signal_analysis.bms_systems |

## How it works

```
Schematic JSON ──> simulate_subcircuits.py ──> ngspice (.cir) ──> Results JSON
     │                      │                       │                  │
     │              Template generators      Batch mode (-b)    Evaluators
     │              (spice_templates.py)                    (spice_results.py)
     │                      │
     │              TEMPLATE_REGISTRY          EVALUATOR_REGISTRY
     │              (17 signal_analysis        (17 matching evaluators)
     │               + 1 top-level type)
     │
     └── _context injected for cross-referencing
         (opamp rail inference, pdn_impedance ESR/ESL)
```

1. **Template generators** read detector output dicts and produce ngspice `.cir` files. Each generator returns `None` for non-simulatable detections (e.g., comparator opamps, ground-referenced filter outputs).

2. **ngspice** runs in batch mode (`-b`). Simulations use `.control` blocks with `meas` commands that write key=value results to output files via `echo`.

3. **Evaluators** parse the output files and compare simulated values against expected values from the analyzer, producing pass/warn/fail/skip results.

## Models

All simulations use **generic behavioral models** (no manufacturer SPICE models):

- **Passives**: Native SPICE R/C/L elements (exact)
- **Ideal opamp**: VCVS with Aol=1e6, single-pole at 10Hz (GBW ~10MHz), rail clamping
- **Generic semiconductors**: D, NPN/PNP, NMOS/PMOS with typical parameters
- **Decoupling caps**: Series R-L-C model with ESR from `pdn_impedance` (package-based) or estimated from capacitance
- **RF chain**: Heuristic gain/loss per component role (amplifier +15dB, switch -0.5dB, etc.)

Models are defined in `spice_models.py`. An unused `IDEAL_LDO` model exists for future regulator loop stability simulation.

## Cross-validation

`validate/validate_spice.py` compares SPICE-computed values against the analyzer's analytical calculations:

| Check | Comparison | Agreement |
|-------|-----------|-----------|
| voltage_dividers | SPICE Vout vs analyzer ratio x Vin | 100% |
| rc_filters | SPICE fc vs analyzer cutoff_hz | 99.3% |
| lc_filters | SPICE f0 vs analyzer resonant_hz | 100% |
| current_sense | SPICE I@50mV vs analyzer max_current_50mV_A | 100% |
| feedback_networks | SPICE vfb vs analyzer ratio x Vin | 100% |
| opamp_circuits | SPICE gain_dB vs expected gain | 41.7% |
| regulator_feedback | SPICE vfb vs expected from divider | 100% |

The RC filter mismatches are sub-3% rounding differences at very low frequencies (<1Hz) between analytical 1/(2piRC) and ngspice's numerical AC sweep. The opamp_circuit agreement is lower because many opamp configurations lack expected gain values (unknown topology), and the subcircuit type has a 48% warn rate indicating model limitations.

## Regression assertions

SPICE assertions follow the same SEED/STRUCT pattern as other analyzer types:

- **SEED assertions**: simulation count range, minimum pass count, per-type counts
- **STRUCT assertions**: exact type counts, per-component-ref presence (e.g., "R5 simulated as rc_filter")

```bash
python3 regression/seed.py --all --type spice
python3 regression/seed_structural.py --all --type spice
python3 regression/run_checks.py --type spice
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `KICAD_HAPPY_DIR` | Path to kicad-happy repo (default: `../kicad-happy`) |
| `NGSPICE_PATH` | Path to ngspice binary (default: auto-detect from PATH or common install locations) |

## File locations

| File | Description |
|------|-------------|
| `run/run_spice.py` | Batch runner — iterates schematic outputs, runs simulate_subcircuits.py |
| `validate/validate_spice.py` | Cross-validation — SPICE vs analyzer computed values |
| `results/outputs/spice/` | SPICE output JSONs (git-ignored) |
| `results/outputs/spice/_aggregate.json` | Corpus-wide summary statistics |
| `reference/{repo}/{project}/baselines/spice.json` | SPICE baselines (git-tracked) |
| `reference/{repo}/{project}/assertions/spice/` | SPICE assertions (git-tracked) |

## Current stats

- 30,646 subcircuit simulations across 17 types
- 94.1% pass rate (28,853 pass, 857 warn, 14 fail, 922 skip)
- 89,292 SPICE assertions at 100% pass rate
- 12,777 cross-validation checks at 99.6% agreement
- 0 script errors across the full corpus
