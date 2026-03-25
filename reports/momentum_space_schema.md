# Momentum-Space Input Schema and Maxwell–Jüttner Sampler

**Milestone:** Priority 2 — Add momentum-space distribution specification and
Maxwell–Jüttner initialization metadata.

**Date:** 2026-03-25  
**Status:** Complete — sampler implemented, schema defined, 59 tests pass.

---

## Scientific motivation

Priority 1 established three literature-grounded benchmark targets for
relativistic 1D3V electrostatic PIC (two-stream instability, bump-on-tail
instability, energy-conservation stress test).  Executing those benchmarks
requires initialized particle distributions that are physically correct in the
relativistic regime.

The current JAX-in-Cell code initializes particles from a drifting Maxwell–
Boltzmann (Maxwellian) distribution parameterised by thermal velocity
`vth_electrons_over_c_x`.  This is **incorrect for relativistic beams** for
two reasons:

1. The Maxwellian distribution does not converge to the correct equilibrium in
   special relativity.  The correct relativistic thermal equilibrium distribution
   is the **Maxwell–Jüttner (MJ) distribution** (Jüttner 1911; Synge 1957).

2. The existing input schema specifies particle state in velocity space
   (`vth`, `electron_drift_speed_x`).  A momentum-space description in terms of
   normalized momentum p̃ = γβ is more natural and avoids ambiguity when
   Lorentz factors exceed unity.

This milestone adds:
- a momentum-space input schema (`configs/momentum_space_schema.toml`) with a
  `[[relativistic_species]]` section,
- a pure-Python Maxwell–Jüttner sampler (`src/jaxincell_drift_opt/maxwell_juttner.py`),
- backward-compatible mapping from `vth_electrons_over_c_x` to dimensionless
  temperature Θ, and
- moment validation utilities to confirm sampled distributions are correct.

---

## Physical background

### The Maxwell–Jüttner distribution

The relativistic equilibrium single-particle distribution function in 3D
momentum space is (Jüttner 1911):

```
f(p) ∝ exp(-γ / Θ)
```

where:

| Symbol | Meaning |
|---|---|
| **p̃** = p/(m_e c) | normalized 3-momentum |
| γ = √(1 + \|p̃\|²) | Lorentz factor |
| Θ = k_B T / (m_e c²) | dimensionless temperature |

The isotropic radial density is:

```
f(|p̃|) d|p̃| ∝ |p̃|² exp(-γ / Θ) d|p̃|
```

The 1D J-distribution (distribution of a single component p_x from the
full 3D MJ distribution) is:

```
f₁(p_x) ∝ exp(-√(1 + p_x²) / Θ)
```

### Non-relativistic limit and backward compatibility

In the non-relativistic limit (Θ ≪ 1, |p̃| ≪ 1):

```
γ ≈ 1 + p̃²/2  →  exp(-γ/Θ) ≈ exp(-1/Θ) · exp(-|p̃|²/(2Θ))
```

This reduces to a Gaussian (Maxwellian) in each component with variance Θ,
giving the backward-compatible mapping:

```
Θ = (vth/c)²   →   vth/c = √Θ
```

This is implemented as `theta_from_vth` and `vth_from_theta`.

### Analytic moments

For the 3D isotropic MJ distribution:

| Quantity | NR limit (Θ→0) | UR limit (Θ→∞) |
|---|---|---|
| ⟨γ⟩ | 1 + (3/2)Θ | ≈ 3Θ |
| ⟨\|p̃\|²⟩ | 3Θ | ≈ 12Θ² |

For the 1D J-distribution:

| Quantity | NR limit (Θ→0) |
|---|---|
| ⟨p_x⟩ | 0 |
| ⟨p_x²⟩ | Θ |

These analytic values are computed by numerical integration of the stabilized
integrand `u² exp(-(γ−1)/Θ)`, which factors out the common `exp(−1/Θ)` and
avoids underflow at small Θ.

### Sampling method

Both the 1D and 3D samplers use **inverse CDF** sampling via numerical
integration on a fine adaptive grid:

1. Compute the unnormalized PDF on a grid with p_max adapted to the
   distribution width (`p_max ~ max(50√Θ, 20Θ, 15)`).
2. Numerically integrate with `scipy.integrate.cumulative_trapezoid`.
3. Invert via `scipy.interpolate.interp1d`.

For the 3D isotropic distribution, the magnitude |p̃| is sampled from the
radial CDF, and the direction is drawn uniformly on the unit sphere using the
standard normal-vector trick.

Drifting distributions (beam species) are produced by applying a relativistic
Lorentz boost (`boost_momentum`) to thermal samples drawn at rest.

**Reference:** Zenitani, S. (2015). Loading relativistic Maxwell distributions
in particle simulations. *Phys. Plasmas*, **22**, 042116.

---

## Implementation artifacts

| Artifact | Purpose |
|---|---|
| `src/jaxincell_drift_opt/maxwell_juttner.py` | Sampler, analytic moments, moment validator, Lorentz boost |
| `configs/momentum_space_schema.toml` | Example momentum-space TOML schema with `[[relativistic_species]]` |
| `tests/test_maxwell_juttner.py` | 59 tests covering theta mapping, analytic limits, sampling moments, boost |

### Public API

```python
from jaxincell_drift_opt.maxwell_juttner import (
    theta_from_vth,               # vth/c → Θ (NR backward-compat)
    vth_from_theta,               # Θ → vth/c (NR approximation)
    sample_maxwell_juttner_1d,    # Sample p_x from 1D J-distribution
    sample_maxwell_juttner_3d,    # Sample (p_x, p_y, p_z) from 3D isotropic MJ
    boost_momentum,               # Lorentz boost 3-momenta along an axis
    mean_gamma_analytic,          # Analytic ⟨γ⟩ for 3D MJ
    mean_p2_analytic,             # Analytic ⟨|p̃|²⟩ for 3D MJ
    mean_px2_analytic_1d,         # Analytic ⟨p_x²⟩ for 1D J-distribution
    validate_sample_moments_1d,   # Statistical validation: 1D sampler moments
    validate_sample_moments_3d,   # Statistical validation: 3D sampler moments
)
```

---

## Validation performed

All 99 repository tests pass (`pytest tests/ -q`).

### Analytic moment checks

| Quantity | NR limit (Θ=0.001) | Computed | Error |
|---|---|---|---|
| ⟨γ⟩₃D | 1.00150 | 1.00150 | < 0.1 % |
| ⟨\|p̃\|²⟩₃D | 0.00300 | 0.00300 | < 0.1 % |
| ⟨p_x²⟩₁D_J | 0.00100 | 0.00100 | < 1 % |
| ⟨γ⟩₃D UR (Θ=20) | ≈ 60 | within 5 % of 60 | pass |

### Sampler moment validation (N=100 000, seed=42, 5σ tolerance)

| Test case | Θ | ⟨γ⟩ | ⟨\|p̃\|²⟩ | Isotropy |
|---|---|---|---|---|
| NR regime (3D) | 0.0025 | ✓ | ✓ | ✓ |
| Mildly relativistic (3D) | 0.09 | ✓ | ✓ | ✓ |
| Relativistic (3D) | 1.0 | ✓ | ✓ | ✓ |
| Ultra-relativistic (3D) | 5.0 | ✓ | ✓ | ✓ |
| NR regime (1D) | 0.0025 | — | ✓ | — |
| Mildly relativistic (1D) | 0.09 | — | ✓ | — |
| Relativistic (1D) | 1.0 | — | ✓ | — |
| Ultra-relativistic (1D) | 5.0 | — | ✓ | — |

### Lorentz boost validation

- Zero-drift boost is identity (passes to 10⁻¹² relative tolerance).
- Boost of rest-frame particle `(p̃=0)` at β=0.6 produces p̃_x = γ_d β_d (exact).
- Cold beam (Θ=10⁻⁴) boosted to β=√3/2 gives ⟨γ⟩ ≈ 2.0 ± 1 %.

---

## Limitations and residual risks

1. **CDF grid resolution at very small Θ.** The adaptive grid works well for
   Θ ≥ 10⁻⁴, but for extremely cold distributions (Θ < 10⁻⁵) the distribution
   is so sharply peaked that a uniform grid may under-resolve it.  The minimum
   recommended Θ for reliable sampling is 10⁻⁵.  Colder beams should be
   initialized by direct Lorentz boost from an even colder starting point.

2. **1D J-distribution vs 3D marginal.** The `sample_maxwell_juttner_1d`
   function samples from the 1D J-distribution f₁(p_x) ∝ exp(-γ/Θ), which is
   **not** the 1D marginal of the full 3D MJ distribution.  The correct
   initializer for a 1D3V PIC code is `sample_maxwell_juttner_3d`.  The 1D
   function is provided for theoretical comparison and for genuinely 1D problems.

3. **No JAX-in-Cell integration yet.** The sampler produces NumPy arrays.
   Connecting the new schema and sampler to the JAX-in-Cell particle
   initialization path requires upstream changes not made in this PR.

4. **No drift in transverse directions.** The `[[relativistic_species]]` schema
   supports `beta_drift_y` and `beta_drift_z` fields, but the boost utility
   currently applies a single-axis boost.  Multi-axis drift requires chaining
   boosts (not yet implemented).

5. **Ion sampling.** For heavy ions (mass_ratio ≫ 1) the temperature scale
   differs from that of electrons.  The current schema uses the same Θ
   definition (normalized to m_e c²), so the effective ion temperature in
   physical units is mass_ratio × Θ × m_e c².  This must be documented
   clearly when connecting to JAX-in-Cell.

---

## Next recommended milestone

**Priority 3: Conservation diagnostics and standardized benchmark reports.**

- Implement a `diagnostics.py` module that computes total (kinetic + field)
  energy, total canonical momentum, and their relative drift over time from
  a PIC output trajectory.
- Define a standardized JSON report format for benchmark run summaries,
  including the measured growth rate, energy drift, and pass/fail status
  against the targets in `configs/relativistic_benchmarks.yaml`.
- Add utilities to compare measured growth rates against the analytic
  estimates from `relativistic_benchmarks.py` and flag deviations outside
  the stated tolerance bands.
- This milestone does not require actual PIC runs; it can be validated with
  synthetic (analytic) energy trajectories that mimic the expected outputs.

**Scientific references for Priority 3:**

- Birdsall, C. K. & Langdon, A. B. (1991). *Plasma Physics via Computer
  Simulation*. IOP Publishing. (Chapter 4: diagnostics and energy conservation.)
- Vay, J.-L. (2008). *Phys. Plasmas*, **15**, 056701. (Section III: energy
  conservation properties of relativistic particle pushers.)
- Shadwick, B. A., Tarkenton, G. M., & Esarey, E. H. (2002). *Phys. Rev. Lett.*,
  **93**, 175002. (Hamiltonian variational formulation and energy conservation.)
