# PIC Agentic Workflow

PIC Agentic Workflow is a thin orchestration layer around [uwplasma/JAX-in-Cell](https://github.com/uwplasma/JAX-in-Cell). It mutates the electron drift speed in a base JAX-in-Cell input, runs a bounded simulation, scores the final nonlinear saturation of electric-field energy, and uses a persistent Bayesian optimization loop to choose the next trial.

The repo exists as a reviewable pilot for safe agentic scientific workflows. Public CI stays on GitHub-hosted runners, periodic optimization writes only to a dedicated `agent-state` branch, and code-editing automation is PR-first.

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
- `optimize-scheduled.yml`: scheduled bounded optimization with concurrency control
- `optimize-issue-command.yml`: restricted issue-comment commands, gated by actor allowlist
- `copilot-maintenance.yml`: weekly/manual maintenance checks, with a neutral placeholder for GitHub-native Copilot PR automation

## Promoting to a Trusted Self-Hosted Lane

The optimization workflows currently target GitHub-hosted runners for small cases. To promote them later:

1. provision a trusted runner group for maintainer-only triggers,
2. change the workflow `runs-on` label,
3. keep `pull_request` validation on GitHub-hosted runners,
4. keep state updates isolated to `agent-state`.

No public PRs or arbitrary comments should ever land on self-hosted infrastructure.

## Current Limitations

- The initial campaign is one-dimensional and only tunes `electron_drift_speed_x`.
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
