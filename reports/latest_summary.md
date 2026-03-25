# Latest Summary

## Campaign

- Trials completed: 8
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1
- Objective: minimize the log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0004
- Drift multiplier: 0.250000
- Candidate drift: 1.500000e+07
- Ion temperature ratio: 1.000000e+00
- Ion mass over proton mass: 4.000000e+00
- Optimizer score: 2.849711
- Optimizer objective: -2.849711
- Tail mean E: 1.413477e-03
- Final E: 1.244522e-03

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0004 | 0.250000 | 1.000000e+00 | 4.000000e+00 | 1.413477e-03 | -2.849711 |
| 2 | trial_0002 | 1.970466 | 2.660747e-02 | 3.481060e+00 | 1.422808e-03 | -2.846854 |
| 3 | trial_0006 | 2.500000 | 1.000000e-03 | 3.798054e+00 | 1.484611e-03 | -2.828387 |
| 4 | trial_0007 | 0.250000 | 1.000000e+00 | 2.885806e+00 | 2.997145e-03 | -2.523292 |
| 5 | trial_0000 | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.943575e+00 | 0.288601 |
| 6 | trial_0001 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 2.688404e+00 | 0.429495 |
| 7 | trial_0005 | 1.128629 | 1.533125e-03 | 2.500000e-01 | 2.938961e+00 | 0.468194 |
| 8 | trial_0003 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 4.360650e+00 | 0.639551 |

## Recent Trials

- trial_0000: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, objective=0.288601, failed=False
- trial_0001: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, objective=0.429495, failed=False
- trial_0002: drift=1.970466, temp_ratio=2.660747e-02, mass_ratio=3.481060e+00, objective=-2.846854, failed=False
- trial_0003: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, objective=0.639551, failed=False
- trial_0004: drift=0.250000, temp_ratio=1.000000e+00, mass_ratio=4.000000e+00, objective=-2.849711, failed=False
- trial_0005: drift=1.128629, temp_ratio=1.533125e-03, mass_ratio=2.500000e-01, objective=0.468194, failed=False
- trial_0006: drift=2.500000, temp_ratio=1.000000e-03, mass_ratio=3.798054e+00, objective=-2.828387, failed=False
- trial_0007: drift=0.250000, temp_ratio=1.000000e+00, mass_ratio=2.885806e+00, objective=-2.523292, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

