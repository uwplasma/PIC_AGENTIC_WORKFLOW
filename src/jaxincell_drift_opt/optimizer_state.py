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


def _trial_id_sort_key(trial_id: str) -> tuple[int, int | str]:
    prefix, separator, suffix = trial_id.rpartition("_")
    if prefix == "trial" and separator == "_":
        try:
            return (0, int(suffix))
        except ValueError:
            pass
    return (1, trial_id)


def rebuild_state(search_config: SearchConfig, trials: list[dict], *, template_state: dict | None = None) -> dict:
    state = default_state(search_config)
    template_state = template_state or {}

    state["schema_version"] = max(int(template_state.get("schema_version", STATE_SCHEMA_VERSION)), STATE_SCHEMA_VERSION)
    if template_state.get("created_at"):
        state["created_at"] = template_state["created_at"]

    optimizer_template = template_state.get("optimizer") or {}
    state["optimizer"] = {
        **state["optimizer"],
        **optimizer_template,
    }

    ordered_trials = sorted((dict(trial) for trial in trials), key=lambda trial: _trial_id_sort_key(str(trial.get("trial_id", ""))))
    for trial in ordered_trials:
        register_trial(state, trial)
    return state


def merge_states(preferred_state: dict, incoming_state: dict, search_config: SearchConfig) -> tuple[dict, list[str], list[str]]:
    preferred_by_id = {str(trial["trial_id"]): dict(trial) for trial in preferred_state.get("trials", [])}
    incoming_by_id = {str(trial["trial_id"]): dict(trial) for trial in incoming_state.get("trials", [])}

    new_trial_ids = [trial_id for trial_id in incoming_by_id if trial_id not in preferred_by_id]
    duplicate_trial_ids = [trial_id for trial_id in incoming_by_id if trial_id in preferred_by_id]

    merged_trials_by_id = {**incoming_by_id, **preferred_by_id}
    merged_trials = [merged_trials_by_id[trial_id] for trial_id in sorted(merged_trials_by_id, key=_trial_id_sort_key)]

    template_state = preferred_state if preferred_state else incoming_state
    merged_state = rebuild_state(search_config, merged_trials, template_state=template_state)
    merged_state["schema_version"] = max(
        int(preferred_state.get("schema_version", STATE_SCHEMA_VERSION)),
        int(incoming_state.get("schema_version", STATE_SCHEMA_VERSION)),
        STATE_SCHEMA_VERSION,
    )

    created_candidates = [value for value in [preferred_state.get("created_at"), incoming_state.get("created_at")] if value]
    if created_candidates:
        merged_state["created_at"] = min(created_candidates)

    return merged_state, sorted(new_trial_ids, key=_trial_id_sort_key), sorted(duplicate_trial_ids, key=_trial_id_sort_key)
