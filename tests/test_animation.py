import json
from pathlib import Path

from jaxincell_drift_opt.animation import _apply_render_replay_profile, _effective_save_stride, render_readme_movies
from jaxincell_drift_opt.config import SearchConfig, campaign_paths, load_render_config


def test_load_render_config_defaults_when_missing(tmp_path: Path):
    render_config = load_render_config(tmp_path / "missing-rendering.yaml")

    assert render_config.max_ranked_movies == 1
    assert render_config.replay_max_grid_points == 64
    assert render_config.replay_max_pseudoelectrons == 4000
    assert render_config.replay_max_total_steps == 2000
    assert render_config.max_movie_seconds == 8.0
    assert render_config.gif_width == 640


def test_load_render_config_reads_ranked_movie_count(tmp_path: Path):
    config_path = tmp_path / "rendering.yaml"
    config_path.write_text("max_ranked_movies: 2\n", encoding="utf-8")

    render_config = load_render_config(config_path)

    assert render_config.max_ranked_movies == 2


def test_apply_render_replay_profile_caps_solver_parameters():
    profiled = _apply_render_replay_profile(
        {
            "number_grid_points": 120,
            "number_pseudoelectrons": 12000,
            "total_steps": 5000,
            "number_of_particle_substeps_implicit_CN": 2,
        },
        load_render_config(Path("/does/not/exist.yaml")),
    )

    assert profiled["number_grid_points"] == 64
    assert profiled["number_pseudoelectrons"] == 4000
    assert profiled["total_steps"] == 2000
    assert profiled["number_of_particle_substeps_implicit_CN"] == 2


def test_effective_save_stride_caps_movie_duration():
    render_config = load_render_config(Path("/does/not/exist.yaml"))

    effective_stride = _effective_save_stride({"total_steps": 2000}, render_config)

    assert effective_stride == 25


def test_effective_save_stride_respects_larger_configured_stride(tmp_path: Path):
    config_path = tmp_path / "rendering.yaml"
    config_path.write_text("save_stride: 40\nmax_movie_seconds: 8\nfps: 10\n", encoding="utf-8")
    render_config = load_render_config(config_path)

    effective_stride = _effective_save_stride({"total_steps": 2000}, render_config)

    assert effective_stride == 40


def test_render_readme_movies_reuses_duplicate_trial_render(tmp_path: Path, monkeypatch):
    root = tmp_path / "repo"
    (root / "configs").mkdir(parents=True)
    (root / "reports" / "readme_assets").mkdir(parents=True)
    (root / "results" / "trial_0000").mkdir(parents=True)

    (root / "configs" / "base_input.toml").write_text(
        "[input_parameters]\nion_temperature_over_electron_temperature_x = 0.01\nion_mass_over_proton_mass = 1.0\n",
        encoding="utf-8",
    )
    (root / "results" / "trial_0000" / "frozen_input.json").write_text(
        json.dumps(
            {
                "input_parameters": {"electron_drift_speed_x": 6e7},
                "solver_parameters": {
                    "number_grid_points": 120,
                    "number_pseudoelectrons": 12000,
                    "total_steps": 5000,
                },
            }
        ),
        encoding="utf-8",
    )

    render_calls: list[tuple[int, int, int]] = []
    convert_calls: list[str] = []

    def fake_render_mp4(_input_parameters, solver_parameters, output_path, _render_config):
        render_calls.append(
            (
                solver_parameters["number_grid_points"],
                solver_parameters["number_pseudoelectrons"],
                solver_parameters["total_steps"],
            )
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("mp4", encoding="utf-8")

    def fake_convert_mp4_to_gif(mp4_path, gif_path, _render_config):
        convert_calls.append(mp4_path.name)
        gif_path.write_text("gif", encoding="utf-8")
        mp4_path.unlink()

    monkeypatch.setattr("jaxincell_drift_opt.animation.shutil.which", lambda name: "/usr/bin/ffmpeg" if name == "ffmpeg" else None)
    monkeypatch.setattr("jaxincell_drift_opt.animation._render_mp4", fake_render_mp4)
    monkeypatch.setattr("jaxincell_drift_opt.animation._convert_mp4_to_gif", fake_convert_mp4_to_gif)

    search_config = SearchConfig(
        base_input=root / "configs" / "base_input.toml",
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
        self_hosted_runner_label=("self-hosted", "macOS", "ARM64", "uwplasma", "macmini"),
    )
    trial = {
        "trial_id": "trial_0000",
        "trial_dir": "results/trial_0000",
        "drift_multiplier": 1.0,
        "candidate_ion_temperature_ratio": 0.01,
        "candidate_ion_mass_over_proton_mass": 1.0,
        "optimizer_score": 0.5,
        "failed": False,
    }

    render_readme_movies(campaign_paths(root), [trial], search_config)

    assert render_calls == [(120, 12000, 5000)]
    assert convert_calls == ["initial-condition.mp4"]
    assert (root / "reports" / "readme_assets" / "initial-condition.gif").exists()
    assert (root / "reports" / "readme_assets" / "leaderboard-rank-1.gif").exists()