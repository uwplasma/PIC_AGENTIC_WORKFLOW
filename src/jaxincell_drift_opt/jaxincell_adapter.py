from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .mutate_input import apply_search_parameters


def _load_jaxincell_symbols() -> dict[str, Any]:
    from jax import block_until_ready
    from jaxincell import diagnostics, load_parameters, simulation
    from jaxincell._simulation import initialize_simulation_parameters

    return {
        "block_until_ready": block_until_ready,
        "diagnostics": diagnostics,
        "initialize_simulation_parameters": initialize_simulation_parameters,
        "load_parameters": load_parameters,
        "simulation": simulation,
    }


def load_base_case(base_input_path: Path) -> tuple[dict, dict, dict]:
    symbols = _load_jaxincell_symbols()
    input_parameters, solver_parameters = symbols["load_parameters"](str(base_input_path))
    initialized_parameters = symbols["initialize_simulation_parameters"](dict(input_parameters))
    return input_parameters, solver_parameters, initialized_parameters


def validate_drift_key(base_input_path: Path, drift_key: str) -> None:
    input_parameters, _, initialized_parameters = load_base_case(base_input_path)
    if drift_key not in input_parameters and drift_key not in initialized_parameters:
        available = sorted(initialized_parameters.keys())
        raise KeyError(f"Drift key '{drift_key}' is not supported by the installed JAX-in-Cell interface. Available keys include: {available}")


def run_jaxincell_case(
    base_input_path: Path,
    drift_multiplier: float,
    ion_temperature_ratio: float | None,
    ion_mass_over_proton_mass: float | None,
    drift_key: str,
    ion_temperature_ratio_key: str,
    ion_mass_key: str,
    seed: int | None = None,
    print_info: bool = False,
) -> dict[str, Any]:
    symbols = _load_jaxincell_symbols()
    input_parameters, solver_parameters, initialized_parameters = load_base_case(base_input_path)

    if drift_key not in input_parameters:
        if drift_key not in initialized_parameters:
            raise KeyError(f"Drift key '{drift_key}' is missing from the current JAX-in-Cell parameter schema")
        input_parameters[drift_key] = initialized_parameters[drift_key]

    mutated_input, mutation = apply_search_parameters(
        input_parameters,
        drift_multiplier=drift_multiplier,
        ion_temperature_ratio=ion_temperature_ratio,
        ion_mass_over_proton_mass=ion_mass_over_proton_mass,
        drift_key=drift_key,
        ion_temperature_ratio_key=ion_temperature_ratio_key,
        ion_mass_key=ion_mass_key,
    )
    mutated_input["print_info"] = bool(print_info)
    if seed is not None:
        mutated_input["seed"] = int(seed)

    start = time.perf_counter()
    output = symbols["block_until_ready"](symbols["simulation"](mutated_input, **solver_parameters))
    wall_time_seconds = time.perf_counter() - start
    symbols["diagnostics"](output)

    return {
        "base_input_path": str(base_input_path),
        "input_parameters": mutated_input,
        "solver_parameters": solver_parameters,
        "mutation": mutation,
        "wall_time_seconds": wall_time_seconds,
        "output": output,
    }
