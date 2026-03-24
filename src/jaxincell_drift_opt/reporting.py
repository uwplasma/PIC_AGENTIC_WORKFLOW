from __future__ import annotations

from pathlib import Path

from .config import ScoringConfig, SearchConfig
from .utils import atomic_write_json, atomic_write_text, write_csv


def write_trials_csv(path: Path, trials: list[dict]) -> None:
    fieldnames = [
        "trial_id",
        "started_at",
        "drift_multiplier",
        "candidate_drift",
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
    lines = [
        "# Latest Summary",
        "",
        "## Campaign",
        "",
        f"- Trials completed: {len(trials)}",
        f"- Drift range: [{search_config.drift_multiplier_min}, {search_config.drift_multiplier_max}]",
        f"- Drift key: {search_config.drift_key}",
        f"- Score version: {scoring_config.score_version}",
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
                f"- Optimizer score: {best_result['optimizer_score']:.6f}",
                f"- Tail mean E: {best_result['tail_mean_E']:.6e}",
                f"- Final E: {best_result['final_E']:.6e}",
                "",
            ]
        )

    if trials:
        lines.extend(["## Recent Trials", ""])
        for trial in trials[-10:]:
            lines.append(
                f"- {trial['trial_id']}: multiplier={trial['drift_multiplier']:.6f}, score={trial['optimizer_score']:.6f}, failed={trial['failed']}"
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
