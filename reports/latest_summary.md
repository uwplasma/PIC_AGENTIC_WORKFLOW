# Latest Summary

## Campaign

- Trials completed: 3
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1
- Objective: minimize the log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0002
- Drift multiplier: 1.970466
- Candidate drift: 1.182280e+08
- Ion temperature ratio: 2.660747e-02
- Ion mass over proton mass: 3.481060e+00
- Optimizer score: 2.846854
- Optimizer objective: -2.846854
- Tail mean E: 1.422808e-03
- Final E: 1.561873e-03

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0002 | 1.970466 | 2.660747e-02 | 3.481060e+00 | 1.422808e-03 | -2.846854 |
| 2 | trial_0000 | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.943575e+00 | 0.288601 |
| 3 | trial_0001 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 2.688404e+00 | 0.429495 |

## Recent Trials

- trial_0000: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, objective=0.288601, failed=False
- trial_0001: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, objective=0.429495, failed=False
- trial_0002: drift=1.970466, temp_ratio=2.660747e-02, mass_ratio=3.481060e+00, objective=-2.846854, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

