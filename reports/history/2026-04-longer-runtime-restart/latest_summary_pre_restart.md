# Latest Summary

## Campaign

- Trials completed: 11
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0010
- Drift multiplier: 1.305280
- Candidate drift: 7.831681e+07
- Ion temperature ratio: 7.328883e+01
- Ion mass over proton mass: 8.310291e-01
- Optimizer score: 0.521818
- Optimizer objective: -0.521818
- Tail mean E: 3.325203e+00
- Final E: 4.216391e+00

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0010 | 2026-04-07 14:35 UTC | 1.305280 | 7.328883e+01 | 8.310291e-01 | 3.325203e+00 | 0.521818 |
| 2 | trial_0009 | 2026-04-07 14:18 UTC | 1.081476 | 3.688025e-03 | 8.880275e-01 | 3.323595e+00 | 0.521608 |
| 3 | trial_0008 | 2026-04-07 11:53 UTC | 1.035567 | 3.307409e-02 | 9.087398e-01 | 3.162970e+00 | 0.500095 |
| 4 | trial_0007 | 2026-04-07 09:50 UTC | 1.012228 | 9.742964e-03 | 9.593326e-01 | 2.870835e+00 | 0.458008 |
| 5 | trial_0001 | 2026-04-06 22:09 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.806108e+00 | 0.448104 |
| 6 | trial_0000 | 2026-04-06 22:06 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 2.583178e+00 | 0.412154 |
| 7 | trial_0002 | 2026-04-06 23:01 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.330451e+00 | 0.367440 |
| 8 | trial_0003 | 2026-04-06 23:56 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 2.054744e+00 | 0.312758 |
| 9 | trial_0004 | 2026-04-07 03:39 UTC | 0.960704 | 1.487234e-02 | 2.379395e-01 | 1.830490e+00 | 0.262567 |
| 10 | trial_0005 | 2026-04-07 06:05 UTC | 0.854412 | 1.124889e-02 | 1.144645e+00 | 1.645037e+00 | 0.216176 |
| 11 | trial_0006 | 2026-04-07 08:04 UTC | 1.263124 | 1.105104e+01 | 1.661493e-01 | 1.510296e+00 | 0.179062 |

## Recent Trials

- trial_0001 at 2026-04-06 22:09 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.448104, failed=False
- trial_0002 at 2026-04-06 23:01 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.367440, failed=False
- trial_0003 at 2026-04-06 23:56 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=0.312758, failed=False
- trial_0004 at 2026-04-07 03:39 UTC: drift=0.960704, temp_ratio=1.487234e-02, mass_ratio=2.379395e-01, score=0.262567, failed=False
- trial_0005 at 2026-04-07 06:05 UTC: drift=0.854412, temp_ratio=1.124889e-02, mass_ratio=1.144645e+00, score=0.216176, failed=False
- trial_0006 at 2026-04-07 08:04 UTC: drift=1.263124, temp_ratio=1.105104e+01, mass_ratio=1.661493e-01, score=0.179062, failed=False
- trial_0007 at 2026-04-07 09:50 UTC: drift=1.012228, temp_ratio=9.742964e-03, mass_ratio=9.593326e-01, score=0.458008, failed=False
- trial_0008 at 2026-04-07 11:53 UTC: drift=1.035567, temp_ratio=3.307409e-02, mass_ratio=9.087398e-01, score=0.500095, failed=False
- trial_0009 at 2026-04-07 14:18 UTC: drift=1.081476, temp_ratio=3.688025e-03, mass_ratio=8.880275e-01, score=0.521608, failed=False
- trial_0010 at 2026-04-07 14:35 UTC: drift=1.305280, temp_ratio=7.328883e+01, mass_ratio=8.310291e-01, score=0.521818, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

