from jaxincell_drift_opt.mutate_input import apply_drift_multiplier, apply_search_parameters


def test_apply_drift_multiplier_updates_candidate_value():
    input_parameters = {"electron_drift_speed_x": 6.0e7, "seed": 1701}
    mutated, mutation = apply_drift_multiplier(input_parameters, 1.5, "electron_drift_speed_x")

    assert input_parameters["electron_drift_speed_x"] == 6.0e7
    assert mutated["electron_drift_speed_x"] == 9.0e7
    assert mutation["base_drift"] == 6.0e7
    assert mutation["candidate_drift"] == 9.0e7


def test_apply_search_parameters_updates_all_campaign_controls():
    input_parameters = {
        "electron_drift_speed_x": 6.0e7,
        "ion_temperature_over_electron_temperature_x": 0.01,
        "ion_mass_over_proton_mass": 1.0,
    }

    mutated, mutation = apply_search_parameters(
        input_parameters,
        drift_multiplier=1.5,
        ion_temperature_ratio=0.2,
        ion_mass_over_proton_mass=3.0,
        drift_key="electron_drift_speed_x",
        ion_temperature_ratio_key="ion_temperature_over_electron_temperature_x",
        ion_mass_key="ion_mass_over_proton_mass",
    )

    assert mutated["electron_drift_speed_x"] == 9.0e7
    assert mutated["ion_temperature_over_electron_temperature_x"] == 0.2
    assert mutated["ion_mass_over_proton_mass"] == 3.0
    assert mutation["candidate_ion_temperature_ratio"] == 0.2
    assert mutation["candidate_ion_mass_over_proton_mass"] == 3.0
