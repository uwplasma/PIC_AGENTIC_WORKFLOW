from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .utils import ensure_directory


def plot_trial_energy_series(time_array: np.ndarray, electric_field_energy: np.ndarray, output_path: Path, title: str) -> None:
    ensure_directory(output_path.parent)
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.plot(time_array, electric_field_energy, linewidth=2)
    axis.set_title(title)
    axis.set_xlabel("time")
    axis.set_ylabel("electric field energy")
    axis.set_yscale("log")
    axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_optimization_trace(trials: list[dict], output_path: Path) -> None:
    if not trials:
        return
    ensure_directory(output_path.parent)
    best_so_far = np.maximum.accumulate([trial["optimizer_score"] for trial in trials])
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.plot(np.arange(1, len(trials) + 1), best_so_far, marker="o")
    axis.set_xlabel("trial")
    axis.set_ylabel("best optimizer score so far")
    axis.set_title("Optimization Trace")
    axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_score_vs_multiplier(trials: list[dict], output_path: Path) -> None:
    if not trials:
        return
    ensure_directory(output_path.parent)
    multipliers = [trial["drift_multiplier"] for trial in trials]
    scores = [trial["optimizer_score"] for trial in trials]
    order = np.argsort(multipliers)
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.scatter(multipliers, scores, s=50)
    axis.plot(np.asarray(multipliers)[order], np.asarray(scores)[order], alpha=0.7)
    axis.set_xlabel("drift multiplier")
    axis.set_ylabel("optimizer score")
    axis.set_title("Score vs Drift Multiplier")
    axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def load_timeseries(npz_path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(npz_path)
    return np.asarray(data["time_array"], dtype=float), np.asarray(data["electric_field_energy"], dtype=float)


def plot_best_run(best_trial: dict, root: Path, output_path: Path) -> None:
    timeseries_path = root / best_trial["timeseries_path"]
    time_array, electric_field_energy = load_timeseries(timeseries_path)
    plot_trial_energy_series(time_array, electric_field_energy, output_path, "Best Run Electric-Field Energy")


def plot_baseline_vs_best(trials: list[dict], root: Path, output_path: Path) -> None:
    baseline = next((trial for trial in trials if abs(trial["drift_multiplier"] - 1.0) < 1e-12), None)
    best = max(trials, key=lambda trial: trial["optimizer_score"], default=None)
    if baseline is None or best is None:
        return

    baseline_time, baseline_energy = load_timeseries(root / baseline["timeseries_path"])
    best_time, best_energy = load_timeseries(root / best["timeseries_path"])
    ensure_directory(output_path.parent)
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.plot(baseline_time, baseline_energy, label=f"baseline ({baseline['drift_multiplier']:.3f})")
    axis.plot(best_time, best_energy, label=f"best ({best['drift_multiplier']:.3f})")
    axis.set_xlabel("time")
    axis.set_ylabel("electric field energy")
    axis.set_yscale("log")
    axis.set_title("Baseline vs Best")
    axis.legend()
    axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
