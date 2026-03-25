from pathlib import Path

from jaxincell_drift_opt.config import campaign_paths
from jaxincell_drift_opt.optimizer_loop import run_campaign


def test_run_campaign_with_mock_runner(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "configs").mkdir()
    (root / "state").mkdir()
    (root / "reports").mkdir()
    (root / "results").mkdir()

    source_root = Path(__file__).resolve().parents[1]
    (root / "configs" / "search.yaml").write_text((source_root / "configs" / "search.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "configs" / "scoring.yaml").write_text((source_root / "configs" / "scoring.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (root / "configs" / "base_input.toml").write_text((source_root / "configs" / "base_input.toml").read_text(encoding="utf-8"), encoding="utf-8")

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
            "optimizer_score": -drift_multiplier,
            "optimizer_objective": drift_multiplier,
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
    assert (root / "state" / "optimizer_state.json").exists()
    assert (root / "reports" / "latest_summary.md").exists()
