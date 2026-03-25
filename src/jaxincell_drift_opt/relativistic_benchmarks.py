"""Relativistic PIC benchmark case definitions and physics utilities.

This module loads the benchmark case specifications from
``configs/relativistic_benchmarks.yaml`` and provides helper functions that
compute expected linear-theory growth rates and perform self-consistency
checks on the benchmark parameters.

The benchmark cases defined here are the first step of the relativistic
milestone roadmap: establishing concrete, literature-grounded reproduction
targets before any relativistic code changes are made upstream.

References
----------
Birdsall, C. K. & Langdon, A. B. (1991). *Plasma Physics via Computer
Simulation*.  IOP Publishing.

Boris, J. P. (1970).  Relativistic plasma simulation — optimization of a
hybrid code.  *Proc. 4th Conf. Numer. Simul. Plasmas*, NRL, pp. 3–67.

Bret, A., Firpo, M.-C., & Deutsch, C. (2004).  Electromagnetic instabilities
for relativistic beam-plasma interaction in whole k space.
*Phys. Rev. E*, **70**, 046401.

Evstatiev, E. G. & Shadwick, B. A. (2013).  Variational formulation of
particle algorithms for kinetic plasma simulations.
*J. Comput. Phys.*, **245**, 376–398.

Vay, J.-L. (2008).  Simulation of beams or plasmas crossing at relativistic
velocity.  *Phys. Plasmas*, **15**, 056701.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml

# Path to the YAML benchmark specification relative to this file.
_YAML_PATH = Path(__file__).parent.parent.parent / "configs" / "relativistic_benchmarks.yaml"


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_benchmark_specs(yaml_path: Path | str | None = None) -> dict[str, Any]:
    """Load and return the raw benchmark specification dictionary.

    Parameters
    ----------
    yaml_path:
        Path to the YAML file.  Defaults to ``configs/relativistic_benchmarks.yaml``
        relative to the repository root.

    Returns
    -------
    dict
        Parsed YAML content.
    """
    path = Path(yaml_path) if yaml_path is not None else _YAML_PATH
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_case(case_id: str, yaml_path: Path | str | None = None) -> dict[str, Any]:
    """Return the specification dict for a single benchmark case by its *id*.

    Parameters
    ----------
    case_id:
        The ``id`` field of the desired case (e.g. ``"rel_two_stream"``).
    yaml_path:
        Optional override for the YAML file path.

    Returns
    -------
    dict
        Case specification dictionary.

    Raises
    ------
    KeyError
        If no case with the given id exists.
    """
    specs = load_benchmark_specs(yaml_path)
    for case in specs.get("cases", []):
        if case.get("id") == case_id:
            return case
    available = [c.get("id") for c in specs.get("cases", [])]
    raise KeyError(f"Benchmark case {case_id!r} not found.  Available: {available}")


def list_case_ids(yaml_path: Path | str | None = None) -> list[str]:
    """Return the list of all benchmark case IDs defined in the YAML file."""
    specs = load_benchmark_specs(yaml_path)
    return [c.get("id") for c in specs.get("cases", [])]


# ---------------------------------------------------------------------------
# Relativistic physics utilities
# ---------------------------------------------------------------------------

def gamma_from_beta(beta: float) -> float:
    """Return the Lorentz factor *gamma* for a given *beta* = v/c.

    Parameters
    ----------
    beta:
        Normalized velocity v/c.  Must satisfy 0 <= |beta| < 1.

    Returns
    -------
    float
        Lorentz factor gamma = 1 / sqrt(1 - beta^2).
    """
    if abs(beta) >= 1.0:
        raise ValueError(f"beta must satisfy |beta| < 1, got beta={beta!r}")
    return 1.0 / math.sqrt(1.0 - beta**2)


def beta_from_gamma(gamma: float) -> float:
    """Return *beta* = v/c for a given Lorentz factor *gamma*.

    Parameters
    ----------
    gamma:
        Lorentz factor.  Must satisfy gamma >= 1.

    Returns
    -------
    float
        Normalized velocity beta = sqrt(1 - 1/gamma^2).
    """
    if gamma < 1.0:
        raise ValueError(f"gamma must be >= 1, got gamma={gamma!r}")
    return math.sqrt(1.0 - 1.0 / gamma**2)


def normalized_momentum_from_beta(beta: float) -> float:
    """Return the normalized 4-momentum magnitude p / (m_e c) for a given beta.

    Parameters
    ----------
    beta:
        Normalized velocity v/c.

    Returns
    -------
    float
        p / (m_e c) = gamma * beta.
    """
    g = gamma_from_beta(beta)
    return g * beta


# ---------------------------------------------------------------------------
# Growth-rate estimates from linear kinetic theory
# ---------------------------------------------------------------------------

def two_stream_growth_rate_cold(
    gamma_beam: float,
    beam_fraction: float = 0.5,
) -> float:
    """Estimate the maximum electrostatic growth rate for the relativistic
    cold two-stream instability.

    For two symmetric counter-streaming cold beams (each carrying fraction *f*
    of the total electron density) the maximum linear growth rate is derived
    from the cold-fluid relativistic dispersion relation:

    .. math::
        \\frac{\\text{Im}(\\omega)}{\\omega_{pe}} =
        \\frac{\\sqrt{f}}{2} \\, \\gamma_{\\text{beam}}^{-3/2}

    The non-relativistic prefactor :math:`\\sqrt{f}/2` (equal to
    :math:`1/(2\\sqrt{2}) \\approx 0.354` for :math:`f = 0.5`) follows from
    the exact symmetric two-stream analysis.  The relativistic factor
    :math:`\\gamma^{-3/2}` enters because the effective beam plasma frequency
    in the cold-fluid equations is :math:`\\omega_{pe,\\text{beam}} / \\gamma^{3/2}`
    (from the linearised relativistic momentum equation).

    Parameters
    ----------
    gamma_beam:
        Lorentz factor of each beam.
    beam_fraction:
        Fraction *f* of total electron density carried by each beam
        (default 0.5 for equal symmetric beams).  Must satisfy
        ``0 < beam_fraction <= 0.5``.

    Returns
    -------
    float
        Im(omega) / omega_pe, the maximum growth rate in units of the
        electron plasma frequency.

    Notes
    -----
    This expression is valid for cold symmetric beams.  Finite thermal spread
    reduces the growth rate by O(beta_th / beta_drift).  The derivation
    assumes the electrostatic approximation; the electromagnetic (Weibel)
    instability has a different scaling with gamma.
    """
    if gamma_beam < 1.0:
        raise ValueError(f"gamma_beam must be >= 1, got {gamma_beam!r}")
    if not (0.0 < beam_fraction <= 0.5):
        raise ValueError(f"beam_fraction must be in (0, 0.5], got {beam_fraction!r}")

    # Exact NR result for symmetric cold beams with fraction f each:
    #   Im(omega)/omega_pe = sqrt(f) / 2
    # (derived by maximising over k the purely imaginary root of the
    #  symmetric two-stream dispersion relation).
    # Relativistic correction: omega_pe_beam^eff = omega_pe_beam / gamma^(3/2)
    # scales the growth rate by gamma^(-3/2).
    nr_prefactor = math.sqrt(beam_fraction) / 2.0
    relativistic_suppression = gamma_beam ** (-1.5)
    return nr_prefactor * relativistic_suppression


def bump_on_tail_growth_rate(
    beam_density_fraction: float,
    gamma_beam: float,
) -> float:
    """Estimate the maximum electrostatic growth rate for the relativistic
    weak-beam bump-on-tail instability.

    For a cold beam with density fraction :math:`n_b/n_0 \\ll 1` on a cold
    background plasma, the resonant three-wave (cubic) dispersion gives the
    growing root:

    .. math::
        \\frac{\\text{Im}(\\omega)}{\\omega_{pe}} \\approx
        \\frac{\\sqrt{3}}{2} \\left(\\frac{n_b}{2 n_0}\\right)^{1/3}
        \\gamma_b^{-1}

    The factor :math:`\\gamma_b^{-1}` (not :math:`\\gamma_b^{-1/3}`) enters
    because the effective beam plasma frequency in the cold relativistic fluid
    equations is :math:`\\omega_{pe,b} / \\gamma_b^{3/2}`, and the cubic
    resonance scales as :math:`(\\omega_{pe,b}^2 / \\gamma_b^3)^{1/3}`.

    Parameters
    ----------
    beam_density_fraction:
        Beam density as a fraction of total electron density (n_b / n_0).
    gamma_beam:
        Lorentz factor of the beam electrons.

    Returns
    -------
    float
        Im(omega) / omega_pe.

    Notes
    -----
    A warm background reduces the growth rate.  The 30 % tolerance in the
    benchmark YAML accounts for this correction.

    Derivation: near Langmuir resonance :math:`k v_b = \\omega_{pe}`, setting
    :math:`\\omega = \\omega_{pe} + \\delta\\omega` and expanding the
    electrostatic dielectric to leading order gives the cubic
    :math:`\\delta\\omega^3 = (n_b/n_0)/(2\\gamma_b^3) \\cdot \\omega_{pe}^3`,
    whose complex roots include a growing mode.
    See Nicholson (1983), *Introduction to Plasma Physics*, Chapter 7.
    """
    if not (0.0 < beam_density_fraction < 1.0):
        raise ValueError(f"beam_density_fraction must be in (0, 1), got {beam_density_fraction!r}")
    if gamma_beam < 1.0:
        raise ValueError(f"gamma_beam must be >= 1, got {gamma_beam!r}")

    # Cubic resonance gives Im(delta_omega) = sqrt(3)/2 * (C)^(1/3)
    # where C = (nb/n0)/(2*gamma_b^3)
    # => Im(omega)/omega_pe = sqrt(3)/2 * (nb/(2*n0))^(1/3) * gamma_b^(-1)
    weak_beam_factor = (beam_density_fraction / 2.0) ** (1.0 / 3.0)
    relativistic_suppression = gamma_beam ** (-1.0)
    return (math.sqrt(3.0) / 2.0) * weak_beam_factor * relativistic_suppression


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def check_species_self_consistency(
    species: dict[str, Any],
    rtol: float = 1e-4,
) -> list[str]:
    """Check internal consistency of a species parameter dictionary.

    Verifies that the declared ``gamma_drift`` and ``beta_drift`` are
    mutually consistent within relative tolerance *rtol*.

    Parameters
    ----------
    species:
        A species entry from the benchmark YAML (must contain ``gamma_drift``
        and ``beta_drift``).
    rtol:
        Relative tolerance for gamma-beta consistency check.

    Returns
    -------
    list[str]
        List of error messages.  Empty if the species is self-consistent.
    """
    errors: list[str] = []
    name = species.get("name", "<unknown>")
    gamma = species.get("gamma_drift")
    beta = species.get("beta_drift")

    if gamma is None or beta is None:
        errors.append(f"Species '{name}': missing gamma_drift or beta_drift.")
        return errors

    if gamma < 1.0:
        errors.append(f"Species '{name}': gamma_drift={gamma} < 1 is unphysical.")
    if abs(beta) >= 1.0:
        errors.append(f"Species '{name}': |beta_drift|={abs(beta)} >= 1 is unphysical.")
    if gamma >= 1.0 and abs(beta) < 1.0:
        expected_gamma = gamma_from_beta(beta)
        rel_err = abs(expected_gamma - gamma) / expected_gamma
        if rel_err > rtol:
            errors.append(
                f"Species '{name}': gamma_drift={gamma} is inconsistent with "
                f"beta_drift={beta} (expected gamma={expected_gamma:.6f}, "
                f"relative error={rel_err:.2e})."
            )
    return errors


def validate_case(
    case: dict[str, Any],
    rtol: float = 1e-4,
) -> list[str]:
    """Validate a single benchmark case for physical and internal consistency.

    Parameters
    ----------
    case:
        A case dictionary from :func:`get_case` or :func:`load_benchmark_specs`.
    rtol:
        Relative tolerance passed to :func:`check_species_self_consistency`.

    Returns
    -------
    list[str]
        List of validation error strings.  Empty list means the case is valid.
    """
    errors: list[str] = []
    case_id = case.get("id", "<unknown>")

    for field in ("id", "label", "species", "reproduction_targets"):
        if field not in case:
            errors.append(f"Case '{case_id}': missing required field '{field}'.")

    for species in case.get("species", []):
        errors.extend(check_species_self_consistency(species, rtol=rtol))

    # Check that total number fractions sum to 1 for same-charge species grouped
    # by charge sign (electron number fractions should sum to 1).
    electron_fractions = sum(
        s.get("number_fraction", 0.0)
        for s in case.get("species", [])
        if s.get("charge_sign", 0) < 0
    )
    if case.get("species") and abs(electron_fractions - 1.0) > 1e-6:
        errors.append(
            f"Case '{case_id}': electron number_fractions sum to "
            f"{electron_fractions:.6f}, expected 1.0."
        )

    return errors


def validate_all_cases(yaml_path: Path | str | None = None) -> dict[str, list[str]]:
    """Validate every benchmark case in the YAML file.

    Parameters
    ----------
    yaml_path:
        Optional path override for the YAML file.

    Returns
    -------
    dict[str, list[str]]
        Mapping from case id to list of validation errors.  An empty list
        means that case is valid.
    """
    specs = load_benchmark_specs(yaml_path)
    results: dict[str, list[str]] = {}
    for case in specs.get("cases", []):
        case_id = case.get("id", "<unknown>")
        results[case_id] = validate_case(case)
    return results
