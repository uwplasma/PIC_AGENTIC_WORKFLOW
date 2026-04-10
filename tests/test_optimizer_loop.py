from pathlib import Path

from jaxincell_drift_opt.config import campaign_paths, load_base_input, load_search_config
from jaxincell_drift_opt.optimizer_loop import choose_next_suggestion, run_campaign
from jaxincell_drift_opt.optimizer_state import default_state, register_trial


def _write_test_configs(root: Path) -> None:
    source_root = Path(__file__).resolve().parents[1]
    (root / "configs" / "search.yaml").write_text((source_root / "configs" / "search.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "configs" / "scoring.yaml").write_text((source_root / "configs" / "scoring.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "configs" / "base_input.toml").write_text((source_root / "configs" / "base_input.toml").read_text(encoding="utf-8"), encoding="utf-8")


def _sample_trial(*, trial_id: str, drift_multiplier: float, ion_temperature_ratio: float, ion_mass_over_proton_mass: float) -> dict:
    return {
        "trial_id": trial_id,
        "started_at": "2026-03-24T00:00:00+00:00",
        "drift_multiplier": drift_multiplier,
        "ion_temperature_ratio": ion_temperature_ratio,
        "ion_mass_over_proton_mass": ion_mass_over_proton_mass,
        "candidate_drift": 2.0e7 * drift_multiplier,
        "candidate_ion_temperature_ratio": ion_temperature_ratio,
        "candidate_ion_mass_over_proton_mass": ion_mass_over_proton_mass,
        "tail_mean_E": 1.0,
        "tail_max_E": 1.0,
        "final_E": 1.0,
        "time_of_peak_E": 1.0,
        "optimizer_score": 0.0,
        "optimizer_objective": 0.0,
        "wall_time_seconds": 0.1,
        "seed": 1701,
        "failed": False,
        "failure_reason": None,
        "timeseries_path": "",
        "plot_path": "",
        "base_drift": 2.0e7,
    }


def test_run_campaign_with_mock_runner(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "configs").mkdir()
    (root / "state").mkdir()
    (root / "reports").mkdir()
    (root / "results").mkdir()

    _write_test_configs(root)

    def fake_trial_runner(*, drift_multiplier, trial_index, output_root, **_kwargs):
        trial_dir = output_root / f"trial_{trial_index:04d}"
        trial_dir.mkdir(parents=True, exist_ok=True)
        timeseries = trial_dir / "timeseries.npz"
        import numpy as np

        np.savez(timeseries, time_array=np.arange(4), electric_field_energy=np.array([1.0, 2.0, 3.0, 4.0]))
        return {
            "trial_id": f"trial_{trial_index:04d}",
            "started_at": "2026-03-24T00:00:00+00:00",
            "drift_multiplier": drift_multiplier,
            "ion_temperature_ratio": _kwargs.get("ion_temperature_ratio") or 0.01,
            "ion_mass_over_proton_mass": _kwargs.get("ion_mass_over_proton_mass") or 1.0,
            "candidate_drift": 6.0e7 * drift_multiplier,
            "candidate_ion_temperature_ratio": _kwargs.get("ion_temperature_ratio") or 0.01,
            "candidate_ion_mass_over_proton_mass": _kwargs.get("ion_mass_over_proton_mass") or 1.0,
            "tail_mean_E": drift_multiplier,
            "tail_max_E": drift_multiplier,
            "final_E": drift_multiplier,
            "time_of_peak_E": 1.0,
            "optimizer_score": drift_multiplier,
            "optimizer_objective": -drift_multiplier,
            "wall_time_seconds": 0.1,
            "seed": 1701 + trial_index,
            "failed": False,
            "failure_reason": None,
            "timeseries_path": str(timeseries.relative_to(root)),
            "plot_path": "",
            "base_drift": 6.0e7,
        }

    state = run_campaign(paths=campaign_paths(root), num_trials=2, trial_runner=fake_trial_runner)
    assert len(state["trials"]) == 3
    assert state["best_result"] is not None
    assert state["best_result"]["optimizer_score"] == max(trial["optimizer_score"] for trial in state["trials"])
    assert (root / "state" / "optimizer_state.json").exists()
    assert (root / "reports" / "latest_summary.md").exists()


def test_run_campaign_renders_movies_once_per_invocation(tmp_path: Path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "configs").mkdir()
    (root / "state").mkdir()
    (root / "reports").mkdir()
    (root / "results").mkdir()

    _write_test_configs(root)

    render_calls: list[int] = []

    def fake_render_readme_movies(_paths, _trials, _search_config):
        render_calls.append(len(_trials))

    def fake_trial_runner(*, drift_multiplier, trial_index, output_root, **_kwargs):
        trial_dir = output_root / f"trial_{trial_index:04d}"
        trial_dir.mkdir(parents=True, exist_ok=True)
        timeseries = trial_dir / "timeseries.npz"
        import numpy as np

        np.savez(timeseries, time_array=np.arange(4), electric_field_energy=np.array([1.0, 2.0, 3.0, 4.0]))
        return {
            "trial_id": f"trial_{trial_index:04d}",
            "started_at": "2026-03-24T00:00:00+00:00",
            "drift_multiplier": drift_multiplier,
            "ion_temperature_ratio": _kwargs.get("ion_temperature_ratio") or 0.01,
            "ion_mass_over_proton_mass": _kwargs.get("ion_mass_over_proton_mass") or 1.0,
            "candidate_drift": 6.0e7 * drift_multiplier,
            "candidate_ion_temperature_ratio": _kwargs.get("ion_temperature_ratio") or 0.01,
            "candidate_ion_mass_over_proton_mass": _kwargs.get("ion_mass_over_proton_mass") or 1.0,
            "tail_mean_E": drift_multiplier,
            "tail_max_E": drift_multiplier,
            "final_E": drift_multiplier,
            "time_of_peak_E": 1.0,
            "optimizer_score": drift_multiplier,
            "optimizer_objective": -drift_multiplier,
            "wall_time_seconds": 0.1,
            "seed": 1701 + trial_index,
            "failed": False,
            "failure_reason": None,
            "timeseries_path": str(timeseries.relative_to(root)),
            "plot_path": "",
            "base_drift": 6.0e7,
        }

    monkeypatch.setattr("jaxincell_drift_opt.optimizer_loop.render_readme_movies", fake_render_readme_movies)

    state = run_campaign(paths=campaign_paths(root), num_trials=2, trial_runner=fake_trial_runner)

    assert len(state["trials"]) == 3
    assert render_calls == [3]


def test_base_input_meets_hourly_leaderboard_particle_floor():
    base_input = load_base_input(Path(__file__).resolve().parents[1] / "configs" / "base_input.toml")
    assert int(base_input["solver_parameters"]["number_pseudoelectrons"]) >= 3500


def test_choose_next_suggestion_skips_duplicate_batch_candidate(tmp_path: Path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "configs").mkdir()
    _write_test_configs(root)

    search_config = load_search_config((root / "configs" / "search.yaml").resolve())
    state = default_state(search_config)
    register_trial(
        state,
        _sample_trial(
            trial_id="trial_0000",
            drift_multiplier=1.0,
            ion_temperature_ratio=0.01,
            ion_mass_over_proton_mass=1.0,
        ),
    )

    class FakeOptimizer:
        def ask(self, n_points=None, strategy=None):
            assert n_points == search_config.suggestion_batch_size
            assert strategy == "cl_min"
            return [[1.0, 0.01, 1.0], [1.8, 0.02, 0.5]]

    monkeypatch.setattr("jaxincell_drift_opt.optimizer_loop.replay_optimizer", lambda *_args, **_kwargs: FakeOptimizer())

    suggestion = choose_next_suggestion(state, search_config)

    assert suggestion["drift_multiplier"] == 1.8
    assert suggestion["ion_temperature_ratio"] == 0.02
    assert suggestion["ion_mass_over_proton_mass"] == 0.5


def test_choose_next_suggestion_falls_back_when_batch_is_all_duplicate(tmp_path: Path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "configs").mkdir()
    _write_test_configs(root)

    search_config = load_search_config((root / "configs" / "search.yaml").resolve())
    state = default_state(search_config)
    register_trial(
        state,
        _sample_trial(
            trial_id="trial_0000",
            drift_multiplier=1.0,
            ion_temperature_ratio=0.01,
            ion_mass_over_proton_mass=1.0,
        ),
    )

    class FakeOptimizer:
        def ask(self, n_points=None, strategy=None):
            return [[1.0, 0.01, 1.0]] * n_points

    monkeypatch.setattr("jaxincell_drift_opt.optimizer_loop.replay_optimizer", lambda *_args, **_kwargs: FakeOptimizer())
    monkeypatch.setattr("jaxincell_drift_opt.optimizer_loop._sample_fallback_point", lambda *_args, **_kwargs: [2.0, 0.001, 4.0])

    suggestion = choose_next_suggestion(state, search_config)

    assert suggestion["drift_multiplier"] == 2.0
    assert suggestion["ion_temperature_ratio"] == 0.001
    assert suggestion["ion_mass_over_proton_mass"] == 4.0
