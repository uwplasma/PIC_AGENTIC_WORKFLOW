# UWPlasma agentic runners plan + JAX-in-Cell showcase repo

Prepared for internal group discussion and for direct handoff to Codex.

Date: March 24, 2026

---

## 1. Purpose of this document

This document turns the presentation deck into a detailed written plan that can be shared with the group and also handed to Codex as an execution brief. It has two goals:

1. Define a safe, reviewable, and realistic architecture for AI agents operating in the `uwplasma` GitHub organization.
2. Specify one concrete first demonstration repo that showcases the architecture on a bounded scientific task using **JAX-in-Cell**: optimize the electron drift speed input to maximize the final nonlinear saturation of the electric-field energy.

The intent is not to create an always-on autonomous bot with broad org-wide power. The intent is to create **narrow, event-driven, review-first workflows** that can repair code, run bounded experiments, and produce artifacts that humans can inspect.

---

## 2. Executive recommendation

### Bottom line

Yes, `uwplasma` should adopt AI-agent workflows, but only in a controlled, layered way.

The right design is:

- **event-driven, not always-on**
- **PR-first for code changes**
- **trusted self-hosted lanes only for trusted triggers**
- **public CI stays GitHub-hosted**
- **long science runs are detached to a scheduler**
- **every outward result is human-readable and reviewable**

### Why this fits uwplasma

`uwplasma` is a particularly good fit because many repos already have:

- Python and JAX code paths
- CLI or script-driven entry points
- numerical outputs that can be compared to baselines
- examples that finish in minutes
- pull-request review habits
- scientific runs that naturally produce plots, tables, and logs

This makes the org much more suitable for bounded agent tasks than a typical codebase with opaque state or GUI-only workflows.

---

## 3. Expanded architecture plan for the organization

### 3.1 Core principle

Use GitHub Actions as the **control plane** and keep the actual agent execution narrow, auditable, and isolated.

The system should look like this:

- **GitHub events** trigger workflows.
- A **gate layer** validates repo, actor, trigger type, budget, and permissions.
- The workflow sends the job to either:
  - a **GitHub-hosted runner** for public/untrusted CI,
  - a **trusted self-hosted maintenance runner** for agent code edits and controlled automation,
  - or a **compute orchestration runner** that submits detached work to Slurm/Kubernetes/Ray and harvests outputs later.
- The agent outputs one of a small number of allowed products:
  - draft PR
  - issue/review comment
  - benchmark diff
  - markdown report
  - artifact bundle

The agent should not merge to protected branches directly.

### 3.2 What not to do

Do **not** allow:

- fork PRs to land on self-hosted runners
- public comments from arbitrary users to invoke write-capable workflows
- persistent runners with broad repo or cluster access to process untrusted code
- one shared org-wide bot token with write access everywhere
- long-running simulations to remain attached to a single GitHub Actions job as if it were an HPC scheduler

### 3.3 Recommended trust tiers

#### Tier A: Public CI

Use GitHub-hosted runners only.

Typical triggers:

- `pull_request`
- `push`
- public validation

Capabilities:

- install dependencies
- run tests
- run documentation checks
- run very small smoke examples

Restrictions:

- no self-hosted access
- no model secrets
- minimal `GITHUB_TOKEN`
- no access to internal lab infrastructure

#### Tier B: Trusted maintenance

Use self-hosted ephemeral runners for bounded agent tasks.

Typical triggers:

- `workflow_dispatch`
- `schedule`
- maintainer-only `issue_comment`
- trusted `workflow_run`

Capabilities:

- run Codex or another coding agent
- reproduce failures
- patch code or docs
- run targeted tests/examples
- open draft PRs
- write structured summaries

Restrictions:

- selected repos only
- no fork PRs
- minimal repo-scoped write permissions
- no scheduler credentials unless explicitly needed

#### Tier C: Compute orchestration

Use a separate self-hosted lane for long or expensive scientific work.

Typical triggers:

- `workflow_dispatch`
- `schedule`
- `repository_dispatch`

Capabilities:

- validate configs and budgets
- submit detached work to Slurm/K8s/Ray
- poll or receive callbacks
- harvest plots, tables, logs
- post reports and artifacts

Restrictions:

- separate credentials from maintenance lane
- no general write access beyond what is necessary to publish artifacts or comments
- no direct exposure to public/untrusted events

### 3.4 Recommended first workflow patterns

#### A. CI autofix

When CI fails on a trusted branch or scheduled maintenance check:

1. reproduce the failing step
2. patch code/config/docs
3. rerun only the necessary tests
4. open a draft PR with a before/after summary

This is one of the best first pilots because success or failure is obvious.

#### B. Maintainer-commanded patch

A maintainer writes a controlled command such as:

- `/agent fix-ci`
- `/agent update-docs`
- `/agent reproduce issue #123`

The workflow validates actor + repo + command, then runs a bounded task.

#### C. Nightly hygiene

Scheduled checks can:

- run smoke examples
- check dependency drift
- refresh docs or benchmarks
- detect stale notebooks/examples
- open low-risk maintenance PRs

#### D. Experiment orchestrator

This is the key research-science pattern:

1. preflight the run
2. submit detached jobs
3. later harvest results
4. package a report
5. post a summary comment or PR

The orchestration lives in GitHub; the heavy simulation lives in the scheduler.

### 3.5 Long-running runs: the correct pattern

GitHub should orchestrate long scientific work, not babysit it.

The correct flow is:

1. **Preflight**
   - validate actor
   - validate repo allowlist
   - validate config
   - validate budget
   - compute config hash
2. **Submit**
   - submit to Slurm/K8s/Ray
   - record job id, commit SHA, seed, config hash
3. **Track**
   - poll or handle callback via `repository_dispatch`
4. **Harvest**
   - collect plots, logs, tables, serialized outputs
5. **Publish**
   - generate markdown report and artifact bundle
   - open PR or post comment

Every detached run should have a manifest containing:

- repo
- branch
- commit SHA
- workflow run id
- config hash
- random seed
- owner
- wall-clock budget
- software environment metadata

### 3.6 Model/tooling decision

The org should hide model choice behind an internal adapter.

That means standardizing:

- prompt file layout
- allowed tools
- logging schema
- run summary format
- retry behavior
- budgets and timeouts
- policy files

Then the backend can be:

- Codex via GitHub Actions or SDK
- Claude Code / Agent SDK
- a future model later

For the first PR-centric pilots, **Codex is the best first fit** because it already has a GitHub Action path and maps naturally to review-oriented workflows.

### 3.7 Governance defaults

Every agent repo or org workflow should have:

- explicit prompt files in-repo and code-reviewed
- repo allowlist
- actor allowlist where needed
- concurrency groups
- budgets and retry policies
- machine-readable summaries
- audit logs
- branch protection on `main`
- human review before merge

### 3.8 90-day rollout plan

#### Weeks 1–2

- choose pilot repos
- define policy allowlist
- tighten smoke tests/examples
- decide runner labels and runner groups
- create baseline metrics

#### Weeks 3–6

- ship PR-only autofix on one or two repos
- start nightly smoke workflows
- instrument acceptance rate and rerun pass rate

#### Weeks 7–10

- deploy ephemeral trusted lane
- add maintainer-triggered issue commands
- centralize logs and summaries

#### Weeks 11–12

- pilot detached experiment orchestration
- review governance burden
- decide whether to expand

### 3.9 Success metrics

Measure:

- median time to fix red CI
- fraction of agent PRs merged after review
- first-rerun pass rate for agent PRs
- smoke coverage across examples
- reproducibility rate of experiment reports
- review burden on maintainers
- security incidents or secret exposures

The security target is zero incidents.

---

## 4. Why JAX-in-Cell is the right first scientific showcase

JAX-in-Cell is a strong first showcase because it already appears to have most of the traits needed for a good bounded pilot:

- it can be run from the CLI (`jaxincell`) or from scripts
- it accepts TOML-driven inputs
- it has an `examples/` directory
- it already includes a parameter-optimization example in the repo
- it has tests and GitHub Actions
- it is fast enough for repeated short runs
- its outputs are naturally scientific and visual

This makes it an ideal place to showcase:

- configuration mutation
- bounded experiment loops
- objective scoring
- artifact generation
- periodic execution
- agent-generated summaries

In other words, it exercises the architecture in a scientifically meaningful way without needing immediate HPC-scale complexity.

---

## 5. Concrete showcase repo proposal

### 5.1 Proposed repo name

Default proposed repo name:

`uwplasma/jaxincell-drift-opt-agent`

Other acceptable names:

- `uwplasma/JAX-in-Cell-Drift-Optimizer`
- `uwplasma/jaxincell-agent-demo`
- `uwplasma/agentic-jaxincell-drift-opt`

I recommend **`jaxincell-drift-opt-agent`** because it is explicit, compact, and clearly signals that this is a demonstration of agentic optimization rather than the core solver itself.

### 5.2 Purpose of the repo

The repo is a **thin orchestration layer** around JAX-in-Cell.

It should:

- import or install JAX-in-Cell
- load a base JAX-in-Cell input file
- mutate the electron drift velocity according to a configurable rule
- run the simulation
- compute a scalar score representing final nonlinear saturation of electric-field energy
- use Bayesian optimization to select the next candidate parameter
- persist optimizer state and results
- produce plots, logs, and markdown summaries
- run periodically via GitHub Actions
- optionally invoke a coding agent periodically for repo hygiene and maintenance

The repo should not initially modify the internals of JAX-in-Cell.

### 5.3 Scientific target

The demonstration objective is:

> Adjust the electron drift velocity in a JAX-in-Cell base input so as to maximize the final nonlinear saturation of electric-field energy.

This is a good showcase because:

- it is scientifically interpretable
- it produces a scalar objective for optimization
- it produces time traces and plots for human review
- it can be made cheap enough for repeated runs
- it is closely aligned with instability physics already present in JAX-in-Cell examples

### 5.4 Parameterization rule

The repo should not hard-code one brittle absolute number. Instead it should define a **rule** that is easy to tweak.

Recommended default rule:

```text
base_drift = value from base input file
candidate drift = base_drift * drift_multiplier
```

Default search parameter:

- `drift_multiplier`

Recommended default search range:

- `[0.25, 2.5]`

This gives a simple and dimensionless way to vary the physical control parameter while preserving the meaning of the original example.

The repo should also support an alternate mode:

```text
candidate drift = absolute drift speed in m/s
```

This can be activated later if desired.

### 5.5 Base input choice

The first implementation should start from a known JAX-in-Cell example input with a nonzero electron drift speed already present.

The implementation should:

1. inspect the current JAX-in-Cell repo,
2. identify the most suitable existing example/input pair,
3. copy a minimal base input into this new repo under `configs/base_input.toml`,
4. document exactly which original JAX-in-Cell example it came from.

Important implementation note:

The current JAX-in-Cell materials appear to show small inconsistencies between README parameter names and an existing optimization example. Therefore the code must inspect the **current actual parameter names in the installed/current JAX-in-Cell code path** rather than relying on stale assumptions.

### 5.6 Score definition

The repo must define a score that is robust enough for optimization and interpretable enough for humans.

Recommended default primary score:

```text
tail_mean_E = mean of electric_field_energy over the last tail_fraction of the simulation
```

Recommended defaults:

- `tail_fraction = 0.20`
- if `electric_field_energy` is directly available in the JAX-in-Cell output, use it
- otherwise compute it from the electric field data in a physically consistent way

Recommended optimizer target:

```text
objective_for_optimizer = -log10(tail_mean_E + eps)
```

or equivalently maximize:

```text
score_for_reporting = log10(tail_mean_E + eps)
```

Why use a log score?

- electric-field energy can vary across many orders of magnitude
- a log objective is often smoother for Bayesian optimization
- it gives a more interpretable leaderboard

Also compute secondary diagnostics for every trial:

- raw `tail_mean_E`
- `tail_max_E`
- time of peak electric-field energy
- final electric-field energy
- whether the run failed
- wall-clock time
- config hash
- random seed

### 5.7 Failure handling

Not every simulation will complete successfully. Failed runs should not break the campaign.

If a run fails, the repo should:

- record failure status
- capture traceback/stdout/stderr
- assign a very poor objective value
- keep the campaign state consistent
- continue the optimizer loop unless a configurable failure threshold is exceeded

### 5.8 Bayesian optimization engine

Use a lightweight global Bayesian optimizer.

Recommended default:

- `scikit-optimize` with a Gaussian-process-based `Optimizer`
- use `ask` / `tell` so the state can be resumed across scheduled GitHub runs

Suggested default campaign settings:

- initial random points: 5
- new points per scheduled run: 3 to 5
- total target evaluations per campaign: 20 to 40
- acquisition: default GP EI or LCB

Important design choice:

The optimizer state must be **persistent across workflow runs**.

### 5.9 Persistent state design

Do not rely only on temporary workflow artifacts for optimizer state.

Recommended design:

- keep canonical state in a dedicated branch such as `agent-state`
- store machine-readable files such as:
  - `state/optimizer_state.json`
  - `state/trials.csv`
  - `state/best_result.json`
  - `reports/latest_summary.md`
- upload the same files as workflow artifacts for convenience

This makes the campaign resumable even after artifact retention windows or workflow history turnover.

### 5.10 Repo layout

Recommended initial repo structure:

```text
jaxincell-drift-opt-agent/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── configs/
│   ├── base_input.toml
│   ├── search.yaml
│   └── scoring.yaml
├── src/
│   └── jaxincell_drift_opt/
│       ├── __init__.py
│       ├── config.py
│       ├── jaxincell_adapter.py
│       ├── mutate_input.py
│       ├── run_trial.py
│       ├── scoring.py
│       ├── optimizer_state.py
│       ├── optimizer_loop.py
│       ├── reporting.py
│       ├── plotting.py
│       └── utils.py
├── scripts/
│   ├── run_campaign.py
│   ├── run_one_trial.py
│   ├── suggest_next.py
│   ├── summarize_results.py
│   └── bootstrap_state.py
├── tests/
│   ├── test_mutation.py
│   ├── test_scoring.py
│   ├── test_optimizer_state.py
│   └── test_smoke_mocked.py
├── outputs/
│   └── .gitkeep
├── state/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── agent/
│   ├── prompts/
│   │   └── maintenance.md
│   ├── policies/
│   │   ├── repos.yaml
│   │   └── actors.yaml
│   └── summarize.py
└── .github/
    ├── workflows/
    │   ├── ci.yml
    │   ├── optimize-scheduled.yml
    │   ├── optimize-dispatch.yml
    │   ├── optimize-issue-command.yml
    │   └── codex-maintenance.yml
    ├── ISSUE_TEMPLATE/
    │   └── experiment_request.md
    └── pull_request_template.md
```

### 5.11 Core software behavior

#### `jaxincell_adapter.py`

Responsibilities:

- load base input TOML
- validate actual parameter names used by installed/current JAX-in-Cell
- mutate `electron_drift_speed_x` or the chosen equivalent field
- call the correct JAX-in-Cell run path
- return normalized outputs used by scoring

This adapter should be the only place that knows about JAX-in-Cell specifics.

#### `mutate_input.py`

Responsibilities:

- apply multiplier or absolute update rule
- optionally clamp to configured min/max bounds
- record the mutated parameter set
- write a per-trial frozen input TOML into outputs for reproducibility

#### `run_trial.py`

Responsibilities:

- run exactly one trial
- save plots and machine-readable results
- return a dictionary with metrics and failure status

#### `scoring.py`

Responsibilities:

- compute primary score
- compute secondary diagnostics
- define the penalty for failed runs
- keep score definition versioned so future campaigns are comparable

#### `optimizer_state.py`

Responsibilities:

- serialize/deserialize optimizer state
- keep track of all tried points and scores
- support resuming after a previous GitHub Actions run

#### `optimizer_loop.py`

Responsibilities:

- initialize optimizer if no state exists
- ask for the next candidate(s)
- execute trials
- tell the optimizer the observed results
- update leaderboard and best result
- write markdown summary

#### `reporting.py`

Responsibilities:

- generate a human-readable markdown report
- generate a CSV leaderboard
- generate JSON summary files
- write a concise status suitable for GitHub Actions summary output

### 5.12 Artifacts expected from each campaign execution

Each scheduled run should publish:

- leaderboard CSV
- best-result JSON
- markdown campaign summary
- one optimization-trace plot
- one plot of score vs drift multiplier
- one plot of electric-field energy vs time for the current best run
- frozen input file for each new trial
- stdout/stderr logs for each trial

### 5.13 The minimal scientific plots

At minimum the repo should produce:

1. **optimization trace**
   - best score so far vs trial number
2. **objective landscape (sampled)**
   - drift multiplier vs score for all completed trials
3. **best run time trace**
   - electric-field energy vs time for the current best configuration
4. **comparison plot**
   - baseline run vs best-so-far run electric-field-energy traces

### 5.14 GitHub workflows to create

#### Workflow 1: `ci.yml`

Use GitHub-hosted runners.

Trigger on:

- push
- pull_request

Run:

- install package
- unit tests
- a mocked or very short smoke test
- formatting/lint if included

Purpose:

- keep the showcase repo healthy
- avoid sending public PR traffic to self-hosted infrastructure

#### Workflow 2: `optimize-scheduled.yml`

Trigger on:

- `schedule`
- `workflow_dispatch`

Default behavior:

- resume optimizer state
- run a small number of new trials
- update state branch
- upload artifacts
- write GitHub Actions job summary

For the very first version, it is acceptable for this to run on `ubuntu-latest` if runner labels or org-level self-hosted routing are not yet ready. The code and workflow should still be structured so it can be promoted to a self-hosted trusted lane later with minimal changes.

#### Workflow 3: `optimize-dispatch.yml`

Trigger on:

- `workflow_dispatch`

Inputs:

- number of new trials
- exploration mode
- search range override
- seed override
- whether to commit state branch

Purpose:

- make it easy to manually test the system
- make it easy for maintainers to run a bounded campaign

#### Workflow 4: `optimize-issue-command.yml`

Trigger on:

- `issue_comment`

Allowed commands:

- `/optimize 3`
- `/optimize 5`
- `/summarize`

Must include a strict actor allowlist.

Purpose:

- demonstrate safe maintainer-commanded orchestration

#### Workflow 5: `codex-maintenance.yml`

Trigger on:

- weekly `schedule`
- manual `workflow_dispatch`

Purpose:

- run a very narrow maintenance prompt
- detect low-risk issues such as doc drift, broken examples, weak tests, or README inconsistencies
- open a draft PR if Codex makes changes

Important restriction:

- this workflow should be dormant unless the necessary model secret exists
- code changes must always go through a PR

### 5.15 Permissions model

Recommended defaults:

For CI:

- `contents: read`

For optimization workflows that commit state:

- `contents: write`
- no broader permissions than needed

For Codex maintenance:

- `contents: write`
- `pull-requests: write`
- `issues: write` only if the workflow comments back to issues

No workflow should use more permissions than necessary.

### 5.16 Branching model

Recommended branches:

- `main`: code, reviewed and protected
- `agent-state`: optimizer state and campaign history
- short-lived feature branches for Codex maintenance PRs

Do **not** let periodic optimization runs write directly to `main`.

### 5.17 Concurrency model

Use GitHub Actions concurrency to prevent overlapping campaigns on the same repo.

Recommended default:

- one scheduled optimization campaign at a time
- cancel stale in-progress dispatch runs if a newer manual run supersedes them

### 5.18 Logging and auditability

Each workflow run should make it obvious:

- what was attempted
- what parameter was tried
- what score was obtained
- what failed
- whether optimizer state advanced
- whether code was modified
- whether anything was pushed

All summaries should be machine-readable and human-readable.

### 5.19 Success criteria for the demo repo

The demo is successful if the repo can reliably:

- run repeated JAX-in-Cell trials from a base input
- mutate drift speed according to a configurable rule
- score trials robustly
- continue the optimizer state over time
- produce understandable plots and markdown summaries
- run periodically in GitHub Actions
- remain reviewable and easy to disable

---

## 6. Immediate practical design choices

### 6.1 Start as a thin wrapper, not a JAX-in-Cell fork

The first version should be a new repo that depends on JAX-in-Cell rather than modifying the JAX-in-Cell repo directly.

Why:

- lower review burden
- less risk of destabilizing the core solver repo
- easier to demonstrate the architecture cleanly
- allows rapid iteration on agent/workflow design

### 6.2 Keep the first campaign cheap

Do not start with a large parameter scan or GPU-scale workload.

The first campaign should be small enough that:

- each trial is short
- scheduled workflows finish comfortably
- plots and reports are quick to review
- failures are easy to diagnose

### 6.3 Preserve every evaluated point

The point of this repo is not only to find the current best drift speed. It is also to demonstrate a scientific audit trail.

Therefore every evaluated point should record:

- frozen input
- score
- diagnostics
- logs
- time trace plot
- seed
- software revision

### 6.4 Make the score definition explicit and versioned

The repo should include something like:

```text
score_version = v1_tail_mean_logE
```

This avoids confusion later if the definition changes.

### 6.5 Separate agentic code maintenance from experiment execution

These are different workflows with different risk profiles:

- experiment execution changes state/data
- maintenance may edit code and open PRs

Keep them separate from day one.

---

## 7. Recommended first meeting talking points for the group

When sharing this with the group, emphasize:

1. this is **not** a plan for uncontrolled autonomous coding across all repos
2. this is a plan for **isolated, reviewable workflows**
3. the first scientific demo is intentionally narrow
4. the main value is not just code generation, but also:
   - reproducibility
   - regression detection
   - automated reporting
   - bounded experiment loops
5. the first repo is a wrapper around JAX-in-Cell, not a rewrite of JAX-in-Cell itself
6. the architecture is designed so risky parts can be turned off independently

---

## 8. Full Codex execution brief

The text below is written to be pasted directly into Codex.

---

# Codex prompt: create the showcase repo, code, and workflows

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

---

## 9. Recommended manual follow-up after Codex finishes

After Codex completes the initial repo, the human follow-up should be:

1. inspect the repo structure and score definition
2. confirm the chosen JAX-in-Cell base example is physically the right one
3. confirm the drift search range is physically reasonable
4. review workflow permissions
5. decide whether the scheduled optimization should remain GitHub-hosted for now or move to a trusted self-hosted lane
6. add the Codex secret only if the maintenance workflow is actually desired
7. watch the first few scheduled runs before scaling the campaign

---

## 10. Short version to say out loud in the meeting

We are not proposing an uncontrolled org-wide coding bot. We are proposing a safe, event-driven architecture with narrow runner lanes and human review gates. As a first scientific demonstration, we create a small wrapper repo around JAX-in-Cell that periodically optimizes electron drift speed to maximize the final nonlinear saturation of electric-field energy, stores every trial and artifact, and showcases how agentic workflows can be useful for real plasma-science code without taking unsafe control of the organization.

---

## 11. Notes from the current public materials checked while preparing this plan

These notes are included so the implementation brief stays anchored to the present public state.

- The public `uwplasma` organization page currently lists around 35 repositories and identifies JAX-in-Cell and ESSOS among the representative public projects.
- The public JAX-in-Cell repository currently shows an `examples/` directory, a `jaxincell/` package, `tests/`, and GitHub workflow files.
- The public README indicates JAX-in-Cell can be run from the CLI as `jaxincell`, from TOML inputs, and from Python examples.
- The public README also shows an existing optimization example file named `examples/optimize_two_stream_saturation.py`, which is strong evidence that the showcase repo should reuse that style rather than inventing a completely unrelated interface.

---

## 12. Sources checked

### Current public repo/docs state

- `https://github.com/uwplasma`
- `https://github.com/uwplasma/JAX-in-Cell`
- `https://github.com/uwplasma/JAX-in-Cell/actions`
- `https://raw.githubusercontent.com/uwplasma/JAX-in-Cell/main/examples/input.toml`
- `https://raw.githubusercontent.com/uwplasma/JAX-in-Cell/main/examples/optimize_two_stream_saturation.py`
- `https://raw.githubusercontent.com/uwplasma/JAX-in-Cell/main/examples/two-stream_instability.py`

### GitHub runner/security references

- `https://docs.github.com/actions/hosting-your-own-runners`
- `https://docs.github.com/actions/hosting-your-own-runners/managing-self-hosted-runners/managing-access-to-self-hosted-runners-using-groups`
- `https://docs.github.com/en/actions/reference/limits`
- `https://docs.github.com/en/actions/reference/security/secure-use`
- `https://docs.github.com/en/organizations/managing-organization-settings/disabling-or-limiting-github-actions-for-your-organization`

### Codex references

- `https://developers.openai.com/codex/github-action/`
- `https://developers.openai.com/codex/sdk/`

