# Latest Summary

## Campaign

- Trials completed: 3
- Drift range: [0.25, 2.5]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1

## Best Result

- Trial: trial_0000
- Drift multiplier: 1.000000
- Candidate drift: 6.000000e+07
- Optimizer score: -2.606681
- Tail mean E: 2.473540e-03
- Final E: 3.735943e-03

## Recent Trials

- trial_0000: multiplier=1.000000, score=-2.606681, failed=False
- trial_0001: multiplier=1.417163, score=-2.995602, failed=False
- trial_0002: multiplier=2.065030, score=-3.010257, failed=False

## Drift-Window Investigation (2026-03-25)

Three trials have been collected across the initial range [0.25, 2.5]:

| Trial     | Multiplier | Optimizer objective | Tail mean E |
|-----------|------------|---------------------|-------------|
| trial_0000 | 1.000 | 2.607 (**best**) | 2.47 × 10⁻³ |
| trial_0001 | 1.417 | 2.996              | 1.01 × 10⁻³ |
| trial_0002 | 2.065 | 3.010              | 9.77 × 10⁻⁴ |

Key observations:
- The best result is at the baseline multiplier (1.0), which produces the highest electric-field energy saturation.
- Performance degrades monotonically as the multiplier increases above 1.0.
- No trials have yet sampled the sub-baseline region (< 1.0).

Conclusion: the upper end of the original range (above ~1.6) is clearly underperforming.
A tighter window of **[0.6, 1.6]** is justified to focus future budget on the region around
the current best while still permitting symmetric exploration below the baseline.
`configs/search.yaml` has been updated to reflect this narrowed range.

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.
- `configs/search.yaml` drift range updated from [0.25, 2.5] to [0.6, 1.6] on 2026-03-25.

