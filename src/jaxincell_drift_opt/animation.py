from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .config import CampaignPaths, SearchConfig, load_base_input
from .utils import ensure_directory


def _to_hashable(value):
    if isinstance(value, list):
        return tuple(_to_hashable(item) for item in value)
    if isinstance(value, dict):
        return {key: _to_hashable(item) for key, item in value.items()}
    return value


def _load_frozen_case(trial_dir: Path) -> tuple[dict, dict] | None:
    frozen_input_path = trial_dir / "frozen_input.json"
    if not frozen_input_path.exists():
        return None
    payload = json.loads(frozen_input_path.read_text(encoding="utf-8"))
    return payload.get("input_parameters", {}), payload.get("solver_parameters", {})


def _render_mp4(input_parameters: dict, solver_parameters: dict, output_path: Path) -> None:
    from jax import block_until_ready
    from jaxincell import diagnostics, simulation
    from jaxincell._plot import plot as plot_movie

    ensure_directory(output_path.parent)
    normalized_solver_parameters = {key: _to_hashable(value) for key, value in solver_parameters.items()}
    rendered_output = block_until_ready(simulation(input_parameters, **normalized_solver_parameters))
    diagnostics(rendered_output)
    plot_movie(
        rendered_output,
        direction="x",
        save_mp4=str(output_path),
        fps=12,
        dpi=90,
        show=False,
        animation_interval=1,
        save_stride=2,
        save_dpi=70,
        save_crf=34,
    )


def _convert_mp4_to_gif(mp4_path: Path, gif_path: Path) -> None:
    ensure_directory(gif_path.parent)
    palette_path = gif_path.with_suffix(".palette.png")
    try:
        subprocess.run(
            [
                shutil.which("ffmpeg") or "ffmpeg",
                "-y",
                "-i",
                str(mp4_path),
                "-vf",
                "fps=10,scale=960:-1:flags=lanczos,palettegen",
                str(palette_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                shutil.which("ffmpeg") or "ffmpeg",
                "-y",
                "-i",
                str(mp4_path),
                "-i",
                str(palette_path),
                "-lavfi",
                "fps=10,scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse",
                str(gif_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        if palette_path.exists():
            palette_path.unlink()
        if mp4_path.exists():
            mp4_path.unlink()


def _baseline_trial(trials: list[dict], search_config: SearchConfig) -> dict | None:
    base_input = load_base_input(search_config.base_input).get("input_parameters", {})
    base_ion_temperature_ratio = float(base_input.get(search_config.ion_temperature_ratio_key, 0.01))
    base_ion_mass = float(base_input.get(search_config.ion_mass_key, 1.0))
    for trial in trials:
        if trial.get("failed"):
            continue
        if abs(float(trial["drift_multiplier"]) - float(search_config.baseline_multiplier)) > 1.0e-12:
            continue
        if abs(float(trial["candidate_ion_temperature_ratio"]) - base_ion_temperature_ratio) > 1.0e-12:
            continue
        if abs(float(trial["candidate_ion_mass_over_proton_mass"]) - base_ion_mass) > 1.0e-12:
            continue
        return trial
    return None


def _clear_readme_movie_assets(paths: CampaignPaths) -> None:
    for asset_name in [
        "initial-condition.gif",
        "leaderboard-rank-1.gif",
        "leaderboard-rank-2.gif",
        "initial-condition.mp4",
        "leaderboard-rank-1.mp4",
        "leaderboard-rank-2.mp4",
    ]:
        asset_path = paths.readme_assets_dir / asset_name
        if asset_path.exists():
            asset_path.unlink()


def render_readme_movies(paths: CampaignPaths, trials: list[dict], search_config: SearchConfig) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        return

    successful_trials = [trial for trial in trials if not trial.get("failed")]
    if not successful_trials:
        _clear_readme_movie_assets(paths)
        return

    ranked_trials = sorted(successful_trials, key=lambda trial: float(trial["optimizer_score"]), reverse=True)
    targets: list[tuple[str, str, dict]] = []
    baseline = _baseline_trial(successful_trials, search_config)
    if baseline is not None:
        targets.append(("initial-condition", "Initial condition", baseline))
    if ranked_trials:
        targets.append(("leaderboard-rank-1", "Leaderboard rank 1", ranked_trials[0]))
    if len(ranked_trials) > 1:
        targets.append(("leaderboard-rank-2", "Leaderboard rank 2", ranked_trials[1]))

    rendered_slugs = {slug for slug, _title, _trial in targets}
    for asset_name in ["initial-condition", "leaderboard-rank-1", "leaderboard-rank-2"]:
        if asset_name in rendered_slugs:
            continue
        for suffix in [".gif", ".mp4"]:
            asset_path = paths.readme_assets_dir / f"{asset_name}{suffix}"
            if asset_path.exists():
                asset_path.unlink()

    for slug, _title, trial in targets:
        if "trial_dir" not in trial:
            continue
        trial_dir = paths.root / trial["trial_dir"]
        frozen_case = _load_frozen_case(trial_dir)
        if frozen_case is None:
            continue
        input_parameters, solver_parameters = frozen_case
        mp4_path = paths.readme_assets_dir / f"{slug}.mp4"
        gif_path = paths.readme_assets_dir / f"{slug}.gif"
        _render_mp4(input_parameters, solver_parameters, mp4_path)
        _convert_mp4_to_gif(mp4_path, gif_path)
