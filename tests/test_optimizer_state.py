from pathlib import Path

from jaxincell_drift_opt.config import load_search_config
from jaxincell_drift_opt.optimizer_state import default_state, load_state, register_trial, save_state


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
