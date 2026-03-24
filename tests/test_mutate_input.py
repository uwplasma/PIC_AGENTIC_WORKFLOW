from jaxincell_drift_opt.mutate_input import apply_drift_multiplier


def test_apply_drift_multiplier_updates_candidate_value():
    input_parameters = {"electron_drift_speed_x": 6.0e7, "seed": 1701}
    mutated, mutation = apply_drift_multiplier(input_parameters, 1.5, "electron_drift_speed_x")

    assert input_parameters["electron_drift_speed_x"] == 6.0e7
    assert mutated["electron_drift_speed_x"] == 9.0e7
    assert mutation["base_drift"] == 6.0e7
    assert mutation["candidate_drift"] == 9.0e7
