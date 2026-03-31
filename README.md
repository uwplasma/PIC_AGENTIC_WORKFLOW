# PIC Agentic Workflow

PIC Agentic Workflow is a live optimization lab around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It continuously explores a plasma parameter space and publishes the latest leaderboard, reasoning, and artifacts back into this repository.

The current goal is simple: find parameter settings that maximize the nonlinear saturation of electrostatic energy in the two-stream instability, while keeping every trial visible and reproducible.

## Start Here

- Read the agent's running decision log: [reports/agent_reasoning.md](reports/agent_reasoning.md)
- Watch live scheduled runs: [Optimize Scheduled](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-scheduled.yml)
- Watch manual restarts and on-demand runs: [Optimize Dispatch](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-dispatch.yml)
- Watch the public README update workflow: [README Leaderboard Sync](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/readme-leaderboard-sync.yml)
- See how the next run is chosen: [reports/agent_reasoning.md](reports/agent_reasoning.md), [src/jaxincell_drift_opt/optimizer_loop.py](src/jaxincell_drift_opt/optimizer_loop.py), and [configs/search.yaml](configs/search.yaml)

## What This Repo Is Doing

- The optimizer searches over `drift_multiplier`, `ion_temperature_over_electron_temperature_x`, and `ion_mass_over_proton_mass`.
- Each run writes trial artifacts, a public summary, and a leaderboard snapshot.
- The canonical live state is stored on `agent-state`, then synced back into `main` for public viewing.
- The parameter-space figure in the leaderboard shows where the optimizer has already explored and how it moved between trials.

## Objective

The physical quantity being optimized is the tail mean of the electric-field energy over the final part of each simulation:

`tail_mean_E = mean(electric_field_energy over final 20% of steps)`

The public leaderboard uses:

`optimizer_score = log10(tail_mean_E + eps)`

Internally, the Bayesian optimizer still minimizes the sign-flipped objective because `scikit-optimize` is a minimizer:

`optimizer_objective = -optimizer_score`

Higher score means a stronger nonlinear electrostatic saturation.

## How The Next Run Is Figured Out

- Search ranges live in [configs/search.yaml](configs/search.yaml).
- The loop replays all prior observations from `state/optimizer_state.json`.
- It rebuilds the Bayesian optimizer and asks for the next suggested point in [src/jaxincell_drift_opt/optimizer_loop.py](src/jaxincell_drift_opt/optimizer_loop.py).
- The current public explanation of that next step is always refreshed in [reports/agent_reasoning.md](reports/agent_reasoning.md).

## Public Reasoning Log

[reports/agent_reasoning.md](reports/agent_reasoning.md) is the public decision log for the optimizer. It records what has been tried, what the model currently thinks is promising, and what it wants to try next.

<!-- leaderboard:start -->

## Optimization Leaderboard

This table updates from the live `agent-state` branch. Higher score means stronger nonlinear electrostatic saturation.

Search ranges: drift=[0.01, 2.5], ion temperature ratio=[0.001, 100.0], ion mass over proton mass=[0.01, 4.0]

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0184 | 2026-03-29 20:51 UTC | 2.230586 | 1.000000e-03 | 1.000000e-02 | 1.965345e+01 | 1.293439 |
| 2 | trial_0182 | 2026-03-29 19:58 UTC | 2.234738 | 1.000000e-03 | 1.000000e-02 | 1.876810e+01 | 1.273420 |
| 3 | trial_0173 | 2026-03-29 17:04 UTC | 2.232236 | 1.000000e-03 | 1.000000e-02 | 1.845095e+01 | 1.266019 |
| 4 | trial_0185 | 2026-03-29 21:00 UTC | 2.278048 | 1.000000e-03 | 1.000000e-02 | 1.824489e+01 | 1.261141 |
| 5 | trial_0179 | 2026-03-29 19:13 UTC | 2.261338 | 1.000000e-03 | 1.000000e-02 | 1.763901e+01 | 1.246474 |
| 6 | trial_0265 | 2026-03-31 19:31 UTC | 1.977430 | 1.253960e-03 | 2.635736e-02 | 1.737146e+01 | 1.239836 |
| 7 | trial_0166 | 2026-03-29 14:55 UTC | 2.207717 | 1.000000e-03 | 1.000000e-02 | 1.681553e+01 | 1.225711 |
| 8 | trial_0161 | 2026-03-29 11:54 UTC | 2.199477 | 1.000000e-03 | 1.000000e-02 | 1.665201e+01 | 1.221467 |
| 9 | trial_0175 | 2026-03-29 17:50 UTC | 2.234429 | 1.000000e-03 | 1.000000e-02 | 1.638307e+01 | 1.214395 |
| 10 | trial_0162 | 2026-03-29 12:03 UTC | 2.162362 | 1.000000e-03 | 1.000000e-02 | 1.617447e+01 | 1.208830 |
| 11 | trial_0174 | 2026-03-29 17:12 UTC | 2.244200 | 1.000000e-03 | 1.000000e-02 | 1.605103e+01 | 1.205503 |
| 12 | trial_0168 | 2026-03-29 15:13 UTC | 2.207899 | 1.000000e-03 | 1.000000e-02 | 1.597734e+01 | 1.203505 |
| 13 | trial_0176 | 2026-03-29 17:59 UTC | 2.230971 | 1.000000e-03 | 1.000000e-02 | 1.543867e+01 | 1.188610 |
| 14 | trial_0181 | 2026-03-29 19:49 UTC | 2.247710 | 8.259731e-03 | 1.000000e-02 | 1.496932e+01 | 1.175202 |
| 15 | trial_0163 | 2026-03-29 13:30 UTC | 2.181396 | 1.000000e-03 | 1.000000e-02 | 1.483122e+01 | 1.171177 |
| 16 | trial_0164 | 2026-03-29 13:39 UTC | 2.181046 | 1.000000e-03 | 1.000000e-02 | 1.479427e+01 | 1.170094 |
| 17 | trial_0266 | 2026-03-31 19:40 UTC | 1.978410 | 1.000000e-03 | 2.061141e-02 | 1.468263e+01 | 1.166804 |
| 18 | trial_0180 | 2026-03-29 19:22 UTC | 2.254021 | 1.000000e-03 | 1.000000e-02 | 1.419248e+01 | 1.152058 |
| 19 | trial_0186 | 2026-03-29 21:09 UTC | 2.272388 | 1.000000e-03 | 1.000000e-02 | 1.409226e+01 | 1.148981 |
| 20 | trial_0125 | 2026-03-28 19:12 UTC | 1.708263 | 1.922651e-02 | 8.328336e-02 | 1.390057e+01 | 1.143033 |

### Parameter Space Map

This live figure shows where the optimizer has already looked, the order it moved through the search space, the current best point, and the next suggested point.

![Optimizer path through parameter space](reports/plots/parameter_space_trajectory.png)

### Follow The Search

- Read the agent's public reasoning: [reports/agent_reasoning.md](reports/agent_reasoning.md)
- Watch scheduled live runs: [Optimize Scheduled](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-scheduled.yml)
- Watch manual or restart runs: [Optimize Dispatch](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/optimize-dispatch.yml)
- Watch README updates land: [README Leaderboard Sync](https://github.com/uwplasma/PIC_AGENTIC_WORKFLOW/actions/workflows/readme-leaderboard-sync.yml)
- See how the next point is chosen: [reports/agent_reasoning.md](reports/agent_reasoning.md), [src/jaxincell_drift_opt/optimizer_loop.py](src/jaxincell_drift_opt/optimizer_loop.py), and [configs/search.yaml](configs/search.yaml)

### Movies

The GIFs below reuse the multi-panel JAX-in-Cell movie layout so you can inspect phase space, field evolution, and the energy subplot directly in the public repository.

#### Initial condition

![Initial condition](reports/readme_assets/initial-condition.gif)

#### Leaderboard rank 1

![Leaderboard rank 1](reports/readme_assets/leaderboard-rank-1.gif)

#### Leaderboard rank 2

![Leaderboard rank 2](reports/readme_assets/leaderboard-rank-2.gif)

<!-- leaderboard:end -->

## Repo Map

- `configs/`: base input, search settings, scoring settings
- `src/jaxincell_drift_opt/`: adapter, scoring, optimizer, reporting, plotting
- `scripts/`: local and workflow entry points
- `tests/`: lightweight unit tests and mocked optimizer smoke tests
- `.github/workflows/`: CI, scheduled optimization, manual dispatch, issue-command gate, maintenance
- `agent/`: narrow prompts and allowlists for safe automation

## Local Setup

### Option 1: use the local sibling JAX-in-Cell checkout

```bash
python -m pip install --upgrade pip
python -m pip install -e /Users/rogerio/local/JAX-in-Cell
python -m pip install -r requirements.txt
python -m pip install -e .
```

### Option 2: install JAX-in-Cell from GitHub

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run One Trial Locally

```bash
python scripts/run_one_trial.py --drift-multiplier 1.0 --ion-temperature-ratio 0.01 --ion-mass-over-proton-mass 1.0
```

This writes:

- `results/trial_XXXX/metrics.json`
- `results/trial_XXXX/frozen_input.json`
- `results/trial_XXXX/timeseries.npz`
- `results/trial_XXXX/electric_field_energy.png`

## Run a Small Campaign Locally

```bash
python scripts/run_campaign.py --num-trials 3
```

This updates:

- `state/optimizer_state.json`
- `state/trials.csv`
- `state/best_result.json`
- `reports/latest_summary.md`
- `reports/plots/*.png`

## State Persistence

The canonical persistence target is the `agent-state` branch. Optimization workflows:

1. run a bounded number of new trials,
2. update `state/`, `reports/`, and `results/`,
3. upload those directories as artifacts,
4. optionally copy them onto the `agent-state` branch.

The optimizer state is stored as JSON observations rather than a Python pickle. On resume, the repo reconstructs the `scikit-optimize` `Optimizer` and replays prior `tell(...)` calls.

## Workflows

- `ci.yml`: install, test, and run one smoke trial on GitHub-hosted runners
- `optimize-dispatch.yml`: manual run with trial count, seed, range override, and optional state-branch push
- `optimize-scheduled.yml`: hourly bounded optimization with concurrency control on the self-hosted runner
- `optimize-issue-command.yml`: restricted issue-comment commands, gated by actor allowlist
- `copilot-maintenance.yml`: weekly/manual maintenance checks, with a neutral placeholder for GitHub-native Copilot PR automation
- `copilot-automerge.yml`: trusted auto-approval and auto-merge for Copilot-authored PRs when a maintainer token is configured
- `readme-leaderboard-sync.yml`: GitHub-hosted sync that lifts the generated leaderboard README from `agent-state` back onto `main`
- `relativistic-agent-loop.yml`: hourly GitHub-hosted watchdog that ensures exactly one open Copilot-assigned relativistic milestone issue exists for the PR-first research loop

## Relativistic Research Agent

This repository can also host PR-first research-agent work aimed at a future relativistic upgrade path for JAX-in-Cell.

- The dedicated agent brief lives in [agent/prompts/relativistic_research.md](agent/prompts/relativistic_research.md).
- A matching issue template lives in [.github/ISSUE_TEMPLATE/relativistic-research-agent.md](.github/ISSUE_TEMPLATE/relativistic-research-agent.md).
- The loop policy lives in [agent/policies/relativistic_loop.toml](agent/policies/relativistic_loop.toml).
- The watchdog automation lives in [.github/workflows/relativistic-agent-loop.yml](.github/workflows/relativistic-agent-loop.yml).
- The intended use is iterative: each agent run should complete one bounded scientific milestone, open one reviewable PR, and recommend the next milestone.

This is the safe way to pursue a momentum-space relativistic design in this repository: benchmark first, define validation criteria, prototype interfaces and diagnostics here, and only then carry the validated upstream changes into JAX-in-Cell itself.

The loop is now partially self-maintaining inside GitHub: when there is no open relativistic milestone issue, the watchdog workflow creates one and assigns it to the configured maintainers, and it attempts to attach `Copilot` as well. In testing, the standard GitHub Issues API created the issue successfully but did not attach the `Copilot` assignee even when called with a maintainer token, which indicates a current platform limitation rather than a repository bug. The repository can keep the queue populated automatically, but it cannot force the closed-source Copilot service to run continuously or attach itself through the public API if GitHub does not expose that capability.

Trusted Copilot PRs can, however, be auto-approved and auto-merged after CI if you configure a repository secret named `AUTOMERGE_GITHUB_TOKEN` containing a maintainer token with repository access. The workflow policy for that path lives in [agent/policies/automerge.toml](agent/policies/automerge.toml).

The same maintainer token is also used by the README sync workflow to auto-merge the public leaderboard updates that are generated from the hourly optimization state.

## Trusted Self-Hosted Optimization

The trusted optimization lanes now target a maintainer-controlled self-hosted runner with labels `self-hosted`, `macOS`, `ARM64`, `uwplasma`, and `macmini`.

- `optimize-dispatch.yml` runs on the self-hosted runner
- `optimize-scheduled.yml` runs on the self-hosted runner
- `ci.yml` stays on GitHub-hosted runners
- `optimize-issue-command.yml` stays on GitHub-hosted runners
- `copilot-maintenance.yml` stays on GitHub-hosted runners

This split keeps public PR validation and public comment handling away from self-hosted infrastructure while still allowing trusted optimization jobs to use the local machine. Because this repository is public, the runner group access policy in the organization must explicitly allow this repository to use the selected self-hosted runner group.

## What You Will See In GitHub

The unattended hourly experiment loop is a scheduled GitHub Actions workflow, not a GitHub Copilot coding agent task.

1. The workflow runs appear in the `Actions` tab under `Optimize Scheduled`.
2. Each run will show the job landing on the self-hosted labels when the runner is online.
3. The runner itself is managed under the organization Actions runner settings, not inside a Copilot coding-agent session view.

If by "agent tab" you mean a GitHub Copilot coding-agent surface, that is not the right GitHub mechanism for an hourly unattended scientific optimization loop. The correct GitHub-native mechanism is a scheduled workflow running on your self-hosted runner.

## Current Limitations

- The current global campaign still operates within the non-relativistic JAX-in-Cell wrapper interface and does not yet change the upstream particle pusher.
- This repository does not itself contain the JAX-in-Cell particle pusher or particle state internals, so a true momentum-space relativistic implementation requires a later upstream change in JAX-in-Cell.
- The repo assumes `diagnostics(output)` continues to expose `electric_field_energy`; if that changes, the fallback recomputes from `electric_field` and `dx`.
- The issue-command workflow ships fail-closed with an empty actor allowlist until maintainers populate [agent/policies/actors.yaml](agent/policies/actors.yaml).
- The maintenance workflow includes a safe placeholder hook for GitHub-native Copilot PR preparation, but the exact org-approved integration is still repository-specific.

## Manual GitHub Steps If Permissions Differ

If local `gh` credentials or org permissions prevent automation, the remaining manual steps are:

1. Create the remote repository from this local folder.
2. Push `main` and create `agent-state`.
3. Populate the actor allowlist.
4. Add any organization-approved GitHub Copilot automation wiring if you later want PR-first maintenance automation.
5. Protect `main` and restrict direct pushes.
