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
