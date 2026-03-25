# PIC Agentic Workflow

PIC Agentic Workflow is a thin orchestration layer around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It mutates the electron drift speed in a base JAX-in-Cell input, runs a bounded simulation, scores the final nonlinear saturation of electric-field energy, and uses a persistent Bayesian optimization loop to choose the next trial.

The repo exists as a reviewable pilot for safe agentic scientific workflows. Public CI stays on GitHub-hosted runners, trusted manual and scheduled optimization run on a maintainer-controlled self-hosted macOS runner, periodic optimization writes only to a dedicated `agent-state` branch, and code-editing automation is PR-first.

## Relationship to JAX-in-Cell

This repo does not fork or patch JAX-in-Cell internals. It imports the public package and uses the current supported flow:

1. `load_parameters(...)` reads a TOML input.
2. `simulation(...)` runs the case.
3. `diagnostics(output)` computes `electric_field_energy` and related metrics.

The adapter validates the real drift parameter name against the installed package before each run. With the current code path, the optimized parameter is `electron_drift_speed_x`.

## Objective and Score

The optimization variable is `drift_multiplier`, with candidate drift defined as:

`candidate_drift = base_drift * drift_multiplier`

The default search range is configured in [configs/search.yaml](/Users/rogerio/local/PIC_agentic_workflow/configs/search.yaml).

The physical target is the final nonlinear saturation of electric-field energy. The default score is:

`tail_mean_E = mean(electric_field_energy over final 20% of steps)`

`optimizer_score = log10(tail_mean_E + eps)`

Since `scikit-optimize` minimizes by default, the stored optimizer objective is `-optimizer_score`.

Secondary metrics include:

- `tail_mean_E`
- `tail_max_E`
- `final_E`
- `time_of_peak_E`
- `wall_time_seconds`
- `seed`
- `failed`

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
python scripts/run_one_trial.py --drift-multiplier 1.0
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

## Relativistic Research Agent

This repository can also host PR-first research-agent work aimed at a future relativistic upgrade path for JAX-in-Cell.

- The dedicated agent brief lives in [agent/prompts/relativistic_research.md](/Users/rogerio/local/PIC_agentic_workflow/agent/prompts/relativistic_research.md).
- A matching issue template lives in [.github/ISSUE_TEMPLATE/relativistic-research-agent.md](/Users/rogerio/local/PIC_agentic_workflow/.github/ISSUE_TEMPLATE/relativistic-research-agent.md).
- The intended use is iterative: each agent run should complete one bounded scientific milestone, open one reviewable PR, and recommend the next milestone.

This is the safe way to pursue a momentum-space relativistic design in this repository: benchmark first, define validation criteria, prototype interfaces and diagnostics here, and only then carry the validated upstream changes into JAX-in-Cell itself.

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

- The initial campaign is one-dimensional and only tunes `electron_drift_speed_x`.
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
