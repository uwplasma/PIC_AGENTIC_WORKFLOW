from __future__ import annotations

from math import dist, log10
from pathlib import Path

import numpy as np

from .animation import render_readme_movies
from .config import CampaignPaths, load_scoring_config, load_search_config
from .optimizer_state import load_state, register_trial, replay_optimizer, save_state
from .plotting import (
    plot_baseline_vs_best,
    plot_best_run,
    plot_optimization_trace,
    plot_parameter_space_trajectory,
    plot_score_vs_multiplier,
)
from .reporting import write_agent_reasoning, write_best_result, write_readme_leaderboard, write_summary_markdown, write_trials_csv
from .run_trial import run_trial
from .utils import ensure_directory


def _normalize_point(point: list[float] | tuple[float, float, float], search_config) -> tuple[float, float, float]:
    drift = (float(point[0]) - search_config.drift_multiplier_min) / (
        search_config.drift_multiplier_max - search_config.drift_multiplier_min
    )
    log_temp_min = log10(search_config.ion_temperature_ratio_min)
    log_temp_max = log10(search_config.ion_temperature_ratio_max)
    log_mass_min = log10(search_config.ion_mass_min)
    log_mass_max = log10(search_config.ion_mass_max)
    ion_temp = (log10(float(point[1])) - log_temp_min) / (log_temp_max - log_temp_min)
    ion_mass = (log10(float(point[2])) - log_mass_min) / (log_mass_max - log_mass_min)
    return drift, ion_temp, ion_mass


def _minimum_distance(point: list[float] | tuple[float, float, float], existing_points: list[list[float]], search_config) -> float:
    if not existing_points:
        return float("inf")
    normalized = _normalize_point(point, search_config)
    return min(dist(normalized, _normalize_point(existing, search_config)) for existing in existing_points)


def _is_duplicate_point(point: list[float] | tuple[float, float, float], existing_points: list[list[float]], search_config) -> bool:
    return _minimum_distance(point, existing_points, search_config) <= search_config.duplicate_distance_threshold


def _coerce_point(point: list[float] | tuple[float, float, float]) -> list[float]:
    return [float(point[0]), float(point[1]), float(point[2])]


def _sample_fallback_point(existing_points: list[list[float]], search_config, *, random_state: int) -> list[float]:
    rng = np.random.default_rng(random_state)
    drift_samples = rng.uniform(
        search_config.drift_multiplier_min,
        search_config.drift_multiplier_max,
        search_config.fallback_random_candidates,
    )
    temp_logs = rng.uniform(
        log10(search_config.ion_temperature_ratio_min),
        log10(search_config.ion_temperature_ratio_max),
        search_config.fallback_random_candidates,
    )
    mass_logs = rng.uniform(
        log10(search_config.ion_mass_min),
        log10(search_config.ion_mass_max),
        search_config.fallback_random_candidates,
    )
    candidates = [
        [float(drift), float(10**temp_log), float(10**mass_log)]
        for drift, temp_log, mass_log in zip(drift_samples, temp_logs, mass_logs, strict=True)
    ]
    return max(candidates, key=lambda candidate: _minimum_distance(candidate, existing_points, search_config))


def choose_next_suggestion(state: dict, search_config) -> dict:
    optimizer = replay_optimizer(state, search_config)
    existing_points = [_coerce_point(point) for point in state.get("observations", {}).get("x", [])]

    try:
        candidate_pool = optimizer.ask(n_points=search_config.suggestion_batch_size, strategy="cl_min")
    except TypeError:
        candidate_pool = [optimizer.ask()]

    for candidate in candidate_pool:
        if not _is_duplicate_point(candidate, existing_points, search_config):
            chosen = _coerce_point(candidate)
            break
    else:
        fallback_seed = int(state["optimizer"]["random_state"]) + len(existing_points)
        chosen = _sample_fallback_point(existing_points, search_config, random_state=fallback_seed)

    return {
        "drift_multiplier": chosen[0],
        "ion_temperature_ratio": chosen[1],
        "ion_mass_over_proton_mass": chosen[2],
        "observations": len(state["trials"]),
        "ranges": {
            "drift_multiplier": [search_config.drift_multiplier_min, search_config.drift_multiplier_max],
            "ion_temperature_ratio": [search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max],
            "ion_mass_over_proton_mass": [search_config.ion_mass_min, search_config.ion_mass_max],
        },
    }


def refresh_outputs(paths: CampaignPaths, state: dict, search_config, scoring_config, *, render_movies: bool = True) -> None:
    ensure_directory(paths.state_dir)
    ensure_directory(paths.reports_dir)
    ensure_directory(paths.report_plots_dir)
    ensure_directory(paths.readme_assets_dir)
    write_trials_csv(paths.trials_csv_path, state["trials"])
    write_best_result(paths.best_result_path, state.get("best_result"))
    write_summary_markdown(paths.latest_summary_path, state["trials"], state.get("best_result"), search_config, scoring_config)
    next_suggestion = choose_next_suggestion(state, search_config)
    plot_optimization_trace(state["trials"], paths.report_plots_dir / "optimization_trace.png")
    plot_score_vs_multiplier(state["trials"], paths.report_plots_dir / "score_vs_drift_multiplier.png")
    plot_parameter_space_trajectory(
        state["trials"],
        search_config,
        paths.report_plots_dir / "parameter_space_trajectory.png",
        next_suggestion=next_suggestion,
    )
    if state.get("best_result"):
        plot_best_run(state["best_result"], paths.root, paths.report_plots_dir / "best_run_energy.png")
        plot_baseline_vs_best(state["trials"], paths.root, paths.report_plots_dir / "baseline_vs_best.png")
    write_agent_reasoning(paths.agent_reasoning_path, state["trials"], state.get("best_result"), search_config, next_suggestion)
    if render_movies:
        render_readme_movies(paths, state["trials"], search_config)
    write_readme_leaderboard(paths.root / "README.md", state["trials"], search_config)


def run_campaign(
    *,
    paths: CampaignPaths,
    num_trials: int,
    seed: int | None = None,
    drift_range_override: tuple[float, float] | None = None,
    trial_runner=run_trial,
) -> dict:
    search_config = load_search_config(paths.search_config_path)
    scoring_config = load_scoring_config(paths.scoring_config_path)
    if drift_range_override is not None:
        search_config = search_config.__class__(
            **{**search_config.__dict__, "drift_multiplier_min": drift_range_override[0], "drift_multiplier_max": drift_range_override[1]}
        )

    ensure_directory(paths.results_dir)
    state = load_state(paths.optimizer_state_path, search_config)

    if search_config.include_baseline and not state["trials"]:
        baseline_metrics = trial_runner(
            base_input_path=search_config.base_input,
            search_config=search_config,
            scoring_config=scoring_config,
            drift_multiplier=search_config.baseline_multiplier,
            ion_temperature_ratio=None,
            ion_mass_over_proton_mass=None,
            trial_index=0,
            output_root=paths.results_dir,
            seed=search_config.optimizer_random_state if seed is None else seed,
        )
        register_trial(state, baseline_metrics)
        save_state(paths.optimizer_state_path, state)
        refresh_outputs(paths, state, search_config, scoring_config, render_movies=False)

    start_index = len(state["trials"])

    for offset in range(num_trials):
        suggestion = choose_next_suggestion(state, search_config)
        drift_multiplier = float(suggestion["drift_multiplier"])
        ion_temperature_ratio = float(suggestion["ion_temperature_ratio"])
        ion_mass_over_proton_mass = float(suggestion["ion_mass_over_proton_mass"])
        trial_index = start_index + offset
        trial_seed = (search_config.optimizer_random_state if seed is None else seed) + trial_index
        trial_metrics = trial_runner(
            base_input_path=search_config.base_input,
            search_config=search_config,
            scoring_config=scoring_config,
            drift_multiplier=drift_multiplier,
            ion_temperature_ratio=ion_temperature_ratio,
            ion_mass_over_proton_mass=ion_mass_over_proton_mass,
            trial_index=trial_index,
            output_root=paths.results_dir,
            seed=trial_seed,
        )
        register_trial(state, trial_metrics)
        save_state(paths.optimizer_state_path, state)
        refresh_outputs(paths, state, search_config, scoring_config, render_movies=False)

    refresh_outputs(paths, state, search_config, scoring_config, render_movies=True)

    return state


def suggest_next(paths: CampaignPaths) -> dict:
    search_config = load_search_config(paths.search_config_path)
    state = load_state(paths.optimizer_state_path, search_config)
    return choose_next_suggestion(state, search_config)
