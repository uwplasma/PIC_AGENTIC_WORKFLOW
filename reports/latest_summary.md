# Latest Summary

## Campaign

- Trials completed: 12
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0005
- Drift multiplier: 2.477981
- Candidate drift: 4.955963e+07
- Ion temperature ratio: 3.372570e-02
- Ion mass over proton mass: 3.801734e+00
- Optimizer score: 0.042780
- Optimizer objective: -0.042780
- Tail mean E: 1.103520e+00
- Final E: 1.165849e+00

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0005 | 2026-04-10 20:57 UTC | 2.477981 | 3.372570e-02 | 3.801734e+00 | 1.103520e+00 | 0.042780 |
| 2 | trial_0004 | 2026-04-10 20:51 UTC | 2.499108 | 4.819857e+00 | 6.003403e-01 | 1.051772e+00 | 0.021922 |
| 3 | trial_0007 | 2026-04-10 22:00 UTC | 2.488163 | 9.771405e+01 | 1.789365e+00 | 1.016955e+00 | 0.007302 |
| 4 | trial_0010 | 2026-04-11 03:27 UTC | 2.497472 | 3.803905e-03 | 1.057138e+00 | 9.483466e-01 | -0.023033 |
| 5 | trial_0011 | 2026-04-11 05:45 UTC | 2.307996 | 9.507244e+01 | 1.357109e+00 | 7.718813e-01 | -0.112449 |
| 6 | trial_0009 | 2026-04-10 23:57 UTC | 2.125038 | 7.868152e+01 | 3.969206e+00 | 7.519213e-01 | -0.123828 |
| 7 | trial_0006 | 2026-04-10 21:07 UTC | 2.495020 | 6.263080e-03 | 3.344370e+00 | 7.399855e-01 | -0.130777 |
| 8 | trial_0002 | 2026-04-10 20:04 UTC | 2.173129 | 8.068861e-03 | 3.652143e-01 | 7.317231e-01 | -0.135653 |
| 9 | trial_0008 | 2026-04-10 23:02 UTC | 2.499977 | 8.475897e+01 | 6.210031e-02 | 3.945269e-01 | -0.403923 |
| 10 | trial_0003 | 2026-04-10 20:14 UTC | 1.474236 | 5.784718e-01 | 1.037382e+00 | 1.935047e-01 | -0.713309 |
| 11 | trial_0000 | 2026-04-10 19:47 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.867578e-02 | -1.728721 |
| 12 | trial_0001 | 2026-04-10 19:54 UTC | 0.222720 | 3.885929e-01 | 4.429115e-01 | 6.986131e-04 | -3.155763 |

## Recent Trials

- trial_0002 at 2026-04-10 20:04 UTC: drift=2.173129, temp_ratio=8.068861e-03, mass_ratio=3.652143e-01, score=-0.135653, failed=False
- trial_0003 at 2026-04-10 20:14 UTC: drift=1.474236, temp_ratio=5.784718e-01, mass_ratio=1.037382e+00, score=-0.713309, failed=False
- trial_0004 at 2026-04-10 20:51 UTC: drift=2.499108, temp_ratio=4.819857e+00, mass_ratio=6.003403e-01, score=0.021922, failed=False
- trial_0005 at 2026-04-10 20:57 UTC: drift=2.477981, temp_ratio=3.372570e-02, mass_ratio=3.801734e+00, score=0.042780, failed=False
- trial_0006 at 2026-04-10 21:07 UTC: drift=2.495020, temp_ratio=6.263080e-03, mass_ratio=3.344370e+00, score=-0.130777, failed=False
- trial_0007 at 2026-04-10 22:00 UTC: drift=2.488163, temp_ratio=9.771405e+01, mass_ratio=1.789365e+00, score=0.007302, failed=False
- trial_0008 at 2026-04-10 23:02 UTC: drift=2.499977, temp_ratio=8.475897e+01, mass_ratio=6.210031e-02, score=-0.403923, failed=False
- trial_0009 at 2026-04-10 23:57 UTC: drift=2.125038, temp_ratio=7.868152e+01, mass_ratio=3.969206e+00, score=-0.123828, failed=False
- trial_0010 at 2026-04-11 03:27 UTC: drift=2.497472, temp_ratio=3.803905e-03, mass_ratio=1.057138e+00, score=-0.023033, failed=False
- trial_0011 at 2026-04-11 05:45 UTC: drift=2.307996, temp_ratio=9.507244e+01, mass_ratio=1.357109e+00, score=-0.112449, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

