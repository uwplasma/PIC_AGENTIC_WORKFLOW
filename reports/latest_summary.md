# Latest Summary

## Campaign

- Trials completed: 2
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0000
- Drift multiplier: 1.000000
- Candidate drift: 6.000000e+07
- Ion temperature ratio: 1.000000e-02
- Ion mass over proton mass: 1.000000e+00
- Optimizer score: 0.028707
- Optimizer objective: -0.028707
- Tail mean E: 1.068335e+00
- Final E: 9.834905e-01

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0000 | 2026-04-07 17:21 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.068335e+00 | 0.028707 |
| 2 | trial_0001 | 2026-04-07 17:24 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 8.807393e-01 | -0.055153 |

## Recent Trials

- trial_0000 at 2026-04-07 17:21 UTC: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, score=0.028707, failed=False
- trial_0001 at 2026-04-07 17:24 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=-0.055153, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

