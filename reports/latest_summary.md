# Latest Summary

## Campaign

- Trials completed: 5
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
| 2 | trial_0003 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 4.360650e+00 | 0.639551 |
| 3 | trial_0001 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 2.688404e+00 | 0.429495 |
| 4 | trial_0000 | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.943575e+00 | 0.288601 |
| 5 | trial_0002 | 1.970466 | 2.660747e-02 | 3.481060e+00 | 1.422808e-03 | -2.846854 |

## Recent Trials

- trial_0000: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, score=0.288601, failed=False
- trial_0001: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, score=0.429495, failed=False
- trial_0002: drift=1.970466, temp_ratio=2.660747e-02, mass_ratio=3.481060e+00, score=-2.846854, failed=False
- trial_0003: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, score=0.639551, failed=False
- trial_0004: drift=1.610619, temp_ratio=2.546783e-01, mass_ratio=2.500000e-01, score=0.948376, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

