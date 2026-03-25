# Relativistic PIC Benchmark Plan

**Milestone:** Priority 1 — Define benchmark cases and literature reproduction
targets for relativistic 1D3V electrostatic PIC.

**Date:** 2026-03-25  
**Status:** Complete — benchmark specifications implemented and validated.

---

## Scientific motivation

JAX-in-Cell currently integrates particle trajectories in velocity space
(`vth_electrons_over_c_x`, `electron_drift_speed_x`) and sets `relativistic =
false` by default.  Before any upstream code changes are proposed, this
repository must establish *concrete, falsifiable reproduction targets* from the
published literature so that future relativistic runs can be validated.

This report defines three benchmark cases, grounded in the cold-fluid
relativistic dispersion theory, that span the key physics regimes of a 1D3V
electrostatic PIC code operating at relativistic beam energies.

---

## Normalization conventions

All benchmark cases use the following normalisation (defined in
`configs/relativistic_benchmarks.yaml`):

| Quantity | Normalisation | Symbol |
|---|---|---|
| time | inverse electron plasma frequency | t ω_pe |
| velocity | speed of light | β = v/c |
| momentum | m_e c | p̃ = p / (m_e c) = γβ |
| length | electron inertial length | x ω_pe / c |
| electric field | m_e c ω_pe / e | Ẽ |

These conventions match the standard used in JAX-in-Cell and in the benchmark
literature (Birdsall & Langdon 1991; Vay 2008).

---

## Benchmark Case 1: Relativistic two-stream instability

### Physical setup

Two symmetric cold electron beams counter-streaming at Lorentz factor γ = 2
(β = √3/2 ≈ 0.866) in a stationary, cold-ion background.  Each beam carries
half the total electron density.

### Linear theory

The cold-fluid relativistic electrostatic dispersion relation for symmetric
beams is:

```
(ω_pe²/2) / [γ³ (ω − kv₀)²]  +  (ω_pe²/2) / [γ³ (ω + kv₀)²]  =  1
```

This is algebraically identical to the non-relativistic form but with an
effective plasma frequency `ω_pe,eff = ω_pe / γ^(3/2)`.  Maximising the
purely imaginary root over k gives the exact result:

```
Im(ω)_max / ω_pe  =  √f / 2  ×  γ^(−3/2)
```

where f = 0.5 is the fraction of electrons in each beam.

| Parameter | Value |
|---|---|
| γ_beam | 2.0 |
| β_beam | √3/2 ≈ 0.866 |
| Im(ω)_max / ω_pe (theory) | √0.5/2 × 2^(−3/2) = 0.125 |
| Tolerance | ±15 % |
| Optimal wave-number k c/ω_pe | ≈ 0.5 |

### Validation target

A relativistic 1D3V PIC run should exhibit exponential growth of longitudinal
electric field energy at a rate matching 0.125 ω_pe ± 15 %.

**References:**  
- Birdsall, C. K. & Langdon, A. B. (1991). *Plasma Physics via Computer Simulation*. IOP Publishing. (Ch. 15, relativistic PIC).  
- Bret, A., Firpo, M.-C., & Deutsch, C. (2005). Phys. Rev. Lett., **94**, 115002.

---

## Benchmark Case 2: Relativistic bump-on-tail instability

### Physical setup

Warm background electron plasma (n_background = 0.9 n₀, β_th = 0.05) plus a
cold relativistic electron beam (n_beam = 0.1 n₀, γ_beam = 3, β_beam ≈ 0.943).
This tests the beam-plasma resonance under relativistic kinematics.

### Linear theory

Near the Langmuir resonance `k v_beam ≈ ω_pe`, setting ω = ω_pe + δω gives
the cubic dispersion:

```
δω³  =  (n_b/n₀) / (2 γ_b³)  ×  ω_pe³
```

The growing complex root yields:

```
Im(ω)_max / ω_pe  =  (√3/2)  ×  (n_b / 2n₀)^(1/3)  ×  γ_b^(−1)
```

Note: the relativistic suppression is `γ_b^(−1)` (not `γ_b^(−1/3)`) because
the effective beam plasma frequency `ω_pe,b / γ_b^(3/2)` appears inside the
cubic, and the cube root of `γ_b^(−3)` gives `γ_b^(−1)`.

| Parameter | Value |
|---|---|
| n_b / n₀ | 0.1 |
| γ_beam | 3.0 |
| β_beam | √(8/9) ≈ 0.943 |
| Im(ω)_max / ω_pe (theory) | √3/2 × (0.05)^(1/3) × 1/3 ≈ 0.106 |
| Tolerance | ±30 % (warm background) |
| Resonance wave-number k c/ω_pe | ≈ 1.06 |

**References:**  
- Evstatiev, E. G. & Shadwick, B. A. (2013). J. Comput. Phys., **245**, 376.  
- Nicholson, D. R. (1983). *Introduction to Plasma Physics*. Wiley. (Ch. 7).

---

## Benchmark Case 3: Relativistic energy-conservation stress test

### Physical setup

Thermally initialised electrons (β_th = 0.3, moderately relativistic) in a
periodic box with no external fields and no instability drive.  This case
isolates integrator quality: total energy must not drift.

### Targets

| Scheme | Max energy drift |
|---|---|
| Implicit / energy-conserving (e.g. Crank–Nicolson) | < 0.1 % |
| Explicit Boris push (CFL = 0.5) | < 1 % |
| Total canonical momentum | < 0.1 % |

**References:**  
- Boris, J. P. (1970). Proc. 4th Conf. Numer. Simul. Plasmas, NRL, pp. 3–67.  
- Vay, J.-L. (2008). Phys. Plasmas, **15**, 056701. (Section III).

---

## Implementation artifacts

| Artifact | Purpose |
|---|---|
| `configs/relativistic_benchmarks.yaml` | Machine-readable benchmark specs with all parameters and reproduction targets |
| `src/jaxincell_drift_opt/relativistic_benchmarks.py` | Python interface: load specs, compute growth rates, validate self-consistency |
| `tests/test_relativistic_benchmarks.py` | 33 tests: YAML loading, physical self-consistency, kinematics helpers, growth-rate formulas |

---

## Validation performed

- All 38 repository tests pass (`pytest tests/ -v`).
- YAML self-consistency: gamma-beta values consistent to < 0.01 %.
- Growth-rate formulas verified against analytic limits:
  - Two-stream at γ=1: formula recovers classical result 1/(2√2) ≈ 0.354.
  - Two-stream at γ=2: 0.125 ω_pe (exact cold-fluid).
  - Bump-on-tail at γ_b=3, n_b/n₀=0.1: 0.106 ω_pe.
- Physical sanity checks: all growth rates positive and sub-ω_pe.

---

## Limitations and residual risks

1. **Cold-beam approximation.** Both growth-rate formulas assume zero thermal
   spread in the beams.  Thermal corrections reduce growth rates by
   O(β_th / β_drift).  The 15–30 % tolerances in the YAML account for this
   but should be replaced by more precise warm-beam dispersion solutions.

2. **Electrostatic approximation.** The benchmark cases assume purely
   electrostatic (longitudinal) waves.  At β > 0.5 the electromagnetic
   (transverse) Weibel instability can compete; in a full 1D3V simulation one
   must confirm the fastest-growing mode is longitudinal.

3. **No PIC runs yet.** These are literature-grounded reproduction *targets*,
   not yet measured against actual JAX-in-Cell outputs.  The targets will be
   tested when the `relativistic = true` path in JAX-in-Cell is enabled and
   momentum-based particle updates are available.

4. **Maxwell–Jüttner initialization not yet defined.** Proper relativistic
   thermalization of the beam populations requires sampling from the
   Maxwell–Jüttner distribution rather than a boosted Maxwellian.  This is the
   subject of the next milestone.

---

## Next recommended milestone

**Priority 2: Add momentum-space input schema and Maxwell–Jüttner initialization
metadata.**

- Define a `[relativistic_species]` input section in the TOML schema that
  specifies particles in terms of normalized momentum p̃ = γβ rather than
  velocity β.
- Add a Maxwell–Jüttner sampler (pure Python, scipy-based) that draws
  normalized 3-momenta from the relativistic thermal distribution at a given
  dimensionless temperature Θ = k_B T / (m_e c²).
- Add validation tests: sampled moments ⟨γ⟩, ⟨p̃²⟩ must match the known
  Maxwell–Jüttner analytic expressions within statistical error.
- Provide a mapping from the existing `vth_electrons_over_c_x` parameter to
  the corresponding Θ so the new schema is backward-compatible.
