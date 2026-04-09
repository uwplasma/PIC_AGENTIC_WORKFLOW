from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import ScoringConfig, SearchConfig, load_base_input
from .utils import atomic_write_json, atomic_write_text, replace_marked_section, write_csv


def _sorted_successful_trials(trials: list[dict]) -> list[dict]:
    return sorted((trial for trial in trials if not trial["failed"]), key=lambda trial: trial["optimizer_score"], reverse=True)


def _format_started_at(value: str | None) -> str:
    if not value:
        return "-"
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized).astimezone(timezone.utc)
        return parsed.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def _format_repo_relative_path(value: Path, repo_root: Path) -> str:
    try:
        return value.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return value.as_posix()


def write_trials_csv(path: Path, trials: list[dict]) -> None:
    fieldnames = [
        "trial_id",
        "started_at",
        "drift_multiplier",
        "ion_temperature_ratio",
        "ion_mass_over_proton_mass",
        "candidate_drift",
        "candidate_ion_temperature_ratio",
        "candidate_ion_mass_over_proton_mass",
        "tail_mean_E",
        "tail_max_E",
        "final_E",
        "time_of_peak_E",
        "optimizer_score",
        "optimizer_objective",
        "wall_time_seconds",
        "seed",
        "failed",
        "failure_reason",
    ]
    write_csv(path, fieldnames, trials)


def write_best_result(path: Path, best_result: dict | None) -> None:
    atomic_write_json(path, best_result or {})


def write_summary_markdown(
    path: Path,
    trials: list[dict],
    best_result: dict | None,
    search_config: SearchConfig,
    scoring_config: ScoringConfig,
) -> None:
    sorted_trials = _sorted_successful_trials(trials)
    lines = [
        "# Latest Summary",
        "",
        "## Campaign",
        "",
        f"- Trials completed: {len(trials)}",
        f"- Drift range: [{search_config.drift_multiplier_min}, {search_config.drift_multiplier_max}]",
        f"- Ion temperature ratio range: [{search_config.ion_temperature_ratio_min}, {search_config.ion_temperature_ratio_max}]",
        f"- Ion mass range: [{search_config.ion_mass_min}, {search_config.ion_mass_max}]",
        f"- Drift key: {search_config.drift_key}",
        f"- Score version: {scoring_config.score_version}",
        "- Physical target: maximize the tail-mean electrostatic energy over the final window.",
        "- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.",
        "",
    ]

    if best_result:
        lines.extend(
            [
                "## Best Result",
                "",
                f"- Trial: {best_result['trial_id']}",
                f"- Drift multiplier: {best_result['drift_multiplier']:.6f}",
                f"- Candidate drift: {best_result['candidate_drift']:.6e}",
                f"- Ion temperature ratio: {best_result['candidate_ion_temperature_ratio']:.6e}",
                f"- Ion mass over proton mass: {best_result['candidate_ion_mass_over_proton_mass']:.6e}",
                f"- Optimizer score: {best_result['optimizer_score']:.6f}",
                f"- Optimizer objective: {best_result['optimizer_objective']:.6f}",
                f"- Tail mean E: {best_result['tail_mean_E']:.6e}",
                f"- Final E: {best_result['final_E']:.6e}",
                "",
            ]
        )

    if sorted_trials:
        lines.extend(["## Leaderboard", "", "| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"])
        for index, trial in enumerate(sorted_trials[: search_config.leaderboard_size], start=1):
            lines.append(
                "| "
                f"{index} | {trial['trial_id']} | {_format_started_at(trial.get('started_at'))} | {trial['drift_multiplier']:.6f} | {trial['candidate_ion_temperature_ratio']:.6e} | "
                f"{trial['candidate_ion_mass_over_proton_mass']:.6e} | {trial['tail_mean_E']:.6e} | {trial['optimizer_score']:.6f} |"
            )
        lines.append("")

    if trials:
        lines.extend(["## Recent Trials", ""])
        for trial in trials[-10:]:
            lines.append(
                f"- {trial['trial_id']} at {_format_started_at(trial.get('started_at'))}: drift={trial['drift_multiplier']:.6f}, temp_ratio={trial['ion_temperature_ratio']:.6e}, mass_ratio={trial['ion_mass_over_proton_mass']:.6e}, score={trial['optimizer_score']:.6f}, failed={trial['failed']}"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- State is replayable from JSON observations in `state/optimizer_state.json`.",
            "- Workflow artifacts mirror `state/`, `reports/`, and `results/`.",
            (
                "- Scheduled workflow writes state, reports, and results directly to `main`."
                if search_config.state_branch == "main"
                else f"- Scheduled workflow should publish state to `{search_config.state_branch}`, not `main`."
            ),
            "",
        ]
    )
    atomic_write_text(path, "\n".join(lines) + "\n")


def write_agent_reasoning(
    path: Path,
    trials: list[dict],
    best_result: dict | None,
    search_config: SearchConfig,
    next_suggestion: dict | None,
) -> None:
    sorted_trials = _sorted_successful_trials(trials)
    base_input = load_base_input(search_config.base_input)
    repo_root = path.parent.parent.resolve()
    input_parameters = base_input.get("input_parameters", {})
    solver_parameters = base_input.get("solver_parameters", {})
    lines = [
        "# Agent Reasoning",
        "",
        "This report exposes the public-facing reasoning of the automated optimization loop.",
        "It is not a hidden chain-of-thought dump. It is a structured decision log covering the active run configuration, per-trial outcomes, current optimizer beliefs, and the planned next experiment.",
        "",
        "## Active Competition Configuration",
        "",
        f"- Base input: {_format_repo_relative_path(search_config.base_input, repo_root)}",
        f"- Number of grid points: {int(solver_parameters.get('number_grid_points', 0))}",
        f"- Number of pseudoelectrons: {int(solver_parameters.get('number_pseudoelectrons', 0))}",
        f"- Total steps: {int(solver_parameters.get('total_steps', 0))}",
        f"- Time step over spatial step times c: {float(input_parameters.get('timestep_over_spatialstep_times_c', 0.0)):.6g}",
        f"- Particle substeps per solver step: {int(solver_parameters.get('number_of_particle_substeps_implicit_CN', 0))}",
        f"- Baseline included: {search_config.include_baseline}",
        f"- Baseline drift multiplier: {search_config.baseline_multiplier:.6f}",
        "",
        "## Objective",
        "",
        "- Physical target: maximize the tail-mean electrostatic energy for the two-stream instability.",
        "- Optimizer objective: minimize the negative log10 of the tail-mean electrostatic energy.",
        f"- Drift multiplier range: [{search_config.drift_multiplier_min}, {search_config.drift_multiplier_max}]",
        f"- Ion temperature ratio range: [{search_config.ion_temperature_ratio_min}, {search_config.ion_temperature_ratio_max}]",
        f"- Ion mass range: [{search_config.ion_mass_min}, {search_config.ion_mass_max}]",
        "",
    ]

    if best_result is not None:
        lines.extend(
            [
                "## Current Best Hypothesis",
                "",
                f"- Best trial: {best_result['trial_id']}",
                f"- Score: {best_result['optimizer_score']:.6f}",
                f"- Optimizer objective: {best_result['optimizer_objective']:.6f}",
                f"- Tail mean electrostatic energy: {best_result['tail_mean_E']:.6e}",
                f"- Drift multiplier: {best_result['drift_multiplier']:.6f}",
                f"- Ion temperature ratio: {best_result['candidate_ion_temperature_ratio']:.6e}",
                f"- Ion mass over proton mass: {best_result['candidate_ion_mass_over_proton_mass']:.6e}",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Current Best Hypothesis",
                "",
                "- No completed successful trials are recorded yet for this competition reset.",
                "- The next run will establish the fresh baseline and first posterior update under the current solver parameters.",
                "",
            ]
        )

    if sorted_trials:
        lines.extend(["## What The Optimizer Has Learned", ""])
        for index, trial in enumerate(sorted_trials[:3], start=1):
            lines.append(
                f"- Rank {index}: {trial['trial_id']} reached score={trial['optimizer_score']:.6f} with drift={trial['drift_multiplier']:.6f}, temp_ratio={trial['candidate_ion_temperature_ratio']:.6e}, mass_ratio={trial['candidate_ion_mass_over_proton_mass']:.6e}."
            )
        lines.append("")

    if len(sorted_trials) >= 2:
        best = sorted_trials[0]
        runner_up = sorted_trials[1]
        lines.extend(
            [
                "## Relative Comparison",
                "",
                f"- The current best trial improves the public score over the runner-up by {best['optimizer_score'] - runner_up['optimizer_score']:.6f}.",
                f"- Compared with the initial condition, the best trial changes drift by a factor of {best['drift_multiplier']:.6f} and moves the ion temperature ratio to {best['candidate_ion_temperature_ratio']:.6e}.",
                "",
            ]
        )

    lines.extend(["## Trial-By-Trial Public Decision Log", ""])
    if trials:
        for trial in trials:
            lines.append(
                "- "
                f"{trial['trial_id']}: score={trial['optimizer_score']:.6f}, objective={trial['optimizer_objective']:.6f}, "
                f"tail_mean_E={trial['tail_mean_E']:.6e}, drift={trial['drift_multiplier']:.6f}, "
                f"temp_ratio={trial['candidate_ion_temperature_ratio']:.6e}, "
                f"mass_ratio={trial['candidate_ion_mass_over_proton_mass']:.6e}, "
                f"failed={trial['failed']}."
            )
    else:
        lines.append("- No trials have been run since the fresh-start reset.")
    lines.append("")

    if next_suggestion is not None:
        lines.extend(
            [
                "## Next Suggested Experiment",
                "",
                f"- Drift multiplier: {next_suggestion['drift_multiplier']:.6f}",
                f"- Ion temperature ratio: {next_suggestion['ion_temperature_ratio']:.6e}",
                f"- Ion mass over proton mass: {next_suggestion['ion_mass_over_proton_mass']:.6e}",
                f"- Observations available to the optimizer: {next_suggestion['observations']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Public Copilot Research Trail",
            "",
            "- Repository issue and pull request threads are the public review trail for the relativistic porting agent.",
            "- This markdown report is the public reasoning and decision trail for the unattended optimization loop.",
            "",
        ]
    )

    lines.extend(
        [
            "## How The Next Run Is Chosen",
            "",
            f"- The optimizer replays every prior observation stored in `state/optimizer_state.json` and then asks the Bayesian model for the next point using `{search_config.base_estimator}` with `{search_config.acq_func}` acquisition.",
            "- The public decision summary here is refreshed after every trial, so the next suggestion is always tied to the current recorded campaign state.",
            "- The live search bounds come from `configs/search.yaml`, and the execution loop lives in `src/jaxincell_drift_opt/optimizer_loop.py`.",
            "",
        ]
    )
    atomic_write_text(path, "\n".join(lines) + "\n")


def write_readme_leaderboard(path: Path, trials: list[dict], search_config: SearchConfig) -> None:
    if not path.exists():
        return
    marker_start = "<!-- leaderboard:start -->"
    marker_end = "<!-- leaderboard:end -->"
    sorted_trials = _sorted_successful_trials(trials)
    section_lines = [
        "## Optimization Leaderboard",
        "",
        f"This table updates directly on the live `{search_config.state_branch}` branch. Higher score means stronger nonlinear electrostatic saturation.",
        "",
        f"Search ranges: drift=[{search_config.drift_multiplier_min}, {search_config.drift_multiplier_max}], ion temperature ratio=[{search_config.ion_temperature_ratio_min}, {search_config.ion_temperature_ratio_max}], ion mass over proton mass=[{search_config.ion_mass_min}, {search_config.ion_mass_max}]",
        "",
    ]
    if sorted_trials:
        section_lines.extend(
            [
                "| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for index, trial in enumerate(sorted_trials[: search_config.leaderboard_size], start=1):
            section_lines.append(
                "| "
                f"{index} | {trial['trial_id']} | {_format_started_at(trial.get('started_at'))} | {trial['drift_multiplier']:.6f} | {trial['candidate_ion_temperature_ratio']:.6e} | "
                f"{trial['candidate_ion_mass_over_proton_mass']:.6e} | {trial['tail_mean_E']:.6e} | {trial['optimizer_score']:.6f} |"
            )
    else:
        section_lines.append("No successful optimization trials have been recorded yet for the restarted campaign.")
    section_lines.append("")
    if (path.parent / "reports/plots/parameter_space_trajectory.png").exists():
        section_lines.extend(
            [
                "### Parameter Space Map",
                "",
                "This live figure shows where the optimizer has already looked, the order it moved through the search space, the current best point, and the next suggested point.",
                "",
                "![Optimizer path through parameter space](reports/plots/parameter_space_trajectory.png)",
                "",
            ]
        )
    section_lines.extend(
        [
            "### Follow The Search",
            "",
            "- Read the agent's public reasoning: [reports/agent_reasoning.md](reports/agent_reasoning.md)",
            "- Watch scheduled live runs: [Optimize Scheduled](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-scheduled.yml)",
            "- Watch manual or restart runs: [Optimize Dispatch](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-dispatch.yml)",
            "- Watch optimization commits land on main: [main commit history](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/commits/main/)",
            "- See how the next point is chosen: [reports/agent_reasoning.md](reports/agent_reasoning.md), [src/jaxincell_drift_opt/optimizer_loop.py](src/jaxincell_drift_opt/optimizer_loop.py), and [configs/search.yaml](configs/search.yaml)",
            "",
        ]
    )
    exact_plot_assets = [
        ("Best scored run", Path("reports/plots/best_run_energy.png")),
        ("Baseline vs best", Path("reports/plots/baseline_vs_best.png")),
    ]
    existing_exact_plot_assets = [(title, asset_path) for title, asset_path in exact_plot_assets if (path.parent / asset_path).exists()]
    if existing_exact_plot_assets:
        section_lines.extend(
            [
                "### Exact Scored Energy Traces",
                "",
                "These PNGs come from the exact saved trial timeseries used for scoring. Use them for quantitative electric-field-energy comparisons; the time axis is shown in $\\omega_{pe}^{-1}$.",
                "",
            ]
        )
    for title, asset_path in existing_exact_plot_assets:
        section_lines.extend([f"#### {title}", "", f"![{title}]({asset_path.as_posix()})", ""])
    movie_assets = [
        ("Initial condition", Path("reports/readme_assets/initial-condition.mp4")),
        ("Leaderboard rank 1", Path("reports/readme_assets/leaderboard-rank-1.mp4")),
        ("Leaderboard rank 2", Path("reports/readme_assets/leaderboard-rank-2.mp4")),
    ]
    existing_movie_assets = [(title, asset_path) for title, asset_path in movie_assets if (path.parent / asset_path).exists()]
    if existing_movie_assets:
        section_lines.extend(
            [
                "### Full-Simulation Movies",
                "",
                "These MP4 movies are rerun from the full saved trial configurations with no solver caps. They use frame skipping only, so the movie duration stays short while still covering the full simulation window.",
                "GitHub renders them as direct MP4 links on the README page rather than inline video players.",
                "",
            ]
        )
    for title, asset_path in existing_movie_assets:
        section_lines.extend(
            [
                f"#### {title}",
                "",
                f"[Open {title} MP4]({asset_path.as_posix()})",
                "",
            ]
        )
    updated = replace_marked_section(path.read_text(encoding="utf-8"), marker_start, marker_end, section_lines)
    atomic_write_text(path, updated)
