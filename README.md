# PIC Agentic Workflow

PIC Agentic Workflow is a live optimization lab around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It continuously explores a plasma parameter space and publishes the latest leaderboard, reasoning, and artifacts back into this repository.

The goal is simple: find parameter settings that maximize late-time electrostatic energy in the two-stream instability, while keeping every trial visible, reproducible, and easy to inspect from the repository page itself.

<!-- leaderboard:start -->

## Optimization Leaderboard

This table updates directly on the live `main` branch. Higher score means stronger nonlinear electrostatic saturation.

Search ranges: drift=[0.01, 2.5], ion temperature ratio=[0.001, 100.0], ion mass over proton mass=[0.01, 4.0]

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0033 | 2026-04-14 06:16 UTC | 2.481669 | 7.803510e-03 | 3.951147e+00 | 1.297681e+00 | 0.113168 |
| 2 | trial_0059 | 2026-04-16 06:18 UTC | 2.486595 | 1.802741e-03 | 3.599527e+00 | 1.255918e+00 | 0.098961 |
| 3 | trial_0027 | 2026-04-13 19:45 UTC | 2.494558 | 3.152023e-03 | 1.072994e+00 | 1.248429e+00 | 0.096364 |
| 4 | trial_0013 | 2026-04-11 09:06 UTC | 2.492201 | 2.578101e+01 | 3.706636e+00 | 1.246468e+00 | 0.095681 |

<details>
<summary>Show ranks 5-20</summary>

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 5 | trial_0022 | 2026-04-11 20:58 UTC | 2.492772 | 7.997212e-03 | 3.804760e+00 | 1.228527e+00 | 0.089385 |
| 6 | trial_0024 | 2026-04-13 14:22 UTC | 2.495804 | 1.869924e+01 | 3.645885e+00 | 1.220066e+00 | 0.086383 |
| 7 | trial_0023 | 2026-04-11 21:57 UTC | 2.466572 | 1.090467e-03 | 3.871901e+00 | 1.217734e+00 | 0.085552 |
| 8 | trial_0036 | 2026-04-14 11:35 UTC | 2.483024 | 1.274137e-03 | 3.761200e+00 | 1.200742e+00 | 0.079450 |
| 9 | trial_0044 | 2026-04-15 00:06 UTC | 2.498922 | 2.349722e-03 | 8.883015e-01 | 1.194413e+00 | 0.077155 |
| 10 | trial_0056 | 2026-04-15 23:08 UTC | 2.492607 | 4.559871e+01 | 3.503618e+00 | 1.178031e+00 | 0.071157 |
| 11 | trial_0060 | 2026-04-16 08:11 UTC | 2.495055 | 1.535075e-03 | 3.107468e+00 | 1.150832e+00 | 0.061012 |
| 12 | trial_0040 | 2026-04-14 19:47 UTC | 2.498908 | 1.805235e+00 | 3.804995e+00 | 1.150278e+00 | 0.060803 |
| 13 | trial_0046 | 2026-04-15 06:16 UTC | 2.490287 | 2.223682e-03 | 6.075856e-01 | 1.134511e+00 | 0.054809 |
| 14 | trial_0058 | 2026-04-16 03:53 UTC | 2.482595 | 2.813879e-03 | 3.933675e+00 | 1.126234e+00 | 0.051629 |
| 15 | trial_0057 | 2026-04-16 00:05 UTC | 2.496196 | 1.624134e-03 | 3.348923e+00 | 1.122950e+00 | 0.050361 |
| 16 | trial_0005 | 2026-04-10 20:57 UTC | 2.477981 | 3.372570e-02 | 3.801734e+00 | 1.103520e+00 | 0.042780 |
| 17 | trial_0064 | 2026-04-16 16:03 UTC | 2.359187 | 1.411468e-03 | 3.784988e+00 | 1.103076e+00 | 0.042605 |
| 18 | trial_0016 | 2026-04-11 11:50 UTC | 2.492894 | 9.065440e-03 | 3.815874e+00 | 1.101343e+00 | 0.041923 |
| 19 | trial_0061 | 2026-04-16 09:55 UTC | 2.490123 | 2.470623e-03 | 3.888515e+00 | 1.095978e+00 | 0.039802 |
| 20 | trial_0020 | 2026-04-11 17:00 UTC | 2.494755 | 1.461639e+00 | 3.668480e+00 | 1.088557e+00 | 0.036851 |

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
