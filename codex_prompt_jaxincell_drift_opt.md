# Codex prompt for the JAX-in-Cell drift-optimization showcase repo

You have commit and push rights to the `uwplasma` GitHub organization. Your job is to create a new public demonstration repository that showcases safe agentic scientific workflows around `uwplasma/JAX-in-Cell`.

## Mission

Create a new repo called `uwplasma/jaxincell-drift-opt-agent` unless that name is unavailable, in which case use the closest clear alternative. This repo should be a thin orchestration layer around JAX-in-Cell, not a fork of it.

The scientific task is:

- import/install JAX-in-Cell,
- start from a base JAX-in-Cell input,
- vary the **electron drift velocity** according to a simple configurable rule,
- run JAX-in-Cell,
- compute a scalar score equal to the **final nonlinear saturation of electric-field energy**,
- use a **global Bayesian optimization loop** to choose the next point,
- persist optimizer state across GitHub workflow runs,
- produce plots, logs, CSV/JSON summaries, and markdown reports,
- set up GitHub workflows so the repo runs periodically and can also be triggered manually,
- optionally set up a narrow Codex maintenance workflow that opens PRs for low-risk repo fixes.

## Important operating style

Do not over-engineer this. Keep it simple, robust, and easy to review.

Do not assume JAX-in-Cell internals from memory. Inspect the **current actual repo** and adapt to what is there now.

Do not assume that parameter names shown in old examples or docs are perfectly consistent. Check the real code path and real loaded parameter names before finalizing the adapter.

Do not modify the internals of `uwplasma/JAX-in-Cell` in this task unless absolutely necessary. Build a wrapper/orchestrator repo around it.

Do not create a dangerous autonomous workflow. All code-editing workflows must be PR-first.

## First steps

1. Create the repository in the `uwplasma` org with `gh`.
2. Clone it locally.
3. Inspect `uwplasma/JAX-in-Cell` carefully:
   - README
   - examples
   - input files
   - current install/run path
   - any existing optimization examples
   - tests
4. Decide the cleanest way to run JAX-in-Cell from this new repo.
5. Then create the new repo structure and implementation.

## GitHub actions and runner philosophy

Implement the repo so that it works immediately on GitHub-hosted runners for small smoke/testing workflows.

Also structure the scheduled optimization workflow so it can later be promoted to a trusted self-hosted lane with only a small runner-label change.

Do not route public PRs to self-hosted infrastructure.

## Scientific design requirements

### Optimization variable

Use the electron drift speed as the optimized variable.

Preferred default parameterization:

- base input provides `base_drift`
- search variable is `drift_multiplier`
- candidate drift = `base_drift * drift_multiplier`

Default search range:

- `drift_multiplier in [0.25, 2.5]`

Make this configurable in a small YAML or TOML config file.

### Score definition

Primary physical target:

- maximize the final nonlinear saturation of electric-field energy

Default implementation:

- compute `tail_mean_E` = mean of the electric-field energy over the final 20 percent of time steps
- if `electric_field_energy` already exists in the output, use it
- otherwise compute it from the electric field data in a physically consistent way

For optimization stability, optimize a transformed score such as:

- maximize `log10(tail_mean_E + eps)`

Also record secondary metrics:

- raw `tail_mean_E`
- `tail_max_E`
- `final_E`
- time of peak E-energy
- wall time
- seed
- whether the run failed

### Bayesian optimization

Use a lightweight global Bayesian optimization package.

Preferred default:

- `scikit-optimize`
- use an `Optimizer` with ask/tell so state can persist across scheduled runs

Keep it one-dimensional for the first version.

### Persistent state

The campaign state must survive across GitHub workflow runs.

Canonical design:

- keep optimizer state and campaign history in a dedicated branch such as `agent-state`
- also upload them as workflow artifacts

Persist at least:

- optimizer state
- all tried points
- scores
- best-so-far result
- markdown summary

## Repository structure to create

Create something close to this:

```text
README.md
pyproject.toml
requirements.txt
configs/
  base_input.toml
  search.yaml
  scoring.yaml
src/jaxincell_drift_opt/
  __init__.py
  config.py
  jaxincell_adapter.py
  mutate_input.py
  run_trial.py
  scoring.py
  optimizer_state.py
  optimizer_loop.py
  reporting.py
  plotting.py
  utils.py
scripts/
  run_campaign.py
  run_one_trial.py
  suggest_next.py
  summarize_results.py
  bootstrap_state.py
tests/
.github/workflows/
  ci.yml
  optimize-scheduled.yml
  optimize-dispatch.yml
  optimize-issue-command.yml
  codex-maintenance.yml
agent/prompts/maintenance.md
agent/policies/repos.yaml
agent/policies/actors.yaml
```

You may simplify a little if needed, but do not collapse everything into one file.

## Implementation details

### `jaxincell_adapter.py`

Build one adapter layer that:

- loads the base JAX-in-Cell input
- applies the drift mutation rule
- validates the real parameter names present in the current code path
- runs JAX-in-Cell through the cleanest supported interface
- returns a normalized results dictionary for scoring and reporting

### `run_trial.py`

One trial should:

- create a frozen copy of the exact input used
- run JAX-in-Cell
- compute the score
- save logs and plots
- return a machine-readable metrics dict

### `scoring.py`

Implement:

- tail mean E-energy score
- log-transformed optimizer objective
- failure penalty
- score version string

### `optimizer_loop.py`

Implement:

- initialize state if needed
- ask for N new points
- execute them one by one
- tell results back to the optimizer
- update leaderboard and best result
- write summary markdown

### Plotting

Create at least:

- optimization trace plot
- scatter/line plot of score vs drift multiplier
- best-run electric-field-energy vs time plot
- baseline-vs-best comparison plot if possible

### Reports

Write:

- `reports/latest_summary.md`
- `state/trials.csv`
- `state/best_result.json`
- `state/optimizer_state.json`

### Tests

Add lightweight tests for:

- drift mutation rule
- score calculation
- state serialization/deserialization
- mocked optimizer flow or a very small smoke test

Do not make CI depend on long expensive runs.

## GitHub workflows to create

### `ci.yml`

Use GitHub-hosted runners.

Trigger on push and pull_request.

Run:

- install
- tests
- very small smoke check

### `optimize-dispatch.yml`

Trigger on workflow_dispatch.

Inputs:

- number of trials
- optional seed
- optional drift range override
- optional flag to push state branch

This workflow is for easy manual testing.

### `optimize-scheduled.yml`

Trigger on schedule and workflow_dispatch.

Run a small number of new optimization trials and update the state branch.

Add concurrency so overlapping runs do not step on each other.

### `optimize-issue-command.yml`

Trigger on issue_comment.

Accept only a tiny command vocabulary, for example:

- `/optimize 3`
- `/summarize`

Validate actor against an allowlist in-repo before doing anything.

### `codex-maintenance.yml`

Create a narrow maintenance workflow that can:

- run weekly or manually
- check docs/examples/tests for obvious drift
- optionally use Codex to prepare a draft PR

This workflow must be PR-first.

If the repo secret needed for Codex is absent, the workflow should exit safely with a clear message rather than failing dangerously.

## Security and permissions

- Keep `main` protected.
- Never auto-merge code changes.
- Use minimal GitHub token permissions.
- Public PR validation must stay on GitHub-hosted runners.
- Keep code-editing workflows distinct from experiment workflows.
- State updates should go to `agent-state`, not `main`.

## `gh` CLI tasks

Using `gh`, do as much of the following as your permissions allow:

1. create the repo under `uwplasma`
2. push the initial implementation
3. enable and commit all workflows
4. create the `agent-state` branch if useful
5. set the repo description
6. optionally create labels for experiment tracking
7. if you have the required permission and an available secret value in environment, set repo secrets/variables needed for the maintenance workflow
8. trigger at least one manual dispatch run to validate the setup

If a permissions boundary prevents one of these, do not stop. Complete the rest and record the exact remaining manual steps in the README.

## README requirements

The README should explain:

- what the repo does
- why it exists
- how it relates to JAX-in-Cell
- how the score is defined
- how to run one trial locally
- how to run a campaign locally
- how state persistence works
- how scheduled workflows work
- what the current limitations are
- how to promote the workflow from GitHub-hosted to a trusted self-hosted lane later

## Quality bar

The result should feel like a real, reviewable pilot repo for the group, not a toy script.

Favor clarity, reproducibility, and maintainability over fancy abstractions.

## Final deliverables

By the end, the repo should contain:

- working code
- working workflows
- tests
- documentation
- at least one example successful run or at minimum one validated smoke run
- a clean initial commit history

When done, write a concise summary in the repo README and, if possible, trigger the first workflow run.
