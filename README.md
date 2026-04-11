# PIC Agentic Workflow

PIC Agentic Workflow is a live optimization lab around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It continuously explores a plasma parameter space and publishes the latest leaderboard, reasoning, and artifacts back into this repository.

The goal is simple: find parameter settings that maximize late-time electrostatic energy in the two-stream instability, while keeping every trial visible, reproducible, and easy to inspect from the repository page itself.

<!-- leaderboard:start -->

## Optimization Leaderboard

This table updates directly on the live `main` branch. Higher score means stronger nonlinear electrostatic saturation.

Search ranges: drift=[0.01, 2.5], ion temperature ratio=[0.001, 100.0], ion mass over proton mass=[0.01, 4.0]

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0013 | 2026-04-11 09:06 UTC | 2.492201 | 2.578101e+01 | 3.706636e+00 | 1.246468e+00 | 0.095681 |
| 2 | trial_0022 | 2026-04-11 20:58 UTC | 2.492772 | 7.997212e-03 | 3.804760e+00 | 1.228527e+00 | 0.089385 |
| 3 | trial_0023 | 2026-04-11 21:57 UTC | 2.466572 | 1.090467e-03 | 3.871901e+00 | 1.217734e+00 | 0.085552 |
| 4 | trial_0005 | 2026-04-10 20:57 UTC | 2.477981 | 3.372570e-02 | 3.801734e+00 | 1.103520e+00 | 0.042780 |

<details>
<summary>Show ranks 5-20</summary>

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 5 | trial_0016 | 2026-04-11 11:50 UTC | 2.492894 | 9.065440e-03 | 3.815874e+00 | 1.101343e+00 | 0.041923 |
| 6 | trial_0020 | 2026-04-11 17:00 UTC | 2.494755 | 1.461639e+00 | 3.668480e+00 | 1.088557e+00 | 0.036851 |
| 7 | trial_0015 | 2026-04-11 11:00 UTC | 2.497119 | 5.109101e-02 | 3.257907e+00 | 1.072983e+00 | 0.030593 |
| 8 | trial_0021 | 2026-04-11 19:10 UTC | 2.480722 | 1.378668e+01 | 3.983710e+00 | 1.062662e+00 | 0.026395 |
| 9 | trial_0004 | 2026-04-10 20:51 UTC | 2.499108 | 4.819857e+00 | 6.003403e-01 | 1.051772e+00 | 0.021922 |
| 10 | trial_0007 | 2026-04-10 22:00 UTC | 2.488163 | 9.771405e+01 | 1.789365e+00 | 1.016955e+00 | 0.007302 |
| 11 | trial_0018 | 2026-04-11 15:04 UTC | 2.498290 | 3.920928e+01 | 3.656892e+00 | 1.006871e+00 | 0.002974 |
| 12 | trial_0010 | 2026-04-11 03:27 UTC | 2.497472 | 3.803905e-03 | 1.057138e+00 | 9.483466e-01 | -0.023033 |
| 13 | trial_0014 | 2026-04-11 10:02 UTC | 2.476352 | 6.322479e+01 | 3.931967e+00 | 8.993351e-01 | -0.046078 |
| 14 | trial_0019 | 2026-04-11 15:54 UTC | 2.497817 | 2.437541e-03 | 1.232648e+00 | 8.846031e-01 | -0.053252 |
| 15 | trial_0017 | 2026-04-11 13:36 UTC | 2.268737 | 1.549247e-03 | 3.890740e+00 | 8.753116e-01 | -0.057837 |
| 16 | trial_0011 | 2026-04-11 05:45 UTC | 2.307996 | 9.507244e+01 | 1.357109e+00 | 7.718813e-01 | -0.112449 |
| 17 | trial_0009 | 2026-04-10 23:57 UTC | 2.125038 | 7.868152e+01 | 3.969206e+00 | 7.519213e-01 | -0.123828 |
| 18 | trial_0006 | 2026-04-10 21:07 UTC | 2.495020 | 6.263080e-03 | 3.344370e+00 | 7.399855e-01 | -0.130777 |
| 19 | trial_0002 | 2026-04-10 20:04 UTC | 2.173129 | 8.068861e-03 | 3.652143e-01 | 7.317231e-01 | -0.135653 |
| 20 | trial_0008 | 2026-04-10 23:02 UTC | 2.499977 | 8.475897e+01 | 6.210031e-02 | 3.945269e-01 | -0.403923 |

</details>

### Parameter Space Map

This live figure shows where the optimizer has already looked, the order it moved through the search space, the current best point, and the next suggested point.

![Optimizer path through parameter space](reports/plots/parameter_space_trajectory.png)

### Follow The Search

- Read the agent's public reasoning: [reports/agent_reasoning.md](reports/agent_reasoning.md)
- Watch scheduled live runs: [Optimize Scheduled](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-scheduled.yml)
- Watch manual runs: [Optimize Dispatch](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-dispatch.yml)
- Watch optimization commits land on main: [main commit history](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/commits/main/)
- See how the next point is chosen: [reports/agent_reasoning.md](reports/agent_reasoning.md), [src/jaxincell_drift_opt/optimizer_loop.py](src/jaxincell_drift_opt/optimizer_loop.py), and [configs/search.yaml](configs/search.yaml)

### Exact Scored Energy Traces

These PNGs come from the exact saved trial timeseries used for scoring. Use them for quantitative electric-field-energy comparisons; the time axis is shown in $\omega_{pe}^{-1}$.

#### Best scored run

![Best scored run](reports/plots/best_run_energy.png)

#### Baseline vs best

![Baseline vs best](reports/plots/baseline_vs_best.png)

### Movies

These GIFs are rendered from the full saved trial configurations with no solver caps. They use frame skipping only, so they stay short while still covering the full simulation window.

#### Initial baseline

![Initial baseline](reports/readme_assets/initial-condition.gif)

#### Leaderboard rank 1

![Leaderboard rank 1](reports/readme_assets/leaderboard-rank-1.gif)

#### Leaderboard rank 2

![Leaderboard rank 2](reports/readme_assets/leaderboard-rank-2.gif)

<!-- leaderboard:end -->

## What You’re Looking At

- The leaderboard above is the live public state of the current optimization campaign.
- The static plots use inverse plasma-frequency units, so the time axis is shown in $\omega_{pe}^{-1}$ instead of seconds.
- This leaderboard is a fresh post-fix campaign: the resumed Bayesian optimizer now rejects duplicate suggestions and falls back to novelty-seeking candidates, so scheduled runs do not get stuck replaying one point.
- The GIFs are rendered from the full saved simulations for the initial baseline and the current top two leaderboard entries.
- The live solver baseline lives in [configs/base_input.toml](configs/base_input.toml), and the smaller CI smoke case lives in [configs/base_input_smoke.toml](configs/base_input_smoke.toml).

## How Scoring Works

The optimization target is the tail mean of the electric-field energy over the final 20% of each run:

`tail_mean_E = mean(electric_field_energy over final 20% of steps)`

The public leaderboard score is:

`optimizer_score = log10(tail_mean_E + eps)`

Higher is better.

## Run Locally

If you have a local sibling checkout of JAX-in-Cell:

```bash
python -m pip install --upgrade pip
python -m pip install -e /Users/rogerio/local/JAX-in-Cell
python -m pip install -r requirements.txt
python -m pip install -e .
```

If you want to install against the pinned GitHub dependency path instead:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Run one trial:

```bash
python scripts/run_one_trial.py --drift-multiplier 1.0 --ion-temperature-ratio 0.01 --ion-mass-over-proton-mass 1.0
```

Run a small campaign:

```bash
python scripts/run_campaign.py --num-trials 3
```

## Where Things Live

- [configs](configs): live and smoke input decks, search ranges, scoring, and movie render settings
- [state](state): current optimizer state, trials table, and best-result snapshot
- [results](results): per-trial artifacts, frozen inputs, plots, and time series
- [reports](reports): live summaries, reasoning logs, plots, and README assets
- [.github/workflows](.github/workflows): CI plus scheduled and manual optimization workflows

## Follow The Automation

- [Optimize Scheduled](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-scheduled.yml)
- [Optimize Dispatch](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-dispatch.yml)
- [main commit history](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/commits/main/)
- [reports/agent_reasoning.md](reports/agent_reasoning.md)

If you want to inspect the optimizer internals in more detail, start with [reports/agent_reasoning.md](reports/agent_reasoning.md), [src/jaxincell_drift_opt](src/jaxincell_drift_opt), and [.github/workflows](.github/workflows).
