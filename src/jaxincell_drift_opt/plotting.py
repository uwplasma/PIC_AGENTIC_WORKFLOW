from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .config import SearchConfig
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


def plot_parameter_space_trajectory(
    trials: list[dict],
    search_config: SearchConfig,
    output_path: Path,
    *,
    next_suggestion: dict | None = None,
) -> None:
    ensure_directory(output_path.parent)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), constrained_layout=True)

    successful_trials = [trial for trial in trials if not trial.get("failed")]
    if not successful_trials:
        panels = [
            (axes[0], "Drift Multiplier", "Ion Temp Ratio", False, True),
            (axes[1], "Drift Multiplier", "Ion Mass / Proton", False, True),
            (axes[2], "Ion Temp Ratio", "Ion Mass / Proton", True, True),
        ]
        for axis, x_label, y_label, x_log, y_log in panels:
            if next_suggestion is not None:
                next_x = next_suggestion["drift_multiplier"] if x_label == "Drift Multiplier" else next_suggestion["ion_temperature_ratio"] if x_label == "Ion Temp Ratio" else next_suggestion["ion_mass_over_proton_mass"]
                next_y = next_suggestion["ion_temperature_ratio"] if y_label == "Ion Temp Ratio" else next_suggestion["ion_mass_over_proton_mass"]
                axis.scatter(next_x, next_y, marker="X", s=120, color="#f59e0b", edgecolors="black", linewidths=0.6, zorder=3)
            if x_log:
                axis.set_xscale("log")
            if y_log:
                axis.set_yscale("log")
            axis.set_xlabel(x_label)
            axis.set_ylabel(y_label)
            axis.grid(alpha=0.25)
            axis.text(0.5, 0.08, "No completed trials yet", ha="center", va="center", transform=axis.transAxes, fontsize=10, color="#374151")

        axes[0].set_xlim(search_config.drift_multiplier_min, search_config.drift_multiplier_max)
        axes[0].set_ylim(search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max)
        axes[1].set_xlim(search_config.drift_multiplier_min, search_config.drift_multiplier_max)
        axes[1].set_ylim(search_config.ion_mass_min, search_config.ion_mass_max)
        axes[2].set_xlim(search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max)
        axes[2].set_ylim(search_config.ion_mass_min, search_config.ion_mass_max)

        fig.suptitle("Optimizer Path Through Parameter Space", fontsize=14)
        fig.savefig(output_path, dpi=180)
        plt.close(fig)
        return

    drift = np.asarray([trial["drift_multiplier"] for trial in successful_trials], dtype=float)
    ion_temp = np.asarray([trial["candidate_ion_temperature_ratio"] for trial in successful_trials], dtype=float)
    ion_mass = np.asarray([trial["candidate_ion_mass_over_proton_mass"] for trial in successful_trials], dtype=float)
    scores = np.asarray([trial["optimizer_score"] for trial in successful_trials], dtype=float)
    best_index = int(np.argmax(scores))

    panels = [
        (axes[0], drift, ion_temp, "Drift Multiplier", "Ion Temp Ratio", False, True),
        (axes[1], drift, ion_mass, "Drift Multiplier", "Ion Mass / Proton", False, True),
        (axes[2], ion_temp, ion_mass, "Ion Temp Ratio", "Ion Mass / Proton", True, True),
    ]

    color_map = plt.cm.viridis
    color_norm = plt.Normalize(vmin=float(np.min(scores)), vmax=float(np.max(scores)))

    for axis, x_values, y_values, x_label, y_label, x_log, y_log in panels:
        axis.plot(x_values, y_values, color="#1f2937", alpha=0.35, linewidth=1.5, zorder=1)
        scatter = axis.scatter(x_values, y_values, c=scores, cmap=color_map, norm=color_norm, s=70, edgecolors="white", linewidths=0.6, zorder=2)
        axis.scatter(x_values[best_index], y_values[best_index], marker="*", s=240, color="#dc2626", edgecolors="white", linewidths=0.8, zorder=3)

        if next_suggestion is not None:
            next_x = next_suggestion["drift_multiplier"] if x_label == "Drift Multiplier" else next_suggestion["ion_temperature_ratio"] if x_label == "Ion Temp Ratio" else next_suggestion["ion_temperature_ratio"]
            next_y = next_suggestion["ion_temperature_ratio"] if y_label == "Ion Temp Ratio" else next_suggestion["ion_mass_over_proton_mass"]
            if x_label == "Ion Mass / Proton":
                next_x = next_suggestion["ion_mass_over_proton_mass"]
            axis.scatter(next_x, next_y, marker="X", s=110, color="#f59e0b", edgecolors="black", linewidths=0.6, zorder=4)

        if x_log:
            axis.set_xscale("log")
        if y_log:
            axis.set_yscale("log")

        axis.set_xlabel(x_label)
        axis.set_ylabel(y_label)
        axis.grid(alpha=0.25)

    axes[0].set_xlim(search_config.drift_multiplier_min, search_config.drift_multiplier_max)
    axes[0].set_ylim(search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max)
    axes[1].set_xlim(search_config.drift_multiplier_min, search_config.drift_multiplier_max)
    axes[1].set_ylim(search_config.ion_mass_min, search_config.ion_mass_max)
    axes[2].set_xlim(search_config.ion_temperature_ratio_min, search_config.ion_temperature_ratio_max)
    axes[2].set_ylim(search_config.ion_mass_min, search_config.ion_mass_max)

    fig.suptitle("Optimizer Path Through Parameter Space", fontsize=14)
    cbar = fig.colorbar(scatter, ax=axes, shrink=0.86, pad=0.02)
    cbar.set_label("optimizer score")
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
