"""Tests for the relativistic benchmark case definitions and physics utilities.

Validates that:
  1. The benchmark YAML file loads without error.
  2. Every benchmark case passes physical self-consistency checks.
  3. Linear-theory growth-rate functions return physically reasonable values.
  4. Relativistic kinematics helpers (gamma/beta conversions) are correct.
"""

from __future__ import annotations

import math

import pytest

from jaxincell_drift_opt.relativistic_benchmarks import (
    beta_from_gamma,
    bump_on_tail_growth_rate,
    gamma_from_beta,
    get_case,
    list_case_ids,
    load_benchmark_specs,
    normalized_momentum_from_beta,
    two_stream_growth_rate_cold,
    validate_all_cases,
    validate_case,
)


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

class TestBenchmarkYamlLoads:
    def test_specs_have_version_key(self):
        specs = load_benchmark_specs()
        assert "version" in specs

    def test_specs_have_cases_list(self):
        specs = load_benchmark_specs()
        assert isinstance(specs.get("cases"), list)
        assert len(specs["cases"]) > 0

    def test_expected_case_ids_present(self):
        ids = list_case_ids()
        assert "rel_two_stream" in ids
        assert "rel_bump_on_tail" in ids
        assert "energy_conservation" in ids

    def test_get_case_returns_dict(self):
        case = get_case("rel_two_stream")
        assert isinstance(case, dict)
        assert case["id"] == "rel_two_stream"

    def test_get_case_raises_for_unknown_id(self):
        with pytest.raises(KeyError, match="not found"):
            get_case("nonexistent_case_xyz")


# ---------------------------------------------------------------------------
# Physical self-consistency of every benchmark case
# ---------------------------------------------------------------------------

class TestBenchmarkCaseSelfConsistency:
    def test_all_cases_pass_validation(self):
        errors_by_case = validate_all_cases()
        for case_id, errors in errors_by_case.items():
            assert errors == [], (
                f"Case '{case_id}' failed validation:\n" + "\n".join(errors)
            )

    def test_rel_two_stream_has_symmetric_beams(self):
        case = get_case("rel_two_stream")
        electron_species = [s for s in case["species"] if s["charge_sign"] < 0]
        assert len(electron_species) == 2  # two beams
        betas = [abs(s["beta_drift"]) for s in electron_species]
        # Beams are symmetric: same |beta|
        assert abs(betas[0] - betas[1]) < 1e-6

    def test_rel_two_stream_electron_fractions_sum_to_one(self):
        case = get_case("rel_two_stream")
        total = sum(
            s["number_fraction"]
            for s in case["species"]
            if s["charge_sign"] < 0
        )
        assert abs(total - 1.0) < 1e-9

    def test_bump_on_tail_electron_fractions_sum_to_one(self):
        case = get_case("rel_bump_on_tail")
        total = sum(
            s["number_fraction"]
            for s in case["species"]
            if s["charge_sign"] < 0
        )
        assert abs(total - 1.0) < 1e-9

    def test_energy_conservation_has_no_net_drift(self):
        case = get_case("energy_conservation")
        for species in case["species"]:
            assert species["beta_drift"] == 0.0, (
                f"Species '{species['name']}' has non-zero drift in energy "
                "conservation case."
            )

    def test_all_cases_have_reproduction_targets(self):
        ids = list_case_ids()
        for case_id in ids:
            case = get_case(case_id)
            assert "reproduction_targets" in case, (
                f"Case '{case_id}' is missing reproduction_targets."
            )

    def test_all_cases_have_geometry_and_physics(self):
        ids = list_case_ids()
        for case_id in ids:
            case = get_case(case_id)
            assert case.get("geometry") == "1D3V"
            assert case.get("physics") == "electrostatic"


# ---------------------------------------------------------------------------
# Relativistic kinematics helpers
# ---------------------------------------------------------------------------

class TestKinematicsHelpers:
    def test_gamma_from_beta_at_zero_is_one(self):
        assert gamma_from_beta(0.0) == pytest.approx(1.0)

    def test_gamma_from_beta_known_value(self):
        # beta = sqrt(3)/2 → gamma = 2
        beta = math.sqrt(3.0) / 2.0
        assert gamma_from_beta(beta) == pytest.approx(2.0, rel=1e-6)

    def test_gamma_from_beta_rejects_superluminal(self):
        with pytest.raises(ValueError, match=r"beta"):
            gamma_from_beta(1.0)
        with pytest.raises(ValueError, match=r"beta"):
            gamma_from_beta(1.5)

    def test_beta_from_gamma_at_one_is_zero(self):
        assert beta_from_gamma(1.0) == pytest.approx(0.0, abs=1e-12)

    def test_beta_from_gamma_known_value(self):
        # gamma = 2 → beta = sqrt(3)/2
        assert beta_from_gamma(2.0) == pytest.approx(math.sqrt(3.0) / 2.0, rel=1e-6)

    def test_beta_from_gamma_rejects_subluminal_gamma(self):
        with pytest.raises(ValueError, match=r"gamma"):
            beta_from_gamma(0.5)

    def test_gamma_beta_roundtrip(self):
        for beta in [0.1, 0.5, 0.8, 0.99]:
            assert beta_from_gamma(gamma_from_beta(beta)) == pytest.approx(beta, rel=1e-10)

    def test_normalized_momentum_at_rest_is_zero(self):
        assert normalized_momentum_from_beta(0.0) == pytest.approx(0.0, abs=1e-12)

    def test_normalized_momentum_known_value(self):
        # gamma=2, beta=sqrt(3)/2: p/(m_e c) = gamma*beta = 2*sqrt(3)/2 = sqrt(3)
        beta = beta_from_gamma(2.0)
        assert normalized_momentum_from_beta(beta) == pytest.approx(math.sqrt(3.0), rel=1e-6)

    def test_benchmark_beta_values_consistent_with_gamma(self):
        """Every species beta_drift in the YAML should be consistent with gamma_drift."""
        ids = list_case_ids()
        for case_id in ids:
            case = get_case(case_id)
            for species in case["species"]:
                gamma = species["gamma_drift"]
                beta = abs(species["beta_drift"])
                expected_beta = beta_from_gamma(gamma)
                assert beta == pytest.approx(expected_beta, rel=1e-4), (
                    f"Case '{case_id}', species '{species['name']}': "
                    f"beta_drift={beta} inconsistent with gamma_drift={gamma} "
                    f"(expected beta={expected_beta:.7f})."
                )


# ---------------------------------------------------------------------------
# Growth-rate formulas
# ---------------------------------------------------------------------------

class TestGrowthRateFormulas:
    def test_two_stream_growth_rate_decreases_with_gamma(self):
        """Relativistic suppression: higher gamma → lower growth rate."""
        gr1 = two_stream_growth_rate_cold(gamma_beam=1.0)
        gr2 = two_stream_growth_rate_cold(gamma_beam=2.0)
        gr5 = two_stream_growth_rate_cold(gamma_beam=5.0)
        assert gr1 > gr2 > gr5

    def test_two_stream_nonrelativistic_limit(self):
        """At gamma=1 the result should equal sqrt(0.5)/2 = 1/(2*sqrt(2)) for equal beams."""
        expected = math.sqrt(0.5) / 2.0   # = 1 / (2 * sqrt(2)) ~ 0.354
        assert two_stream_growth_rate_cold(gamma_beam=1.0) == pytest.approx(expected, rel=1e-6)

    def test_two_stream_growth_at_gamma_2(self):
        """Match the value expected by the rel_two_stream benchmark case."""
        gr = two_stream_growth_rate_cold(gamma_beam=2.0)
        target = get_case("rel_two_stream")["reproduction_targets"][
            "growth_rate_over_omega_pe"
        ]
        expected = target["expected"]
        tol = target["tolerance_relative"]
        assert gr == pytest.approx(expected, rel=tol)

    def test_two_stream_rejects_invalid_gamma(self):
        with pytest.raises(ValueError, match=r"gamma_beam"):
            two_stream_growth_rate_cold(gamma_beam=0.5)

    def test_two_stream_rejects_invalid_beam_fraction(self):
        with pytest.raises(ValueError, match=r"beam_fraction"):
            two_stream_growth_rate_cold(gamma_beam=2.0, beam_fraction=0.0)
        with pytest.raises(ValueError, match=r"beam_fraction"):
            two_stream_growth_rate_cold(gamma_beam=2.0, beam_fraction=0.6)

    def test_bump_on_tail_growth_rate_decreases_with_gamma(self):
        """Relativistic suppression applies to bump-on-tail as well."""
        gr1 = bump_on_tail_growth_rate(beam_density_fraction=0.1, gamma_beam=1.0)
        gr3 = bump_on_tail_growth_rate(beam_density_fraction=0.1, gamma_beam=3.0)
        assert gr1 > gr3

    def test_bump_on_tail_growth_rate_increases_with_beam_fraction(self):
        gr_small = bump_on_tail_growth_rate(beam_density_fraction=0.05, gamma_beam=3.0)
        gr_large = bump_on_tail_growth_rate(beam_density_fraction=0.20, gamma_beam=3.0)
        assert gr_large > gr_small

    def test_bump_on_tail_growth_at_benchmark_params(self):
        """Growth rate estimate should be within tolerance of the benchmark target."""
        gr = bump_on_tail_growth_rate(
            beam_density_fraction=0.1,
            gamma_beam=3.0,
        )
        target = get_case("rel_bump_on_tail")["reproduction_targets"][
            "growth_rate_over_omega_pe"
        ]
        expected = target["expected"]
        tol = target["tolerance_relative"]
        assert gr == pytest.approx(expected, rel=tol)

    def test_bump_on_tail_rejects_invalid_density_fraction(self):
        with pytest.raises(ValueError, match=r"beam_density_fraction"):
            bump_on_tail_growth_rate(beam_density_fraction=0.0, gamma_beam=2.0)
        with pytest.raises(ValueError, match=r"beam_density_fraction"):
            bump_on_tail_growth_rate(beam_density_fraction=1.1, gamma_beam=2.0)

    def test_bump_on_tail_rejects_invalid_gamma(self):
        with pytest.raises(ValueError, match=r"gamma_beam"):
            bump_on_tail_growth_rate(beam_density_fraction=0.1, gamma_beam=0.9)

    def test_growth_rates_are_positive_and_sub_unity(self):
        """All growth rates should be physically in (0, 1) * omega_pe."""
        for gamma in [1.0, 2.0, 5.0, 10.0]:
            gr = two_stream_growth_rate_cold(gamma_beam=gamma)
            assert 0.0 < gr < 1.0, f"two_stream growth rate out of range at gamma={gamma}"
        for f in [0.01, 0.05, 0.1, 0.3]:
            gr = bump_on_tail_growth_rate(beam_density_fraction=f, gamma_beam=3.0)
            assert 0.0 < gr < 1.0, f"bump_on_tail growth rate out of range at f={f}"
