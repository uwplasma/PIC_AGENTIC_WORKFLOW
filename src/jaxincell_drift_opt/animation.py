from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from .config import CampaignPaths, RenderConfig, SearchConfig, load_base_input, load_render_config
from .utils import ensure_directory


def _movie_manifest_path(paths: CampaignPaths) -> Path:
    return paths.readme_assets_dir / "movie_manifest.json"


def _load_movie_manifest(paths: CampaignPaths) -> dict[str, str]:
    manifest_path = _movie_manifest_path(paths)
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items()}


def _save_movie_manifest(paths: CampaignPaths, manifest: dict[str, str]) -> None:
    manifest_path = _movie_manifest_path(paths)
    if not manifest:
        if manifest_path.exists():
            manifest_path.unlink()
        return
    ensure_directory(manifest_path.parent)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def _effective_save_stride(solver_parameters: dict, render_config: RenderConfig) -> int:
    base_stride = max(1, int(render_config.save_stride))
    total_steps = int(solver_parameters.get("total_steps", 0))
    if total_steps <= 0:
        return base_stride

    max_movie_seconds = float(render_config.max_movie_seconds)
    fps = max(1, int(render_config.fps))
    max_frames = max(1, math.floor(max_movie_seconds * fps))
    duration_limited_stride = max(1, math.ceil(total_steps / max_frames))
    return max(base_stride, duration_limited_stride)


def _render_mp4(input_parameters: dict, solver_parameters: dict, output_path: Path, render_config: RenderConfig) -> None:
    from jax import block_until_ready
    from jaxincell import diagnostics, simulation
    from jaxincell._plot import plot as plot_movie

    ensure_directory(output_path.parent)
    full_solver_parameters = dict(solver_parameters)
    effective_save_stride = _effective_save_stride(full_solver_parameters, render_config)
    normalized_solver_parameters = {key: _to_hashable(value) for key, value in full_solver_parameters.items()}
    rendered_output = block_until_ready(simulation(input_parameters, **normalized_solver_parameters))
    diagnostics(rendered_output)
    plot_movie(
        rendered_output,
        direction="x",
        save_mp4=str(output_path),
        fps=render_config.fps,
        dpi=render_config.dpi,
        show=False,
        animation_interval=1,
        save_stride=effective_save_stride,
        save_dpi=render_config.save_dpi,
        save_crf=render_config.save_crf,
        save_preset=render_config.save_preset,
        save_codec=render_config.save_codec,
    )


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
    _save_movie_manifest(paths, {})


def _movie_targets(trials: list[dict], search_config: SearchConfig, render_config: RenderConfig) -> list[tuple[str, str, dict]]:
    ranked_trials = sorted(trials, key=lambda trial: float(trial["optimizer_score"]), reverse=True)
    targets: list[tuple[str, str, dict]] = []
    baseline = _baseline_trial(trials, search_config)
    if render_config.include_baseline_movie and baseline is not None:
        targets.append(("initial-condition", "Initial condition", baseline))
    for rank, trial in enumerate(ranked_trials[: max(0, render_config.max_ranked_movies)], start=1):
        targets.append((f"leaderboard-rank-{rank}", f"Leaderboard rank {rank}", trial))
    return targets


def render_readme_movies(paths: CampaignPaths, trials: list[dict], search_config: SearchConfig) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        return

    render_config = load_render_config(paths.rendering_config_path)

    successful_trials = [trial for trial in trials if not trial.get("failed")]
    if not successful_trials:
        _clear_readme_movie_assets(paths)
        return

    targets = _movie_targets(successful_trials, search_config, render_config)
    existing_manifest = _load_movie_manifest(paths)
    updated_manifest: dict[str, str] = {}

    rendered_slugs = {slug for slug, _title, _trial in targets}
    for asset_name in ["initial-condition", "leaderboard-rank-1", "leaderboard-rank-2"]:
        if asset_name in rendered_slugs:
            continue
        for suffix in [".gif", ".mp4"]:
            asset_path = paths.readme_assets_dir / f"{asset_name}{suffix}"
            if asset_path.exists():
                asset_path.unlink()

    rendered_movies: dict[str, Path] = {}
    for slug, _title, trial in targets:
        if "trial_dir" not in trial:
            continue
        trial_key = str(trial.get("trial_id") or trial["trial_dir"])
        mp4_path = paths.readme_assets_dir / f"{slug}.mp4"
        existing_asset_path = paths.readme_assets_dir / f"{slug}.mp4"
        if existing_manifest.get(slug) == trial_key and existing_asset_path.exists():
            updated_manifest[slug] = trial_key
            rendered_movies[trial_key] = existing_asset_path
            continue
        if trial_key in rendered_movies:
            shutil.copyfile(rendered_movies[trial_key], mp4_path)
            updated_manifest[slug] = trial_key
            continue
        copied_from_existing = False
        for existing_slug, existing_trial_key in existing_manifest.items():
            if existing_trial_key != trial_key:
                continue
            existing_mp4_path = paths.readme_assets_dir / f"{existing_slug}.mp4"
            if not existing_mp4_path.exists():
                continue
            shutil.copyfile(existing_mp4_path, mp4_path)
            rendered_movies[trial_key] = mp4_path
            updated_manifest[slug] = trial_key
            copied_from_existing = True
            break
        if copied_from_existing:
            continue
        trial_dir = paths.root / trial["trial_dir"]
        frozen_case = _load_frozen_case(trial_dir)
        if frozen_case is None:
            continue
        input_parameters, solver_parameters = frozen_case
        _render_mp4(input_parameters, solver_parameters, mp4_path, render_config)
        rendered_movies[trial_key] = mp4_path
        updated_manifest[slug] = trial_key

    _save_movie_manifest(paths, updated_manifest)
