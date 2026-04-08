from pathlib import Path

import numpy as np

from jaxincell_drift_opt.plotting import load_timeseries


def test_load_timeseries_normalizes_time_with_saved_plasma_frequency(tmp_path: Path):
    npz_path = tmp_path / "timeseries.npz"
    np.savez(
        npz_path,
        time_array=np.array([0.0, 0.5, 1.0]),
        electric_field_energy=np.array([1.0, 2.0, 3.0]),
        plasma_frequency=np.array(4.0),
    )

    time_array, electric_field_energy = load_timeseries(npz_path)

    assert np.allclose(time_array, np.array([0.0, 2.0, 4.0]))
    assert np.allclose(electric_field_energy, np.array([1.0, 2.0, 3.0]))


def test_load_timeseries_uses_raw_time_without_plasma_frequency(tmp_path: Path):
    npz_path = tmp_path / "timeseries.npz"
    np.savez(
        npz_path,
        time_array=np.array([0.0, 0.5, 1.0]),
        electric_field_energy=np.array([1.0, 2.0, 3.0]),
    )

    time_array, electric_field_energy = load_timeseries(npz_path)

    assert np.allclose(time_array, np.array([0.0, 0.5, 1.0]))
    assert np.allclose(electric_field_energy, np.array([1.0, 2.0, 3.0]))