# Latest Summary

## Campaign

- Trials completed: 23
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0014
- Drift multiplier: 1.556915
- Candidate drift: 9.341492e+07
- Ion temperature ratio: 1.000000e+00
- Ion mass over proton mass: 2.500000e-01
- Optimizer score: 1.047918
- Optimizer objective: -1.047918
- Tail mean E: 1.116652e+01
- Final E: 1.296134e+01

## Leaderboard

| Rank | Trial | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0014 | 1.556915 | 1.000000e+00 | 2.500000e-01 | 1.116652e+01 | 1.047918 |
| 2 | trial_0020 | 1.593855 | 1.000000e-03 | 2.500000e-01 | 9.385850e+00 | 0.972474 |
| 3 | trial_0021 | 1.592669 | 1.000000e-03 | 2.500000e-01 | 9.205208e+00 | 0.964034 |
| 4 | trial_0004 | 1.610619 | 2.546783e-01 | 2.500000e-01 | 8.879253e+00 | 0.948376 |
| 5 | trial_0012 | 1.534184 | 1.000000e+00 | 2.500000e-01 | 8.733743e+00 | 0.941200 |
| 6 | trial_0013 | 1.548860 | 1.000000e-03 | 2.500000e-01 | 8.655493e+00 | 0.937292 |
| 7 | trial_0011 | 1.522543 | 1.000000e+00 | 2.500000e-01 | 8.523101e+00 | 0.930598 |
| 8 | trial_0009 | 1.510646 | 1.000000e-03 | 2.500000e-01 | 8.280516e+00 | 0.918057 |
| 9 | trial_0019 | 1.599256 | 1.000000e+00 | 4.000000e+00 | 6.514460e+00 | 0.813878 |
| 10 | trial_0016 | 1.675581 | 1.000000e+00 | 2.500000e-01 | 6.375680e+00 | 0.804526 |

## Recent Trials

- trial_0013: drift=1.548860, temp_ratio=1.000000e-03, mass_ratio=2.500000e-01, score=0.937292, failed=False
- trial_0014: drift=1.556915, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=1.047918, failed=False
- trial_0015: drift=0.688840, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=-0.091474, failed=False
- trial_0016: drift=1.675581, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.804526, failed=False
- trial_0017: drift=1.066581, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.485743, failed=False
- trial_0018: drift=0.250000, temp_ratio=6.537736e-01, mass_ratio=2.500000e-01, score=-2.709946, failed=False
- trial_0019: drift=1.599256, temp_ratio=1.000000e+00, mass_ratio=4.000000e+00, score=0.813878, failed=False
- trial_0020: drift=1.593855, temp_ratio=1.000000e-03, mass_ratio=2.500000e-01, score=0.972474, failed=False
- trial_0021: drift=1.592669, temp_ratio=1.000000e-03, mass_ratio=2.500000e-01, score=0.964034, failed=False
- trial_0022: drift=1.242376, temp_ratio=1.000000e-03, mass_ratio=2.500000e-01, score=0.692072, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

