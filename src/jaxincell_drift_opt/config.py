from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

import yaml


@dataclass(frozen=True)
class SearchConfig:
    base_input: Path
    drift_key: str
    drift_multiplier_min: float
    drift_multiplier_max: float
    ion_temperature_ratio_key: str
    ion_temperature_ratio_min: float
    ion_temperature_ratio_max: float
    ion_mass_key: str
    ion_mass_min: float
    ion_mass_max: float
    include_baseline: bool
    baseline_multiplier: float
    optimizer_random_state: int
    n_initial_points: int
    acq_func: str
    base_estimator: str
    state_branch: str
    trials_per_run_default: int
    leaderboard_size: int
    trusted_runner_label: str
    self_hosted_runner_label: tuple[str, ...]


@dataclass(frozen=True)
class ScoringConfig:
    tail_fraction: float
    eps: float
    failure_penalty: float
    score_version: str


@dataclass(frozen=True)
class CampaignPaths:
    root: Path

    @property
    def configs_dir(self) -> Path:
        return self.root / "configs"

    @property
    def results_dir(self) -> Path:
        return self.root / "results"

    @property
    def reports_dir(self) -> Path:
        return self.root / "reports"

    @property
    def report_plots_dir(self) -> Path:
        return self.reports_dir / "plots"

    @property
    def readme_assets_dir(self) -> Path:
        return self.reports_dir / "readme_assets"

    @property
    def state_dir(self) -> Path:
        return self.root / "state"

    @property
    def search_config_path(self) -> Path:
        return self.configs_dir / "search.yaml"

    @property
    def scoring_config_path(self) -> Path:
        return self.configs_dir / "scoring.yaml"

    @property
    def optimizer_state_path(self) -> Path:
        return self.state_dir / "optimizer_state.json"

    @property
    def trials_csv_path(self) -> Path:
        return self.state_dir / "trials.csv"

    @property
    def best_result_path(self) -> Path:
        return self.state_dir / "best_result.json"

    @property
    def latest_summary_path(self) -> Path:
        return self.reports_dir / "latest_summary.md"

    @property
    def agent_reasoning_path(self) -> Path:
        return self.reports_dir / "agent_reasoning.md"


def campaign_paths(root: Path | None = None) -> CampaignPaths:
    resolved_root = (root or Path.cwd()).resolve()
    return CampaignPaths(root=resolved_root)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_search_config(path: Path) -> SearchConfig:
    data = load_yaml(path)
    return SearchConfig(
        base_input=(path.parent.parent / data["base_input"]).resolve(),
        drift_key=data["drift_key"],
        drift_multiplier_min=float(data["drift_multiplier_min"]),
        drift_multiplier_max=float(data["drift_multiplier_max"]),
        ion_temperature_ratio_key=str(data.get("ion_temperature_ratio_key", "ion_temperature_over_electron_temperature_x")),
        ion_temperature_ratio_min=float(data.get("ion_temperature_ratio_min", 1.0e-3)),
        ion_temperature_ratio_max=float(data.get("ion_temperature_ratio_max", 1.0)),
        ion_mass_key=str(data.get("ion_mass_key", "ion_mass_over_proton_mass")),
        ion_mass_min=float(data.get("ion_mass_min", 0.25)),
        ion_mass_max=float(data.get("ion_mass_max", 4.0)),
        include_baseline=bool(data.get("include_baseline", True)),
        baseline_multiplier=float(data.get("baseline_multiplier", 1.0)),
        optimizer_random_state=int(data.get("optimizer_random_state", 1701)),
        n_initial_points=int(data.get("n_initial_points", 4)),
        acq_func=str(data.get("acq_func", "EI")),
        base_estimator=str(data.get("base_estimator", "GP")),
        state_branch=str(data.get("state_branch", "main")),
        trials_per_run_default=int(data.get("trials_per_run_default", 2)),
        leaderboard_size=int(data.get("leaderboard_size", 10)),
        trusted_runner_label=str(data.get("trusted_runner_label", "ubuntu-latest")),
        self_hosted_runner_label=tuple(data.get("self_hosted_runner_label", ["self-hosted", "trusted-uwplasma"])),
    )


def load_scoring_config(path: Path) -> ScoringConfig:
    data = load_yaml(path)
    return ScoringConfig(
        tail_fraction=float(data.get("tail_fraction", 0.2)),
        eps=float(data.get("eps", 1.0e-30)),
        failure_penalty=float(data.get("failure_penalty", 1.0e6)),
        score_version=str(data.get("score_version", "tail_mean_electric_field_energy_v1")),
    )


def load_base_input(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)
