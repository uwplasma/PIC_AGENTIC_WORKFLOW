from pathlib import Path

from jaxincell_drift_opt.config import load_search_config
from jaxincell_drift_opt.optimizer_state import compute_campaign_id, default_state, load_state, merge_states, rebuild_state, register_trial, save_state


def test_optimizer_state_round_trip(tmp_path: Path):
    search_config = load_search_config(Path(__file__).resolve().parents[1] / "configs" / "search.yaml")
    state = default_state(search_config)
    register_trial(
        state,
        {
            "trial_id": "trial_0000",
            "drift_multiplier": 1.0,
            "ion_temperature_ratio": 0.01,
            "ion_mass_over_proton_mass": 1.0,
            "optimizer_score": -1.0,
            "optimizer_objective": 1.0,
            "failed": False,
        },
    )
    state_path = tmp_path / "optimizer_state.json"
    save_state(state_path, state)

    loaded = load_state(state_path, search_config)
    assert loaded["trials"][0]["trial_id"] == "trial_0000"
    assert loaded["observations"]["x"] == [[1.0, 0.01, 1.0]]
    assert loaded["observations"]["y"] == [1.0]


def test_load_state_recomputes_score_direction_from_tail_energy(tmp_path: Path):
    search_config = load_search_config(Path(__file__).resolve().parents[1] / "configs" / "search.yaml")
    state = {
        "schema_version": 1,
        "created_at": "2026-03-25T00:00:00+00:00",
        "updated_at": "2026-03-25T00:00:00+00:00",
        "optimizer": {},
        "observations": {"x": [[1.0, 0.01, 1.0]], "y": [999.0]},
        "trials": [
            {
                "trial_id": "trial_0000",
                "drift_multiplier": 1.0,
                "ion_temperature_ratio": 0.01,
                "ion_mass_over_proton_mass": 1.0,
                "candidate_ion_temperature_ratio": 0.01,
                "candidate_ion_mass_over_proton_mass": 1.0,
                "tail_mean_E": 1000.0,
                "optimizer_score": -3.0,
                "optimizer_objective": 3.0,
                "failed": False,
            }
        ],
        "best_result": None,
    }
    state_path = tmp_path / "optimizer_state.json"
    save_state(state_path, state)

    loaded = load_state(state_path, search_config)
    assert loaded["trials"][0]["optimizer_score"] == 3.0
    assert loaded["trials"][0]["optimizer_objective"] == -3.0
    assert loaded["best_result"]["trial_id"] == "trial_0000"


def test_default_state_includes_campaign_id():
    search_config = load_search_config(Path(__file__).resolve().parents[1] / "configs" / "search.yaml")

    state = default_state(search_config)

    assert state["campaign_id"] == compute_campaign_id(search_config)


def test_rebuild_state_reconstructs_observations_in_trial_order(tmp_path: Path):
    search_config = load_search_config(Path(__file__).resolve().parents[1] / "configs" / "search.yaml")
    trials = [
        {
            "trial_id": "trial_0002",
            "drift_multiplier": 1.2,
            "ion_temperature_ratio": 0.03,
            "ion_mass_over_proton_mass": 0.9,
            "optimizer_score": 0.2,
            "optimizer_objective": -0.2,
            "failed": False,
        },
        {
            "trial_id": "trial_0001",
            "drift_multiplier": 1.1,
            "ion_temperature_ratio": 0.02,
            "ion_mass_over_proton_mass": 1.1,
            "optimizer_score": 0.1,
            "optimizer_objective": -0.1,
            "failed": False,
        },
    ]

    rebuilt = rebuild_state(search_config, trials)

    assert [trial["trial_id"] for trial in rebuilt["trials"]] == ["trial_0001", "trial_0002"]
    assert rebuilt["observations"]["x"] == [[1.1, 0.02, 1.1], [1.2, 0.03, 0.9]]
    assert rebuilt["observations"]["y"] == [-0.1, -0.2]
    assert rebuilt["best_result"]["trial_id"] == "trial_0002"


def test_merge_states_keeps_preferred_duplicate_trial_and_adds_new_trials():
    search_config = load_search_config(Path(__file__).resolve().parents[1] / "configs" / "search.yaml")
    preferred = default_state(search_config)
    register_trial(
        preferred,
        {
            "trial_id": "trial_0001",
            "drift_multiplier": 1.1,
            "ion_temperature_ratio": 0.02,
            "ion_mass_over_proton_mass": 1.1,
            "optimizer_score": 0.4,
            "optimizer_objective": -0.4,
            "failed": False,
        },
    )

    incoming = default_state(search_config)
    register_trial(
        incoming,
        {
            "trial_id": "trial_0001",
            "drift_multiplier": 9.9,
            "ion_temperature_ratio": 9.9,
            "ion_mass_over_proton_mass": 9.9,
            "optimizer_score": 9.9,
            "optimizer_objective": -9.9,
            "failed": False,
        },
    )
    register_trial(
        incoming,
        {
            "trial_id": "trial_0002",
            "drift_multiplier": 1.2,
            "ion_temperature_ratio": 0.03,
            "ion_mass_over_proton_mass": 0.9,
            "optimizer_score": 0.5,
            "optimizer_objective": -0.5,
            "failed": False,
        },
    )

    merged, new_trial_ids, duplicate_trial_ids = merge_states(preferred, incoming, search_config)

    assert new_trial_ids == ["trial_0002"]
    assert duplicate_trial_ids == ["trial_0001"]
    assert [trial["trial_id"] for trial in merged["trials"]] == ["trial_0001", "trial_0002"]
    assert merged["trials"][0]["drift_multiplier"] == 1.1
    assert merged["best_result"]["trial_id"] == "trial_0002"
