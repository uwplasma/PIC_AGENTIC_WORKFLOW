# Latest Summary

## Campaign

- Trials completed: 3
- Drift range: [0.01, 2.5]
- Ion temperature ratio range: [0.001, 100.0]
- Ion mass range: [0.01, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_max_v2
- Physical target: maximize the tail-mean electrostatic energy over the final window.
- Optimizer objective: minimize the negative log10 of tail-mean electrostatic energy.

## Best Result

- Trial: trial_0002
- Drift multiplier: 1.913983
- Candidate drift: 3.827965e+07
- Ion temperature ratio: 2.371407e-01
- Ion mass over proton mass: 2.962437e+00
- Optimizer score: -0.268038
- Optimizer objective: 0.268038
- Tail mean E: 5.394634e-01
- Final E: 6.141308e-01

## Leaderboard

| Rank | Trial | Started | Drift x Base | Ion Temp Ratio | Ion Mass / Proton | Tail Mean E | Score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | trial_0002 | 2026-04-09 14:52 UTC | 1.913983 | 2.371407e-01 | 2.962437e+00 | 5.394634e-01 | -0.268038 |
| 2 | trial_0001 | 2026-04-09 14:50 UTC | 1.301660 | 1.079942e+01 | 2.420796e-01 | 4.571948e-02 | -1.339899 |
| 3 | trial_0000 | 2026-04-09 14:48 UTC | 1.000000 | 1.000000e-02 | 1.000000e+00 | 1.867578e-02 | -1.728721 |

## Recent Trials

- trial_0000 at 2026-04-09 14:48 UTC: drift=1.000000, temp_ratio=1.000000e-02, mass_ratio=1.000000e+00, score=-1.728721, failed=False
- trial_0001 at 2026-04-09 14:50 UTC: drift=1.301660, temp_ratio=1.079942e+01, mass_ratio=2.420796e-01, score=-1.339899, failed=False
- trial_0002 at 2026-04-09 14:52 UTC: drift=1.913983, temp_ratio=2.371407e-01, mass_ratio=2.962437e+00, score=-0.268038, failed=False

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow writes state, reports, and results directly to `main`.

