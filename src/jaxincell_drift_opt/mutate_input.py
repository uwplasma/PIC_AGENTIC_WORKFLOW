from __future__ import annotations

from copy import deepcopy


def apply_drift_multiplier(input_parameters: dict, drift_multiplier: float, drift_key: str) -> tuple[dict, dict]:
    if drift_key not in input_parameters:
        raise KeyError(f"Drift key '{drift_key}' is not present in the loaded input parameters")

    mutated = deepcopy(input_parameters)
    base_drift = float(mutated[drift_key])
    candidate_drift = base_drift * float(drift_multiplier)
    mutated[drift_key] = candidate_drift
    mutation = {
        "drift_key": drift_key,
        "base_drift": base_drift,
        "drift_multiplier": float(drift_multiplier),
        "candidate_drift": candidate_drift,
    }
    return mutated, mutation


def apply_search_parameters(
    input_parameters: dict,
    *,
    drift_multiplier: float,
    ion_temperature_ratio: float | None,
    ion_mass_over_proton_mass: float | None,
    drift_key: str,
    ion_temperature_ratio_key: str,
    ion_mass_key: str,
) -> tuple[dict, dict]:
    mutated = deepcopy(input_parameters)

    if drift_key not in mutated:
        raise KeyError(f"Drift key '{drift_key}' is not present in the loaded input parameters")
    if ion_temperature_ratio_key not in mutated:
        raise KeyError(f"Temperature ratio key '{ion_temperature_ratio_key}' is not present in the loaded input parameters")
    if ion_mass_key not in mutated:
        raise KeyError(f"Ion mass key '{ion_mass_key}' is not present in the loaded input parameters")

    base_drift = float(mutated[drift_key])
    candidate_drift = base_drift * float(drift_multiplier)
    mutated[drift_key] = candidate_drift

    base_ion_temperature_ratio = float(mutated[ion_temperature_ratio_key])
    candidate_ion_temperature_ratio = (
        base_ion_temperature_ratio if ion_temperature_ratio is None else float(ion_temperature_ratio)
    )
    mutated[ion_temperature_ratio_key] = candidate_ion_temperature_ratio

    base_ion_mass_over_proton_mass = float(mutated[ion_mass_key])
    candidate_ion_mass_over_proton_mass = (
        base_ion_mass_over_proton_mass if ion_mass_over_proton_mass is None else float(ion_mass_over_proton_mass)
    )
    mutated[ion_mass_key] = candidate_ion_mass_over_proton_mass

    mutation = {
        "drift_key": drift_key,
        "base_drift": base_drift,
        "drift_multiplier": float(drift_multiplier),
        "candidate_drift": candidate_drift,
        "ion_temperature_ratio_key": ion_temperature_ratio_key,
        "base_ion_temperature_ratio": base_ion_temperature_ratio,
        "candidate_ion_temperature_ratio": candidate_ion_temperature_ratio,
        "ion_mass_key": ion_mass_key,
        "base_ion_mass_over_proton_mass": base_ion_mass_over_proton_mass,
        "candidate_ion_mass_over_proton_mass": candidate_ion_mass_over_proton_mass,
    }
    return mutated, mutation
