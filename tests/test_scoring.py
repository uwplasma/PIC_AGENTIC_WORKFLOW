import numpy as np

from jaxincell_drift_opt.scoring import extract_electric_field_energy, score_trial_output


def test_extract_electric_field_energy_prefers_existing_series():
    series = np.array([1.0, 2.0, 3.0])
    output = {"electric_field_energy": series}
    np.testing.assert_allclose(extract_electric_field_energy(output), series)


def test_score_trial_output_uses_tail_mean_log_score():
    output = {
        "electric_field_energy": np.array([1.0, 10.0, 100.0, 1000.0]),
        "time_array": np.array([0.0, 1.0, 2.0, 3.0]),
    }
    metrics = score_trial_output(
        output,
        drift_multiplier=1.0,
        ion_temperature_ratio=0.01,
        ion_mass_over_proton_mass=1.0,
        seed=1701,
        wall_time_seconds=1.25,
        tail_fraction=0.25,
        eps=1.0e-30,
        failure_penalty=-1.0e6,
    )

    assert metrics["tail_mean_E"] == 1000.0
    assert metrics["tail_max_E"] == 1000.0
    assert metrics["final_E"] == 1000.0
    assert metrics["time_of_peak_E"] == 3.0
    assert metrics["optimizer_score"] == 3.0
    assert metrics["optimizer_objective"] == -3.0
