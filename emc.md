# EMC Pre-Compliance Testing

The test harness validates the kicad-happy EMC pre-compliance analyzer (`analyze_emc.py`) against the full 1,035-repo corpus. The EMC skill reads schematic and/or PCB analyzer JSON outputs, applies geometric rule checks and analytical formulas, and produces a structured risk report with findings, severity scores, and recommendations.

Unlike SPICE (which runs simulations), EMC is purely analytical — all estimates come from textbook formulas (Ott, Paul, Bogatin) and geometric heuristics on the PCB layout. No external tools are required.

## Quick start

```bash
# Run EMC analysis (reads existing schematic + PCB JSON outputs)
python3 run/run_emc.py --repo {repo}       # single repo
python3 run/run_emc.py --jobs 16           # full corpus
python3 run/run_emc.py --standard cispr-class-b  # non-default standard

# Check aggregate results
cat results/outputs/emc/_aggregate.json | python3 -m json.tool

# Cross-validate EMC vs analyzer values
python3 validate/validate_emc.py --summary

# Run EMC regression assertions
python3 regression/run_checks.py --type emc
```

## Input pairing

EMC is keyed to schematic files. For each schematic output in `results/outputs/schematic/{repo}/`, the batch runner looks for a matching PCB output in `results/outputs/pcb/{repo}/` by replacing `.kicad_sch.json` with `.kicad_pcb.json` (or `.sch.json` with `.kicad_pcb.json` for legacy KiCad 5). If a PCB match exists, both are passed to `analyze_emc.py`; if not, schematic-only analysis runs (fewer checks but still useful).

In the full corpus run, ~46% of files pair with a PCB output.

## EMC standards supported

| Standard | Bands | Use case |
|----------|-------|----------|
| `fcc-class-b` (default) | 30 MHz – 40 GHz | Consumer electronics (US) |
| `fcc-class-a` | 30 MHz – 40 GHz | Industrial/commercial (US) |
| `cispr-class-b` | 30 MHz – 1 GHz | Consumer electronics (EU/international) |
| `cispr-class-a` | 30 MHz – 1 GHz | Industrial (EU/international) |
| `cispr-25` | 30 MHz – 1 GHz | Automotive (Class 5) |
| `mil-std-461` | 2 MHz – 18 GHz | Military |

## Rule categories (15)

| Category | Rule IDs | Checks | Requires |
|----------|----------|--------|----------|
| `ground_plane` | GP-001 to GP-005 | Return path coverage, ground zone presence/fragmentation, ground domains | PCB |
| `decoupling` | DC-001, DC-002 | Cap placement distance, missing decoupling for ICs | PCB |
| `io_filtering` | IO-001 | Filter/ESD components near external connectors | PCB (+ schematic optional) |
| `switching_emc` | SW-001 | Switching regulator harmonic overlap with emission bands | Schematic |
| `clock_routing` | CK-001, CK-002 | Clock on outer layers, long clock traces | PCB (+ schematic optional) |
| `via_stitching` | VS-001 | Via stitching spacing vs lambda/20 at highest frequency | PCB (+ schematic optional) |
| `stackup` | SU-001 to SU-003 | Adjacent signal layers, reference plane proximity, interplane capacitance | PCB |
| `diff_pair` | DP-001 to DP-004 | Skew, CM radiation, reference plane change, outer layer routing | PCB + Schematic |
| `board_edge` | BE-001 to BE-003 | Trace near edge, ground pour ring, connector stitching | PCB |
| `pdn` | PD-001, PD-002 | Anti-resonance exceeds/within target impedance | Schematic |
| `crosstalk` | XT-001 | 3H spacing rule violation | PCB |
| `emi_filter` | EF-001, EF-002 | Filter cutoff vs switching frequency | Schematic |
| `esd_path` | ES-001, ES-002 | TVS distance from connector, ground via proximity | PCB + Schematic |
| `thermal_emc` | TH-001, TH-002 | MLCC DC bias derating, ferrite proximity to hot components | PCB + Schematic |
| `shielding` | SH-001 | Connector aperture slot resonance advisory | PCB (+ schematic optional) |

Two additional "estimate" checks (`EE-001` board cavity resonance, `EE-002` switching emission estimate) produce INFO-level findings.

## Analytical formulas (emc_formulas.py)

Pure math with zero dependencies:

- **Differential-mode radiation**: E = K × f² × A × I / r (electrically small loop)
- **Common-mode radiation**: E = µ₀ × f × L × I_CM / r (cable monopole)
- **Trapezoidal harmonic spectrum**: Corner frequencies, per-harmonic amplitude with sinc rolloffs
- **Board cavity resonance**: f_mn = (c / 2√εr) × √((m/L)² + (n/W)²)
- **Capacitor impedance**: Series RLC model with SRF, ESR/ESL lookup by package
- **Bandwidth/wavelength**: BW = 0.35/t_r, λ/20 via stitching rule

All formulas are tagged with `# EQ-NNN:` comments in the source code and tracked in
`reference/equation_registry.json`. The critical EMC radiation formulas (EQ-001, EQ-003)
are verified against the [MSU EMC Lab Module 9](https://www.egr.msu.edu/emrg/sites/default/files/content/module9_radiated_emissions.pdf)
derivation which confirms the exact coefficients (1.317×10⁻¹⁴ for DM, 1.257×10⁻⁶ for CM).
Formulas are also validated by unit tests in `tests/test_emc.py`.

Run `python3 validate/audit_equations.py list --file emc_formulas.py` to see all 22 tracked
EMC equations with their verification status and sources.

## Risk scoring

```
score = 100 - (CRITICAL × 15) - (HIGH × 8) - (MEDIUM × 3) - (LOW × 1)
```

Clamped to [0, 100]. A score of 100 means no EMC findings; scores below 50 indicate significant EMC risk.

## Cross-validation

`validate/validate_emc.py` compares EMC's extracted board_info against the source analyzer outputs:

| Check | Comparison | Agreement |
|-------|-----------|-----------|
| component_count | EMC vs schematic statistics | 100% |
| crystal_frequencies | EMC vs schematic crystal_circuits | 100% |
| footprint_count | EMC vs PCB statistics | 100% |
| layer_count | EMC vs PCB statistics | 100% |
| switching_regulator_count | SW-001 findings vs non-LDO regulators | 14.3% |

The switching_regulator_count mismatch is expected — EMC's `_estimate_switching_freq()` lookup table covers ~23 common regulators (TPS62xxx, MP1584, LM2596, etc.), while the schematic analyzer detects switching regulators more broadly by topology. EMC only flags harmonics for parts whose switching frequency it knows.

## Regression assertions

EMC assertions follow the same SEED/STRUCT pattern as other analyzer types:

- **SEED assertions**: finding count range, per-severity counts, risk score range, per-category counts, target standard
- **STRUCT assertions**: exact per-category counts, per-rule_id presence, per-component-ref presence

```bash
python3 regression/seed.py --all --type emc
python3 regression/seed_structural.py --all --type emc
python3 regression/run_checks.py --type emc
```

## File locations

| File | Description |
|------|-------------|
| `run/run_emc.py` | Batch runner — pairs schematic+PCB outputs, runs analyze_emc.py |
| `validate/validate_emc.py` | Cross-validation — EMC board_info vs analyzer values |
| `tests/test_emc.py` | 29 unit tests (seed, structural, roundtrip, cross-validation) |
| `results/outputs/emc/` | EMC output JSONs (git-ignored) |
| `results/outputs/emc/_aggregate.json` | Corpus-wide summary statistics |
| `reference/{repo}/{project}/baselines/emc.json` | EMC baselines (git-tracked) |
| `reference/{repo}/{project}/assertions/emc/` | EMC assertions (git-tracked) |

## Current stats

- 6,853 files processed, 0 script errors
- 3,165 paired with PCB (46%), 6,838 files with findings
- 141,343 total findings across 15 categories
- 88,808 EMC assertions (32,741 SEED + 56,067 STRUCT) at 100% pass rate
- 14,415 cross-validation checks at 90.1% agreement
- 29 unit tests (harness) + 31 test plan tests (phases 2-4)
- 290 constants tracked, 0 critical-risk
