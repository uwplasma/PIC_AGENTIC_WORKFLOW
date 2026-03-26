# PIC Agentic Workflow

PIC Agentic Workflow is a thin orchestration layer around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It now runs a persistent global Bayesian search loop over the two-stream-instability setup, exploring drift multiplier, ion-to-electron temperature ratio, and ion mass proxy to drive the final nonlinear electrostatic energy as high as possible.

The repo exists as a reviewable pilot for safe agentic scientific workflows. Public CI stays on GitHub-hosted runners, trusted manual and scheduled optimization run on a maintainer-controlled self-hosted macOS runner, periodic optimization writes only to a dedicated `agent-state` branch, and code-editing automation is PR-first.

## Public Reasoning Log

The first file to inspect for the current competition state is [reports/agent_reasoning.md](/Users/rogerio/local/PIC_agentic_workflow/reports/agent_reasoning.md).

That report is the public decision log for the optimization loop: active solver parameters, the per-trial public analysis record, what the optimizer currently believes, and the planned next experiment. It is intentionally a structured public rationale rather than a hidden private chain-of-thought dump.

## Relationship to JAX-in-Cell

This repo does not fork or patch JAX-in-Cell internals. It imports the public package and uses the current supported flow:

1. `load_parameters(...)` reads a TOML input.
2. `simulation(...)` runs the case.
3. `diagnostics(output)` computes `electric_field_energy` and related metrics.

The adapter validates the real drift parameter name against the installed package before each run. With the current code path, the global search space includes `electron_drift_speed_x`, `ion_temperature_over_electron_temperature_x`, and `ion_mass_over_proton_mass`.

## Objective and Score

The default search variables are:

- `drift_multiplier`, applied as `candidate_drift = base_drift * drift_multiplier`
- `ion_temperature_over_electron_temperature_x`
- `ion_mass_over_proton_mass`

The default search range is configured in [configs/search.yaml](/Users/rogerio/local/PIC_agentic_workflow/configs/search.yaml).

The physical target is the final nonlinear saturation of electric-field energy. The search maximizes that physical target while minimizing a sign-flipped optimizer objective:

`tail_mean_E = mean(electric_field_energy over final 20% of steps)`

`optimizer_score = log10(tail_mean_E + eps)`

`optimizer_objective = -optimizer_score`

The optimizer still minimizes `optimizer_objective` because `scikit-optimize` is a minimizer, but that is now equivalent to maximizing `tail_mean_E`. Public summaries and leaderboards use `optimizer_score`, so higher score means stronger nonlinear electrostatic saturation.

Secondary metrics include:

- `tail_mean_E`
- `tail_max_E`
- `final_E`
- `time_of_peak_E`
- `wall_time_seconds`
- `seed`
- `failed`

<!-- leaderboard:start -->

## Optimization Leaderboard

Hourly self-hosted search maximizes the tail-mean electrostatic energy for the two-stream instability over drift multiplier, ion-to-electron temperature ratio, and ion mass proxy.

Search ranges: drift=[0.25, 2.5], ion temperature ratio=[0.001, 1.0], ion mass over proton mass=[0.25, 4.0]

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0014 | 1.556915 | 1.000000e+00 | 2.500000e-01 | 1.116652e+01 | 1.047918 |
| 2 | trial_0030 | 1.623804 | 1.468625e-03 | 2.663768e-01 | 1.012072e+01 | 1.005211 |
| 3 | trial_0029 | 1.550189 | 1.215519e-03 | 2.583534e-01 | 9.400365e+00 | 0.973145 |
| 4 | trial_0020 | 1.593855 | 1.000000e-03 | 2.500000e-01 | 9.385850e+00 | 0.972474 |
| 5 | trial_0028 | 1.568203 | 2.439017e-01 | 2.568994e-01 | 9.308397e+00 | 0.968875 |
| 6 | trial_0021 | 1.592669 | 1.000000e-03 | 2.500000e-01 | 9.205208e+00 | 0.964034 |
| 7 | trial_0004 | 1.610619 | 2.546783e-01 | 2.500000e-01 | 8.879253e+00 | 0.948376 |
| 8 | trial_0026 | 1.605683 | 1.000000e-03 | 2.500000e-01 | 8.758897e+00 | 0.942449 |
| 9 | trial_0012 | 1.534184 | 1.000000e+00 | 2.500000e-01 | 8.733743e+00 | 0.941200 |
| 10 | trial_0013 | 1.548860 | 1.000000e-03 | 2.500000e-01 | 8.655493e+00 | 0.937292 |

### Movies

The GIFs below reuse the multi-panel JAX-in-Cell movie layout so you can inspect phase space, field evolution, and the energy subplot directly in the public repository.

#### Initial condition

![Initial condition](reports/readme_assets/initial-condition.gif)

#### Leaderboard rank 1

![Leaderboard rank 1](reports/readme_assets/leaderboard-rank-1.gif)

#### Leaderboard rank 2

![Leaderboard rank 2](reports/readme_assets/leaderboard-rank-2.gif)

See [reports/agent_reasoning.md](reports/agent_reasoning.md) for the public optimizer reasoning and next suggested experiment.

<!-- leaderboard:end -->

## Repository Layout

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

- The dedicated agent brief lives in [agent/prompts/relativistic_research.md](/Users/rogerio/local/PIC_agentic_workflow/agent/prompts/relativistic_research.md).
- A matching issue template lives in [.github/ISSUE_TEMPLATE/relativistic-research-agent.md](/Users/rogerio/local/PIC_agentic_workflow/.github/ISSUE_TEMPLATE/relativistic-research-agent.md).
- The loop policy lives in [agent/policies/relativistic_loop.toml](/Users/rogerio/local/PIC_agentic_workflow/agent/policies/relativistic_loop.toml).
- The watchdog automation lives in [.github/workflows/relativistic-agent-loop.yml](/Users/rogerio/local/PIC_agentic_workflow/.github/workflows/relativistic-agent-loop.yml).
- The intended use is iterative: each agent run should complete one bounded scientific milestone, open one reviewable PR, and recommend the next milestone.

This is the safe way to pursue a momentum-space relativistic design in this repository: benchmark first, define validation criteria, prototype interfaces and diagnostics here, and only then carry the validated upstream changes into JAX-in-Cell itself.

The loop is now partially self-maintaining inside GitHub: when there is no open relativistic milestone issue, the watchdog workflow creates one and assigns it to the configured maintainers, and it attempts to attach `Copilot` as well. In testing, the standard GitHub Issues API created the issue successfully but did not attach the `Copilot` assignee even when called with a maintainer token, which indicates a current platform limitation rather than a repository bug. The repository can keep the queue populated automatically, but it cannot force the closed-source Copilot service to run continuously or attach itself through the public API if GitHub does not expose that capability.

Trusted Copilot PRs can, however, be auto-approved and auto-merged after CI if you configure a repository secret named `AUTOMERGE_GITHUB_TOKEN` containing a maintainer token with repository access. The workflow policy for that path lives in [agent/policies/automerge.toml](/Users/rogerio/local/PIC_agentic_workflow/agent/policies/automerge.toml).

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
- The issue-command workflow ships fail-closed with an empty actor allowlist until maintainers populate [agent/policies/actors.yaml](/Users/rogerio/local/PIC_agentic_workflow/agent/policies/actors.yaml).
- The maintenance workflow includes a safe placeholder hook for GitHub-native Copilot PR preparation, but the exact org-approved integration is still repository-specific.

## Manual GitHub Steps If Permissions Differ

If local `gh` credentials or org permissions prevent automation, the remaining manual steps are:

1. Create the remote repository from this local folder.
2. Push `main` and create `agent-state`.
3. Populate the actor allowlist.
4. Add any organization-approved GitHub Copilot automation wiring if you later want PR-first maintenance automation.
5. Protect `main` and restrict direct pushes.
