from __future__ import annotations

import json
from pathlib import Path

from skopt import Optimizer
from skopt.space import Real

from .config import SearchConfig
from .utils import atomic_write_json, utc_timestamp


STATE_SCHEMA_VERSION = 1


def build_optimizer(search_config: SearchConfig, random_state: int | None = None) -> Optimizer:
    return Optimizer(
        dimensions=[Real(search_config.drift_multiplier_min, search_config.drift_multiplier_max, name="drift_multiplier")],
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
            "range": [search_config.drift_multiplier_min, search_config.drift_multiplier_max],
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
    state.setdefault("trials", [])
    state.setdefault("observations", {"x": [], "y": []})
    state.setdefault("best_result", None)
    state.setdefault("optimizer", {})
    state["optimizer"].setdefault("random_state", search_config.optimizer_random_state)
    state["optimizer"].setdefault("base_estimator", search_config.base_estimator)
    state["optimizer"].setdefault("acq_func", search_config.acq_func)
    state["optimizer"].setdefault("n_initial_points", search_config.n_initial_points)
    state["optimizer"].setdefault("range", [search_config.drift_multiplier_min, search_config.drift_multiplier_max])
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
    state["observations"]["x"].append([float(trial_metrics["drift_multiplier"])])
    state["observations"]["y"].append(float(trial_metrics["optimizer_objective"]))

    if not trial_metrics["failed"]:
        best_result = state.get("best_result")
        if best_result is None or trial_metrics["optimizer_score"] > best_result["optimizer_score"]:
            state["best_result"] = trial_metrics
    return state
