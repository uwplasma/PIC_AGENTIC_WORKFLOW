from pathlib import Path

from jaxincell_drift_opt.config import SearchConfig
from jaxincell_drift_opt.reporting import write_readme_leaderboard


def test_write_readme_leaderboard_emphasizes_exact_plots_over_preview_movies(tmp_path: Path):
    readme_path = tmp_path / "README.md"
    readme_path.write_text("before\n<!-- leaderboard:start -->\nold\n<!-- leaderboard:end -->\nafter\n", encoding="utf-8")

    (tmp_path / "reports" / "plots").mkdir(parents=True)
    (tmp_path / "reports" / "readme_assets").mkdir(parents=True)
    (tmp_path / "reports" / "plots" / "best_run_energy.png").write_text("png", encoding="utf-8")
    (tmp_path / "reports" / "plots" / "baseline_vs_best.png").write_text("png", encoding="utf-8")
    (tmp_path / "reports" / "readme_assets" / "leaderboard-rank-1.mp4").write_text("mp4", encoding="utf-8")

    search_config = SearchConfig(
        base_input=tmp_path / "configs" / "base_input.toml",
        drift_key="electron_drift_speed_x",
        drift_multiplier_min=0.01,
        drift_multiplier_max=2.5,
        ion_temperature_ratio_key="ion_temperature_over_electron_temperature_x",
        ion_temperature_ratio_min=1.0e-3,
        ion_temperature_ratio_max=1.0e2,
        ion_mass_key="ion_mass_over_proton_mass",
        ion_mass_min=0.01,
        ion_mass_max=4.0,
        include_baseline=True,
        baseline_multiplier=1.0,
        optimizer_random_state=1701,
        n_initial_points=4,
        acq_func="EI",
        base_estimator="GP",
        state_branch="main",
        trials_per_run_default=1,
        leaderboard_size=20,
        trusted_runner_label="ubuntu-latest",
        self_hosted_runner_label=("self-hosted", "macOS"),
    )

    write_readme_leaderboard(readme_path, [], search_config)

    content = readme_path.read_text(encoding="utf-8")
    assert "### Exact Scored Energy Traces" in content
    assert "Use them for quantitative electric-field-energy comparisons" in content
    assert "### Full-Simulation Movies" in content
    assert "They use frame skipping only" in content
    assert "<video src=\"reports/readme_assets/leaderboard-rank-1.mp4\" controls" in content