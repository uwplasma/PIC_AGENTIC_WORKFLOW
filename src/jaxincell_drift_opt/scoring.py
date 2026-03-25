from __future__ import annotations

from math import ceil, log10

import numpy as np


EPSILON_0 = 8.8541878128e-12
SCORE_VERSION = "tail_mean_electric_field_energy_v1"


def extract_electric_field_energy(output: dict) -> np.ndarray:
    if "electric_field_energy" in output:
        return np.asarray(output["electric_field_energy"], dtype=float)

    if "electric_field" not in output or "dx" not in output:
        raise KeyError("Output must contain either 'electric_field_energy' or both 'electric_field' and 'dx'")

    electric_field = np.asarray(output["electric_field"], dtype=float)
    abs_e_squared = np.sum(electric_field**2, axis=-1)
    return 0.5 * EPSILON_0 * np.sum(abs_e_squared, axis=-1) * float(output["dx"])


def score_trial_output(
    output: dict,
    *,
    drift_multiplier: float,
    ion_temperature_ratio: float,
    ion_mass_over_proton_mass: float,
    seed: int | None,
    wall_time_seconds: float,
    tail_fraction: float,
    eps: float,
    failure_penalty: float,
    score_version: str = SCORE_VERSION,
    failed: bool = False,
    failure_reason: str | None = None,
) -> dict:
    if failed:
        return {
            "drift_multiplier": float(drift_multiplier),
            "ion_temperature_ratio": float(ion_temperature_ratio),
            "ion_mass_over_proton_mass": float(ion_mass_over_proton_mass),
            "seed": seed,
            "failed": True,
            "failure_reason": failure_reason or "unknown_failure",
            "wall_time_seconds": float(wall_time_seconds),
            "tail_mean_E": 0.0,
            "tail_max_E": 0.0,
            "final_E": 0.0,
            "time_of_peak_E": None,
            "optimizer_score": float(-failure_penalty),
            "optimizer_objective": float(failure_penalty),
            "score_version": score_version,
        }

    energy = extract_electric_field_energy(output)
    time_array = np.asarray(output.get("time_array", np.arange(energy.size)), dtype=float)
    tail_count = max(1, ceil(energy.size * tail_fraction))
    tail = energy[-tail_count:]
    peak_index = int(np.argmax(energy))
    tail_mean = float(np.mean(tail))
    optimizer_objective = float(log10(tail_mean + eps))
    optimizer_score = float(-optimizer_objective)

    return {
        "drift_multiplier": float(drift_multiplier),
        "ion_temperature_ratio": float(ion_temperature_ratio),
        "ion_mass_over_proton_mass": float(ion_mass_over_proton_mass),
        "seed": seed,
        "failed": False,
        "failure_reason": None,
        "wall_time_seconds": float(wall_time_seconds),
        "tail_mean_E": tail_mean,
        "tail_max_E": float(np.max(tail)),
        "final_E": float(energy[-1]),
        "time_of_peak_E": float(time_array[peak_index]),
        "optimizer_score": optimizer_score,
        "optimizer_objective": optimizer_objective,
        "score_version": score_version,
    }
