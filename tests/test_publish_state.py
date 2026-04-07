import json
from pathlib import Path

from jaxincell_drift_opt.config import load_search_config
from jaxincell_drift_opt.optimizer_state import default_state, register_trial, save_state
from jaxincell_drift_opt.publish_state import merge_campaign_state


def _write_repo_skeleton(root: Path) -> None:
    (root / "configs").mkdir(parents=True)
    (root / "state").mkdir(parents=True)
    (root / "reports").mkdir(parents=True)
    (root / "results").mkdir(parents=True)
    (root / "README.md").write_text(
        "<!-- leaderboard:start -->\nplaceholder\n<!-- leaderboard:end -->\n",
        encoding="utf-8",
    )
    (root / "configs" / "base_input.toml").write_text(
        "[input_parameters]\n"
        "electron_drift_speed_x = 60000000.0\n"
        "ion_temperature_over_electron_temperature_x = 0.01\n"
        "ion_mass_over_proton_mass = 1.0\n\n"
        "[solver_parameters]\n"
        "number_grid_points = 120\n"
        "number_pseudoelectrons = 12000\n"
        "total_steps = 5000\n"
        "number_of_particle_substeps_implicit_CN = 2\n",
        encoding="utf-8",
    )
    (root / "configs" / "search.yaml").write_text(
        "base_input: configs/base_input.toml\n"
        "drift_key: electron_drift_speed_x\n"
        "drift_multiplier_min: 0.01\n"
        "drift_multiplier_max: 2.5\n"
        "ion_temperature_ratio_key: ion_temperature_over_electron_temperature_x\n"
        "ion_temperature_ratio_min: 0.001\n"
        "ion_temperature_ratio_max: 100.0\n"
        "ion_mass_key: ion_mass_over_proton_mass\n"
        "ion_mass_min: 0.01\n"
        "ion_mass_max: 4.0\n"
        "include_baseline: true\n"
        "baseline_multiplier: 1.0\n"
        "optimizer_random_state: 1701\n"
        "n_initial_points: 4\n"
        "acq_func: EI\n"
        "base_estimator: GP\n"
        "state_branch: main\n"
        "trials_per_run_default: 1\n"
        "leaderboard_size: 10\n"
        "trusted_runner_label: ubuntu-latest\n"
        "self_hosted_runner_label: [self-hosted]\n",
        encoding="utf-8",
    )
    (root / "configs" / "scoring.yaml").write_text(
        "tail_fraction: 0.2\n"
        "eps: 1.0e-30\n"
        "failure_penalty: 1000000.0\n"
        "score_version: tail_mean_electric_field_energy_max_v2\n",
        encoding="utf-8",
    )


def _trial(trial_id: str, drift_multiplier: float, score: float) -> dict:
    return {
        "trial_id": trial_id,
        "trial_dir": f"results/{trial_id}",
        "plot_path": f"results/{trial_id}/electric_field_energy.png",
        "timeseries_path": f"results/{trial_id}/timeseries.npz",
        "drift_multiplier": drift_multiplier,
        "ion_temperature_ratio": 0.01,
        "ion_mass_over_proton_mass": 1.0,
        "candidate_drift": 60000000.0 * drift_multiplier,
        "candidate_ion_temperature_ratio": 0.01,
        "candidate_ion_mass_over_proton_mass": 1.0,
        "tail_mean_E": 10**score,
        "tail_max_E": 10**score,
        "final_E": 10**score,
        "time_of_peak_E": 0.0,
        "optimizer_score": score,
        "optimizer_objective": -score,
        "wall_time_seconds": 1.0,
        "seed": 1701,
        "failed": False,
        "failure_reason": None,
        "started_at": "2026-04-07T00:00:00+00:00",
    }


def test_merge_campaign_state_copies_new_trials_and_saves_merged_state(tmp_path: Path, monkeypatch):
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_repo_skeleton(source_root)
    _write_repo_skeleton(target_root)

    search_config = load_search_config(target_root / "configs" / "search.yaml")

    target_state = default_state(search_config)
    register_trial(target_state, _trial("trial_0000", 1.0, 0.2))
    save_state(target_root / "state" / "optimizer_state.json", target_state)

    source_state = default_state(search_config)
    register_trial(source_state, _trial("trial_0000", 1.0, 0.2))
    register_trial(source_state, _trial("trial_0001", 1.1, 0.4))
    save_state(source_root / "state" / "optimizer_state.json", source_state)

    (source_root / "results" / "trial_0001").mkdir(parents=True)
    (source_root / "results" / "trial_0001" / "metrics.json").write_text(json.dumps({"trial_id": "trial_0001"}), encoding="utf-8")

    refresh_calls: list[list[str]] = []

    def fake_refresh_outputs(_paths, state, _search_config, _scoring_config, *, render_movies=True):
        refresh_calls.append([trial["trial_id"] for trial in state["trials"]])

    monkeypatch.setattr("jaxincell_drift_opt.publish_state.refresh_outputs", fake_refresh_outputs)

    result = merge_campaign_state(source_root, target_root)

    merged = json.loads((target_root / "state" / "optimizer_state.json").read_text(encoding="utf-8"))
    assert result["changed"] is True
    assert result["reason"] == "merged"
    assert result["new_trial_ids"] == ["trial_0001"]
    assert (target_root / "results" / "trial_0001" / "metrics.json").exists()
    assert [trial["trial_id"] for trial in merged["trials"]] == ["trial_0000", "trial_0001"]
    assert refresh_calls == [["trial_0000", "trial_0001"]]


def test_merge_campaign_state_skips_duplicate_only_updates(tmp_path: Path, monkeypatch):
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_repo_skeleton(source_root)
    _write_repo_skeleton(target_root)

    search_config = load_search_config(target_root / "configs" / "search.yaml")
    target_state = default_state(search_config)
    register_trial(target_state, _trial("trial_0000", 1.0, 0.2))
    save_state(target_root / "state" / "optimizer_state.json", target_state)
    save_state(source_root / "state" / "optimizer_state.json", target_state)

    refresh_calls: list[int] = []
    monkeypatch.setattr(
        "jaxincell_drift_opt.publish_state.refresh_outputs",
        lambda *_args, **_kwargs: refresh_calls.append(1),
    )

    result = merge_campaign_state(source_root, target_root)

    assert result["changed"] is False
    assert result["reason"] == "no_new_trials"
    assert result["duplicate_trial_ids"] == ["trial_0000"]
    assert refresh_calls == []


def test_merge_campaign_state_rejects_mismatched_campaign_id(tmp_path: Path, monkeypatch):
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_repo_skeleton(source_root)
    _write_repo_skeleton(target_root)

    search_config = load_search_config(target_root / "configs" / "search.yaml")
    target_state = default_state(search_config)
    save_state(target_root / "state" / "optimizer_state.json", target_state)

    source_state = default_state(search_config)
    source_state["campaign_id"] = "old-campaign"
    register_trial(source_state, _trial("trial_0000", 1.0, 0.2))
    save_state(source_root / "state" / "optimizer_state.json", source_state)

    refresh_calls: list[int] = []
    monkeypatch.setattr(
        "jaxincell_drift_opt.publish_state.refresh_outputs",
        lambda *_args, **_kwargs: refresh_calls.append(1),
    )

    result = merge_campaign_state(source_root, target_root)

    assert result["changed"] is False
    assert result["reason"] == "campaign_mismatch"
    assert refresh_calls == []


def test_merge_campaign_state_rejects_legacy_source_state_when_target_has_campaign_id(tmp_path: Path, monkeypatch):
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    _write_repo_skeleton(source_root)
    _write_repo_skeleton(target_root)

    search_config = load_search_config(target_root / "configs" / "search.yaml")
    target_state = default_state(search_config)
    save_state(target_root / "state" / "optimizer_state.json", target_state)

    legacy_source_state = {
        "schema_version": 2,
        "created_at": "2026-04-07T00:00:00+00:00",
        "updated_at": "2026-04-07T00:00:00+00:00",
        "optimizer": target_state["optimizer"],
        "observations": {"x": [[1.0, 0.01, 1.0]], "y": [-0.2]},
        "trials": [_trial("trial_0000", 1.0, 0.2)],
        "best_result": _trial("trial_0000", 1.0, 0.2),
    }
    (source_root / "state" / "optimizer_state.json").write_text(json.dumps(legacy_source_state, indent=2), encoding="utf-8")

    refresh_calls: list[int] = []
    monkeypatch.setattr(
        "jaxincell_drift_opt.publish_state.refresh_outputs",
        lambda *_args, **_kwargs: refresh_calls.append(1),
    )

    result = merge_campaign_state(source_root, target_root)

    assert result["changed"] is False
    assert result["reason"] == "legacy_source_campaign"
    assert refresh_calls == []