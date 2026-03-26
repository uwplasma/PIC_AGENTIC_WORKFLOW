# Latest Summary

## Campaign

- Trials completed: 13
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0004
- Drift multiplier: 1.610619
- Candidate drift: 9.663717e+07
- Ion temperature ratio: 2.546783e-01
- Ion mass over proton mass: 2.500000e-01
- Optimizer score: 0.948376
- Optimizer objective: -0.948376
- Tail mean E: 8.879253e+00
- Final E: 5.731253e+00

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0004 | 1.610619 | 2.546783e-01 | 2.500000e-01 | 8.879253e+00 | 0.948376 |
| 2 | trial_0012 | 1.534184 | 1.000000e+00 | 2.500000e-01 | 8.733743e+00 | 0.941200 |
| 3 | trial_0011 | 1.522543 | 1.000000e+00 | 2.500000e-01 | 8.523101e+00 | 0.930598 |
| 4 | trial_0009 | 1.510646 | 1.000000e-03 | 2.500000e-01 | 8.280516e+00 | 0.918057 |
| 5 | trial_0007 | 1.340682 | 1.000000e+00 | 2.500000e-01 | 5.691461e+00 | 0.755224 |
| 6 | trial_0003 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 4.360650e+00 | 0.639551 |
| 7 | trial_0010 | 1.150519 | 1.000000e+00 | 4.000000e+00 | 2.786722e+00 | 0.445094 |
| 8 | trial_0001 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 2.688404e+00 | 0.429495 |
| 9 | trial_0000 | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.943575e+00 | 0.288601 |
| 10 | trial_0008 | 0.250000 | 1.189503e-03 | 4.000000e+00 | 2.074299e-03 | -2.683129 |

## Recent Trials

- trial_0003: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, score=0.639551, failed=False
- trial_0004: drift=1.610619, temp_ratio=2.546783e-01, mass_ratio=2.500000e-01, score=0.948376, failed=False
- trial_0005: drift=2.273853, temp_ratio=5.224265e-01, mass_ratio=3.725675e-01, score=-2.712817, failed=False
- trial_0006: drift=2.367550, temp_ratio=2.168931e-01, mass_ratio=2.500000e-01, score=-2.786179, failed=False
- trial_0007: drift=1.340682, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.755224, failed=False
- trial_0008: drift=0.250000, temp_ratio=1.189503e-03, mass_ratio=4.000000e+00, score=-2.683129, failed=False
- trial_0009: drift=1.510646, temp_ratio=1.000000e-03, mass_ratio=2.500000e-01, score=0.918057, failed=False
- trial_0010: drift=1.150519, temp_ratio=1.000000e+00, mass_ratio=4.000000e+00, score=0.445094, failed=False
- trial_0011: drift=1.522543, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.930598, failed=False
- trial_0012: drift=1.534184, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.941200, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

