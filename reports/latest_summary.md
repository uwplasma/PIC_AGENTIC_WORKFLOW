# Latest Summary

## Campaign

- Trials completed: 43
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
| 2 | trial_0030 | 1.623804 | 1.468625e-03 | 2.663768e-01 | 1.012072e+01 | 1.005211 |
| 3 | trial_0039 | 1.550145 | 1.215525e-03 | 2.583556e-01 | 9.766342e+00 | 0.989732 |
| 4 | trial_0037 | 1.610618 | 2.546762e-01 | 2.502109e-01 | 9.406616e+00 | 0.973433 |
| 5 | trial_0029 | 1.550189 | 1.215519e-03 | 2.583534e-01 | 9.400365e+00 | 0.973145 |
| 6 | trial_0020 | 1.593855 | 1.000000e-03 | 2.500000e-01 | 9.385850e+00 | 0.972474 |
| 7 | trial_0040 | 1.728667 | 4.776756e-03 | 2.500433e-01 | 9.353437e+00 | 0.970971 |
| 8 | trial_0036 | 1.568204 | 2.438989e-01 | 2.569085e-01 | 9.323194e+00 | 0.969565 |
| 9 | trial_0028 | 1.568203 | 2.439017e-01 | 2.568994e-01 | 9.308397e+00 | 0.968875 |
| 10 | trial_0021 | 1.592669 | 1.000000e-03 | 2.500000e-01 | 9.205208e+00 | 0.964034 |

## Recent Trials

- trial_0033: drift=1.653932, temp_ratio=1.112069e-03, mass_ratio=3.889555e+00, score=0.722938, failed=False
- trial_0034: drift=1.584512, temp_ratio=1.862219e-03, mass_ratio=2.548901e-01, score=0.911428, failed=False
- trial_0035: drift=1.295744, temp_ratio=3.801622e-01, mass_ratio=3.873886e+00, score=0.446799, failed=False
- trial_0036: drift=1.568204, temp_ratio=2.438989e-01, mass_ratio=2.569085e-01, score=0.969565, failed=False
- trial_0037: drift=1.610618, temp_ratio=2.546762e-01, mass_ratio=2.502109e-01, score=0.973433, failed=False
- trial_0038: drift=1.529372, temp_ratio=7.143841e-01, mass_ratio=2.666373e-01, score=0.962539, failed=False
- trial_0039: drift=1.550145, temp_ratio=1.215525e-03, mass_ratio=2.583556e-01, score=0.989732, failed=False
- trial_0040: drift=1.728667, temp_ratio=4.776756e-03, mass_ratio=2.500433e-01, score=0.970971, failed=False
- trial_0041: drift=1.762363, temp_ratio=1.484321e-03, mass_ratio=2.500000e-01, score=0.842774, failed=False
- trial_0042: drift=1.740035, temp_ratio=6.932656e-01, mass_ratio=4.000000e+00, score=-0.054630, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

