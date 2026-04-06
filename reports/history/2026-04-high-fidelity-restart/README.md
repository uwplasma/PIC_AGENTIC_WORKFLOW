# High-Fidelity Restart Archive

This directory preserves the public artifacts from the saturation campaign that ran before the April 2026 restart.

## What The Previous Campaign Achieved

- Completed trials: `418`
- Best trial: `trial_0184`
- Best public score: `1.293439`
- Best tail-mean electric-field energy: `1.965345e+01`
- Best parameters: drift multiplier `2.230586`, ion temperature ratio `1.000000e-03`, ion mass over proton mass `1.000000e-02`

## Best Previous Leaderboard Entries

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0184 | 2026-03-29 20:51 UTC | 2.230586 | 1.000000e-03 | 1.000000e-02 | 1.965345e+01 | 1.293439 |
| 2 | trial_0182 | 2026-03-29 19:58 UTC | 2.234738 | 1.000000e-03 | 1.000000e-02 | 1.876810e+01 | 1.273420 |
| 3 | trial_0334 | 2026-04-02 10:16 UTC | 1.924501 | 1.119754e-02 | 3.866414e-02 | 1.855863e+01 | 1.268546 |
| 4 | trial_0173 | 2026-03-29 17:04 UTC | 2.232236 | 1.000000e-03 | 1.000000e-02 | 1.845095e+01 | 1.266019 |
| 5 | trial_0185 | 2026-03-29 21:00 UTC | 2.278048 | 1.000000e-03 | 1.000000e-02 | 1.824489e+01 | 1.261141 |

## Why The Campaign Was Restarted

The old leaderboard did not fail. It converged onto a physically interesting regime and then exposed a limit in the simulation budget used by the original baseline.

- The strongest candidates were clustering in a narrow high-drift, low-ion-temperature, low-ion-mass corner.
- Those candidates were producing enough nonlinear activity that the shorter run length was no longer obviously sufficient.
- The combination of low particle count and larger time step risked confusing numerical artifacts with true saturation behavior.

The restart therefore upgrades the baseline simulation fidelity while keeping the optimization objective and search dimensions fixed.

## Solver Changes Introduced For The Restart

| Setting | Previous | Restarted campaign |
| --- | ---: | ---: |
| `timestep_over_spatialstep_times_c` | `2.0` | `1.0` |
| `number_grid_points` | `100` | `120` |
| `number_pseudoelectrons` | `5000` | `12000` |
| `total_steps` | `1500` | `5000` |
| `number_of_particle_substeps_implicit_CN` | `2` | `2` |

## Archived Public Artifacts

- Previous public summary: [latest_summary_pre_restart.md](latest_summary_pre_restart.md)
- Previous public reasoning log: [agent_reasoning_pre_restart.md](agent_reasoning_pre_restart.md)
- Previous parameter-space trajectory: [parameter_space_trajectory_pre_restart.png](parameter_space_trajectory_pre_restart.png)
- Previous initial-condition movie: [initial-condition.gif](initial-condition.gif)
- Previous rank-1 movie: [leaderboard-rank-1.gif](leaderboard-rank-1.gif)
- Previous rank-2 movie: [leaderboard-rank-2.gif](leaderboard-rank-2.gif)

## Interpretation

The old campaign established that the optimizer could reliably find strongly saturating two-stream configurations. The new campaign starts from an empty leaderboard not because the previous run was discarded, but because the next scientific step needs a cleaner, longer, and less noisy baseline.