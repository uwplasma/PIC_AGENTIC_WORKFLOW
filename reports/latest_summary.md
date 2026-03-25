# Latest Summary

## Campaign

- Trials completed: 6
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1
- Objective: minimize the log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0005
- Drift multiplier: 2.116681
- Candidate drift: 1.270009e+08
- Ion temperature ratio: 1.543591e-02
- Ion mass over proton mass: 3.108284e+00
- Optimizer score: 3.024196
- Optimizer objective: -3.024196
- Tail mean E: 9.458102e-04
- Final E: 1.352992e-03

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0005 | 2.116681 | 1.543591e-02 | 3.108284e+00 | 9.458102e-04 | -3.024196 |
| 2 | trial_0002 | 2.065030 | 1.000000e-02 | 1.000000e+00 | 9.766588e-04 | -3.010257 |
| 3 | trial_0001 | 1.417163 | 1.000000e-02 | 1.000000e+00 | 1.010178e-03 | -2.995602 |
| 4 | trial_0004 | 2.050522 | 8.852368e-03 | 6.039016e-01 | 1.119452e-03 | -2.950994 |
| 5 | trial_0000 | 1.000000 | 1.000000e-02 | 1.000000e+00 | 2.473540e-03 | -2.606681 |
| 6 | trial_0003 | 1.417163 | 2.630512e-01 | 1.092385e+00 | 3.588426e-03 | -2.445096 |

## Recent Trials

- trial_0000: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, objective=-2.606681, failed=False
- trial_0001: drift=1.417163, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, objective=-2.995602, failed=False
- trial_0002: drift=2.065030, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, objective=-3.010257, failed=False
- trial_0003: drift=1.417163, temp_ratio=2.630512e-01, mass_ratio=1.092385e+00, objective=-2.445096, failed=False
- trial_0004: drift=2.050522, temp_ratio=8.852368e-03, mass_ratio=6.039016e-01, objective=-2.950994, failed=False
- trial_0005: drift=2.116681, temp_ratio=1.543591e-02, mass_ratio=3.108284e+00, objective=-3.024196, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

