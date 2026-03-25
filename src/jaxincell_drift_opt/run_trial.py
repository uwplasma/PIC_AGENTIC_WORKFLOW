from __future__ import annotations

from pathlib import Path

import numpy as np

from .config import ScoringConfig, SearchConfig
from .jaxincell_adapter import run_jaxincell_case
from .plotting import plot_trial_energy_series
from .scoring import extract_electric_field_energy, score_trial_output
from .utils import atomic_write_json, atomic_write_text, ensure_directory, to_serializable, utc_timestamp


def run_trial(
    *,
    base_input_path: Path,
    search_config: SearchConfig,
    scoring_config: ScoringConfig,
    drift_multiplier: float,
    ion_temperature_ratio: float | None,
    ion_mass_over_proton_mass: float | None,
    trial_index: int,
    output_root: Path,
    seed: int | None = None,
) -> dict:
    trial_id = f"trial_{trial_index:04d}"
    trial_dir = ensure_directory(output_root / trial_id)

    try:
        result = run_jaxincell_case(
            base_input_path=base_input_path,
            drift_multiplier=drift_multiplier,
            ion_temperature_ratio=ion_temperature_ratio,
            ion_mass_over_proton_mass=ion_mass_over_proton_mass,
            drift_key=search_config.drift_key,
            ion_temperature_ratio_key=search_config.ion_temperature_ratio_key,
            ion_mass_key=search_config.ion_mass_key,
            seed=seed,
            print_info=False,
        )
        output = result["output"]
        electric_field_energy = extract_electric_field_energy(output)
        time_array = np.asarray(output.get("time_array"), dtype=float)
        metrics = score_trial_output(
            output,
            drift_multiplier=drift_multiplier,
            ion_temperature_ratio=result["mutation"]["candidate_ion_temperature_ratio"],
            ion_mass_over_proton_mass=result["mutation"]["candidate_ion_mass_over_proton_mass"],
            seed=seed,
            wall_time_seconds=result["wall_time_seconds"],
            tail_fraction=scoring_config.tail_fraction,
            eps=scoring_config.eps,
            failure_penalty=scoring_config.failure_penalty,
            score_version=scoring_config.score_version,
        )
        metrics.update(
            {
                "trial_id": trial_id,
                "started_at": utc_timestamp(),
                "base_input_path": str(base_input_path),
                "drift_key": search_config.drift_key,
                "base_drift": result["mutation"]["base_drift"],
                "candidate_drift": result["mutation"]["candidate_drift"],
                "ion_temperature_ratio_key": search_config.ion_temperature_ratio_key,
                "base_ion_temperature_ratio": result["mutation"]["base_ion_temperature_ratio"],
                "candidate_ion_temperature_ratio": result["mutation"]["candidate_ion_temperature_ratio"],
                "ion_mass_key": search_config.ion_mass_key,
                "base_ion_mass_over_proton_mass": result["mutation"]["base_ion_mass_over_proton_mass"],
                "candidate_ion_mass_over_proton_mass": result["mutation"]["candidate_ion_mass_over_proton_mass"],
                "trial_dir": str(trial_dir.relative_to(output_root.parent)),
                "timeseries_path": str((trial_dir / "timeseries.npz").relative_to(output_root.parent)),
                "plot_path": str((trial_dir / "electric_field_energy.png").relative_to(output_root.parent)),
            }
        )

        np.savez(
            trial_dir / "timeseries.npz",
            time_array=time_array,
            electric_field_energy=electric_field_energy,
        )
        plot_trial_energy_series(
            time_array,
            electric_field_energy,
            trial_dir / "electric_field_energy.png",
            title=f"{trial_id} electric-field energy",
        )
        atomic_write_json(
            trial_dir / "frozen_input.json",
            {
                "input_parameters": result["input_parameters"],
                "solver_parameters": result["solver_parameters"],
            },
        )
        atomic_write_json(trial_dir / "metrics.json", metrics)
        atomic_write_text(
            trial_dir / "run.log",
            "\n".join(
                [
                    f"trial_id={trial_id}",
                    f"drift_multiplier={drift_multiplier}",
                    f"candidate_drift={metrics['candidate_drift']}",
                    f"candidate_ion_temperature_ratio={metrics['candidate_ion_temperature_ratio']}",
                    f"candidate_ion_mass_over_proton_mass={metrics['candidate_ion_mass_over_proton_mass']}",
                    f"optimizer_score={metrics['optimizer_score']}",
                    f"optimizer_objective={metrics['optimizer_objective']}",
                    f"wall_time_seconds={metrics['wall_time_seconds']}",
                ]
            )
            + "\n",
        )
        return metrics
    except Exception as exc:
        metrics = score_trial_output(
            {},
            drift_multiplier=drift_multiplier,
            ion_temperature_ratio=1.0 if ion_temperature_ratio is None else ion_temperature_ratio,
            ion_mass_over_proton_mass=1.0 if ion_mass_over_proton_mass is None else ion_mass_over_proton_mass,
            seed=seed,
            wall_time_seconds=0.0,
            tail_fraction=scoring_config.tail_fraction,
            eps=scoring_config.eps,
            failure_penalty=scoring_config.failure_penalty,
            score_version=scoring_config.score_version,
            failed=True,
            failure_reason=str(exc),
        )
        metrics.update(
            {
                "trial_id": trial_id,
                "started_at": utc_timestamp(),
                "base_input_path": str(base_input_path),
                "drift_key": search_config.drift_key,
                "base_drift": None,
                "candidate_drift": None,
                "ion_temperature_ratio_key": search_config.ion_temperature_ratio_key,
                "base_ion_temperature_ratio": None,
                "candidate_ion_temperature_ratio": ion_temperature_ratio,
                "ion_mass_key": search_config.ion_mass_key,
                "base_ion_mass_over_proton_mass": None,
                "candidate_ion_mass_over_proton_mass": ion_mass_over_proton_mass,
                "trial_dir": str(trial_dir.relative_to(output_root.parent)),
                "timeseries_path": "",
                "plot_path": "",
            }
        )
        atomic_write_json(trial_dir / "metrics.json", to_serializable(metrics))
        atomic_write_text(trial_dir / "run.log", f"failure={exc}\n")
        return metrics
