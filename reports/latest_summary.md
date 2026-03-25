# Latest Summary

## Campaign

- Trials completed: 0
- Drift range: [0.25, 2.5]
- Ion temperature ratio range: [0.001, 1.0]
- Ion mass range: [0.25, 4.0]
- Drift key: electron_drift_speed_x
- Score version: tail_mean_electric_field_energy_v1
- Objective: minimize the log10 of tail-mean electrostatic energy.

## Notes

- State is replayable from JSON observations in `state/optimizer_state.json`.
- Workflow artifacts mirror `state/`, `reports/`, and `results/`.
- Scheduled workflow should publish state to `agent-state`, not `main`.

