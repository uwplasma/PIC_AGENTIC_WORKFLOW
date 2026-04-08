# Latest Summary

## Campaign

- Trials completed: 9
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0005
- Drift multiplier: 0.976904
- Candidate drift: 5.861424e+07
- Ion temperature ratio: 6.340485e-01
- Ion mass over proton mass: 9.488015e-01
- Optimizer score: 0.098600
- Optimizer objective: -0.098600
- Tail mean E: 1.254875e+00
- Final E: 1.699060e+00

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0005 | 2026-04-07 22:04 UTC | 0.976904 | 6.340485e-01 | 9.488015e-01 | 1.254875e+00 | 0.098600 |
| 2 | trial_0000 | 2026-04-07 17:21 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.068335e+00 | 0.028707 |
| 3 | trial_0002 | 2026-04-07 18:16 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 9.054071e-01 | -0.043156 |
| 4 | trial_0003 | 2026-04-07 19:37 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 9.029193e-01 | -0.044351 |
| 5 | trial_0001 | 2026-04-07 17:24 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 8.807393e-01 | -0.055153 |
| 6 | trial_0006 | 2026-04-07 23:05 UTC | 0.796987 | 1.000000e+02 | 5.685356e-01 | 7.915079e-01 | -0.101545 |
| 7 | trial_0008 | 2026-04-08 03:39 UTC | 1.053174 | 1.000000e+02 | 1.000000e-02 | 2.062695e-01 | -0.685565 |
| 8 | trial_0004 | 2026-04-07 21:09 UTC | 0.317386 | 1.175833e-02 | 3.517104e+00 | 1.514915e-02 | -1.819612 |
| 9 | trial_0007 | 2026-04-07 23:59 UTC | 2.297878 | 1.088750e+01 | 8.316879e-02 | 8.462895e-03 | -2.072481 |

## Recent Trials

- trial_0000 at 2026-04-07 17:21 UTC: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, score=0.028707, failed=False
- trial_0001 at 2026-04-07 17:24 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=-0.055153, failed=False
- trial_0002 at 2026-04-07 18:16 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=-0.043156, failed=False
- trial_0003 at 2026-04-07 19:37 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=-0.044351, failed=False
- trial_0004 at 2026-04-07 21:09 UTC: drift=0.317386, temp_ratio=1.175833e-02, mass_ratio=3.517104e+00, score=-1.819612, failed=False
- trial_0005 at 2026-04-07 22:04 UTC: drift=0.976904, temp_ratio=6.340485e-01, mass_ratio=9.488015e-01, score=0.098600, failed=False
- trial_0006 at 2026-04-07 23:05 UTC: drift=0.796987, temp_ratio=1.000000e+02, mass_ratio=5.685356e-01, score=-0.101545, failed=False
- trial_0007 at 2026-04-07 23:59 UTC: drift=2.297878, temp_ratio=1.088750e+01, mass_ratio=8.316879e-02, score=-2.072481, failed=False
- trial_0008 at 2026-04-08 03:39 UTC: drift=1.053174, temp_ratio=1.000000e+02, mass_ratio=1.000000e-02, score=-0.685565, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

