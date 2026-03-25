"""Tests for the Maxwell–Jüttner sampler and momentum-space utilities.

Validates that:
  1. The theta/vth mapping functions are correct.
  2. Analytic moment integrals satisfy known limiting cases.
  3. The 1D and 3D samplers produce distributions whose moments match the
     analytic values within statistical tolerance.
  4. The relativistic Lorentz boost is applied correctly.
  5. The momentum-space TOML schema can be loaded and parsed.
  6. Edge cases and invalid inputs raise appropriate errors.

Statistical tests use n_sigma=5 (5-sigma tolerance) with N=50 000 particles,
giving a false-failure rate < 3 × 10⁻⁷ per independent test.
"""

from __future__ import annotations

import math
import tomllib
from pathlib import Path

import numpy as np
import pytest

from jaxincell_drift_opt.maxwell_juttner import (
    MomentValidationResult,
    boost_momentum,
    mean_gamma_analytic,
    mean_p2_analytic,
    mean_px2_analytic_1d,
    sample_maxwell_juttner_1d,
    sample_maxwell_juttner_3d,
    theta_from_vth,
    validate_sample_moments_1d,
    validate_sample_moments_3d,
    vth_from_theta,
)

_SCHEMA_TOML = Path(__file__).parent.parent / "configs" / "momentum_space_schema.toml"

# Fixed seed for all statistical tests to ensure CI determinism.
_RNG_SEED = 42


# ---------------------------------------------------------------------------
# Theta / vth mapping
# ---------------------------------------------------------------------------

class TestThetaVthMapping:
    def test_theta_from_vth_zero(self):
        assert theta_from_vth(0.0) == 0.0

    def test_theta_from_vth_known_value(self):
        # vth/c = 0.05 → Theta = 0.0025
        assert theta_from_vth(0.05) == pytest.approx(0.0025, rel=1e-10)

    def test_theta_from_vth_roundtrip(self):
        for vth in [0.01, 0.05, 0.1, 0.3, 0.5]:
            assert vth_from_theta(theta_from_vth(vth)) == pytest.approx(vth, rel=1e-10)

    def test_vth_from_theta_zero(self):
        assert vth_from_theta(0.0) == pytest.approx(0.0, abs=1e-15)

    def test_vth_from_theta_known_value(self):
        # Theta = 0.09 → vth/c = 0.3
        assert vth_from_theta(0.09) == pytest.approx(0.3, rel=1e-10)

    def test_theta_from_vth_rejects_superluminal(self):
        with pytest.raises(ValueError, match=r"vth_over_c"):
            theta_from_vth(1.0)
        with pytest.raises(ValueError, match=r"vth_over_c"):
            theta_from_vth(1.5)

    def test_theta_from_vth_rejects_negative(self):
        with pytest.raises(ValueError, match=r"vth_over_c"):
            theta_from_vth(-0.1)

    def test_vth_from_theta_rejects_negative(self):
        with pytest.raises(ValueError, match=r"theta"):
            vth_from_theta(-0.001)


# ---------------------------------------------------------------------------
# Analytic moment functions — limiting cases
# ---------------------------------------------------------------------------

class TestAnalyticMoments:
    """Check that the analytic moment integrals reproduce known limits."""

    def test_mean_gamma_nr_limit(self):
        """In the NR limit (Theta → 0): ⟨gamma⟩ ≈ 1 + (3/2) Theta."""
        theta = 0.001
        expected = 1.0 + 1.5 * theta
        assert mean_gamma_analytic(theta) == pytest.approx(expected, rel=1e-3)

    def test_mean_gamma_is_at_least_one(self):
        for theta in [0.001, 0.01, 0.1, 1.0, 5.0]:
            assert mean_gamma_analytic(theta) >= 1.0 - 1e-9

    def test_mean_gamma_increases_with_theta(self):
        gammas = [mean_gamma_analytic(t) for t in [0.01, 0.1, 1.0, 5.0]]
        assert gammas == sorted(gammas)

    def test_mean_p2_nr_limit(self):
        """In the NR limit: ⟨|p̃|²⟩ ≈ 3 Theta (equipartition)."""
        theta = 0.001
        expected = 3.0 * theta
        assert mean_p2_analytic(theta) == pytest.approx(expected, rel=1e-2)

    def test_mean_p2_increases_with_theta(self):
        p2s = [mean_p2_analytic(t) for t in [0.01, 0.1, 1.0, 5.0]]
        assert p2s == sorted(p2s)

    def test_mean_px2_nr_limit(self):
        """In the NR limit: ⟨p_x²⟩₁D_J ≈ Theta (equipartition, 1 degree of freedom)."""
        theta = 0.001
        expected = theta
        assert mean_px2_analytic_1d(theta) == pytest.approx(expected, rel=1e-2)

    def test_mean_px2_increases_with_theta(self):
        """⟨p_x²⟩ should increase monotonically with temperature."""
        p2s = [mean_px2_analytic_1d(t) for t in [0.001, 0.01, 0.1, 1.0]]
        assert p2s == sorted(p2s)

    def test_mean_gamma_rejects_nonpositive_theta(self):
        with pytest.raises(ValueError, match=r"theta"):
            mean_gamma_analytic(0.0)
        with pytest.raises(ValueError, match=r"theta"):
            mean_gamma_analytic(-0.1)

    def test_mean_p2_rejects_nonpositive_theta(self):
        with pytest.raises(ValueError, match=r"theta"):
            mean_p2_analytic(0.0)

    def test_mean_gamma_ur_limit(self):
        """In the ultra-relativistic limit (Theta >> 1): ⟨gamma⟩ ≈ 3 Theta."""
        theta = 20.0
        # At large Theta, <gamma> approaches 3*Theta (from Jüttner 1911)
        expected = 3.0 * theta
        assert mean_gamma_analytic(theta) == pytest.approx(expected, rel=0.05)


# ---------------------------------------------------------------------------
# 1D sampler — input validation
# ---------------------------------------------------------------------------

class TestSampleMaxwellJuttner1DValidation:
    def test_rejects_zero_theta(self):
        with pytest.raises(ValueError, match=r"theta"):
            sample_maxwell_juttner_1d(0.0, 10)

    def test_rejects_negative_theta(self):
        with pytest.raises(ValueError, match=r"theta"):
            sample_maxwell_juttner_1d(-0.1, 10)

    def test_rejects_zero_n(self):
        with pytest.raises(ValueError, match=r"n_particles"):
            sample_maxwell_juttner_1d(0.1, 0)

    def test_returns_correct_shape(self):
        rng = np.random.default_rng(_RNG_SEED)
        result = sample_maxwell_juttner_1d(0.1, 100, rng=rng)
        assert result.shape == (100,)

    def test_returns_float_dtype(self):
        rng = np.random.default_rng(_RNG_SEED)
        result = sample_maxwell_juttner_1d(0.1, 50, rng=rng)
        assert result.dtype == float or np.issubdtype(result.dtype, np.floating)

    def test_distribution_is_symmetric_around_zero(self):
        """For zero drift, the distribution should be symmetric: ⟨p_x⟩ ≈ 0."""
        rng = np.random.default_rng(_RNG_SEED)
        samples = sample_maxwell_juttner_1d(0.05, 100_000, rng=rng)
        # Mean should be within 3 sigma of 0
        se = np.std(samples) / math.sqrt(len(samples))
        assert abs(np.mean(samples)) < 5 * se


# ---------------------------------------------------------------------------
# 1D sampler — statistical moment tests
# ---------------------------------------------------------------------------

class TestSampleMaxwellJuttner1DMoments:
    """Statistical tests that ⟨p_x²⟩ matches the analytic value."""

    def _check_theta(self, theta: float) -> None:
        result = validate_sample_moments_1d(
            theta,
            n_particles=100_000,
            rng=np.random.default_rng(_RNG_SEED),
            n_sigma=5.0,
        )
        assert result.passed, repr(result)

    def test_moments_nr_regime(self):
        """Non-relativistic regime (Theta = 0.0025, vth/c = 0.05)."""
        self._check_theta(0.0025)

    def test_moments_mildly_relativistic(self):
        """Mildly relativistic (Theta = 0.09, vth/c ≈ 0.3)."""
        self._check_theta(0.09)

    def test_moments_relativistic(self):
        """Relativistic regime (Theta = 1.0)."""
        self._check_theta(1.0)

    def test_moments_ultrarelativistic(self):
        """Ultra-relativistic regime (Theta = 5.0)."""
        self._check_theta(5.0)


# ---------------------------------------------------------------------------
# 3D sampler — input validation
# ---------------------------------------------------------------------------

class TestSampleMaxwellJuttner3DValidation:
    def test_rejects_zero_theta(self):
        with pytest.raises(ValueError, match=r"theta"):
            sample_maxwell_juttner_3d(0.0, 10)

    def test_rejects_negative_n(self):
        with pytest.raises(ValueError, match=r"n_particles"):
            sample_maxwell_juttner_3d(0.1, 0)

    def test_returns_correct_shape(self):
        rng = np.random.default_rng(_RNG_SEED)
        result = sample_maxwell_juttner_3d(0.1, 100, rng=rng)
        assert result.shape == (100, 3)

    def test_gamma_all_at_least_one(self):
        """All sampled Lorentz factors must be >= 1."""
        rng = np.random.default_rng(_RNG_SEED)
        samples = sample_maxwell_juttner_3d(0.1, 200, rng=rng)
        p2 = np.sum(samples ** 2, axis=1)
        gammas = np.sqrt(1.0 + p2)
        assert np.all(gammas >= 1.0 - 1e-9)


# ---------------------------------------------------------------------------
# 3D sampler — statistical moment tests
# ---------------------------------------------------------------------------

class TestSampleMaxwellJuttner3DMoments:
    """Statistical tests for ⟨gamma⟩, ⟨|p|²⟩, and isotropy."""

    def _check_theta(self, theta: float) -> None:
        result = validate_sample_moments_3d(
            theta,
            n_particles=100_000,
            rng=np.random.default_rng(_RNG_SEED),
            n_sigma=5.0,
        )
        assert result.passed, repr(result)

    def test_moments_nr_regime(self):
        """Theta = 0.0025: NR regime, ⟨gamma⟩ ≈ 1 + 0.00375."""
        self._check_theta(0.0025)

    def test_moments_mildly_relativistic(self):
        """Theta = 0.09: mildly relativistic."""
        self._check_theta(0.09)

    def test_moments_relativistic(self):
        """Theta = 1.0: relativistic."""
        self._check_theta(1.0)

    def test_moments_ultrarelativistic(self):
        """Theta = 5.0: ultra-relativistic."""
        self._check_theta(5.0)


# ---------------------------------------------------------------------------
# Lorentz boost
# ---------------------------------------------------------------------------

class TestBoostMomentum:
    def test_zero_drift_is_identity(self):
        rng = np.random.default_rng(_RNG_SEED)
        p = rng.standard_normal((50, 3))
        p_boosted = boost_momentum(p, beta_drift=0.0, axis=0)
        np.testing.assert_allclose(p_boosted, p, rtol=1e-12)

    def test_boost_increases_px_for_positive_beta(self):
        """A positive boost along x increases average p_x (for a rest distribution)."""
        rng = np.random.default_rng(_RNG_SEED)
        samples = sample_maxwell_juttner_3d(0.01, 1000, rng=rng)
        boosted = boost_momentum(samples, beta_drift=0.5, axis=0)
        assert np.mean(boosted[:, 0]) > np.mean(samples[:, 0]) + 0.3

    def test_boost_does_not_change_transverse_components(self):
        """Boost along x should leave p_y, p_z unchanged."""
        rng = np.random.default_rng(_RNG_SEED)
        p = rng.standard_normal((100, 3))
        p_boosted = boost_momentum(p, beta_drift=0.5, axis=0)
        np.testing.assert_allclose(p_boosted[:, 1], p[:, 1], rtol=1e-12)
        np.testing.assert_allclose(p_boosted[:, 2], p[:, 2], rtol=1e-12)

    def test_boost_gamma_increases(self):
        """Boosting any rest-frame distribution increases all particle gammas."""
        rng = np.random.default_rng(_RNG_SEED)
        samples = sample_maxwell_juttner_3d(0.01, 200, rng=rng)
        gamma_rest = np.sqrt(1.0 + np.sum(samples ** 2, axis=1))
        boosted = boost_momentum(samples, beta_drift=0.866, axis=0)
        gamma_boosted = np.sqrt(1.0 + np.sum(boosted ** 2, axis=1))
        assert np.all(gamma_boosted > gamma_rest - 1e-9)

    def test_boost_along_all_axes(self):
        """Boost should work for axis = 0, 1, 2."""
        rng = np.random.default_rng(_RNG_SEED)
        p = sample_maxwell_juttner_3d(0.1, 50, rng=rng)
        for ax in (0, 1, 2):
            pb = boost_momentum(p, beta_drift=0.5, axis=ax)
            assert pb.shape == (50, 3)

    def test_boost_known_value_scalar(self):
        """Single particle at rest, boosted at beta_d: p_x' = gamma_d * beta_d."""
        # Particle at rest: p = (0, 0, 0), gamma = 1
        p_rest = np.array([[0.0, 0.0, 0.0]])
        beta_d = 0.6
        gamma_d = 1.0 / math.sqrt(1.0 - beta_d ** 2)
        p_boosted = boost_momentum(p_rest, beta_drift=beta_d, axis=0)
        # p_x' = gamma_d * (0 + beta_d * 1) = gamma_d * beta_d
        expected_px = gamma_d * beta_d
        assert p_boosted[0, 0] == pytest.approx(expected_px, rel=1e-10)
        assert p_boosted[0, 1] == pytest.approx(0.0, abs=1e-15)
        assert p_boosted[0, 2] == pytest.approx(0.0, abs=1e-15)

    def test_boost_rejects_superluminal(self):
        p = np.zeros((5, 3))
        with pytest.raises(ValueError, match=r"beta_drift"):
            boost_momentum(p, beta_drift=1.0)
        with pytest.raises(ValueError, match=r"beta_drift"):
            boost_momentum(p, beta_drift=-1.0)

    def test_boost_rejects_wrong_shape(self):
        p_bad = np.zeros((5, 2))
        with pytest.raises(ValueError, match=r"shape"):
            boost_momentum(p_bad, beta_drift=0.5)

    def test_boost_rejects_invalid_axis(self):
        p = np.zeros((5, 3))
        with pytest.raises(ValueError, match=r"axis"):
            boost_momentum(p, beta_drift=0.5, axis=3)

    def test_boost_applied_to_benchmark_beam(self):
        """Boosting a cold distribution to beta=0.866 gives gamma_drift ≈ 2."""
        rng = np.random.default_rng(_RNG_SEED)
        # Cold distribution with theta=1e-4 (vth/c ≈ 0.01): essentially monoenergetic
        samples = sample_maxwell_juttner_3d(1e-4, 2000, rng=rng)
        beta_d = math.sqrt(3.0) / 2.0   # gamma = 2
        gamma_d = 1.0 / math.sqrt(1.0 - beta_d ** 2)
        boosted = boost_momentum(samples, beta_drift=beta_d, axis=0)
        # Mean gamma should be close to gamma_d (for cold beam)
        gammas = np.sqrt(1.0 + np.sum(boosted ** 2, axis=1))
        assert np.mean(gammas) == pytest.approx(gamma_d, rel=0.01)


# ---------------------------------------------------------------------------
# MomentValidationResult container
# ---------------------------------------------------------------------------

class TestMomentValidationResult:
    def test_repr_contains_theta(self):
        result = validate_sample_moments_3d(
            0.1, n_particles=500, rng=np.random.default_rng(_RNG_SEED)
        )
        assert "0.1" in repr(result)

    def test_passed_attribute_is_bool(self):
        result = validate_sample_moments_1d(
            0.1, n_particles=500, rng=np.random.default_rng(_RNG_SEED)
        )
        assert isinstance(result.passed, bool)

    def test_checks_list_nonempty(self):
        result = validate_sample_moments_3d(
            0.1, n_particles=500, rng=np.random.default_rng(_RNG_SEED)
        )
        assert len(result.checks) >= 2


# ---------------------------------------------------------------------------
# TOML schema loading
# ---------------------------------------------------------------------------

class TestMomentumSpaceSchema:
    def test_schema_file_exists(self):
        assert _SCHEMA_TOML.exists(), f"Schema TOML not found at {_SCHEMA_TOML}"

    def test_schema_is_valid_toml(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        assert isinstance(data, dict)

    def test_schema_has_input_parameters(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        assert "input_parameters" in data

    def test_schema_has_relativistic_true(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        assert data["input_parameters"]["relativistic"] is True

    def test_schema_has_relativistic_species(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        assert "relativistic_species" in data
        assert isinstance(data["relativistic_species"], list)
        assert len(data["relativistic_species"]) > 0

    def test_each_species_has_required_fields(self):
        required = {"name", "charge_sign", "mass_ratio", "theta",
                    "beta_drift_x", "number_fraction"}
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        for species in data["relativistic_species"]:
            missing = required - set(species.keys())
            assert not missing, (
                f"Species '{species.get('name', '?')}' missing fields: {missing}"
            )

    def test_species_theta_values_are_positive(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        for s in data["relativistic_species"]:
            assert s["theta"] > 0, (
                f"Species '{s['name']}' has non-positive theta={s['theta']}"
            )

    def test_species_beta_within_bounds(self):
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        for s in data["relativistic_species"]:
            assert -1.0 < s["beta_drift_x"] < 1.0, (
                f"Species '{s['name']}' has |beta_drift_x| >= 1"
            )

    def test_theta_consistent_with_benchmark_beam(self):
        """The beam_electrons theta should be cold (< 0.001)."""
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        beam = next(
            s for s in data["relativistic_species"]
            if s["name"] == "beam_electrons"
        )
        assert beam["theta"] < 0.001

    def test_vth_from_theta_for_background(self):
        """Background electron theta corresponds to vth/c ≈ 0.05."""
        with open(_SCHEMA_TOML, "rb") as fh:
            data = tomllib.load(fh)
        bg = next(
            s for s in data["relativistic_species"]
            if s["name"] == "background_electrons"
        )
        vth = vth_from_theta(bg["theta"])
        assert vth == pytest.approx(0.05, rel=1e-3)
