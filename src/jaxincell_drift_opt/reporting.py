from __future__ import annotations

from pathlib import Path

from .config import ScoringConfig, SearchConfig, load_base_input
from .utils import atomic_write_json, atomic_write_text, replace_marked_section, write_csv


def _sorted_successful_trials(trials: list[dict]) -> list[dict]:
    return sorted((trial for trial in trials if not trial["failed"]), key=lambda trial: trial["optimizer_objective"])


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
        "- Objective: minimize the log10 of tail-mean electrostatic energy.",
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
        lines.extend(["## Leaderboard", "", "| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"])
        for index, trial in enumerate(sorted_trials[: search_config.leaderboard_size], start=1):
            lines.append(
                "| "
                f"{index} | {trial['trial_id']} | {trial['drift_multiplier']:.6f} | {trial['candidate_ion_temperature_ratio']:.6e} | "
                f"{trial['candidate_ion_mass_over_proton_mass']:.6e} | {trial['tail_mean_E']:.6e} | {trial['optimizer_objective']:.6f} |"
            )
        lines.append("")

    if trials:
        lines.extend(["## Recent Trials", ""])
        for trial in trials[-10:]:
            lines.append(
                f"- {trial['trial_id']}: drift={trial['drift_multiplier']:.6f}, temp_ratio={trial['ion_temperature_ratio']:.6e}, mass_ratio={trial['ion_mass_over_proton_mass']:.6e}, objective={trial['optimizer_objective']:.6f}, failed={trial['failed']}"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- State is replayable from JSON observations in `state/optimizer_state.json`.",
            "- Workflow artifacts mirror `state/`, `reports/`, and `results/`.",
            f"- Scheduled workflow should publish state to `{search_config.state_branch}`, not `main`.",
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
    solver_parameters = base_input.get("solver_parameters", {})
    lines = [
        "# Agent Reasoning",
        "",
        "This report exposes the public-facing reasoning of the automated optimization loop.",
        "It is not a hidden chain-of-thought dump. It is a structured decision log covering the active run configuration, per-trial outcomes, current optimizer beliefs, and the planned next experiment.",
        "",
        "## Active Competition Configuration",
        "",
        f"- Base input: {search_config.base_input}",
        f"- Number of grid points: {int(solver_parameters.get('number_grid_points', 0))}",
        f"- Number of pseudoelectrons: {int(solver_parameters.get('number_pseudoelectrons', 0))}",
        f"- Total steps: {int(solver_parameters.get('total_steps', 0))}",
        f"- Baseline included: {search_config.include_baseline}",
        f"- Baseline drift multiplier: {search_config.baseline_multiplier:.6f}",
        "",
        "## Objective",
        "",
        "- Minimize the log10 of the tail-mean electrostatic energy for the two-stream instability.",
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
                f"- Objective: {best_result['optimizer_objective']:.6f}",
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
                f"- Rank {index}: {trial['trial_id']} reached objective={trial['optimizer_objective']:.6f} with drift={trial['drift_multiplier']:.6f}, temp_ratio={trial['candidate_ion_temperature_ratio']:.6e}, mass_ratio={trial['candidate_ion_mass_over_proton_mass']:.6e}."
            )
        lines.append("")

    if len(sorted_trials) >= 2:
        best = sorted_trials[0]
        runner_up = sorted_trials[1]
        lines.extend(
            [
                "## Relative Comparison",
                "",
                f"- The current best trial improves the objective over the runner-up by {runner_up['optimizer_objective'] - best['optimizer_objective']:.6f}.",
                f"- Compared with the initial condition, the best trial changes drift by a factor of {best['drift_multiplier']:.6f} and moves the ion temperature ratio to {best['candidate_ion_temperature_ratio']:.6e}.",
                "",
            ]
        )

    lines.extend(["## Trial-By-Trial Public Decision Log", ""])
    if trials:
        for trial in trials:
            lines.append(
                "- "
                f"{trial['trial_id']}: objective={trial['optimizer_objective']:.6f}, "
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
        "Hourly self-hosted search minimizes the log10 of the tail-mean electrostatic energy for the two-stream instability over drift multiplier, ion-to-electron temperature ratio, and ion mass proxy.",
        "",
        f"Search ranges: drift=[{search_config.drift_multiplier_min}, {search_config.drift_multiplier_max}], ion temperature ratio=[{search_config.ion_temperature_ratio_min}, {search_config.ion_temperature_ratio_max}], ion mass over proton mass=[{search_config.ion_mass_min}, {search_config.ion_mass_max}]",
        "",
    ]
    if sorted_trials:
        section_lines.extend(
            [
                "| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for index, trial in enumerate(sorted_trials[: search_config.leaderboard_size], start=1):
            section_lines.append(
                "| "
                f"{index} | {trial['trial_id']} | {trial['drift_multiplier']:.6f} | {trial['candidate_ion_temperature_ratio']:.6e} | "
                f"{trial['candidate_ion_mass_over_proton_mass']:.6e} | {trial['tail_mean_E']:.6e} | {trial['optimizer_objective']:.6f} |"
            )
    else:
        section_lines.append("No successful optimization trials have been recorded yet.")
    section_lines.append("")
    section_lines.extend(
        [
            "### Movies",
            "",
            "The GIFs below reuse the multi-panel JAX-in-Cell movie layout so you can inspect phase space, field evolution, and the energy subplot directly in the public repository.",
            "",
        ]
    )
    movie_assets = [
        ("Initial condition", Path("reports/readme_assets/initial-condition.gif")),
        ("Leaderboard rank 1", Path("reports/readme_assets/leaderboard-rank-1.gif")),
        ("Leaderboard rank 2", Path("reports/readme_assets/leaderboard-rank-2.gif")),
    ]
    for title, asset_path in movie_assets:
        if (path.parent / asset_path).exists():
            section_lines.extend([f"#### {title}", "", f"![{title}]({asset_path.as_posix()})", ""])
    if (path.parent / "reports/agent_reasoning.md").exists():
        section_lines.append("See [reports/agent_reasoning.md](reports/agent_reasoning.md) for the public optimizer reasoning and next suggested experiment.")
        section_lines.append("")
    updated = replace_marked_section(path.read_text(encoding="utf-8"), marker_start, marker_end, section_lines)
    atomic_write_text(path, updated)
