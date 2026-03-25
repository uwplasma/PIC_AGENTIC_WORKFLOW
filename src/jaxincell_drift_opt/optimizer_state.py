from __future__ import annotations

import json
from pathlib import Path

from skopt import Optimizer
from skopt.space import Real

from .config import SearchConfig, load_base_input
from .utils import atomic_write_json, utc_timestamp


STATE_SCHEMA_VERSION = 2


def build_optimizer(search_config: SearchConfig, random_state: int | None = None) -> Optimizer:
    return Optimizer(
        dimensions=[
            Real(search_config.drift_multiplier_min, search_config.drift_multiplier_max, name="drift_multiplier"),
            Real(
                search_config.ion_temperature_ratio_min,
                search_config.ion_temperature_ratio_max,
                name="ion_temperature_ratio",
                prior="log-uniform",
            ),
            Real(
                search_config.ion_mass_min,
                search_config.ion_mass_max,
                name="ion_mass_over_proton_mass",
                prior="log-uniform",
            ),
        ],
        base_estimator=search_config.base_estimator,
        acq_func=search_config.acq_func,
        random_state=search_config.optimizer_random_state if random_state is None else int(random_state),
        n_initial_points=search_config.n_initial_points,
    )


def default_state(search_config: SearchConfig) -> dict:
    now = utc_timestamp()
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "created_at": now,
        "updated_at": now,
        "optimizer": {
            "random_state": search_config.optimizer_random_state,
            "base_estimator": search_config.base_estimator,
            "acq_func": search_config.acq_func,
            "n_initial_points": search_config.n_initial_points,
            "dimensions": {
                "drift_multiplier": [search_config.drift_multiplier_min, search_config.drift_multiplier_max],
                "ion_temperature_ratio": [search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max],
                "ion_mass_over_proton_mass": [search_config.ion_mass_min, search_config.ion_mass_max],
            },
        },
        "observations": {"x": [], "y": []},
        "trials": [],
        "best_result": None,
    }


def load_state(path: Path, search_config: SearchConfig) -> dict:
    if not path.exists():
        return default_state(search_config)
    with path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)

    base_input = load_base_input(search_config.base_input).get("input_parameters", {})
    default_ion_temperature_ratio = float(base_input.get(search_config.ion_temperature_ratio_key, 0.01))
    default_ion_mass = float(base_input.get(search_config.ion_mass_key, 1.0))

    state.setdefault("trials", [])
    state.setdefault("observations", {"x": [], "y": []})
    state.setdefault("best_result", None)
    state.setdefault("optimizer", {})
    state["optimizer"].setdefault("random_state", search_config.optimizer_random_state)
    state["optimizer"].setdefault("base_estimator", search_config.base_estimator)
    state["optimizer"].setdefault("acq_func", search_config.acq_func)
    state["optimizer"].setdefault("n_initial_points", search_config.n_initial_points)
    state["optimizer"].setdefault(
        "dimensions",
        {
            "drift_multiplier": [search_config.drift_multiplier_min, search_config.drift_multiplier_max],
            "ion_temperature_ratio": [search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max],
            "ion_mass_over_proton_mass": [search_config.ion_mass_min, search_config.ion_mass_max],
        },
    )

    for trial in state["trials"]:
        trial.setdefault("ion_temperature_ratio", float(trial.get("candidate_ion_temperature_ratio", default_ion_temperature_ratio)))
        trial.setdefault("ion_mass_over_proton_mass", float(trial.get("candidate_ion_mass_over_proton_mass", default_ion_mass)))
        trial.setdefault("candidate_ion_temperature_ratio", float(trial["ion_temperature_ratio"]))
        trial.setdefault("candidate_ion_mass_over_proton_mass", float(trial["ion_mass_over_proton_mass"]))
        if not trial.get("failed") and trial.get("tail_mean_E") is not None:
            tail_mean = float(trial.get("tail_mean_E", 0.0))
            if tail_mean > 0.0:
                from math import log10

                score = float(log10(tail_mean))
                trial["optimizer_score"] = score
                trial["optimizer_objective"] = -score

    repaired_xs = []
    for index, point in enumerate(state["observations"].get("x", [])):
        if len(point) == 3:
            repaired_xs.append(point)
            continue
        trial = state["trials"][index] if index < len(state["trials"]) else {}
        repaired_xs.append(
            [
                float(point[0]),
                float(trial.get("ion_temperature_ratio", default_ion_temperature_ratio)),
                float(trial.get("ion_mass_over_proton_mass", default_ion_mass)),
            ]
        )
    state["observations"]["x"] = repaired_xs
    state["observations"]["y"] = [float(trial["optimizer_objective"]) for trial in state["trials"]]
    successful_trials = [trial for trial in state["trials"] if not trial.get("failed")]
    state["best_result"] = min(successful_trials, key=lambda trial: float(trial["optimizer_objective"]), default=None)

    return state


def save_state(path: Path, state: dict) -> None:
    state["updated_at"] = utc_timestamp()
    atomic_write_json(path, state)


def replay_optimizer(state: dict, search_config: SearchConfig) -> Optimizer:
    optimizer = build_optimizer(search_config, random_state=state["optimizer"]["random_state"])
    xs = state["observations"].get("x", [])
    ys = state["observations"].get("y", [])
    if xs and ys:
        optimizer.tell(xs, ys)
    return optimizer


def register_trial(state: dict, trial_metrics: dict) -> dict:
    state["trials"].append(trial_metrics)
    state["observations"]["x"].append(
        [
            float(trial_metrics["drift_multiplier"]),
            float(trial_metrics["ion_temperature_ratio"]),
            float(trial_metrics["ion_mass_over_proton_mass"]),
        ]
    )
    state["observations"]["y"].append(float(trial_metrics["optimizer_objective"]))

    if not trial_metrics["failed"]:
        best_result = state.get("best_result")
        if best_result is None or trial_metrics["optimizer_objective"] < best_result["optimizer_objective"]:
            state["best_result"] = trial_metrics
    return state
