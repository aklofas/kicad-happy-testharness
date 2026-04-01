# Equation Registry

Auto-generated from `equation_registry.json` — do not edit manually.

**Last scan:** 2026-04-01T21:47:25.249114+00:00

## Summary

| Metric | Count |
|--------|------:|
| Total equations | 83 |
| Verified | 83 |
| Unverified | 0 |
| Stale | 0 |
| Critical impact | 9 |
| High impact | 28 |
| Medium impact | 31 |
| Low impact | 15 |

## analyze_pcb.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-023 | `_microstrip_impedance` | Z₀ = (60/√εr)ln(8h/w+w/4h) (Wheeler narrow microstrip) | impedance | high | **verified** |
| EQ-024 | `_microstrip_impedance` | Z₀ = 120π/(√εr(w/h+1.393+0.667ln(w/h+1.444))) (Wheeler wide) | impedance | high | **verified** |
| EQ-044 | `_arc_length_3pt` | arc = R × θ from circumcircle (3-point arc length) | geometry | low | **verified** |
| EQ-045 | `_build_routing_graph` | d = √(Δx²+Δy²) (routing graph edge weight) | geometry | low | **verified** |
| EQ-046 | `_mark` | d = √(Δx²+Δy²) (grid cell marking) | geometry | low | **verified** |
| EQ-047 | `_norm` | Angle normalization to [0, 2π) | geometry | low | **verified** |
| EQ-048 | `analyze_decoupling_placement` | d = √(Δx²+Δy²) (cap-to-IC distance) | geometry | low | **verified** |
| EQ-049 | `analyze_dfm` | d = √(Δx²+Δy²) (DFM clearance measurement) | geometry | low | **verified** |
| EQ-050 | `analyze_net_lengths` | L = √(Δx²+Δy²) (track segment length) | geometry | low | **verified** |
| EQ-051 | `analyze_pad_to_pad_distances` | d = √(Δx²+Δy²) (pad-to-pad distance) | geometry | low | **verified** |
| EQ-052 | `analyze_power_nets` | d = √(Δx²+Δy²) (Euclidean distance) | geometry | low | **verified** |
| EQ-053 | `analyze_return_path_continuity` | d = √(Δx²+Δy²) (trace-to-plane gap detection) | geometry | low | **verified** |
| EQ-054 | `analyze_thermal_pad_vias` | effective = Σ(drill/0.3)² (drill-weighted via count) | thermal | medium | **verified** |
| EQ-055 | `analyze_thermal_vias` | density = count / area_cm² (thermal via density) | thermal | medium | **verified** |
| EQ-056 | `analyze_tombstoning_risk` | d = √(Δx²+Δy²) (pad center asymmetry) | geometry | low | **verified** |
| EQ-057 | `analyze_trace_proximity` | d = √(Δx²+Δy²) (grid-based proximity scan) | geometry | low | **verified** |
| EQ-058 | `analyze_vias` | area = π(d/2)² (via annular ring) | geometry | low | **verified** |
| EQ-059 | `compute_statistics` | d = √(w²+h²) (board diagonal) | geometry | low | **verified** |
| EQ-060 | `extract_footprints` | x'=x·cosθ-y·sinθ, y'=x·sinθ+y·cosθ (2D rotation) | geometry | low | **verified** |

## analyze_schematic.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-061 | `_cap_impedance` | \|Z\| = √(ESR²+(2πfL-1/(2πfC))²) at given frequency | filter_design | high | **verified** |
| EQ-062 | `analyze_pdn_impedance` | \|Z\| = √(ESR²+(ωL-1/ωC)²) swept over frequency | impedance | high | **verified** |
| EQ-063 | `analyze_protocol_compliance` | t_rise = 0.8473 × R × C (I2C rise time estimation) | filter_design | high | **verified** |
| EQ-064 | `analyze_wire_geometry` | L = √(Δx²+Δy²) (wire segment length) | filter_design | high | **verified** |
| EQ-065 | `apply_rotation` | x'=x·cosθ-y·sinθ, y'=x·sinθ+y·cosθ (2D rotation) | filter_design | high | **verified** |

## emc_formulas.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-001 | `dm_radiation_v_m` | E = K × f² × A × I / r (differential-mode loop radiation) | emc_radiation | critical | **verified** |
| EQ-002 | `dm_radiation_dbuv_m` | dBµV/m = 20 × log₁₀(E × 10⁶) | unknown | medium | **verified** |
| EQ-003 | `cm_radiation_v_m` | E = 1.257e-6 × f × L × I_CM / r (common-mode cable radiation) | emc_radiation | critical | **verified** |
| EQ-004 | `trapezoidal_harmonic_amplitude` | A_n = \|a₀ × sinc(nπτ/T) × sinc(nπt_r/T)\| (trapezoidal harmonic) | emc_radiation | critical | **verified** |
| EQ-005 | `trapezoidal_corner_frequencies` | f₁ = 1/(πτ), f₂ = 1/(πt_r) (trapezoidal envelope corners) | emc_radiation | critical | **verified** |
| EQ-006 | `cavity_resonance_hz` | f_mn = (c/2√εr) × √((m/L)² + (n/W)²) (PCB cavity resonance) | emc_radiation | critical | **verified** |
| EQ-007 | `bandwidth_from_rise_time` | BW = 0.35/t_r (3dB bandwidth from 10-90% rise time) | signal_integrity | medium | **verified** |
| EQ-008 | `knee_frequency` | f_knee = 0.5/t_r (EMC spectral content upper bound) | emc_radiation | critical | **verified** |
| EQ-009 | `wavelength_in_pcb` | λ = c/(f × √εr) (wavelength in PCB dielectric) | signal_integrity | medium | **verified** |
| EQ-010 | `via_inductance_nh` | L = 0.2h(ln(4h/d)+1) nH (via self-inductance) | parasitic | high | **verified** |
| EQ-011 | `interplane_capacitance_pf_per_cm2` | C = ε₀εr/d (interplane capacitance per unit area) | parasitic | high | **verified** |
| EQ-012 | `cap_self_resonant_freq` | f_SRF = 1/(2π√(LC)) (capacitor self-resonant frequency) | emc_radiation | critical | **verified** |
| EQ-013 | `cap_impedance_at_freq` | \|Z\| = √(ESR² + (ωL - 1/ωC)²) (series RLC impedance) | impedance | high | **verified** |
| EQ-025 | `cm_max_current_a` | I_max = E_limit × r / (µ₀ × f × L) (max CM current) | unknown | medium | **verified** |
| EQ-026 | `cm_radiation_dbuv_m` | dBµV/m = 20 × log₁₀(E × 10⁶) (CM radiation in dBuV/m) | emc_radiation | critical | **verified** |
| EQ-027 | `dm_max_loop_area_m2` | A = E_limit × r / (K × f² × I) (max allowable loop area) | unknown | medium | **verified** |
| EQ-028 | `harmonic_spectrum` | Full harmonic spectrum using EQ-004 per harmonic | emc_radiation | critical | **verified** |
| EQ-029 | `parallel_cap_impedance` | 1/Z_total = Σ(1/Z_i) (parallel impedance combination) | impedance | high | **verified** |
| EQ-030 | `pdn_impedance_sweep` | Z(f) = parallel cap impedance swept over log frequency | impedance | high | **verified** |
| EQ-031 | `point_to_segment_distance` | d = perpendicular distance from point to line segment | unknown | medium | **verified** |
| EQ-032 | `propagation_delay_ps_per_mm` | delay = √((εr+1)/2)/c (microstrip propagation delay) | signal_integrity | medium | **verified** |
| EQ-033 | `trace_inductance_nh_per_mm` | L/mm = Z₀/v_phase (Wheeler microstrip inductance per mm) | parasitic | high | **verified** |

## emc_rules.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-034 | `check_connector_area_stitching` | Via density in connector proximity region | parasitic | high | **verified** |
| EQ-035 | `check_connector_filtering` | d = √(Δx²+Δy²) (filter-to-connector distance) | filter_design | high | **verified** |
| EQ-036 | `check_diff_pair_cm_radiation` | E_cm from V_cm and cable length using EQ-003 | unknown | medium | **verified** |
| EQ-037 | `check_emi_filter_effectiveness` | ratio = f_sw/f_cutoff; ratio >= 5 for adequate EMI filter | filter_design | high | **verified** |
| EQ-038 | `check_esd_protection_path` | V_overshoot = L × dI/dt; dI/dt = 37.5 GA/s for 8kV ESD | unknown | medium | **verified** |
| EQ-039 | `check_ground_pour_ring` | Edge coverage from GND zone bounding box sampling | unknown | medium | **verified** |
| EQ-040 | `check_layer_transition_stitching` | Via distance from layer transition vias | parasitic | high | **verified** |
| EQ-041 | `check_pdn_impedance` | Z_pdn(f) vs Z_target = V×ripple%/(0.5×I_transient) | unknown | medium | **verified** |
| EQ-042 | `check_thermal_emc` | DC bias derating lookup + ferrite µ thermal degradation | thermal | medium | **verified** |
| EQ-043 | `check_via_stitching` | spacing = √(area/count) vs λ/20 (via stitching check) | parasitic | high | **verified** |

## extract_parasitics.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-016 | `trace_resistance` | R = ρL/(WT) (DC trace resistance) | parasitic | high | **verified** |
| EQ-017 | `via_resistance` | R = ρH/(π(r²outer-r²inner)) (via barrel resistance) | parasitic | high | **verified** |
| EQ-018 | `via_inductance` | L = (µ₀H/2π)ln(2H/D) (via self-inductance) | parasitic | high | **verified** |
| EQ-019 | `coupling_capacitance` | C = ε₀εrLT/S (inter-trace coupling capacitance, parallel-plate approx) | parasitic | high | **verified** |
| EQ-072 | `extract_parasitics` | Orchestrates EQ-016..019 per net from PCB data | parasitic | high | **verified** |

## kicad_utils.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-066 | `estimate_cap_esl` | ESL estimate from package size (empirical table) | unknown | medium | **verified** |
| EQ-067 | `estimate_cap_esr` | ESR estimate from package size + capacitance (empirical) | unknown | medium | **verified** |
| EQ-068 | `parse_value` | SI prefix: p=1e-12 n=1e-9 u=1e-6 m=1e-3 k=1e3 M=1e6 | unknown | medium | **verified** |

## signal_detectors.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-020 | `detect_rc_filters` | f_c = 1/(2πRC) (RC filter cutoff frequency) | filter_design | high | **verified** |
| EQ-021 | `detect_lc_filters` | f₀ = 1/(2π√(LC)) (LC resonant frequency) | filter_design | high | **verified** |
| EQ-022 | `detect_lc_filters` | Z₀ = √(L/C) (LC characteristic impedance) | filter_design | high | **verified** |
| EQ-069 | `detect_decoupling` | f_SRF = 1/(2π√(ESL×C)) (decoupling SRF) | filter_design | high | **verified** |
| EQ-070 | `detect_design_observations` | Threshold comparisons for design quality metrics | filter_design | high | **verified** |
| EQ-071 | `detect_opamp_circuits` | G = 1+Rf/Ri or -Rf/Ri; G_dB = 20log₁₀\|G\| (opamp gain) | opamp | medium | **verified** |

## spice_model_generator.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-073 | `generate_comparator_model` | V_out = Aol × (V+ - V-) clamped (comparator model) | spice_model | medium | **verified** |
| EQ-074 | `generate_opamp_model` | GBW = Aol × f_pole (opamp behavioral SPICE model) | spice_model | medium | **verified** |

## spice_models.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-075 | `_format_eng` | SI engineering notation formatting | spice_model | medium | **verified** |

## spice_results.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-076 | `evaluate_bridge_circuit` | Gate sweep Vgs threshold detection | spice_model | medium | **verified** |
| EQ-077 | `evaluate_snubber` | f_damp from AC impedance minimum detection | spice_model | medium | **verified** |
| EQ-078 | `evaluate_transistor_circuit` | Vth from DC sweep (transistor threshold detection) | spice_model | medium | **verified** |

## spice_templates.py

| ID | Function | Formula | Category | Impact | Status |
|---|---|---|---|---|---|
| EQ-079 | `_get_parasitic_lines` | R_trace + L_via parasitic element injection | spice_model | medium | **verified** |
| EQ-080 | `generate_crystal_circuit` | C_L = 1/(1/C₁+1/C₂) + C_stray (crystal load cap) | spice_model | medium | **verified** |
| EQ-081 | `generate_decoupling` | \|Z\| at target freq from ESR+ESL cap model | spice_model | medium | **verified** |
| EQ-082 | `generate_inrush` | I_peak = V/R at t=0 (startup inrush current) | spice_model | medium | **verified** |
| EQ-083 | `generate_lc_filter` | f₀ = 1/(2π√(LC)) testbench (validates EQ-021) | spice_model | medium | **verified** |
| EQ-084 | `generate_opamp_circuit` | G_expected = 1+Rf/Ri or -Rf/Ri (validates EQ-071) | spice_model | medium | **verified** |
| EQ-085 | `generate_snubber` | f_damp = 1/(2πRC) (snubber damping frequency) | spice_model | medium | **verified** |
