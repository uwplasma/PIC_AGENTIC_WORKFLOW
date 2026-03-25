"""Maxwell–Jüttner distribution sampler and momentum-space utilities.

This module implements Priority 2 of the relativistic PIC milestone roadmap:
a momentum-space particle initialization scheme based on the Maxwell–Jüttner
(MJ) distribution, which is the relativistic analogue of the Maxwell–Boltzmann
distribution.

All momenta are expressed in normalized units:

    p̃ = p / (m_e c)  (dimensionless)

so that the Lorentz factor is gamma = sqrt(1 + p̃²).

The dimensionless temperature is:

    Theta = k_B T / (m_e c²)

For Theta << 1 (non-relativistic limit), the MJ distribution reduces to the
Maxwell–Boltzmann distribution with thermal velocity vth/c = sqrt(Theta), giving
the backward-compatible mapping ``theta_from_vth``.

Scientific references
---------------------
Jüttner, F. (1911).  Das Maxwellsche Gesetz der Geschwindigkeitsverteilung
  in der Relativtheorie.  *Ann. Phys.*, **34**, 856–882.

Synge, J. L. (1957).  *The Relativistic Gas*.  North-Holland.

Zenitani, S. (2015).  Loading relativistic Maxwell distributions in particle
  simulations.  *Phys. Plasmas*, **22**, 042116.
  doi:10.1063/1.4919383

Vay, J.-L. (2008).  Simulation of beams or plasmas crossing at relativistic
  velocity.  *Phys. Plasmas*, **15**, 056701.  doi:10.1063/1.2837054

Birdsall, C. K. & Langdon, A. B. (1991).  *Plasma Physics via Computer
  Simulation*.  IOP Publishing.  (Chapter 15: relativistic PIC.)
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d

__all__ = [
    "theta_from_vth",
    "vth_from_theta",
    "sample_maxwell_juttner_1d",
    "sample_maxwell_juttner_3d",
    "boost_momentum",
    "mean_gamma_analytic",
    "mean_p2_analytic",
    "mean_px2_analytic_1d",
    "validate_sample_moments_1d",
    "validate_sample_moments_3d",
    "MomentValidationResult",
]


# ---------------------------------------------------------------------------
# Temperature ↔ thermal-velocity mapping
# ---------------------------------------------------------------------------

def theta_from_vth(vth_over_c: float) -> float:
    """Convert non-relativistic thermal velocity to dimensionless temperature.

    In the non-relativistic limit the Maxwell–Boltzmann 1D thermal velocity
    along any axis satisfies::

        vth² = k_B T / m_e  →  (vth/c)² = k_B T / (m_e c²) = Theta

    This mapping provides backward compatibility with the existing
    ``vth_electrons_over_c_x`` parameter in ``configs/base_input.toml``.

    Parameters
    ----------
    vth_over_c:
        Thermal velocity normalized to the speed of light (vth/c).  Must be
        non-negative and strictly less than 1.

    Returns
    -------
    float
        Dimensionless temperature Theta = k_B T / (m_e c²).

    Notes
    -----
    The mapping is exact in the non-relativistic limit.  For vth/c > 0.3 the
    Maxwell–Jüttner distribution differs significantly from a Maxwellian and
    this approximation underestimates the true relativistic thermal width.
    """
    if vth_over_c < 0.0 or vth_over_c >= 1.0:
        raise ValueError(
            f"vth_over_c must be in [0, 1), got {vth_over_c!r}"
        )
    return vth_over_c ** 2


def vth_from_theta(theta: float) -> float:
    """Convert dimensionless temperature to the non-relativistic thermal velocity.

    This is the inverse of :func:`theta_from_vth`:  vth/c = sqrt(Theta).

    Parameters
    ----------
    theta:
        Dimensionless temperature Theta = k_B T / (m_e c²).  Must be >= 0.

    Returns
    -------
    float
        Non-relativistic thermal velocity vth/c.

    Notes
    -----
    Valid as a backward-compatible approximation when Theta << 1.  For large
    Theta the true relativistic mean speed differs from sqrt(Theta).
    """
    if theta < 0.0:
        raise ValueError(f"theta must be >= 0, got {theta!r}")
    return math.sqrt(theta)


# ---------------------------------------------------------------------------
# Analytic moment integrals
# ---------------------------------------------------------------------------
#
# Numerical stability note
# ------------------------
# The Maxwell–Jüttner weight exp(-gamma/Theta) underflows to zero for small
# Theta because gamma >= 1 and exp(-1/Theta) → 0 as Theta → 0.  All moment
# integrals are *ratios*, however, so we factor out the common exp(-1/Theta)
# and integrate the stabilised weight:
#
#     w(u) = exp(-(gamma - 1) / Theta)
#
# This is numerically well-conditioned for all Theta > 0.  The factor
# exp(-1/Theta) cancels exactly in every numerator/denominator ratio.

def _u_max(theta: float) -> float:
    """Return a safe upper integration limit covering the meaningful tail."""
    # For small Theta the distribution is sharply peaked at u ~ sqrt(2*Theta).
    # For large Theta the distribution extends to u ~ 15*Theta.
    peak = math.sqrt(max(2.0 * theta, 1e-30))
    return max(50.0 * peak, 20.0 * theta, 15.0)


def _mj_3d_norm_stable(theta: float) -> float:
    """Return the stabilised 3D MJ norm ∫₀^∞ u² exp(-(gamma-1)/Theta) du."""
    def integrand(u: float) -> float:
        gamma = math.sqrt(1.0 + u * u)
        return u * u * math.exp(-(gamma - 1.0) / theta)
    result, _ = quad(integrand, 0.0, _u_max(theta), limit=400)
    return result


def mean_gamma_analytic(theta: float) -> float:
    """Compute the analytic mean Lorentz factor ⟨gamma⟩ for a 3D isotropic
    Maxwell–Jüttner distribution at dimensionless temperature *theta*.

    .. math::

        \\langle \\gamma \\rangle =
        \\frac{\\int_0^\\infty \\sqrt{1+u^2}\\, u^2 e^{-(\\sqrt{1+u^2}-1)/\\Theta}\\,du}
              {\\int_0^\\infty u^2 e^{-(\\sqrt{1+u^2}-1)/\\Theta}\\,du}

    The integrands are factored to remove the common exp(-1/Theta) for
    numerical stability at small Theta.

    Parameters
    ----------
    theta:
        Dimensionless temperature Theta = k_B T / (m_e c²).  Must be > 0.

    Returns
    -------
    float
        ⟨gamma⟩ >= 1.  Approaches 1 + 1.5 * theta in the NR limit (theta→0)
        and 3 * theta in the ultra-relativistic limit (theta→∞).
    """
    if theta <= 0.0:
        raise ValueError(f"theta must be > 0, got {theta!r}")

    def numerator_integrand(u: float) -> float:
        gamma = math.sqrt(1.0 + u * u)
        return gamma * u * u * math.exp(-(gamma - 1.0) / theta)

    num, _ = quad(numerator_integrand, 0.0, _u_max(theta), limit=400)
    den = _mj_3d_norm_stable(theta)
    return num / den


def mean_p2_analytic(theta: float) -> float:
    """Compute the analytic mean squared 3-momentum ⟨|p̃|²⟩ for a 3D isotropic
    Maxwell–Jüttner distribution.

    .. math::

        \\langle |\\tilde{p}|^2 \\rangle =
        \\frac{\\int_0^\\infty u^4 e^{-(\\sqrt{1+u^2}-1)/\\Theta}\\,du}
              {\\int_0^\\infty u^2 e^{-(\\sqrt{1+u^2}-1)/\\Theta}\\,du}

    Parameters
    ----------
    theta:
        Dimensionless temperature Theta = k_B T / (m_e c²).  Must be > 0.

    Returns
    -------
    float
        ⟨|p̃|²⟩.  In the NR limit this approaches 3 * theta.
        In the UR limit this approaches 12 * theta².
    """
    if theta <= 0.0:
        raise ValueError(f"theta must be > 0, got {theta!r}")

    def numerator_integrand(u: float) -> float:
        gamma = math.sqrt(1.0 + u * u)
        return u ** 4 * math.exp(-(gamma - 1.0) / theta)

    num, _ = quad(numerator_integrand, 0.0, _u_max(theta), limit=400)
    den = _mj_3d_norm_stable(theta)
    return num / den


def mean_px2_analytic_1d(theta: float) -> float:
    """Compute the analytic ⟨p_x²⟩ for the 1D J-distribution.

    The *1D J-distribution* is the single-component Maxwell–Jüttner
    distribution used by :func:`sample_maxwell_juttner_1d`:

    .. math::

        f_1(p_x) \\propto e^{-(\\sqrt{1+p_x^2}-1)/\\Theta}

    The second moment is:

    .. math::

        \\langle p_x^2 \\rangle_{1D} =
        \\frac{\\int_0^\\infty p^2 e^{-(\\sqrt{1+p^2}-1)/\\Theta}\\,dp}
              {\\int_0^\\infty e^{-(\\sqrt{1+p^2}-1)/\\Theta}\\,dp}

    Note: this is **not** equal to ⟨|p̃|²⟩₃D / 3, because the 3D isotropic
    distribution and the 1D J-distribution have different forms.
    The 1D J-distribution ⟨p_x²⟩ is smaller than the 3D marginal ⟨p_x²⟩
    at the same Theta because in 3D the two transverse momenta contribute to
    gamma, widening the distribution in each component.

    In the NR limit (Theta → 0): ⟨p_x²⟩ → Theta for both distributions.

    Parameters
    ----------
    theta:
        Dimensionless temperature.  Must be > 0.

    Returns
    -------
    float
        ⟨p_x²⟩ for the 1D J-distribution.  Approaches Theta in the NR limit.
    """
    if theta <= 0.0:
        raise ValueError(f"theta must be > 0, got {theta!r}")

    u_max = _u_max(theta)

    def num_integrand(u: float) -> float:
        gamma = math.sqrt(1.0 + u * u)
        return u * u * math.exp(-(gamma - 1.0) / theta)

    def den_integrand(u: float) -> float:
        gamma = math.sqrt(1.0 + u * u)
        return math.exp(-(gamma - 1.0) / theta)

    num, _ = quad(num_integrand, 0.0, u_max, limit=400)
    den, _ = quad(den_integrand, 0.0, u_max, limit=400)
    return num / den


# ---------------------------------------------------------------------------
# Internal CDF-inversion helpers
# ---------------------------------------------------------------------------

def _build_1d_mj_cdf(
    theta: float,
    n_grid: int = 4000,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a numerical CDF for the *symmetric* 1D J-distribution on [-p_max, p_max].

    The 1D J-distribution for component p_x with no drift is:

        f(p_x) ∝ exp(-(sqrt(1 + p_x²) - 1) / Theta)

    The common factor exp(-1/Theta) has been divided out for numerical
    stability at small Theta (see module-level note).

    Returns
    -------
    p_grid : ndarray
        Momentum grid (symmetric, ascending).
    cdf_grid : ndarray
        Cumulative distribution values in [0, 1].
    """
    # Adaptive p_max: cover the distribution tail adequately.
    # The half-width scales as sqrt(Theta) in the NR limit.
    p_max = _u_max(theta)
    p_pos = np.linspace(0.0, p_max, n_grid // 2 + 1)
    gamma_pos = np.sqrt(1.0 + p_pos ** 2)
    pdf_pos = np.exp(-(gamma_pos - 1.0) / theta)
    # Integrate the positive half using the trapezoidal rule
    from scipy.integrate import cumulative_trapezoid
    half_cdf = cumulative_trapezoid(pdf_pos, p_pos, initial=0.0)
    total_half = half_cdf[-1]
    if total_half == 0.0:
        raise ValueError(
            f"1D MJ CDF integral is zero at theta={theta!r}; "
            "the grid may need more resolution."
        )

    # Full grid: negative side (mirror of positive), then positive
    p_neg = -p_pos[::-1]  # high negative to 0
    pdf_neg = pdf_pos[::-1]
    half_cdf_neg = cumulative_trapezoid(pdf_neg, p_neg, initial=0.0)

    p_grid = np.concatenate([p_neg, p_pos[1:]])
    cdf_neg = half_cdf_neg / (2.0 * total_half)
    cdf_pos = 0.5 + half_cdf[1:] / (2.0 * total_half)
    cdf_grid = np.concatenate([cdf_neg, cdf_pos])

    # Clamp to [0, 1] and ensure monotonicity
    cdf_grid = np.clip(cdf_grid, 0.0, 1.0)
    return p_grid, cdf_grid


def _build_3d_mj_magnitude_cdf(
    theta: float,
    n_grid: int = 4000,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a numerical CDF for the radial magnitude |p̃| from the 3D MJ.

    The stabilised radial density is:

        f(u) ∝ u² exp(-(sqrt(1 + u²) - 1) / Theta),   u >= 0

    Returns
    -------
    u_grid : ndarray
        Grid of |p̃| values.
    cdf_grid : ndarray
        Corresponding CDF values in [0, 1].
    """
    u_max = _u_max(theta)
    u_grid = np.linspace(0.0, u_max, n_grid)
    gamma_grid = np.sqrt(1.0 + u_grid ** 2)
    pdf = u_grid ** 2 * np.exp(-(gamma_grid - 1.0) / theta)
    from scipy.integrate import cumulative_trapezoid
    cdf_grid = cumulative_trapezoid(pdf, u_grid, initial=0.0)
    if cdf_grid[-1] == 0.0:
        raise ValueError(
            f"3D MJ magnitude CDF integral is zero at theta={theta!r}; "
            "the grid may need more resolution."
        )
    cdf_grid /= cdf_grid[-1]
    cdf_grid = np.clip(cdf_grid, 0.0, 1.0)
    return u_grid, cdf_grid


# ---------------------------------------------------------------------------
# Sampling functions
# ---------------------------------------------------------------------------

def sample_maxwell_juttner_1d(
    theta: float,
    n_particles: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Sample normalized 1D momenta p_x from a Maxwell–Jüttner distribution
    at rest (zero drift).

    The 1D marginal distribution for the x-component is:

        f(p_x) ∝ exp(-sqrt(1 + p_x²) / Theta)

    Sampling is performed via numerical inversion of the CDF, which is
    exact to within the interpolation error of the numerical grid.

    Parameters
    ----------
    theta:
        Dimensionless temperature Theta = k_B T / (m_e c²).  Must be > 0.
    n_particles:
        Number of momenta to sample.
    rng:
        NumPy random Generator.  If ``None``, a fresh default-seeded generator
        is created (results will be non-reproducible across runs).

    Returns
    -------
    ndarray of shape (n_particles,)
        Normalized 1D momenta p̃_x = p_x / (m_e c).

    Notes
    -----
    The CDF inversion is implemented by precomputing a fine numerical grid and
    using linear interpolation.  The method is valid for all theta > 0 and does
    not require special functions.

    For a drifting distribution, apply :func:`boost_momentum` to the result
    (requires knowing the drift momentum in all three components first; use
    :func:`sample_maxwell_juttner_3d` + :func:`boost_momentum` instead).
    """
    if theta <= 0.0:
        raise ValueError(f"theta must be > 0, got {theta!r}")
    if n_particles <= 0:
        raise ValueError(f"n_particles must be > 0, got {n_particles!r}")
    if rng is None:
        rng = np.random.default_rng()

    p_grid, cdf_grid = _build_1d_mj_cdf(theta)
    inv_cdf = interp1d(cdf_grid, p_grid, kind="linear", bounds_error=False,
                       fill_value=(p_grid[0], p_grid[-1]))
    u_uniform = rng.uniform(0.0, 1.0, size=n_particles)
    return inv_cdf(u_uniform)


def sample_maxwell_juttner_3d(
    theta: float,
    n_particles: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Sample normalized 3D momenta (p_x, p_y, p_z) from an isotropic
    Maxwell–Jüttner distribution at rest (zero drift).

    The distribution is isotropic in momentum space:

        f(p) d³p ∝ exp(-gamma / Theta) d³p,   gamma = sqrt(1 + p_x² + p_y² + p_z²)

    Sampling proceeds in two steps:
    1. Draw the magnitude |p̃| from the radial distribution
       f(u) ∝ u² exp(-sqrt(1+u²)/Theta) using numerical CDF inversion.
    2. Draw a uniformly random direction on the unit sphere.

    Parameters
    ----------
    theta:
        Dimensionless temperature Theta = k_B T / (m_e c²).  Must be > 0.
    n_particles:
        Number of 3-vectors to sample.
    rng:
        NumPy random Generator.  If ``None``, a fresh generator is created.

    Returns
    -------
    ndarray of shape (n_particles, 3)
        Each row is (p̃_x, p̃_y, p̃_z) = (p_x, p_y, p_z) / (m_e c).

    Notes
    -----
    The sampled distribution is exactly isotropic in the rest frame.  To
    initialize a drifting beam, apply :func:`boost_momentum` after sampling.
    """
    if theta <= 0.0:
        raise ValueError(f"theta must be > 0, got {theta!r}")
    if n_particles <= 0:
        raise ValueError(f"n_particles must be > 0, got {n_particles!r}")
    if rng is None:
        rng = np.random.default_rng()

    # Step 1: sample magnitude
    u_grid, cdf_grid = _build_3d_mj_magnitude_cdf(theta)
    inv_cdf = interp1d(cdf_grid, u_grid, kind="linear", bounds_error=False,
                       fill_value=(u_grid[0], u_grid[-1]))
    u_uniform = rng.uniform(0.0, 1.0, size=n_particles)
    magnitudes = inv_cdf(u_uniform)

    # Step 2: sample isotropic direction using normal distribution trick
    # Sampling uniform direction: draw 3 standard normals, normalize
    directions = rng.standard_normal(size=(n_particles, 3))
    norms = np.linalg.norm(directions, axis=1, keepdims=True)
    # Avoid division by zero (astronomically unlikely, but safe)
    norms = np.where(norms == 0.0, 1.0, norms)
    directions /= norms

    return magnitudes[:, np.newaxis] * directions


def boost_momentum(
    momenta: np.ndarray,
    beta_drift: float,
    axis: int = 0,
) -> np.ndarray:
    """Apply a relativistic Lorentz boost to an array of 3-momenta.

    Given particles with rest-frame momenta (p̃_x, p̃_y, p̃_z), this function
    computes the momenta as seen in a frame moving at velocity beta_drift along
    the chosen *axis*, which is equivalent to initialising particles drifting
    at beta_drift in the lab frame.

    The boost of a 4-momentum (gamma, p̃_x, p̃_y, p̃_z) along the x-axis is:

    .. math::

        \\gamma' = \\gamma_d (\\gamma + \\beta_d \\tilde{p}_x)

        \\tilde{p}_x' = \\gamma_d (\\tilde{p}_x + \\beta_d \\gamma)

        \\tilde{p}_y' = \\tilde{p}_y, \\quad \\tilde{p}_z' = \\tilde{p}_z

    where :math:`\\gamma_d = 1/\\sqrt{1-\\beta_d^2}`.

    Parameters
    ----------
    momenta:
        Array of shape (N, 3) with columns (p̃_x, p̃_y, p̃_z).
    beta_drift:
        Drift velocity along *axis* in units of c.  Must satisfy
        ``-1 < beta_drift < 1``.
    axis:
        Spatial axis to boost along: 0 = x, 1 = y, 2 = z.

    Returns
    -------
    ndarray of shape (N, 3)
        Boosted momenta.
    """
    if momenta.ndim != 2 or momenta.shape[1] != 3:
        raise ValueError(
            f"momenta must have shape (N, 3), got {momenta.shape!r}"
        )
    if not (-1.0 < beta_drift < 1.0):
        raise ValueError(
            f"beta_drift must satisfy -1 < beta_drift < 1, got {beta_drift!r}"
        )
    if axis not in (0, 1, 2):
        raise ValueError(f"axis must be 0, 1, or 2, got {axis!r}")

    gamma_d = 1.0 / math.sqrt(1.0 - beta_drift ** 2)
    p_out = momenta.copy()
    p_axis = momenta[:, axis]
    # Lorentz factor of each particle in the rest frame
    gamma_particles = np.sqrt(1.0 + np.sum(momenta ** 2, axis=1))
    p_out[:, axis] = gamma_d * (p_axis + beta_drift * gamma_particles)
    # Note: energy (gamma) is also boosted, but for a PIC code we only need
    # the 3-momentum components; gamma is recomputed from p in the pusher.
    return p_out


# ---------------------------------------------------------------------------
# Moment validation
# ---------------------------------------------------------------------------

class MomentValidationResult:
    """Container for the result of a moment validation check.

    Attributes
    ----------
    passed : bool
        Whether the validation passed (sampled moments within tolerance of
        analytic values).
    theta : float
        Dimensionless temperature used.
    n_particles : int
        Number of particles sampled.
    checks : list[dict]
        Per-quantity check results, each with keys:
        ``name``, ``sampled``, ``analytic``, ``rel_err``, ``tol``,
        ``passed``.
    """

    def __init__(
        self,
        theta: float,
        n_particles: int,
        checks: list[dict],
    ) -> None:
        self.theta = theta
        self.n_particles = n_particles
        self.checks = checks
        self.passed = all(c["passed"] for c in checks)

    def __repr__(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        lines = [f"MomentValidationResult [{status}] theta={self.theta}, N={self.n_particles}"]
        for c in self.checks:
            flag = "✓" if c["passed"] else "✗"
            lines.append(
                f"  {flag} {c['name']}: sampled={c['sampled']:.6g}, "
                f"analytic={c['analytic']:.6g}, "
                f"rel_err={c['rel_err']:.3e} (tol={c['tol']:.3e})"
            )
        return "\n".join(lines)


def validate_sample_moments_1d(
    theta: float,
    n_particles: int = 50_000,
    rng: np.random.Generator | None = None,
    n_sigma: float = 5.0,
) -> MomentValidationResult:
    """Validate 1D Maxwell–Jüttner samples against analytic moments.

    Draws *n_particles* samples from :func:`sample_maxwell_juttner_1d` and
    checks that ⟨p_x²⟩ and ⟨p_x⟩ match the analytic values within
    *n_sigma* standard errors.

    Parameters
    ----------
    theta:
        Dimensionless temperature.
    n_particles:
        Number of particles to sample (larger → smaller statistical error).
    rng:
        NumPy random Generator for reproducibility.
    n_sigma:
        Number of standard errors to use as the acceptance tolerance.

    Returns
    -------
    MomentValidationResult
    """
    if rng is None:
        rng = np.random.default_rng()

    samples = sample_maxwell_juttner_1d(theta, n_particles, rng=rng)
    checks = []

    # Check 1: ⟨p_x⟩ should be 0 (symmetric distribution, no drift)
    sampled_mean = float(np.mean(samples))
    sampled_std = float(np.std(samples))
    se_mean = sampled_std / math.sqrt(n_particles)
    tol_mean = n_sigma * se_mean
    analytic_mean = 0.0
    rel_err_mean = abs(sampled_mean - analytic_mean) / (sampled_std + 1e-30)
    checks.append({
        "name": "<p_x>",
        "sampled": sampled_mean,
        "analytic": analytic_mean,
        "rel_err": abs(sampled_mean) / (sampled_std + 1e-30),
        "tol": n_sigma / math.sqrt(n_particles),
        "passed": abs(sampled_mean) < tol_mean,
    })

    # Check 2: ⟨p_x²⟩ should match analytic value
    sampled_p2 = float(np.mean(samples ** 2))
    analytic_p2 = mean_px2_analytic_1d(theta)
    # Standard error of the mean of p_x²
    se_p2 = float(np.std(samples ** 2)) / math.sqrt(n_particles)
    tol_p2 = n_sigma * se_p2 / (analytic_p2 + 1e-30)
    rel_err_p2 = abs(sampled_p2 - analytic_p2) / (analytic_p2 + 1e-30)
    checks.append({
        "name": "<p_x^2>",
        "sampled": sampled_p2,
        "analytic": analytic_p2,
        "rel_err": rel_err_p2,
        "tol": tol_p2,
        "passed": rel_err_p2 < tol_p2,
    })

    return MomentValidationResult(theta, n_particles, checks)


def validate_sample_moments_3d(
    theta: float,
    n_particles: int = 50_000,
    rng: np.random.Generator | None = None,
    n_sigma: float = 5.0,
) -> MomentValidationResult:
    """Validate 3D Maxwell–Jüttner samples against analytic moments.

    Draws *n_particles* samples from :func:`sample_maxwell_juttner_3d` and
    checks that ⟨gamma⟩ and ⟨|p̃|²⟩ match the analytic values within
    *n_sigma* standard errors.

    Parameters
    ----------
    theta:
        Dimensionless temperature.
    n_particles:
        Number of particles to sample.
    rng:
        NumPy random Generator.
    n_sigma:
        Acceptance tolerance in standard errors.

    Returns
    -------
    MomentValidationResult
    """
    if rng is None:
        rng = np.random.default_rng()

    samples = sample_maxwell_juttner_3d(theta, n_particles, rng=rng)
    p2 = np.sum(samples ** 2, axis=1)
    gammas = np.sqrt(1.0 + p2)
    checks = []

    # Check 1: ⟨gamma⟩
    sampled_gamma = float(np.mean(gammas))
    analytic_gamma = mean_gamma_analytic(theta)
    se_gamma = float(np.std(gammas)) / math.sqrt(n_particles)
    tol_gamma = n_sigma * se_gamma / (analytic_gamma + 1e-30)
    rel_err_gamma = abs(sampled_gamma - analytic_gamma) / (analytic_gamma + 1e-30)
    checks.append({
        "name": "<gamma>",
        "sampled": sampled_gamma,
        "analytic": analytic_gamma,
        "rel_err": rel_err_gamma,
        "tol": tol_gamma,
        "passed": rel_err_gamma < tol_gamma,
    })

    # Check 2: ⟨|p̃|²⟩
    sampled_p2 = float(np.mean(p2))
    analytic_p2 = mean_p2_analytic(theta)
    se_p2 = float(np.std(p2)) / math.sqrt(n_particles)
    tol_p2 = n_sigma * se_p2 / (analytic_p2 + 1e-30)
    rel_err_p2 = abs(sampled_p2 - analytic_p2) / (analytic_p2 + 1e-30)
    checks.append({
        "name": "<|p|^2>",
        "sampled": sampled_p2,
        "analytic": analytic_p2,
        "rel_err": rel_err_p2,
        "tol": tol_p2,
        "passed": rel_err_p2 < tol_p2,
    })

    # Check 3: isotropy — ⟨p_x²⟩ ≈ ⟨p_y²⟩ ≈ ⟨p_z²⟩
    px2 = float(np.mean(samples[:, 0] ** 2))
    py2 = float(np.mean(samples[:, 1] ** 2))
    pz2 = float(np.mean(samples[:, 2] ** 2))
    mean_comp = (px2 + py2 + pz2) / 3.0
    max_asymmetry = max(abs(px2 - mean_comp), abs(py2 - mean_comp), abs(pz2 - mean_comp))
    # Expected statistical scatter ~ std(p_i^2)/sqrt(N)
    se_comp = float(np.std(samples[:, 0] ** 2)) / math.sqrt(n_particles)
    tol_iso = n_sigma * se_comp / (mean_comp + 1e-30)
    rel_asym = max_asymmetry / (mean_comp + 1e-30)
    checks.append({
        "name": "isotropy |<px2>-<py2>|/<p2/3>",
        "sampled": rel_asym,
        "analytic": 0.0,
        "rel_err": rel_asym,
        "tol": tol_iso,
        "passed": rel_asym < tol_iso,
    })

    return MomentValidationResult(theta, n_particles, checks)
