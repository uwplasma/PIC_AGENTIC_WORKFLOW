# Longer-Runtime Restart Archive

This directory preserves the public artifacts from the intermediate April 2026 campaign that ran after the first high-fidelity restart and before the live baseline was extended to longer physical time coverage.

## What The Archived Campaign Achieved

- Completed trials: `12`
- Best trial: `trial_0010`
- Best public score: `0.521818`
- Best tail-mean electric-field energy: `3.325203e+00`
- Best parameters: drift multiplier `1.305280`, ion temperature ratio `7.328883e+01`, ion mass over proton mass `8.310291e-01`

## Best Archived Leaderboard Entries

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0010 | 2026-04-07 14:35 UTC | 1.305280 | 7.328883e+01 | 8.310291e-01 | 3.325203e+00 | 0.521818 |
| 2 | trial_0009 | 2026-04-07 14:18 UTC | 1.081476 | 3.688025e-03 | 8.880275e-01 | 3.323595e+00 | 0.521608 |
| 3 | trial_0008 | 2026-04-07 11:53 UTC | 1.035567 | 3.307409e-02 | 9.087398e-01 | 3.162970e+00 | 0.500095 |
| 4 | trial_0007 | 2026-04-07 09:50 UTC | 1.012228 | 9.742964e-03 | 9.593326e-01 | 2.870835e+00 | 0.458008 |
| 5 | trial_0001 | 2026-04-06 22:09 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.806108e+00 | 0.448104 |

## Why The Campaign Was Restarted

The intermediate campaign improved on the restarted baseline, but it still showed that the simulation window was too short for the physics the optimizer was starting to favor.

- The best trials were still pushing significant field growth late in the run.
- The next scientific step was to extend physical-time coverage rather than keep optimizing a short observation window.
- Public movies also had to stay cheap enough to publish, so the render path was decoupled from the longer live baseline by enforcing a short movie-duration cap.
- A stale scheduled publish landed one final extra trial (`trial_0011`) after the first reset commit; this archive preserves that final public state before the corrected reset.

## Solver Changes Introduced For The Live Restart

| Setting | Archived campaign | Live campaign |
| --- | ---: | ---: |
| `timestep_over_spatialstep_times_c` | `1.0` | `1.5` |
| `number_grid_points` | `120` | `100` |
| `number_pseudoelectrons` | `12000` | `10000` |
| `total_steps` | `5000` | `6500` |
| `number_of_particle_substeps_implicit_CN` | `2` | `2` |

## Archived Public Artifacts

- Archived public summary: [latest_summary_pre_restart.md](latest_summary_pre_restart.md)
- Archived public reasoning log: [agent_reasoning_pre_restart.md](agent_reasoning_pre_restart.md)
- Archived parameter-space trajectory: [parameter_space_trajectory_pre_restart.png](parameter_space_trajectory_pre_restart.png)
- Archived initial-condition movie: [initial-condition.gif](initial-condition.gif)
- Archived rank-1 movie: [leaderboard-rank-1.gif](leaderboard-rank-1.gif)
- Archived rank-2 movie: [leaderboard-rank-2.gif](leaderboard-rank-2.gif)