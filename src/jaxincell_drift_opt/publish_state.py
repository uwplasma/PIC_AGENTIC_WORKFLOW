from __future__ import annotations

import shutil
from pathlib import Path

from .config import campaign_paths, load_scoring_config, load_search_config
from .optimizer_loop import refresh_outputs
from .optimizer_state import load_state, merge_states, save_state
from .utils import ensure_directory


def _trial_directory(root: Path, trial: dict) -> Path | None:
    value = trial.get("trial_dir")
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else root / path


def _copy_trial_outputs(source_root: Path, target_root: Path, trial: dict) -> str | None:
    source_dir = _trial_directory(source_root, trial)
    target_dir = _trial_directory(target_root, trial)
    if source_dir is None or target_dir is None or not source_dir.exists():
        return None
    if target_dir.exists():
        for child in source_dir.iterdir():
            destination = target_dir / child.name
            if destination.exists():
                continue
            if child.is_dir():
                shutil.copytree(child, destination)
            else:
                ensure_directory(destination.parent)
                shutil.copy2(child, destination)
        return target_dir.relative_to(target_root).as_posix()

    ensure_directory(target_dir.parent)
    shutil.copytree(source_dir, target_dir)
    return target_dir.relative_to(target_root).as_posix()


def merge_campaign_state(source_root: Path, target_root: Path, *, render_movies: bool = True) -> dict:
    source_paths = campaign_paths(source_root)
    target_paths = campaign_paths(target_root)
    search_config = load_search_config(target_paths.search_config_path)
    scoring_config = load_scoring_config(target_paths.scoring_config_path)

    source_state = load_state(source_paths.optimizer_state_path, search_config)
    target_state = load_state(target_paths.optimizer_state_path, search_config)
    merged_state, new_trial_ids, duplicate_trial_ids = merge_states(target_state, source_state, search_config)

    if not new_trial_ids:
        return {
            "changed": False,
            "new_trial_ids": [],
            "duplicate_trial_ids": duplicate_trial_ids,
            "copied_trial_dirs": [],
        }

    source_trials = {str(trial["trial_id"]): trial for trial in source_state.get("trials", [])}
    copied_trial_dirs: list[str] = []
    for trial_id in new_trial_ids:
        copied_dir = _copy_trial_outputs(source_root, target_root, source_trials[trial_id])
        if copied_dir is not None:
            copied_trial_dirs.append(copied_dir)

    save_state(target_paths.optimizer_state_path, merged_state)
    refresh_outputs(target_paths, merged_state, search_config, scoring_config, render_movies=render_movies)

    return {
        "changed": True,
        "new_trial_ids": new_trial_ids,
        "duplicate_trial_ids": duplicate_trial_ids,
        "copied_trial_dirs": copied_trial_dirs,
    }