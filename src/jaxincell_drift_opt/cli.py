from __future__ import annotations

import argparse
from pathlib import Path

from .config import campaign_paths, load_scoring_config, load_search_config
from .optimizer_loop import run_campaign, suggest_next
from .optimizer_state import default_state, save_state
from .reporting import write_best_result, write_summary_markdown, write_trials_csv
from .run_trial import run_trial


def _parse_range(value: str | None) -> tuple[float, float] | None:
    if not value:
        return None
    lower, upper = value.split(",", maxsplit=1)
    return float(lower), float(upper)


def run_one_trial_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drift-multiplier", type=float, required=True)
    parser.add_argument("--ion-temperature-ratio", type=float, default=None)
    parser.add_argument("--ion-mass-over-proton-mass", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    paths = campaign_paths(args.root)
    search_config = load_search_config(paths.search_config_path)
    scoring_config = load_scoring_config(paths.scoring_config_path)
    metrics = run_trial(
        base_input_path=search_config.base_input,
        search_config=search_config,
        scoring_config=scoring_config,
        drift_multiplier=args.drift_multiplier,
        ion_temperature_ratio=args.ion_temperature_ratio,
        ion_mass_over_proton_mass=args.ion_mass_over_proton_mass,
        trial_index=0,
        output_root=paths.results_dir,
        seed=args.seed,
    )
    print(metrics)


def run_campaign_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-trials", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--drift-range", type=str, default=None)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    paths = campaign_paths(args.root)
    search_config = load_search_config(paths.search_config_path)
    state = run_campaign(
        paths=paths,
        num_trials=args.num_trials or search_config.trials_per_run_default,
        seed=args.seed,
        drift_range_override=_parse_range(args.drift_range),
    )
    print(state.get("best_result"))


def suggest_next_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(suggest_next(campaign_paths(args.root)))


def summarize_results_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    paths = campaign_paths(args.root)
    search_config = load_search_config(paths.search_config_path)
    scoring_config = load_scoring_config(paths.scoring_config_path)
    from .optimizer_state import load_state

    state = load_state(paths.optimizer_state_path, search_config)
    write_trials_csv(paths.trials_csv_path, state["trials"])
    write_best_result(paths.best_result_path, state.get("best_result"))
    write_summary_markdown(paths.latest_summary_path, state["trials"], state.get("best_result"), search_config, scoring_config)
    print(paths.latest_summary_path)


def bootstrap_state_main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    paths = campaign_paths(args.root)
    search_config = load_search_config(paths.search_config_path)
    save_state(paths.optimizer_state_path, default_state(search_config))
    write_trials_csv(paths.trials_csv_path, [])
    write_best_result(paths.best_result_path, None)
    write_summary_markdown(paths.latest_summary_path, [], None, search_config, load_scoring_config(paths.scoring_config_path))
    print(paths.optimizer_state_path)
