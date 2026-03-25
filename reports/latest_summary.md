# Latest Summary

## Campaign

- Trials completed: 24
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1
- Objective: minimize the log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0008
- Drift multiplier: 2.499582
- Candidate drift: 1.499749e+08
- Ion temperature ratio: 8.241718e-03
- Ion mass over proton mass: 1.434882e+00
- Optimizer score: 3.154492
- Optimizer objective: -3.154492
- Tail mean E: 7.006616e-04
- Final E: 1.338988e-03

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Objective |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0008 | 2.499582 | 8.241718e-03 | 1.434882e+00 | 7.006616e-04 | -3.154492 |
| 2 | trial_0011 | 2.490286 | 1.059422e-02 | 1.043739e+00 | 8.958936e-04 | -3.047744 |
| 3 | trial_0007 | 2.499613 | 3.853876e-02 | 1.467770e+00 | 9.064891e-04 | -3.042637 |
| 4 | trial_0002 | 2.065030 | 1.000000e-02 | 1.000000e+00 | 9.766588e-04 | -3.010257 |
| 5 | trial_0001 | 1.417163 | 1.000000e-02 | 1.000000e+00 | 1.010178e-03 | -2.995602 |
| 6 | trial_0019 | 2.113674 | 1.136719e-02 | 1.873329e+00 | 1.045518e-03 | -2.980668 |
| 7 | trial_0016 | 2.499457 | 4.244457e-03 | 1.035684e+00 | 1.153987e-03 | -2.937799 |
| 8 | trial_0004 | 2.172311 | 1.229421e-02 | 1.167692e+00 | 1.251461e-03 | -2.902583 |
| 9 | trial_0005 | 2.350411 | 1.455699e-03 | 2.640412e-01 | 1.354111e-03 | -2.868346 |
| 10 | trial_0006 | 2.015285 | 5.549261e-01 | 4.873775e-01 | 1.472179e-03 | -2.832039 |

## Recent Trials

- trial_0014: drift=2.494322, temp_ratio=1.068982e-02, mass_ratio=2.797835e-01, objective=-2.479243, failed=False
- trial_0015: drift=2.471293, temp_ratio=2.066332e-02, mass_ratio=1.876440e+00, objective=-2.793399, failed=False
- trial_0016: drift=2.499457, temp_ratio=4.244457e-03, mass_ratio=1.035684e+00, objective=-2.937799, failed=False
- trial_0017: drift=2.329854, temp_ratio=2.213720e-03, mass_ratio=1.222580e+00, objective=-2.667667, failed=False
- trial_0018: drift=2.497420, temp_ratio=7.894048e-03, mass_ratio=1.001088e+00, objective=-2.740288, failed=False
- trial_0019: drift=2.113674, temp_ratio=1.136719e-02, mass_ratio=1.873329e+00, objective=-2.980668, failed=False
- trial_0020: drift=2.492328, temp_ratio=9.917124e-03, mass_ratio=2.372967e+00, objective=-2.773748, failed=False
- trial_0021: drift=1.964923, temp_ratio=2.758074e-02, mass_ratio=1.744641e+00, objective=-2.823329, failed=False
- trial_0022: drift=1.791485, temp_ratio=9.894254e-03, mass_ratio=3.562157e+00, objective=-2.696091, failed=False
- trial_0023: drift=2.416092, temp_ratio=2.460280e-02, mass_ratio=1.255054e+00, objective=-2.693135, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

