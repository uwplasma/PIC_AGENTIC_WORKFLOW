# Latest Summary

## Campaign

- Trials completed: 6
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0001
- Drift multiplier: 1.301660
- Candidate drift: 7.809962e+07
- Ion temperature ratio: 1.079942e+01
- Ion mass over proton mass: 2.420796e-01
- Optimizer score: 0.448104
- Optimizer objective: -0.448104
- Tail mean E: 2.806108e+00
- Final E: 2.014327e+00

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0001 | 2026-04-06 22:09 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.806108e+00 | 0.448104 |
| 2 | trial_0000 | 2026-04-06 22:06 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 2.583178e+00 | 0.412154 |
| 3 | trial_0002 | 2026-04-06 23:01 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.330451e+00 | 0.367440 |
| 4 | trial_0003 | 2026-04-06 23:56 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.054744e+00 | 0.312758 |
| 5 | trial_0004 | 2026-04-07 03:39 UTC | 0.960704 | 1.487234e-02 | 2.379395e-01 | 1.830490e+00 | 0.262567 |
| 6 | trial_0005 | 2026-04-07 06:05 UTC | 0.854412 | 1.124889e-02 | 1.144645e+00 | 1.645037e+00 | 0.216176 |

## Recent Trials

- trial_0000 at 2026-04-06 22:06 UTC: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, score=0.412154, failed=False
- trial_0001 at 2026-04-06 22:09 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.448104, failed=False
- trial_0002 at 2026-04-06 23:01 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.367440, failed=False
- trial_0003 at 2026-04-06 23:56 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.312758, failed=False
- trial_0004 at 2026-04-07 03:39 UTC: drift=0.960704, temp_ratio=1.487234e-02, mass_ratio=2.379395e-01, score=0.262567, failed=False
- trial_0005 at 2026-04-07 06:05 UTC: drift=0.854412, temp_ratio=1.124889e-02, mass_ratio=1.144645e+00, score=0.216176, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

