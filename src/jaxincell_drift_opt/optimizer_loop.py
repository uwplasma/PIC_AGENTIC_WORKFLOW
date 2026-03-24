from __future__ import annotations

from pathlib import Path

from .config import CampaignPaths, load_scoring_config, load_search_config
from .optimizer_state import load_state, register_trial, replay_optimizer, save_state
from .plotting import plot_baseline_vs_best, plot_best_run, plot_optimization_trace, plot_score_vs_multiplier
from .reporting import write_best_result, write_summary_markdown, write_trials_csv
from .run_trial import run_trial
from .utils import ensure_directory


def refresh_outputs(paths: CampaignPaths, state: dict, search_config, scoring_config) -> None:
    ensure_directory(paths.state_dir)
    ensure_directory(paths.reports_dir)
    ensure_directory(paths.report_plots_dir)
    write_trials_csv(paths.trials_csv_path, state["trials"])
    write_best_result(paths.best_result_path, state.get("best_result"))
    write_summary_markdown(paths.latest_summary_path, state["trials"], state.get("best_result"), search_config, scoring_config)
    plot_optimization_trace(state["trials"], paths.report_plots_dir / "optimization_trace.png")
    plot_score_vs_multiplier(state["trials"], paths.report_plots_dir / "score_vs_drift_multiplier.png")
    if state.get("best_result"):
        plot_best_run(state["best_result"], paths.root, paths.report_plots_dir / "best_run_energy.png")
        plot_baseline_vs_best(state["trials"], paths.root, paths.report_plots_dir / "baseline_vs_best.png")


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
            trial_index=0,
            output_root=paths.results_dir,
            seed=search_config.optimizer_random_state if seed is None else seed,
        )
        register_trial(state, baseline_metrics)
        save_state(paths.optimizer_state_path, state)
        refresh_outputs(paths, state, search_config, scoring_config)

    optimizer = replay_optimizer(state, search_config)
    start_index = len(state["trials"])

    for offset in range(num_trials):
        suggestion = optimizer.ask()
        drift_multiplier = float(suggestion[0])
        trial_index = start_index + offset
        trial_seed = (search_config.optimizer_random_state if seed is None else seed) + trial_index
        trial_metrics = trial_runner(
            base_input_path=search_config.base_input,
            search_config=search_config,
            scoring_config=scoring_config,
            drift_multiplier=drift_multiplier,
            trial_index=trial_index,
            output_root=paths.results_dir,
            seed=trial_seed,
        )
        optimizer.tell([drift_multiplier], float(trial_metrics["optimizer_objective"]))
        register_trial(state, trial_metrics)
        save_state(paths.optimizer_state_path, state)
        refresh_outputs(paths, state, search_config, scoring_config)

    return state


def suggest_next(paths: CampaignPaths) -> dict:
    search_config = load_search_config(paths.search_config_path)
    state = load_state(paths.optimizer_state_path, search_config)
    optimizer = replay_optimizer(state, search_config)
    suggestion = optimizer.ask()
    return {
        "drift_multiplier": float(suggestion[0]),
        "observations": len(state["trials"]),
        "range": [search_config.drift_multiplier_min, search_config.drift_multiplier_max],
    }
