# Latest Summary

## Campaign

- Trials completed: 59
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

- trial_0049: drift=0.908606, temp_ratio=1.114456e-03, mass_ratio=4.000000e+00, score=0.158491, failed=False
- trial_0050: drift=1.491875, temp_ratio=1.000000e+00, mass_ratio=4.000000e+00, score=0.698705, failed=False
- trial_0051: drift=0.613273, temp_ratio=8.847488e-03, mass_ratio=4.000000e+00, score=-0.341749, failed=False
- trial_0052: drift=1.464259, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.884267, failed=False
- trial_0053: drift=1.293888, temp_ratio=7.763624e-01, mass_ratio=2.500000e-01, score=0.716125, failed=False
- trial_0054: drift=1.066142, temp_ratio=6.999029e-03, mass_ratio=4.000000e+00, score=0.310267, failed=False
- trial_0055: drift=1.638016, temp_ratio=1.000000e+00, mass_ratio=2.500000e-01, score=0.959861, failed=False
- trial_0056: drift=2.112752, temp_ratio=1.212207e-03, mass_ratio=2.500000e-01, score=-2.980717, failed=False
- trial_0057: drift=0.409126, temp_ratio=1.840676e-03, mass_ratio=2.500000e-01, score=-1.018721, failed=False
- trial_0058: drift=0.936535, temp_ratio=5.772285e-01, mass_ratio=2.500000e-01, score=0.301022, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

